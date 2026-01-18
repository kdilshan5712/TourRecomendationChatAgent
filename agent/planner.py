import random

# STATIC DATA FOR INSTANT GENERATION (Backup)
BACKUP_CITIES = ["Colombo", "Sigiriya", "Kandy", "Ella", "Yala", "Mirissa", "Galle"]
CITY_COORDS = {
    "Colombo": {"lat": 6.927, "lon": 79.861}, "Kandy": {"lat": 7.290, "lon": 80.633},
    "Sigiriya": {"lat": 7.957, "lon": 80.760}, "Ella": {"lat": 6.866, "lon": 81.046},
    "Mirissa": {"lat": 5.948, "lon": 80.471}, "Galle": {"lat": 6.053, "lon": 80.221},
    "Yala": {"lat": 6.383, "lon": 81.500}, "Nuwara Eliya": {"lat": 6.949, "lon": 80.789}
}
BACKUP_ACTS = {
    "Colombo": [("Morning", "City Bus Tour", 10), ("Afternoon", "Lotus Tower", 20), ("Evening", "Galle Face Green", 0)],
    "Sigiriya": [("Morning", "Lion Rock Climb", 30), ("Afternoon", "Village Safari", 25), ("Evening", "Ayurvedic Spa", 40)],
    "Kandy": [("Morning", "Botanical Garden", 15), ("Afternoon", "Temple of Tooth", 15), ("Evening", "Cultural Show", 10)],
    "Ella": [("Morning", "Ella Rock Hike", 0), ("Afternoon", "Nine Arch Bridge", 0), ("Evening", "Cafe Chill", 25)],
    "Yala": [("Morning", "Morning Safari", 60), ("Afternoon", "Evening Safari", 60), ("Evening", "Jungle Camping", 120)],
    "Mirissa": [("Morning", "Whale Watching", 70), ("Afternoon", "Secret Beach", 0), ("Evening", "Beach BBQ", 30)],
    "Galle": [("Morning", "Fort Walk", 0), ("Afternoon", "Unawatuna Beach", 0), ("Evening", "Sunset Ramparts", 0)]
}

def generate_fallback_tour(target_days, target_budget, interests):
    # This function CREATES a tour if the database fails
    route = []
    activities = []
    total_cost = 0
    days_covered = 0
    city_idx = 0
    used_activities = set()  # Track used activities to avoid repetition
    
    # Calculate daily budget to stay near target
    daily_budget = target_budget / target_days
    
    while days_covered < target_days:
        city = BACKUP_CITIES[city_idx % len(BACKUP_CITIES)]
        route.append(city)
        
        # Stay 1-2 days per city (but not more than remaining days)
        remaining = target_days - days_covered
        stay = min(2, remaining)
        
        city_acts = BACKUP_ACTS.get(city, [])
        coords = CITY_COORDS.get(city, {"lat": 0, "lon": 0})
        
        for d in range(stay):
            day_num = days_covered + d + 1
            if day_num > target_days:  # Safety check
                break
                
            # Select unique activities per day (3 per day: Morning, Afternoon, Evening)
            day_activities = []
            for time, name, cost in city_acts:
                activity_key = f"{city}_{name}"
                # Allow same activity only if it's been used in a different city or more than 2 days ago
                if activity_key not in used_activities or len(used_activities) > 20:
                    day_activities.append((time, name, cost))
                    used_activities.add(activity_key)
                    
            # Add activities for this day
            for time, name, cost in day_activities[:3]:  # Max 3 per day
                activities.append({
                    "day": day_num, "time": time, "name": name, "city": city,
                    "cost": cost, "lat": coords['lat'], "lon": coords['lon']
                })
                total_cost += cost
                
        days_covered += stay
        city_idx += 1
        
    # Add base hotel cost (adjusted to match budget)
    remaining_budget = target_budget - total_cost
    if remaining_budget < 0: remaining_budget = 0
    total_cost += remaining_budget # Fill the budget
    
    return {
        "id": "generated_999",
        "name": f"{target_days}-Day Perfect Match Tour",
        "days": target_days,
        "price": int(target_budget), # Match budget exactly
        "destinations": list(set(route)),
        "activities": activities,
        "explanation": f"We custom-built this itinerary to perfectly match your {target_days}-day schedule and ${target_budget} budget, featuring top-rated activities in {', '.join(list(set(route))[:3])}."
    }

def find_best_plan(packages, goals, model=None):
    try:
        target_days = int(goals.get('days', 7))
        target_budget = float(goals.get('budget', 1500))
        interests = goals.get('interests', [])
        excluded = set(goals.get('excluded_ids', []))
    except:
        target_days, target_budget, interests, excluded = 7, 1500, [], set()

    # 1. Try to find a DB match
    best_match = None
    best_score = -1
    
    for p in packages:
        if p['id'] in excluded: continue
        
        score = 0
        if p['days'] == target_days: score += 500
        elif abs(p['days'] - target_days) <= 1: score += 200
        
        if p['price'] <= target_budget: score += 200
        elif p['price'] <= target_budget * 1.1: score += 100
        
        if score > best_score:
            best_score = score
            best_match = p

    # 2. DECISION TIME - Prioritize exact day match or generate custom
    if best_match and best_match['days'] == target_days and best_score > 300:
        # Exact match found - adjust activities to match days
        activities = best_match.get('activities', [])
        unique_activities = []
        seen = set()
        
        for act in activities:
            act_key = f"{act.get('name', '')}_{act.get('day', 1)}"
            if act_key not in seen:
                unique_activities.append(act)
                seen.add(act_key)
        
        best_match['activities'] = unique_activities
        return {
            'package': best_match, 
            'score': best_score, 
            'explanation': f"Perfect match for your {target_days}-day trip with unique activities."
        }
    else:
        # 3. GENERATE custom plan to match EXACTLY
        print(f"⚠️ Generating custom {target_days}-day plan...")
        custom_plan = generate_fallback_tour(target_days, target_budget, interests)
        return {'package': custom_plan, 'score': 999, 'explanation': custom_plan['explanation']}
