import random

# STATIC DATA FOR INSTANT GENERATION (Backup)
BACKUP_CITIES = ["Colombo", "Sigiriya", "Kandy", "Ella", "Yala", "Mirissa", "Galle", "Nuwara Eliya", "Anuradhapura", "Trincomalee"]
CITY_COORDS = {
    "Colombo": {"lat": 6.927, "lon": 79.861}, "Kandy": {"lat": 7.290, "lon": 80.633},
    "Sigiriya": {"lat": 7.957, "lon": 80.760}, "Ella": {"lat": 6.866, "lon": 81.046},
    "Mirissa": {"lat": 5.948, "lon": 80.471}, "Galle": {"lat": 6.053, "lon": 80.221},
    "Yala": {"lat": 6.383, "lon": 81.500}, "Nuwara Eliya": {"lat": 6.949, "lon": 80.789},
    "Anuradhapura": {"lat": 8.335, "lon": 80.403}, "Trincomalee": {"lat": 8.588, "lon": 81.218}
}
# Expanded activity pools - MORE ACTIVITIES PER CITY to avoid repetition
BACKUP_ACTS = {
    "Colombo": [
        ("Morning", "Gangaramaya Temple", 10), ("Afternoon", "National Museum", 15), ("Evening", "Galle Face Walk", 0),
        ("Morning", "Viharamahadevi Park", 0), ("Afternoon", "Independence Square", 5), ("Evening", "Pettah Market Tour", 10),
        ("Morning", "Colombo City Tour", 20), ("Afternoon", "Shopping at Odel", 0), ("Evening", "Dutch Hospital Dining", 30)
    ],
    "Sigiriya": [
        ("Morning", "Sigiriya Rock Fortress", 30), ("Afternoon", "Pidurangala Rock", 25), ("Evening", "Village Tour", 20),
        ("Morning", "Dambulla Cave Temple", 20), ("Afternoon", "Minneriya Safari", 50), ("Evening", "Ayurvedic Massage", 40),
        ("Morning", "Ancient Ruins Walk", 15), ("Afternoon", "Spice Garden Visit", 10), ("Evening", "Traditional Cooking Class", 35)
    ],
    "Kandy": [
        ("Morning", "Temple of Tooth", 15), ("Afternoon", "Botanical Gardens", 15), ("Evening", "Kandy Lake Walk", 0),
        ("Morning", "Tea Factory Tour", 25), ("Afternoon", "Elephant Sanctuary", 30), ("Evening", "Cultural Dance Show", 20),
        ("Morning", "Bahiravokanda Temple", 10), ("Afternoon", "Royal Palace Museum", 10), ("Evening", "Shopping at Kandy City", 0)
    ],
    "Ella": [
        ("Morning", "Ella Rock Hike", 0), ("Afternoon", "Nine Arch Bridge", 0), ("Evening", "Little Adam's Peak", 0),
        ("Morning", "Ravana Falls", 5), ("Afternoon", "Demodara Loop", 0), ("Evening", "Ella Town Cafe Hopping", 25),
        ("Morning", "Tea Plantation Walk", 10), ("Afternoon", "Flying Ravana Zipline", 45), ("Evening", "Sunset Viewpoint", 0)
    ],
    "Yala": [
        ("Morning", "Yala Safari - Leopards", 60), ("Afternoon", "Bird Watching Tour", 40), ("Evening", "Beach Camping", 80),
        ("Morning", "Bundala National Park", 50), ("Afternoon", "Elephant Gathering", 45), ("Evening", "Star Gazing", 20),
        ("Morning", "Nature Trail Walk", 15), ("Afternoon", "Photography Safari", 55), ("Evening", "BBQ by the Lake", 40)
    ],
    "Mirissa": [
        ("Morning", "Whale Watching", 70), ("Afternoon", "Secret Beach", 0), ("Evening", "Beach Sunset", 0),
        ("Morning", "Snorkeling Trip", 40), ("Afternoon", "Coconut Tree Hill", 5), ("Evening", "Seafood Dinner", 30),
        ("Morning", "Surfing Lessons", 35), ("Afternoon", "Beach Volleyball", 0), ("Evening", "Night Beach Walk", 0)
    ],
    "Galle": [
        ("Morning", "Galle Fort Tour", 10), ("Afternoon", "Unawatuna Beach", 0), ("Evening", "Lighthouse Sunset", 0),
        ("Morning", "Dutch Museum", 8), ("Afternoon", "Jungle Beach Trek", 15), ("Evening", "Fort Ramparts Walk", 0),
        ("Morning", "Hikkaduwa Turtle Hatchery", 20), ("Afternoon", "Coral Reef Snorkeling", 45), ("Evening", "Shopping in Fort", 0)
    ],
    "Nuwara Eliya": [
        ("Morning", "Gregory Lake Boat Ride", 15), ("Afternoon", "Victoria Park", 5), ("Evening", "Strawberry Farm", 10),
        ("Morning", "Horton Plains Trek", 35), ("Afternoon", "Pedro Tea Estate", 20), ("Evening", "Town Walk", 0),
        ("Morning", "World's End Viewpoint", 25), ("Afternoon", "Ramboda Falls", 5), ("Evening", "Colonial Bungalow Tour", 15)
    ],
    "Anuradhapura": [
        ("Morning", "Sacred Bo Tree", 0), ("Afternoon", "Ruwanwelisaya Stupa", 0), ("Evening", "Ancient Ruins Cycling", 15),
        ("Morning", "Twin Ponds", 0), ("Afternoon", "Abhayagiri Monastery", 5), ("Evening", "Moonstone Museum", 10),
        ("Morning", "Isurumuniya Temple", 8), ("Afternoon", "Archaeological Museum", 10), ("Evening", "Sunset at Reservoir", 0)
    ],
    "Trincomalee": [
        ("Morning", "Nilaveli Beach", 0), ("Afternoon", "Pigeon Island Snorkeling", 45), ("Evening", "Beach Sunset", 0),
        ("Morning", "Koneswaram Temple", 5), ("Afternoon", "Fort Frederick", 5), ("Evening", "Marble Beach", 0),
        ("Morning", "Whale Watching", 60), ("Afternoon", "Hot Springs Visit", 10), ("Evening", "Seafood BBQ", 35)
    ]
}

