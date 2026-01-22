import json

packages = json.load(open('data/tour_packages.json'))
matches = [p for p in packages if 'Mirissa' in p.get('destinations', []) and 'Galle' in p.get('destinations', []) and p['days'] == 7]

print(f'Found {len(matches)} matching tours with Mirissa, Galle, and 7 days')
for p in matches[:5]:
    print(f"\n{p['name']}")
    print(f"  Days: {p['days']}")
    print(f"  Price: ${p['price']}")
    print(f"  Destinations: {', '.join(p['destinations'])}")
    print(f"  Activities: {len(p.get('activities', []))}")

# Create or find a sample tour for display
if not matches:
    print("\nNo exact match found. Creating sample tour...")
    sample_tour = {
        "id": 9999,
        "name": "7-Day Standard Mirissa to Galle Tour",
        "destinations": ["Mirissa", "Galle"],
        "days": 7,
        "price": 1500,
        "interests": ["beach", "relax", "culture"],
        "hotel_level": "Standard",
        "activities": [
            {"name": "Beach Day in Mirissa", "city": "Mirissa", "day": 1, "time": "Morning", "cost": 50, "lat": 5.9549, "lon": 80.4561},
            {"name": "Whale Watching", "city": "Mirissa", "day": 1, "time": "Afternoon", "cost": 80, "lat": 5.9549, "lon": 80.4561},
            {"name": "Sunset at Mirissa Beach", "city": "Mirissa", "day": 1, "time": "Evening", "cost": 0, "lat": 5.9549, "lon": 80.4561},
            
            {"name": "Snorkeling", "city": "Mirissa", "day": 2, "time": "Morning", "cost": 60, "lat": 5.9549, "lon": 80.4561},
            {"name": "Beach Relaxation", "city": "Mirissa", "day": 2, "time": "Afternoon", "cost": 30, "lat": 5.9549, "lon": 80.4561},
            {"name": "Seafood Dinner", "city": "Mirissa", "day": 2, "time": "Evening", "cost": 40, "lat": 5.9549, "lon": 80.4561},
            
            {"name": "Coconut Tree Hill", "city": "Mirissa", "day": 3, "time": "Morning", "cost": 20, "lat": 5.9549, "lon": 80.4561},
            {"name": "Transfer to Galle", "city": "Galle", "day": 3, "time": "Afternoon", "cost": 50, "lat": 6.0535, "lon": 80.2210},
            {"name": "Galle Fort Evening Walk", "city": "Galle", "day": 3, "time": "Evening", "cost": 0, "lat": 6.0235, "lon": 80.2168},
            
            {"name": "Galle Fort Tour", "city": "Galle", "day": 4, "time": "Morning", "cost": 40, "lat": 6.0235, "lon": 80.2168},
            {"name": "Dutch Museum Visit", "city": "Galle", "day": 4, "time": "Afternoon", "cost": 30, "lat": 6.0235, "lon": 80.2168},
            {"name": "Lighthouse View", "city": "Galle", "day": 4, "time": "Evening", "cost": 0, "lat": 6.0235, "lon": 80.2168},
            
            {"name": "Unawatuna Beach", "city": "Galle", "day": 5, "time": "Morning", "cost": 50, "lat": 6.0101, "lon": 80.2506},
            {"name": "Jungle Beach Trek", "city": "Galle", "day": 5, "time": "Afternoon", "cost": 40, "lat": 6.0101, "lon": 80.2506},
            {"name": "Beach BBQ", "city": "Galle", "day": 5, "time": "Evening", "cost": 60, "lat": 6.0101, "lon": 80.2506},
            
            {"name": "Hikkaduwa Turtle Hatchery", "city": "Galle", "day": 6, "time": "Morning", "cost": 35, "lat": 6.1408, "lon": 80.0993},
            {"name": "Coral Reef Snorkeling", "city": "Galle", "day": 6, "time": "Afternoon", "cost": 70, "lat": 6.1408, "lon": 80.0993},
            {"name": "Beach Sunset", "city": "Galle", "day": 6, "time": "Evening", "cost": 0, "lat": 6.1408, "lon": 80.0993},
            
            {"name": "Shopping in Galle", "city": "Galle", "day": 7, "time": "Morning", "cost": 100, "lat": 6.0535, "lon": 80.2210},
            {"name": "Spa & Massage", "city": "Galle", "day": 7, "time": "Afternoon", "cost": 80, "lat": 6.0535, "lon": 80.2210},
            {"name": "Farewell Dinner", "city": "Galle", "day": 7, "time": "Evening", "cost": 70, "lat": 6.0535, "lon": 80.2210}
        ]
    }
    
    # Save to file
    with open('data/sample_tour_mirissa_galle.json', 'w') as f:
        json.dump(sample_tour, f, indent=2)
    print(f"\n✅ Created sample tour: {sample_tour['name']}")
    print(f"   Saved to: data/sample_tour_mirissa_galle.json")
else:
    print(f"\n✅ Using existing tour: {matches[0]['name']}")
