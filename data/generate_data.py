import json
import random

# FULL ACTIVITY DATABASE WITH GPS
CITY_DATA = {
    "Colombo": { 
        "coords": {"lat": 6.927, "lon": 79.861},
        "acts": [
            ("Morning", "City Bus Tour", "city", 10), ("Morning", "National Museum", "history", 15), ("Morning", "Pettah Market", "culture", 0),
            ("Afternoon", "Lotus Tower", "city", 20), ("Afternoon", "Arcade Square", "shopping", 0), ("Afternoon", "Viharamahadevi Park", "relax", 0),
            ("Evening", "Galle Face Green", "relax", 0), ("Evening", "Casino Bellagio", "party", 100), ("Evening", "Ministry of Crab", "food", 50)
        ]
    },
    "Kandy": { 
        "coords": {"lat": 7.290, "lon": 80.633},
        "acts": [
            ("Morning", "Botanical Gardens", "nature", 15), ("Morning", "Udawatta Forest", "hiking", 10), ("Morning", "Ceylon Tea Museum", "history", 10),
            ("Afternoon", "Temple of the Tooth", "culture", 15), ("Afternoon", "Kandy Lake Walk", "relax", 0), ("Afternoon", "Bahirawakanda", "culture", 5),
            ("Evening", "Cultural Dance Show", "culture", 10), ("Evening", "Slightly Chilled Pub", "party", 20), ("Evening", "Viewpoint Dinner", "food", 15)
        ]
    },
    "Sigiriya": { 
        "coords": {"lat": 7.957, "lon": 80.760},
        "acts": [
            ("Morning", "Lion Rock Climb", "history", 30), ("Morning", "Pidurangala Hike", "adventure", 5), ("Morning", "Hiriwadunna Trek", "nature", 10),
            ("Afternoon", "Minneriya Safari", "wildlife", 50), ("Afternoon", "Village Tour", "culture", 25), ("Afternoon", "Bullock Cart Ride", "culture", 15),
            ("Evening", "Ayurvedic Spa", "relax", 40), ("Evening", "Stargazing", "relax", 0), ("Evening", "Traditional Dinner", "food", 12)
        ]
    },
    "Ella": { 
        "coords": {"lat": 6.866, "lon": 81.046},
        "acts": [
            ("Morning", "Ella Rock Hike", "hiking", 0), ("Morning", "Little Adam's Peak", "hiking", 0), ("Morning", "Tea Plantation", "nature", 10),
            ("Afternoon", "9 Arch Bridge", "photo", 0), ("Afternoon", "Flying Ravana Zipline", "adventure", 20), ("Afternoon", "Ravana Falls", "nature", 0),
            ("Evening", "Cafe Chill", "food", 25), ("Evening", "Live Music Bar", "party", 15), ("Evening", "Cooking Class", "food", 25)
        ]
    },
    "Mirissa": { 
        "coords": {"lat": 5.948, "lon": 80.471},
        "acts": [
            ("Morning", "Whale Watching", "wildlife", 70), ("Morning", "Coconut Tree Hill", "photo", 0), ("Morning", "Parrot Rock", "adventure", 0),
            ("Afternoon", "Secret Beach", "beach", 0), ("Afternoon", "Turtle Snorkeling", "wildlife", 20), ("Afternoon", "Surfing Lesson", "adventure", 30),
            ("Evening", "Beach BBQ", "food", 30), ("Evening", "Sunset Cocktails", "party", 15), ("Evening", "Beach Party", "party", 0)
        ]
    },
    "Galle": { 
        "coords": {"lat": 6.053, "lon": 80.221},
        "acts": [
            ("Morning", "Dutch Fort Walk", "history", 0), ("Morning", "Maritime Museum", "history", 5), ("Morning", "Dutch Church", "culture", 0),
            ("Afternoon", "Unawatuna Beach", "beach", 0), ("Afternoon", "Jungle Beach", "beach", 5), ("Afternoon", "Rumassala Hike", "nature", 10),
            ("Evening", "Sunset Ramparts", "relax", 0), ("Evening", "Fort Fine Dining", "food", 60), ("Evening", "Lighthouse Photo", "photo", 0)
        ]
    },
    "Yala": { 
        "coords": {"lat": 6.383, "lon": 81.500},
        "acts": [
            ("Morning", "Morning Jeep Safari", "wildlife", 60), ("Morning", "Bird Watching", "nature", 20),
            ("Afternoon", "Evening Jeep Safari", "wildlife", 60), ("Afternoon", "Kirinda Beach", "beach", 0),
            ("Evening", "Jungle Camping", "adventure", 120), ("Evening", "Campfire BBQ", "food", 0)
        ]
    },
    "Nuwara Eliya": { 
        "coords": {"lat": 6.949, "lon": 80.789},
        "acts": [
            ("Morning", "Horton Plains", "hiking", 35), ("Morning", "Moon Plains", "nature", 15),
            ("Afternoon", "Pedro Tea Estate", "culture", 5), ("Afternoon", "Gregory Lake", "relax", 10),
            ("Evening", "Grand Hotel High Tea", "food", 25), ("Evening", "Colonial Dinner", "food", 30)
        ]
    }
}

