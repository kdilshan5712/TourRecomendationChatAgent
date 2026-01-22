# 🚀 Deployment Guide

## Environment Configuration

### Local Development

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your values:**
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/AITourReccomendation
   SECRET_KEY=your-random-secret-key-here
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

3. **Start server:**
   ```bash
   cd ui
   python app.py
   ```

---

## Hosting Options

### Option 1: Vercel (Serverless - Best for Quick Deploy)

⚠️ **Note:** Vercel has 10-second timeout limit. ML features may be slower on cold starts.

**Quick Deploy:**

1. **Install Vercel CLI (optional):**
   ```bash
   npm install -g vercel
   ```

2. **Deploy from dashboard:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel auto-detects the configuration from `vercel.json`

3. **Add Environment Variables in Vercel Dashboard:**
   - Go to Project Settings → Environment Variables
   - Add `MONGO_URI` = `your_mongodb_connection_string`
   - Add `SECRET_KEY` = `your_secret_key`
   - Add `FLASK_ENV` = `production`

4. **Deploy:**
   - Click "Deploy"
   - Your app will be live at `your-project.vercel.app`

**Using CLI:**
```bash
# Login to Vercel
vercel login

# Deploy
vercel

# Add environment variables
vercel env add MONGO_URI
vercel env add SECRET_KEY

# Deploy to production
vercel --prod
```

**Files Created:**
- ✅ `vercel.json` - Configuration
- ✅ `index.py` - Entry point
- ✅ `.vercelignore` - Ignore files

---

### Option 2: Render (Recommended for Flask)

**Best choice for Flask apps with ML!** Free tier with 750 hours/month.

1. **Go to [render.com](https://render.com)**

2. **Create New Web Service**

3. **Connect your GitHub repository**

4. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd ui && gunicorn app:app`
   - **Environment:** Python 3

5. **Add Environment Variables:**
   - `MONGO_URI` = your MongoDB connection string
   - `SECRET_KEY` = your secret key
   - `FLASK_ENV` = production

6. **Deploy** - Render will auto-deploy from GitHub

---

### Option 3: PythonAnywhere

1. **Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)**

2. **Upload your code** via Git or Files

3. **Create Web App:**
   - Choose Flask
   - Python 3.10+

4. **Configure WSGI file:**
   ```python
   import sys
   import os
   
   # Add your project directory
   project_home = '/home/yourusername/tour_ai_final'
   sys.path.insert(0, project_home)
   
   # Load environment variables
   from dotenv import load_dotenv
   load_dotenv(os.path.join(project_home, '.env'))
   
   # Import your app
   from ui.app import app as application
   ```

5. **Set environment variables** in PythonAnywhere dashboard

6. **Reload web app**

---

### Option 4: Railway

1. **Go to [railway.app](https://railway.app)**

2. **Connect GitHub repository**

3. **Add environment variables:**
   - `MONGO_URI`
   - `SECRET_KEY`
   - `FLASK_ENV=production`

4. **Railway auto-detects Python** and deploys

---

### Option 5: DigitalOcean App Platform

1. **Create account at [digitalocean.com](https://www.digitalocean.com)**

2. **Create App from GitHub**

3. **Configure:**
   - **Run Command:** `cd ui && gunicorn app:app`
   - **HTTP Port:** 8080

4. **Add environment variables** in App settings

5. **Deploy**

---

## Security Checklist

Before deploying to production:

- [ ] `.env` file is NOT committed to Git (check `.gitignore`)
- [ ] Generated a strong random SECRET_KEY
- [ ] MongoDB connection string uses a strong password
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] MongoDB Atlas has IP whitelist configured (or 0.0.0.0/0 for cloud hosts)
- [ ] Enabled HTTPS on your hosting platform

---

## Generating a Strong Secret Key

```python
# Run this to generate a secure secret key
import secrets
print(secrets.token_hex(32))
```

---

## MongoDB Atlas Setup

1. **Create cluster** at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

2. **Create database user** with password

3. **Get connection string:**
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your password
   - Add database name: `/AITourReccomendation?`

4. **Whitelist IPs:**
   - For development: Add your IP
   - For production: Add `0.0.0.0/0` (allow all) or your hosting platform's IPs

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb+srv://...` |
| `SECRET_KEY` | Flask session secret (64 chars) | `a1b2c3d4...` |
| `FLASK_ENV` | Environment mode | `production` or `development` |
| `FLASK_DEBUG` | Debug mode | `False` for production |

---

## Troubleshooting Deployment

### Issue: "ModuleNotFoundError"
**Solution:** Ensure `requirements.txt` is up to date
```bash
pip freeze > requirements.txt
```

### Issue: "Database connection error"
**Solution:** 
- Check MONGO_URI is correct
- Verify MongoDB Atlas IP whitelist
- Check if password has special characters (URL encode them)

### Issue: "Application Error" on Heroku
**Solution:**
```bash
heroku logs --tail  # Check logs for errors
```

### Issue: Static files not loading
**Solution:** Configure static file serving in production
```python
# Add to app.py for production
from whitenoise import WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
```

---

## Post-Deployment Checklist

- [ ] Test registration and login
- [ ] Test tour generation
- [ ] Verify map displays correctly
- [ ] Check database connections
- [ ] Monitor application logs
- [ ] Set up error monitoring (e.g., Sentry)
- [ ] Configure custom domain (optional)

---

**Ready to deploy!** Choose your hosting platform and follow the steps above.
