"""
Personalization Engine - Learns user preferences over time
Creates personalized experiences based on history
"""
from typing import Dict, List
import json
import os
from datetime import datetime
from collections import defaultdict


class PersonalizationEngine:
    """
    Builds user profiles and personalizes recommendations
    - Tracks user preferences
    - Learns from feedback
    - Adapts recommendations
    """
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.profile_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'user_profiles'
        )
        os.makedirs(self.profile_dir, exist_ok=True)
        
        self.profile = self._load_profile()
    
    def _load_profile(self) -> Dict:
        """Load user profile or create new one"""
        if not self.user_id:
            return self._default_profile()
        
        profile_path = os.path.join(self.profile_dir, f'{self.user_id}.json')
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return self._default_profile()
    
    def _default_profile(self) -> Dict:
        """Create default user profile"""
        return {
            'user_id': self.user_id,
            'created_at': datetime.utcnow().isoformat(),
            'preferences': {
                'interests': defaultdict(float),  # Interest: score
                'budget_range': [500, 2000],
                'avg_trip_days': 7,
                'accommodation_preference': 'standard',
                'pace_preference': 'moderate'
            },
            'history': {
                'total_bookings': 0,
                'total_feedback': 0,
                'avg_rating': 0.0,
                'favorite_destinations': [],
                'avoided_interests': []
            },
            'traits': {
                'adventure_seeker': 0.5,
                'cultural_enthusiast': 0.5,
                'luxury_traveler': 0.5,
                'budget_conscious': 0.5,
                'nature_lover': 0.5
            }
        }
    
    def get_preferences(self) -> List[Dict]:
        """
        Get personalized preferences based on profile
        """
        prefs = []
        
        # Top interests
        interests = self.profile['preferences']['interests']
        if interests:
            top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:3]
            for interest, score in top_interests:
                if score > 0.3:
                    prefs.append({
                        'type': 'interest',
                        'value': interest,
                        'weight': score,
                        'source': 'learned'
                    })
        
        # Budget preference
        budget_range = self.profile['preferences']['budget_range']
        prefs.append({
            'type': 'budget_range',
            'value': budget_range,
            'source': 'learned'
        })
        
        # Pace preference
        pace = self.profile['preferences']['pace_preference']
        if pace != 'moderate':
            prefs.append({
                'type': 'pace',
                'value': pace,
                'source': 'learned'
            })
        
        return prefs
    
    def update_from_feedback(self, rating: float, feedback: Dict):
        """
        Update user profile based on feedback
        This is where personalization learning happens
        """
        # Update history
        self.profile['history']['total_feedback'] += 1
        
        # Update average rating
        current_avg = self.profile['history']['avg_rating']
        total = self.profile['history']['total_feedback']
        new_avg = ((current_avg * (total - 1)) + rating) / total
        self.profile['history']['avg_rating'] = new_avg
        
        # Learn from interests
        if 'interests' in feedback:
            for interest in feedback['interests']:
                # Positive feedback increases interest score
                if rating >= 4:
                    self.profile['preferences']['interests'][interest] = \
                        min(1.0, self.profile['preferences']['interests'].get(interest, 0.5) + 0.1)
                # Negative feedback decreases interest score
                elif rating <= 2:
                    self.profile['preferences']['interests'][interest] = \
                        max(0.0, self.profile['preferences']['interests'].get(interest, 0.5) - 0.1)
                    
                    # Track avoided interests
                    if rating == 1:
                        avoided = self.profile['history']['avoided_interests']
                        if interest not in avoided:
                            avoided.append(interest)
        
        # Learn from destinations
        if 'destinations' in feedback and rating >= 4:
            for dest in feedback['destinations']:
                favs = self.profile['history']['favorite_destinations']
                if dest not in favs:
                    favs.append(dest)
        
        # Update traits based on booking patterns
        if 'package' in feedback:
            self._update_traits(feedback['package'], rating)
        
        # Update budget preference
        if 'budget' in feedback:
            self._update_budget_range(feedback['budget'])
        
        # Save profile
        self._save_profile()
    
    def _update_traits(self, package: Dict, rating: float):
        """Update personality traits based on package preference"""
        traits = self.profile['traits']
        
        # Adventure seeker
        if 'adventure' in package.get('interests', []):
            if rating >= 4:
                traits['adventure_seeker'] = min(1.0, traits['adventure_seeker'] + 0.1)
            elif rating <= 2:
                traits['adventure_seeker'] = max(0.0, traits['adventure_seeker'] - 0.1)
        
        # Cultural enthusiast
        if 'culture' in package.get('interests', []):
            if rating >= 4:
                traits['cultural_enthusiast'] = min(1.0, traits['cultural_enthusiast'] + 0.1)
        
        # Luxury vs Budget
        hotel_level = package.get('hotel_level', 'standard').lower()
        if hotel_level == 'luxury' and rating >= 4:
            traits['luxury_traveler'] = min(1.0, traits['luxury_traveler'] + 0.15)
            traits['budget_conscious'] = max(0.0, traits['budget_conscious'] - 0.1)
        elif hotel_level == 'budget' and rating >= 4:
            traits['budget_conscious'] = min(1.0, traits['budget_conscious'] + 0.15)
            traits['luxury_traveler'] = max(0.0, traits['luxury_traveler'] - 0.1)
        
        # Nature lover
        nature_interests = {'nature', 'hiking', 'wildlife', 'beach'}
        if any(i in package.get('interests', []) for i in nature_interests):
            if rating >= 4:
                traits['nature_lover'] = min(1.0, traits['nature_lover'] + 0.1)
    
    def _update_budget_range(self, budget: float):
        """Update budget range based on actual spending"""
        current_range = self.profile['preferences']['budget_range']
        
        # Expand range if needed
        if budget < current_range[0]:
            current_range[0] = int(budget * 0.9)
        if budget > current_range[1]:
            current_range[1] = int(budget * 1.1)
    
    def _save_profile(self):
        """Save user profile to disk"""
        if not self.user_id:
            return
        
        profile_path = os.path.join(self.profile_dir, f'{self.user_id}.json')
        
        try:
            # Convert defaultdict to regular dict for JSON serialization
            profile_copy = json.loads(json.dumps(self.profile, default=dict))
            
            with open(profile_path, 'w') as f:
                json.dump(profile_copy, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save profile: {e}")
    
    def get_recommendations(self, available_packages: List[Dict], count: int = 3) -> List[Dict]:
        """
        Get personalized package recommendations
        """
        scored_packages = []
        
        for pkg in available_packages:
            score = self._score_package(pkg)
            scored_packages.append({
                'package': pkg,
                'personalization_score': score
            })
        
        # Sort by score and return top N
        scored_packages.sort(key=lambda x: x['personalization_score'], reverse=True)
        return scored_packages[:count]
    
    def _score_package(self, package: Dict) -> float:
        """
        Score a package based on user profile
        """
        score = 0.0
        
        # Interest alignment
        pkg_interests = set(package.get('interests', []))
        for interest, weight in self.profile['preferences']['interests'].items():
            if interest in pkg_interests:
                score += weight * 10
        
        # Avoid disliked interests
        avoided = self.profile['history']['avoided_interests']
        if any(interest in avoided for interest in pkg_interests):
            score -= 5
        
        # Budget fit
        budget_range = self.profile['preferences']['budget_range']
        if budget_range[0] <= package['price'] <= budget_range[1]:
            score += 3
        
        # Favorite destinations
        favorite_dests = self.profile['history']['favorite_destinations']
        pkg_dests = set(package.get('destinations', []))
        if any(dest in favorite_dests for dest in pkg_dests):
            score += 5
        
        # Trait alignment
        traits = self.profile['traits']
        if 'luxury' in package.get('hotel_level', '').lower() and traits['luxury_traveler'] > 0.7:
            score += 4
        if 'adventure' in pkg_interests and traits['adventure_seeker'] > 0.7:
            score += 4
        if 'culture' in pkg_interests and traits['cultural_enthusiast'] > 0.7:
            score += 4
        
        return score
    
    def get_profile_summary(self) -> Dict:
        """Get human-readable profile summary"""
        traits = self.profile['traits']
        
        # Find dominant trait
        dominant_trait = max(traits.items(), key=lambda x: x[1])
        
        # Top interests
        interests = self.profile['preferences']['interests']
        top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'personality': dominant_trait[0].replace('_', ' ').title(),
            'top_interests': [i[0] for i in top_interests],
            'avg_rating': self.profile['history']['avg_rating'],
            'total_trips': self.profile['history']['total_bookings'],
            'budget_range': self.profile['preferences']['budget_range']
        }
