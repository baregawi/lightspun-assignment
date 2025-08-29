#!/usr/bin/env python3
"""
Script to generate comprehensive addresses data for all municipalities.
Generates 100 addresses for each of the 20 municipalities in CA, NY, and TX.
Total: 6,000 addresses
"""

import json
import random

# Street names for address generation
street_names = [
    "Main", "First", "Second", "Third", "Oak", "Pine", "Maple", "Cedar", "Elm", "Park",
    "Washington", "Lincoln", "Jefferson", "Adams", "Jackson", "Madison", "Monroe", "Harrison",
    "Tyler", "Polk", "Taylor", "Fillmore", "Pierce", "Buchanan", "Johnson", "Grant", "Hayes",
    "Garfield", "Arthur", "Cleveland", "McKinley", "Roosevelt", "Taft", "Wilson", "Harding",
    "Coolidge", "Hoover", "Truman", "Eisenhower", "Kennedy", "Nixon", "Ford", "Carter",
    "Reagan", "Clinton", "Bush", "Obama", "Spring", "Summer", "Autumn", "Winter", "North",
    "South", "East", "West", "Central", "Highland", "Valley", "Hill", "Lake", "River", "Creek",
    "Bridge", "Market", "Church", "School", "College", "University", "Industrial", "Commercial"
]

street_types = ["St", "Ave", "Blvd", "Dr", "Ln", "Rd", "Way", "Ct", "Pl", "Ter"]

def generate_address(municipality, state_code):
    """Generate a random address for the given municipality and state"""
    house_number = random.randint(100, 9999)
    street_name = random.choice(street_names)
    street_type = random.choice(street_types)
    return f"{house_number} {street_name} {street_type}, {municipality}, {state_code}"

def generate_all_addresses():
    """Generate all addresses for the sample municipalities"""
    
    # Define the municipalities for each state
    municipalities = {
        "CA": [
            "Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno",
            "Sacramento", "Long Beach", "Oakland", "Bakersfield", "Anaheim",
            "Santa Ana", "Riverside", "Stockton", "Irvine", "Fremont",
            "San Bernardino", "Modesto", "Fontana", "Oxnard", "Moreno Valley"
        ],
        "NY": [
            "New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse",
            "Albany", "New Rochelle", "Mount Vernon", "Schenectady", "Utica",
            "White Plains", "Hempstead", "Troy", "Niagara Falls", "Binghamton",
            "Freeport", "Valley Stream", "Long Beach", "Rome", "Jamestown"
        ],
        "TX": [
            "Houston", "San Antonio", "Dallas", "Austin", "Fort Worth",
            "El Paso", "Arlington", "Corpus Christi", "Plano", "Laredo",
            "Lubbock", "Garland", "Irving", "Amarillo", "Grand Prairie",
            "Brownsville", "McKinney", "Frisco", "Pasadena", "Killeen"
        ]
    }
    
    addresses_by_municipality = {}
    
    for state_code, muni_list in municipalities.items():
        addresses_by_municipality[state_code] = {}
        for municipality in muni_list:
            # Generate 100 unique addresses for each municipality
            addresses = set()
            while len(addresses) < 100:
                address = generate_address(municipality, state_code)
                addresses.add(address)
            addresses_by_municipality[state_code][municipality] = sorted(list(addresses))
    
    # Create the complete data structure
    complete_data = {
        "addresses_by_municipality": addresses_by_municipality,
        "summary": {
            "total_states": 3,
            "municipalities_per_state": 20,
            "addresses_per_municipality": 100,
            "total_addresses": 6000,
            "generated_by": "generate_addresses.py script"
        },
        "metadata": {
            "states": ["CA", "NY", "TX"],
            "total_municipalities": 60,
            "address_format": "{house_number} {street_name} {street_type}, {municipality}, {state_code}"
        }
    }
    
    return complete_data

if __name__ == "__main__":
    print("Generating comprehensive addresses data...")
    data = generate_all_addresses()
    
    # Write to file
    with open("addresses_by_municipality_complete.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {data['summary']['total_addresses']} addresses")
    print(f"📁 Saved to: addresses_by_municipality_complete.json")
    print(f"📊 Data structure:")
    print(f"   - {data['summary']['total_states']} states")
    print(f"   - {data['summary']['municipalities_per_state']} municipalities per state")
    print(f"   - {data['summary']['addresses_per_municipality']} addresses per municipality")
    print(f"   - {data['summary']['total_addresses']} total addresses")