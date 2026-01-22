from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
import sys, os, datetime, csv, io
import certifi
from dotenv import load_dotenv

# Optional PDF generation (not available on Vercel)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PDF generation not available (reportlab not installed)")

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Fix path to allow importing agent
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import AI Agent modules - CRITICAL IMPORTS
from agent.advanced_agent import AdvancedTourAgent
from agent.nlp_utils import extract_keywords

# Optional imports with fallback
try:
    from agent.external_apis import ExternalAPIIntegration
except ImportError:
    ExternalAPIIntegration = None
    print("⚠️ External APIs not available")

# Define extract_features function if not available
def extract_features(pkg, budget, days, interests):
    """Extract features from package for ML model"""
    return {
        'price': pkg.get('price', 0),
        'days': pkg.get('days', 0),
        'interest_match': len(set(pkg.get('interests', [])) & set(interests)),
        'budget_ratio': pkg.get('price', 0) / max(budget, 1)
    } 

# Configure Flask with explicit paths for static and template folders
app = Flask(__name__, 
    static_folder=os.path.join(current_dir, 'static'),
    template_folder=os.path.join(current_dir, 'templates'))

# Load configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret-key-123')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/AITourReccomendation')

# SSL Context for Atlas
mongo = PyMongo(app, tlsCAFile=certifi.where())
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

CSV_PATH = os.path.join(parent_dir, 'data', 'training_data.csv')

class User(UserMixin):
    def __init__(self, d):
        self.id = str(d['_id'])
        self.name = d.get('name', 'User')
        self.email = d.get('email', '')

@login_manager.user_loader
def load(uid):
    if mongo.db is None: return None
    u = mongo.db.users.find_one({'_id': ObjectId(uid)})
    return User(u) if u else None

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        if mongo.db is None:
            flash('Database Connection Failed! Check URL.')
            return render_template('login.html')
            
        u = mongo.db.users.find_one({'email': request.form['email']})
        if u and bcrypt.check_password_hash(u['password'], request.form['password']):
            login_user(User(u))
            return redirect(url_for('index'))
        flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        if mongo.db is None:
            flash('Database Connection Failed! Check URL.')
            return render_template('register.html')
            
        if mongo.db.users.find_one({'email': request.form['email']}):
            flash('Email exists')
        else:
            pw = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            mongo.db.users.insert_one({'name':request.form['name'], 'email':request.form['email'], 'password':pw})
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/')
@login_required
def index(): return render_template('index.html', user=current_user)

