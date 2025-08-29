"""
Street Type Standardization Module

This module provides utilities to standardize street types (suffixes) in addresses
to ensure consistency across the database and improve search capabilities.

Standard formats chosen based on USPS publication 28 and common usage:
- Street -> Street (most common, keep as-is)
- Avenue -> Avenue (second most common, keep as-is) 
- Road -> Road (third most common, keep as-is)
- Boulevard -> Boulevard (keep full form)
- Drive -> Drive (keep as-is)
- Lane -> Lane (keep as-is)
- Place -> Place (keep as-is)
- Court -> Court (keep as-is)
- Parkway -> Parkway (keep full form)
- Highway -> Highway (keep full form)
"""

import re
from typing import Dict, Set

# Standard street type formats (target formats)
STANDARD_STREET_TYPES = {
    'Street',
    'Avenue', 
    'Road',
    'Boulevard',
    'Drive',
    'Lane',
    'Place',
    'Court',
    'Parkway',
    'Highway'
}

# Comprehensive mapping of street type variations to standard forms
STREET_TYPE_MAPPING: Dict[str, str] = {
    # Street variations
    'St': 'Street',
    'Str': 'Street',
    'Street': 'Street',
    'Streets': 'Street',
    
    # Avenue variations  
    'Ave': 'Avenue',
    'Av': 'Avenue',
    'Avenue': 'Avenue',
    'Avenu': 'Avenue',
    'Avnue': 'Avenue',
    'Avn': 'Avenue',
    
    # Road variations
    'Rd': 'Road', 
    'Road': 'Road',
    'Roads': 'Road',
    
    # Boulevard variations
    'Blvd': 'Boulevard',
    'Blv': 'Boulevard', 
    'Boulevard': 'Boulevard',
    'Boulevrd': 'Boulevard',
    'Boul': 'Boulevard',
    'Boulv': 'Boulevard',
    
    # Drive variations
    'Dr': 'Drive',
    'Drv': 'Drive',
    'Drive': 'Drive',
    'Drives': 'Drive',
    
    # Lane variations
    'Ln': 'Lane',
    'Lane': 'Lane',
    'Lanes': 'Lane',
    
    # Place variations
    'Pl': 'Place',
    'Place': 'Place',
    'Places': 'Place',
    
    # Court variations
    'Ct': 'Court',
    'Court': 'Court',
    'Courts': 'Court',
    'Crt': 'Court',
    
    # Parkway variations
    'Pkwy': 'Parkway',
    'Pky': 'Parkway',
    'Parkway': 'Parkway',
    'Park': 'Parkway',  # Only when clearly a parkway context
    'Pkway': 'Parkway',
    
    # Highway variations
    'Hwy': 'Highway',
    'Highway': 'Highway',
    'Highways': 'Highway',
    'Hiway': 'Highway',
    'Hiwy': 'Highway',
    
    # Additional common variations
    'Circle': 'Circle',
    'Cir': 'Circle',
    'Terrace': 'Terrace', 
    'Ter': 'Terrace',
    'Way': 'Way',
    'Trail': 'Trail',
    'Trl': 'Trail',
    'Path': 'Path',
    'Walk': 'Walk',
    'Alley': 'Alley',
    'Aly': 'Alley',
    'Plaza': 'Plaza',
    'Plz': 'Plaza',
    'Square': 'Square',
    'Sq': 'Square',
    'Loop': 'Loop',
    'Ridge': 'Ridge',
    'Run': 'Run',
    'Creek': 'Creek',
    'Crk': 'Creek',
}