TEMPLATES = [
    ["Colombo", "Sigiriya", "Kandy", "Nuwara Eliya", "Ella", "Yala", "Mirissa", "Galle", "Colombo"], 
    ["Colombo", "Kandy", "Ella", "Sigiriya", "Trincomalee", "Anuradhapura", "Jaffna"],
    ["Galle", "Mirissa", "Yala", "Ella", "Kandy", "Colombo"],
    ["Colombo", "Sigiriya", "Kandy", "Colombo"]
]

def generate_packages(count=5000):
    packages = []
    pid = 1
    print(f"📦 Assembling {count} Detailed Itineraries...")

    for _ in range(count):
        route = random.choice(TEMPLATES)
        trip_days = random.randint(3, 14)
        
        # Start at a random point in the route to add variety
        start_idx = random.randint(0, max(0, len(route) - 4)) 
        
        current_plan = []
        full_route_names = []
        interests = set()
        total_cost = 0
        
        days_covered = 0
        city_pointer = start_idx
        
        base_hotel_cost = random.randint(40, 400) # Per night
        
        while days_covered < trip_days:
            city_name = route[city_pointer % len(route)]
            full_route_names.append(city_name)
            
            # Stay 1-3 days
            stay_duration = random.randint(1, 3)
            if days_covered + stay_duration > trip_days:
                stay_duration = trip_days - days_covered
            
            city_info = CITY_DATA.get(city_name, {})
            all_acts = city_info.get("acts", [])
            
            # Shuffle activities to ensure uniqueness
            mornings = [a for a in all_acts if a[0] == "Morning"]
            afternoons = [a for a in all_acts if a[0] == "Afternoon"]
            evenings = [a for a in all_acts if a[0] == "Evening"]
            
            random.shuffle(mornings)
            random.shuffle(afternoons)
            random.shuffle(evenings)
            
            for day_in_city in range(stay_duration):
                current_day = days_covered + day_in_city + 1
                
                # Pick unique acts for this day
                daily_picks = []
                if mornings: daily_picks.append(mornings.pop() if len(mornings) > 0 else mornings[0])
                if afternoons: daily_picks.append(afternoons.pop() if len(afternoons) > 0 else afternoons[0])
                if evenings: daily_picks.append(evenings.pop() if len(evenings) > 0 else evenings[0])
                
                for slot, name, cat, price in daily_picks:
                    current_plan.append({
                        "day": current_day,
                        "time": slot,
                        "name": name,
                        "city": city_name,
                        "cost": price,
                        "interest": cat,
                        "lat": city_info['coords']['lat'],
                        "lon": city_info['coords']['lon']
                    })
                    interests.add(cat)
                    total_cost += price
                    
            days_covered += stay_duration
            city_pointer += 1
            
        # Finalize Package
        total_cost += (base_hotel_cost * trip_days)
        tier = "Budget" if base_hotel_cost < 80 else ("Luxury" if base_hotel_cost > 200 else "Standard")
        tags = list(interests) + [tier.lower()]
        
        packages.append({
            "id": pid,
            "name": f"{trip_days}-Day {tier} {full_route_names[0]} to {full_route_names[-1]} Tour",
            "days": trip_days,
            "price": int(total_cost),
            "destinations": list(set(full_route_names)),
            "interests": tags,
            "activities": current_plan,
            "hotel_level": tier
        })
        pid += 1
        
    return packages
