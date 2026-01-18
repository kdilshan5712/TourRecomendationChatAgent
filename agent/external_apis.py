"""
External API Integration - Weather, Currency, and Real-time Data
Makes the agent aware of real-world conditions
"""
import requests
from typing import Dict, List
from datetime import datetime
import json


class WeatherAPI:
    """
    Integrate real-time weather data for intelligent planning
    """
    
    def __init__(self):
        # Using free OpenMeteo API (no key required)
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
        # Sri Lankan city coordinates
        self.locations = {
            "Colombo": {"lat": 6.927, "lon": 79.861},
            "Kandy": {"lat": 7.290, "lon": 80.633},
            "Sigiriya": {"lat": 7.957, "lon": 80.760},
            "Ella": {"lat": 6.866, "lon": 81.046},
            "Mirissa": {"lat": 5.948, "lon": 80.471},
            "Galle": {"lat": 6.053, "lon": 80.221},
            "Yala": {"lat": 6.383, "lon": 81.500},
            "Nuwara Eliya": {"lat": 6.949, "lon": 80.789}
        }
    
    def get_weather_forecast(self, city: str, days: int = 7) -> Dict:
        """
        Get weather forecast for a city
        """
        if city not in self.locations:
            return None
        
        coords = self.locations[city]
        
        try:
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                "forecast_days": min(days, 16),
                "timezone": "Asia/Colombo"
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather(data)
            
        except Exception as e:
            print(f"⚠️ Weather API error: {e}")
        
        return None
    
    def _parse_weather(self, data: Dict) -> Dict:
        """Parse weather API response"""
        daily = data.get('daily', {})
        
        return {
            'temperatures_max': daily.get('temperature_2m_max', []),
            'temperatures_min': daily.get('temperature_2m_min', []),
            'precipitation': daily.get('precipitation_sum', []),
            'weather_codes': daily.get('weathercode', []),
            'dates': daily.get('time', [])
        }
    
    def analyze_weather_suitability(self, city: str, activities: List[str]) -> Dict:
        """
        Analyze if weather is suitable for planned activities
        """
        weather = self.get_weather_forecast(city, 7)
        
        if not weather:
            return {'suitable': True, 'warnings': [], 'info': 'Weather data unavailable'}
        
        warnings = []
        
        # Check for heavy rain
        avg_precipitation = sum(weather['precipitation']) / len(weather['precipitation'])
        if avg_precipitation > 10:
            outdoor_activities = ['hiking', 'beach', 'safari', 'outdoor']
            if any(act in ' '.join(activities).lower() for act in outdoor_activities):
                warnings.append({
                    'type': 'rain',
                    'severity': 'medium',
                    'message': f'Heavy rainfall expected ({avg_precipitation:.1f}mm/day average)',
                    'suggestion': 'Consider indoor activities or rain gear'
                })
        
        # Check temperature extremes
        temps = weather['temperatures_max']
        if temps:
            avg_temp = sum(temps) / len(temps)
            if avg_temp > 35:
                warnings.append({
                    'type': 'heat',
                    'severity': 'medium',
                    'message': f'Very hot weather expected ({avg_temp:.1f}°C)',
                    'suggestion': 'Plan outdoor activities for early morning or evening'
                })
        
        return {
            'suitable': len(warnings) == 0,
            'warnings': warnings,
            'avg_temp': avg_temp if temps else None,
            'avg_precipitation': avg_precipitation
        }
    
    def get_best_month_recommendation(self, interests: List[str]) -> Dict:
        """
        Recommend best months based on interests
        """
        # Sri Lanka weather patterns
        recommendations = {
            'beach_west_coast': {
                'best_months': ['November', 'December', 'January', 'February', 'March', 'April'],
                'reason': 'Calm seas and sunny weather on west/south coast'
            },
            'beach_east_coast': {
                'best_months': ['May', 'June', 'July', 'August', 'September'],
                'reason': 'Perfect weather on east coast'
            },
            'hiking': {
                'best_months': ['January', 'February', 'March', 'April', 'August'],
                'reason': 'Dry weather ideal for trekking'
            },
            'wildlife': {
                'best_months': ['February', 'March', 'April', 'May', 'June', 'August', 'September'],
                'reason': 'Best wildlife viewing during dry season'
            },
            'cultural': {
                'best_months': ['July', 'August'],  # Festival season
                'reason': 'Major cultural festivals and events'
            }
        }
        
        # Match interests to recommendations
        best_months = set()
        reasons = []
        
        for interest in interests:
            if interest in ['beach', 'relax']:
                rec = recommendations['beach_west_coast']
                best_months.update(rec['best_months'])
                reasons.append(rec['reason'])
            elif interest in ['hiking', 'adventure']:
                rec = recommendations['hiking']
                best_months.update(rec['best_months'])
                reasons.append(rec['reason'])
            elif interest in ['wildlife', 'nature']:
                rec = recommendations['wildlife']
                best_months.update(rec['best_months'])
                reasons.append(rec['reason'])
            elif interest in ['culture', 'history']:
                rec = recommendations['cultural']
                best_months.update(rec['best_months'])
                reasons.append(rec['reason'])
        
        if not best_months:
            best_months = {'January', 'February', 'March'}
            reasons = ['Generally good weather']
        
        return {
            'recommended_months': sorted(list(best_months)),
            'reasons': list(set(reasons))
        }


class CurrencyAPI:
    """
    Real-time currency conversion (optional enhancement)
    """
    
    def __init__(self):
        self.base_currency = "USD"
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert currency (simplified - use real API in production)
        """
        # Simplified conversion rates (would use real API in production)
        rates = {
            'USD': 1.0,
            'EUR': 0.92,
            'GBP': 0.79,
            'LKR': 330.0,  # Sri Lankan Rupee
            'INR': 83.0,
            'AUD': 1.52
        }
        
        if from_currency in rates and to_currency in rates:
            # Convert to USD first, then to target
            usd_amount = amount / rates[from_currency]
            return usd_amount * rates[to_currency]
        
        return amount


class ExternalAPIIntegration:
    """
    Main integration class for all external APIs
    """
    
    def __init__(self):
        self.weather = WeatherAPI()
        self.currency = CurrencyAPI()
    
    def enhance_tour_plan(self, tour_plan: Dict, user_goals: Dict) -> Dict:
        """
        Enhance tour plan with real-time external data
        """
        enhanced = tour_plan.copy()
        enhanced['external_insights'] = []
        
        # Add weather insights
        destinations = tour_plan.get('destinations', [])
        if destinations:
            weather_insights = self._get_weather_insights(destinations, user_goals)
            if weather_insights:
                enhanced['external_insights'].extend(weather_insights)
        
        # Add seasonal recommendations
        interests = user_goals.get('interests', [])
        if interests:
            seasonal = self.weather.get_best_month_recommendation(interests)
            enhanced['seasonal_recommendation'] = seasonal
        
        return enhanced
    
    def _get_weather_insights(self, destinations: List[str], goals: Dict) -> List[Dict]:
        """Get weather insights for destinations"""
        insights = []
        
        for dest in destinations[:3]:  # Check first 3 destinations
            activities = [a.get('name', '') for a in goals.get('activities', [])]
            suitability = self.weather.analyze_weather_suitability(dest, activities)
            
            if not suitability['suitable']:
                insights.append({
                    'type': 'weather_warning',
                    'destination': dest,
                    'warnings': suitability['warnings']
                })
        
        return insights