@app.route('/plan', methods=['POST'])
@login_required
def plan():
    try:
        if mongo.db is None: 
            return jsonify({'success': False, 'message': 'Database connection error'}), 500
        
        # Validate request data
        if not request.json:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
        
        # Use Advanced AI Agent - SPEED OPTIMIZED
        agent = AdvancedTourAgent(mongo.db.tour_packages, user_id=current_user.id)
        result = agent.plan_tour(request.json)
        
        # Skip external API calls for faster response (weather etc.)
        # Can be enabled later if needed
        
        return jsonify(result), 200
        
    except Exception as e:
        # Log the error for debugging
        print(f"ERROR in /plan endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return JSON error response
        return jsonify({
            'success': False, 
            'message': f'Server error: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/book', methods=['POST'])
@login_required
def book():
    data = request.json
    booking_id = mongo.db.bookings.insert_one({
        'user_id': current_user.id, 
        'plan': data['plan'], 
        'activities': data['activities'], 
        'total_cost': data['total_cost'], 
        'created_at': datetime.datetime.utcnow()
    }).inserted_id
    
    try:
        goals = data.get('user_goals', {})
        pkg = data['plan']
        u_budget = goals.get('budget', pkg['price'])
        u_days = goals.get('days', pkg['days'])
        u_interests = goals.get('interests', [])
        features = extract_features(pkg, u_budget, u_days, u_interests)
        with open(CSV_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(features + [5.0])
    except: pass
        
    return jsonify({'success': True, 'booking_id': str(booking_id)})

@app.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """
    NEW: Feedback endpoint - Agent learns from user feedback
    """
    data = request.json
    booking_id = data.get('booking_id')
    rating = float(data.get('rating', 0))
    feedback_text = data.get('feedback', '')
    
    # Save feedback to database
    mongo.db.feedback.insert_one({
        'booking_id': booking_id,
        'user_id': current_user.id,
        'rating': rating,
        'feedback': feedback_text,
        'created_at': datetime.datetime.utcnow()
    })
    
    # Let the agent learn from this feedback
    try:
        agent = AdvancedTourAgent(mongo.db.tour_packages, user_id=current_user.id)
        
        # Get booking details
        booking = mongo.db.bookings.find_one({'_id': ObjectId(booking_id)})
        if booking:
            feedback_data = {
                'interests': booking['plan'].get('interests', []),
                'destinations': booking['plan'].get('destinations', []),
                'budget': booking['total_cost'],
                'package': booking['plan']
            }
            
            # Agent learns from this feedback
            agent.learn_from_feedback(booking_id, rating, feedback_data)
    except Exception as e:
        print(f"⚠️ Agent learning error: {e}")
    
    return jsonify({'success': True, 'message': 'Thank you for your feedback! I learned from it.'})

@app.route('/agent/status')
@login_required
def agent_status():
    """
    NEW: Get agent status and personalization info
    """
    try:
        agent = AdvancedTourAgent(mongo.db.tour_packages, user_id=current_user.id)
        
        return jsonify({
            'success': True,
            'agent_state': agent.get_agent_state(),
            'profile_summary': agent.personalizer.get_profile_summary(),
            'ml_stats': agent.ml_model.get_stats()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/logout')
def logout(): logout_user(); return redirect(url_for('login'))

@app.route('/data/<path:filename>')
def serve_data_file(filename):
    """Serve data files like JSON"""
    try:
        data_dir = os.path.join(parent_dir, 'data')
        return send_file(os.path.join(data_dir, filename), mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/history')
@login_required
def history():
    bookings = list(mongo.db.bookings.find({'user_id': current_user.id}).sort('created_at', -1))
    return render_template('history.html', bookings=bookings)

@app.route('/download_pdf/<booking_id>')
@login_required
def download_pdf(booking_id):
    # Check if PDF generation is available
    if not PDF_AVAILABLE:
        flash('PDF generation is not available on this server')
        return redirect(url_for('history'))
    
    booking = mongo.db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': current_user.id})
    if not booking: return redirect(url_for('history'))
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFillColorRGB(0,0,0.5)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(72, height - 72, "Wanderlust AI Itinerary")
    
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 100, f"Traveler: {current_user.name}")
    c.drawString(72, height - 115, f"Trip: {booking['plan']['name']}")
    c.drawString(72, height - 130, f"Cost: ${booking['total_cost']} | Duration: {booking['plan']['days']} Days")
    
    y = height - 180
    activities = booking.get('activities', [])
    days = {}
    for act in activities:
        d = act.get('day', 1)
        if d not in days: days[d] = []
        days[d].append(act)
        
    sorted_days = sorted(days.keys())
    
    for day_num in sorted_days:
        if y < 100: c.showPage(); y = height - 72
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, y, f"Day {day_num}")
        y -= 20
        c.setFont("Helvetica", 11)
        day_acts = days[day_num]
        time_order = {"Morning": 1, "Afternoon": 2, "Evening": 3}
        day_acts.sort(key=lambda x: time_order.get(x.get('time', ''), 4))
        for act in day_acts:
            text = f"• [{act.get('time','Any')}] {act['name']} - ${act.get('cost', 0)}"
            c.drawString(90, y, text)
            y -= 15
        y -= 15
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='My_Trip_Plan.pdf', mimetype='application/pdf')

# For Vercel serverless deployment
if __name__ != '__main__':
    # Running on Vercel - disable debug mode
    app.debug = False

if __name__ == '__main__': 
    # Local development
    app.run(debug=True, host='0.0.0.0', port=5000)
