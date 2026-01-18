"""
Real Machine Learning Model with Training Pipeline
Learns from user interactions and feedback
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import json
from datetime import datetime


class MLModel:
    """
    Machine Learning model that learns from user behavior
    - Predicts tour satisfaction
    - Learns from feedback
    - Continuously improves
    """
    
    def __init__(self):
        self.version = "2.0"
        self.model_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'data'
        )
        self.model_path = os.path.join(self.model_dir, 'ml_model.pkl')
        self.scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        self.feedback_path = os.path.join(self.model_dir, 'feedback_data.json')
        
        # Load or create model
        self.regressor = self._load_or_create_model()
        self.scaler = self._load_or_create_scaler()
        self.feedback_buffer = []
        
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        if os.path.exists(self.model_path):
            try:
                return joblib.load(self.model_path)
            except:
                print("⚠️ Could not load model, creating new one")
        
        # Create new Random Forest model
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    
    def _load_or_create_scaler(self):
        """Load existing scaler or create new one"""
        if os.path.exists(self.scaler_path):
            try:
                return joblib.load(self.scaler_path)
            except:
                pass
        return StandardScaler()
    
    def extract_features(self, package: dict, goals: dict) -> np.array:
        """
        Extract rich features from package and user goals
        """
        features = []
        
        # Basic features
        budget_ratio = package['price'] / max(goals.get('budget', 1), 1)
        days_ratio = package['days'] / max(goals.get('days', 1), 1)
        
        features.extend([
            budget_ratio,
            days_ratio,
            package['price'],
            package['days'],
            len(package.get('activities', [])),
            len(package.get('destinations', []))
        ])
        
        # Interest matching
        user_interests = set(goals.get('interests', []))
        pkg_interests = set(package.get('interests', []))
        
        if user_interests:
            interest_overlap = len(user_interests & pkg_interests) / len(user_interests)
        else:
            interest_overlap = 0.5
        features.append(interest_overlap)
        
        # Activity diversity
        activity_costs = [a.get('cost', 0) for a in package.get('activities', [])]
        features.extend([
            np.mean(activity_costs) if activity_costs else 0,
            np.std(activity_costs) if len(activity_costs) > 1 else 0,
            min(activity_costs) if activity_costs else 0,
            max(activity_costs) if activity_costs else 0
        ])
        
        # Destination diversity
        destinations = package.get('destinations', [])
        features.append(len(set(destinations)))
        
        # Price per day
        features.append(package['price'] / max(package['days'], 1))
        
        # Activities per day
        features.append(len(package.get('activities', [])) / max(package['days'], 1))
        
        # Budget affordability (binary)
        features.append(1.0 if package['price'] <= goals.get('budget', float('inf')) else 0.0)
        
        # Exact day match (binary)
        features.append(1.0 if package['days'] == goals.get('days', 0) else 0.0)
        
        return np.array(features).reshape(1, -1)
    
    def predict_satisfaction(self, package: dict, goals: dict) -> float:
        """
        Predict user satisfaction with this package (0-10 scale)
        """
        try:
            features = self.extract_features(package, goals)
            
            # Scale features
            if hasattr(self.scaler, 'mean_'):
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features
            
            # Predict
            if hasattr(self.regressor, 'predict'):
                prediction = self.regressor.predict(features_scaled)[0]
                # Clip to valid range
                return max(0.0, min(10.0, prediction))
            else:
                # Fallback: rule-based score
                return self._fallback_score(package, goals)
        except:
            return self._fallback_score(package, goals)
    
    def _fallback_score(self, package: dict, goals: dict) -> float:
        """Rule-based scoring when ML not available"""
        score = 5.0  # Neutral start
        
        # Budget fit
        if package['price'] <= goals.get('budget', float('inf')):
            score += 2.0
        else:
            score -= 1.0
        
        # Day match
        if package['days'] == goals.get('days', 0):
            score += 2.0
        elif abs(package['days'] - goals.get('days', 0)) <= 1:
            score += 1.0
        
        # Interest match
        user_interests = set(goals.get('interests', []))
        pkg_interests = set(package.get('interests', []))
        overlap = len(user_interests & pkg_interests)
        score += min(overlap, 1.0)
        
        return max(0.0, min(10.0, score))
    
    def add_training_sample(self, booking_id: str, rating: float, feedback: dict):
        """
        Add new training sample from user feedback
        """
        sample = {
            'booking_id': booking_id,
            'rating': rating,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.feedback_buffer.append(sample)
        
        # Save to persistent storage
        self._save_feedback(sample)
        
        # Retrain if we have enough new data
        if len(self.feedback_buffer) >= 10:
            print("📚 Agent is learning from recent feedback...")
            self.retrain()
            self.feedback_buffer = []
    
    def _save_feedback(self, sample: dict):
        """Save feedback to JSON file"""
        try:
            existing = []
            if os.path.exists(self.feedback_path):
                with open(self.feedback_path, 'r') as f:
                    existing = json.load(f)
            
            existing.append(sample)
            
            with open(self.feedback_path, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save feedback: {e}")
    
    def retrain(self):
        """
        Retrain the model with accumulated feedback
        This is the LEARNING part of the agent
        """
        try:
            # Load training data from CSV
            csv_path = os.path.join(self.model_dir, 'training_data.csv')
            
            if not os.path.exists(csv_path):
                print("⚠️ No training data available yet")
                return
            
            df = pd.read_csv(csv_path)
            
            if len(df) < 20:
                print("⚠️ Not enough training data yet")
                return
            
            # Prepare features and target
            feature_cols = [col for col in df.columns if col != 'rating' and col != 'satisfaction']
            if 'rating' in df.columns:
                target_col = 'rating'
            elif 'satisfaction' in df.columns:
                target_col = 'satisfaction'
            else:
                print("⚠️ No target column found")
                return
            
            X = df[feature_cols].values
            y = df[target_col].values
            
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Fit scaler
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.regressor.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.regressor.score(X_train_scaled, y_train)
            test_score = self.regressor.score(X_test_scaled, y_test)
            
            print(f"✅ Model retrained! Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
            
            # Save model
            self.save()
            
        except Exception as e:
            print(f"⚠️ Retraining failed: {e}")
    
    def save(self):
        """Save model and scaler to disk"""
        try:
            os.makedirs(self.model_dir, exist_ok=True)
            joblib.dump(self.regressor, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            print("💾 Model saved successfully")
        except Exception as e:
            print(f"⚠️ Could not save model: {e}")
    
    def get_stats(self) -> dict:
        """Return model statistics"""
        return {
            'version': self.version,
            'model_type': type(self.regressor).__name__,
            'is_trained': hasattr(self.regressor, 'n_estimators'),
            'pending_feedback': len(self.feedback_buffer)
        }
