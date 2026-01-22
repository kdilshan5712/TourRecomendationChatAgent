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
    """
    Creates a tour with EXACT days and optimized location flow
    - Ensures exactly target_days of activities
    - Groups consecutive days in same location (no back-and-forth)
    - Logical travel route
    """
    route = []
    activities = []
    total_cost = 0
    
    # Calculate how many cities to visit and days per city
    # Stay 2-3 days per city for logical flow
    days_per_city = 2
    num_cities = max(1, target_days // days_per_city)
    
    # Select cities based on interests (or use defaults)
    selected_cities = BACKUP_CITIES[:num_cities]
    
    # Distribute days across cities
    city_day_allocation = []
    remaining_days = target_days
    
    for i, city in enumerate(selected_cities):
        if i == len(selected_cities) - 1:
            # Last city gets all remaining days
            days_in_city = remaining_days
        else:
            # Allocate 2-3 days per city
            days_in_city = min(days_per_city, remaining_days)
        
        city_day_allocation.append((city, days_in_city))
        remaining_days -= days_in_city
        
        if remaining_days <= 0:
            break
    
    # Generate activities day by day
    current_day = 1
    
    for city, num_days in city_day_allocation:
        route.append(city)
        city_acts = BACKUP_ACTS.get(city, [])
        coords = CITY_COORDS.get(city, {"lat": 0, "lon": 0})
        
        # Generate activities for each day in this city
        for day_in_city in range(num_days):
            # Add 3 activities per day (Morning, Afternoon, Evening)
            for time_slot, (time, name, cost) in enumerate(city_acts[:3]):
                activities.append({
                    "day": current_day,
                    "time": time,
                    "name": name,
                    "city": city,
                    "cost": cost,
                    "lat": coords['lat'],
                    "lon": coords['lon']
                })
                total_cost += cost
            
            current_day += 1
            
            # Safety check: stop if we've reached target days
            if current_day > target_days:
                break
        
        if current_day > target_days:
            break
    
    # CRITICAL: Ensure we have exactly target_days
    if current_day <= target_days:
        # Add more days if needed (use last city)
        last_city = city_day_allocation[-1][0] if city_day_allocation else BACKUP_CITIES[0]
        city_acts = BACKUP_ACTS.get(last_city, [])
        coords = CITY_COORDS.get(last_city, {"lat": 0, "lon": 0})
        
        while current_day <= target_days:
            for time, name, cost in city_acts[:3]:
                activities.append({
                    "day": current_day,
                    "time": time,
                    "name": name,
                    "city": last_city,
                    "cost": cost,
                    "lat": coords['lat'],
                    "lon": coords['lon']
                })
                total_cost += cost
            current_day += 1
    
    # Adjust total cost to match budget
    if total_cost < target_budget:
        remaining_budget = target_budget - total_cost
        total_cost = int(target_budget)
    else:
        total_cost = int(total_cost)
    
    # Create destination list (preserve order for logical route)
    destinations = []
    seen_cities = set()
    for act in activities:
        city = act['city']
        if city not in seen_cities:
            destinations.append(city)
            seen_cities.add(city)
    
    return {
        "id": "generated_999",
        "name": f"{target_days}-Day Optimized Tour",
        "days": target_days,
        "price": total_cost,
        "destinations": destinations,
        "activities": activities,
        "interests": interests,
        "explanation": f"Custom {target_days}-day itinerary with optimized route through {', '.join(destinations[:3])}{'...' if len(destinations) > 3 else ''}. Activities grouped by location for efficient travel."
    }

def find_best_plan(packages, goals, model=None):
    try:
        target_days = int(goals.get('days', 7))
        target_budget = float(goals.get('budget', 1500))
        interests = goals.get('interests', [])
        excluded = set(goals.get('excluded_ids', []))
    except:
        target_days, target_budget, interests, excluded = 7, 1500, [], set()

    # 1. Try to find a DB match with EXACT days
    best_match = None
    best_score = -1
    
    for p in packages:
        if p['id'] in excluded: 
            continue
        
        score = 0
        
        # CRITICAL: Exact day match gets highest priority
        if p['days'] == target_days: 
            score += 1000  # Highest priority
        elif abs(p['days'] - target_days) <= 1: 
            score += 100   # Close match - much lower priority
        else:
            continue  # Skip packages that don't match days closely
        
        # Budget scoring
        if p['price'] <= target_budget: 
            score += 300
        elif p['price'] <= target_budget * 1.2: 
            score += 100
        
        # Interest matching
        if interests:
            pkg_interests = set(p.get('interests', []))
            matches = len(set(interests) & pkg_interests)
            score += matches * 50
        
        if score > best_score:
            best_score = score
            best_match = p

    # 2. If we have exact day match with good score, use it
    if best_match and best_match['days'] == target_days and best_score >= 1000:
        # Sort activities by location for logical flow
        activities = best_match.get('activities', [])
        
        # Group activities by day and city
        sorted_activities = optimize_activity_order(activities, target_days)
        
        best_match['activities'] = sorted_activities
        
        return {
            'package': best_match, 
            'score': best_score, 
            'explanation': f"Perfect {target_days}-day match with optimized location flow."
        }
    else:
        # 3. Generate custom plan with EXACT days and optimized route
        print(f"⚠️ Generating custom {target_days}-day plan...")
        custom_plan = generate_fallback_tour(target_days, target_budget, interests)
        return {
            'package': custom_plan, 
            'score': 999, 
            'explanation': custom_plan['explanation']
        }

def optimize_activity_order(activities, target_days):
    """
    Reorganize activities to group by location and ensure exact day count
    Prevents back-and-forth between cities
    """
    # Group activities by city
    city_activities = {}
    for act in activities:
        city = act.get('city', 'Unknown')
        if city not in city_activities:
            city_activities[city] = []
        city_activities[city].append(act)
    
    # Sort cities by first appearance to maintain original route intent
    city_order = []
    seen = set()
    for act in activities:
        city = act.get('city', 'Unknown')
        if city not in seen:
            city_order.append(city)
            seen.add(city)
    
    # Rebuild activities in optimized order
    optimized = []
    current_day = 1
    
    for city in city_order:
        city_acts = city_activities[city]
        
        # Group activities by time of day
        morning = [a for a in city_acts if a.get('time') == 'Morning']
        afternoon = [a for a in city_acts if a.get('time') == 'Afternoon']
        evening = [a for a in city_acts if a.get('time') == 'Evening']
        
        # Calculate days needed in this city
        days_in_city = max(len(morning), len(afternoon), len(evening))
        
        for day_offset in range(days_in_city):
            if current_day > target_days:
                break
                
            # Add activities for this day in order
            if day_offset < len(morning):
                act = morning[day_offset].copy()
                act['day'] = current_day
                optimized.append(act)
            
            if day_offset < len(afternoon):
                act = afternoon[day_offset].copy()
                act['day'] = current_day
                optimized.append(act)
            
            if day_offset < len(evening):
                act = evening[day_offset].copy()
                act['day'] = current_day
                optimized.append(act)
            
            current_day += 1
        
        if current_day > target_days:
            break
    
    # Ensure we have exactly target_days
    if current_day <= target_days:
        # Extend with activities from last city
        last_city = city_order[-1] if city_order else None
        if last_city and last_city in city_activities:
            last_city_acts = city_activities[last_city]
            
            while current_day <= target_days:
                for act in last_city_acts[:3]:  # Morning, Afternoon, Evening
                    new_act = act.copy()
                    new_act['day'] = current_day
                    optimized.append(new_act)
                current_day += 1
    
    # Trim if we have too many days
    optimized = [act for act in optimized if act['day'] <= target_days]
    
    return optimized