def standardize_street_type(street_name: str) -> str:
    """
    Standardize street types in a street name.
    
    Args:
        street_name: The street name to standardize (e.g., "Main St", "Oak Ave")
        
    Returns:
        Standardized street name (e.g., "Main Street", "Oak Avenue")
        
    Examples:
        standardize_street_type("Main St") -> "Main Street"
        standardize_street_type("Oak Ave") -> "Oak Avenue"  
        standardize_street_type("First Blvd") -> "First Boulevard"
        standardize_street_type("Park Pkwy") -> "Park Parkway"
    """
    if not street_name or not street_name.strip():
        return street_name
    
    # Split the street name into parts
    parts = street_name.strip().split()
    if not parts:
        return street_name
    
    # The street type is typically the last word
    last_part = parts[-1]
    
    # Check if the last part is a street type that needs standardization
    # Use case-insensitive lookup
    street_type_key = last_part
    for key in STREET_TYPE_MAPPING.keys():
        if last_part.lower() == key.lower():
            street_type_key = key
            break
    
    if street_type_key in STREET_TYPE_MAPPING:
        # Replace the last part with the standardized version
        parts[-1] = STREET_TYPE_MAPPING[street_type_key]
        return ' '.join(parts)
    
    return street_name

def standardize_full_address_components(street_number: str, street_name: str, unit: str) -> tuple:
    """
    Standardize all components of an address.
    
    Args:
        street_number: Street number (e.g., "123", "456A")
        street_name: Street name (e.g., "Main St", "Oak Ave")
        unit: Unit/apartment (e.g., "Apt 2B", "Suite 100")
        
    Returns:
        Tuple of (standardized_street_number, standardized_street_name, standardized_unit)
    """
    # Street number typically doesn't need standardization, just clean whitespace
    clean_number = street_number.strip() if street_number else street_number
    
    # Standardize street name 
    clean_street_name = standardize_street_type(street_name) if street_name else street_name
    
    # Unit typically doesn't need standardization, just clean whitespace
    clean_unit = unit.strip() if unit else unit
    
    return clean_number, clean_street_name, clean_unit

def rebuild_street_address(street_number: str, street_name: str, unit: str) -> str:
    """
    Rebuild the full street address from components.
    
    Args:
        street_number: Street number
        street_name: Street name  
        unit: Unit/apartment
        
    Returns:
        Complete street address string
    """
    parts = []
    
    if street_number:
        parts.append(street_number)
    
    if street_name:
        parts.append(street_name)
        
    if unit:
        parts.append(unit)
    
    return ' '.join(parts)

def get_street_type_statistics(street_names: list) -> Dict[str, int]:
    """
    Analyze street types in a list of street names and return statistics.
    
    Args:
        street_names: List of street names to analyze
        
    Returns:
        Dictionary with street type counts
    """
    street_type_counts = {}
    
    for street_name in street_names:
        if not street_name:
            continue
            
        parts = street_name.strip().split()
        if parts:
            last_part = parts[-1]
            # Standardize to get the canonical form
            standardized = standardize_street_type(street_name)
            std_parts = standardized.split()
            if std_parts:
                std_type = std_parts[-1]
                street_type_counts[std_type] = street_type_counts.get(std_type, 0) + 1
    
    return street_type_counts

# Pre-compiled regex patterns for performance
STREET_TYPE_PATTERNS = {
    standard_type: re.compile(
        r'\b(' + '|'.join(
            re.escape(variant) for variant, target in STREET_TYPE_MAPPING.items() 
            if target == standard_type
        ) + r')\b$', 
        re.IGNORECASE
    )
    for standard_type in STANDARD_STREET_TYPES
}

def quick_standardize_street_type(street_name: str) -> str:
    """
    Optimized version of street type standardization using pre-compiled regex.
    
    Args:
        street_name: The street name to standardize
        
    Returns:
        Standardized street name
    """
    if not street_name or not street_name.strip():
        return street_name
    
    street_name = street_name.strip()
    
    # Try each standard type pattern
    for standard_type, pattern in STREET_TYPE_PATTERNS.items():
        match = pattern.search(street_name)
        if match:
            # Replace the matched suffix with the standard form
            return pattern.sub(standard_type, street_name)
    
    return street_name