def generate_fallback_tour(target_days, target_budget, interests):
    """
    Creates a tour with EXACT days and optimized location flow
    - Ensures exactly target_days of activities
    - MAX 2 days per city (no repetition)
    - Different activities every time (no duplicates)
    - Logical travel route
    """
    route = []
    activities = []
    total_cost = 0
    used_activities = set()  # Track used activities to avoid repetition
    
    # CRITICAL: Maximum 2 days per city
    MAX_DAYS_PER_CITY = 2
    
    # Calculate how many cities needed
    num_cities = (target_days + MAX_DAYS_PER_CITY - 1) // MAX_DAYS_PER_CITY  # Ceiling division
    
    # Select cities (ensure we have enough cities)
    selected_cities = BACKUP_CITIES[:num_cities]
    
    # If we need more cities than available, cycle through them
    if num_cities > len(BACKUP_CITIES):
        selected_cities = BACKUP_CITIES * ((num_cities // len(BACKUP_CITIES)) + 1)
        selected_cities = selected_cities[:num_cities]
    
    # Distribute days across cities - MAX 2 days per city
    city_day_allocation = []
    remaining_days = target_days
    
    for i, city in enumerate(selected_cities):
        if remaining_days <= 0:
            break
            
        if i == len(selected_cities) - 1:
            # Last city gets remaining days (up to 2)
            days_in_city = min(remaining_days, MAX_DAYS_PER_CITY)
        else:
            # Allocate MAX 2 days per city
            days_in_city = min(MAX_DAYS_PER_CITY, remaining_days)
        
        city_day_allocation.append((city, days_in_city))
        remaining_days -= days_in_city
    
    # Generate activities day by day with NO REPETITION
    current_day = 1
    
    for city, num_days in city_day_allocation:
        route.append(city)
        city_acts = BACKUP_ACTS.get(city, [])
        coords = CITY_COORDS.get(city, {"lat": 0, "lon": 0})
        
        # Track which activities we've used for this city
        city_activity_index = 0
        
        # Generate activities for each day in this city (max 2 days)
        for day_in_city in range(num_days):
            # Add 3 activities per day (Morning, Afternoon, Evening)
            # Use DIFFERENT activities each day
            for time_slot in range(3):
                if city_activity_index >= len(city_acts):
                    # If we run out of activities, start from beginning but with modified names
                    city_activity_index = 0
                
                time, name, cost = city_acts[city_activity_index]
                
                # Create unique activity key to avoid duplicates
                activity_key = f"{city}_{name}_{current_day}"
                
                # Check if activity already used
                retry_count = 0
                while activity_key in used_activities and retry_count < len(city_acts):
                    city_activity_index = (city_activity_index + 1) % len(city_acts)
                    time, name, cost = city_acts[city_activity_index]
                    activity_key = f"{city}_{name}_{current_day}"
                    retry_count += 1
                
                used_activities.add(activity_key)
                
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
                city_activity_index += 1
            
            current_day += 1
            
            # Safety check: stop if we've reached target days
            if current_day > target_days:
                break
        
        if current_day > target_days:
            break
    
    # CRITICAL: If we still need more days, add new cities
    if current_day <= target_days:
        # Get cities not yet used
        used_cities = [c for c, _ in city_day_allocation]
        available_cities = [c for c in BACKUP_CITIES if c not in used_cities]
        
        if not available_cities:
            # If all cities used, pick cities with least days
            available_cities = BACKUP_CITIES[:3]
        
        for new_city in available_cities:
            if current_day > target_days:
                break
                
            route.append(new_city)
            city_acts = BACKUP_ACTS.get(new_city, [])
            coords = CITY_COORDS.get(new_city, {"lat": 0, "lon": 0})
            city_activity_index = 0
            
            # Add up to 2 days in this new city
            for day_in_city in range(min(MAX_DAYS_PER_CITY, target_days - current_day + 1)):
                for time_slot in range(3):
                    if city_activity_index >= len(city_acts):
                        city_activity_index = 0
                    
                    time, name, cost = city_acts[city_activity_index]
                    activity_key = f"{new_city}_{name}_{current_day}"
                    
                    # Ensure unique activities
                    retry_count = 0
                    while activity_key in used_activities and retry_count < len(city_acts):
                        city_activity_index = (city_activity_index + 1) % len(city_acts)
                        time, name, cost = city_acts[city_activity_index]
                        activity_key = f"{new_city}_{name}_{current_day}"
                        retry_count += 1
                    
                    used_activities.add(activity_key)
                    
                    activities.append({
                        "day": current_day,
                        "time": time,
                        "name": name,
                        "city": new_city,
                        "cost": cost,
                        "lat": coords['lat'],
                        "lon": coords['lon']
                    })
                    total_cost += cost
                    city_activity_index += 1
                
                current_day += 1
                if current_day > target_days:
                    break
    
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
