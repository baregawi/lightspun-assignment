#!/usr/bin/env python3
"""
Test script for street type standardization functionality
"""

import sys
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from lightspun.utils.street_standardization import (
    standardize_street_type,
    standardize_full_address_components,
    rebuild_street_address,
    STREET_TYPE_MAPPING
)

def test_street_standardization():
    """Test the street type standardization function"""
    
    test_cases = [
        # Basic street type standardization
        ("Main St", "Main Street"),
        ("Oak Ave", "Oak Avenue"),
        ("First Rd", "First Road"),
        ("Lincoln Blvd", "Lincoln Boulevard"),
        ("Park Dr", "Park Drive"),
        ("Oak Ln", "Oak Lane"),
        ("Washington Pl", "Washington Place"),
        ("Adams Ct", "Adams Court"),
        ("Central Pkwy", "Central Parkway"),
        ("State Hwy", "State Highway"),
        
        # Already standardized (should remain unchanged)
        ("Main Street", "Main Street"),
        ("Oak Avenue", "Oak Avenue"),
        ("First Road", "First Road"),
        ("Lincoln Boulevard", "Lincoln Boulevard"),
        
        # Case variations
        ("main st", "main Street"),
        ("OAK AVE", "OAK Avenue"),
        ("First RD", "First Road"),
        
        # Multiple words
        ("North Main St", "North Main Street"),
        ("East Oak Ave", "East Oak Avenue"),
        ("West First Rd", "West First Road"),
        
        # Edge cases
        ("Main", "Main"),  # No street type
        ("St", "Street"),  # Just street type
        ("", ""),  # Empty string
        
        # Additional types
        ("Oak Cir", "Oak Circle"),
        ("Hill Ter", "Hill Terrace"),
        ("Park Way", "Park Way"),
        ("Forest Trl", "Forest Trail"),
    ]
    
    print("🧪 Testing Street Type Standardization")
    print("=" * 60)
    
    all_passed = True
    
    for i, (input_street, expected) in enumerate(test_cases, 1):
        result = standardize_street_type(input_street)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Test {i:2d}: {status}")
        print(f"  Input:    '{input_street}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
        
        if not passed:
            print(f"  ERROR: Expected '{expected}', got '{result}'")
        print()
    
    return all_passed

def test_full_address_standardization():
    """Test full address component standardization"""
    
    test_cases = [
        # (street_number, street_name, unit) -> expected results
        ("123", "Main St", None, ("123", "Main Street", None)),
        ("456A", "Oak Ave", "Apt 2B", ("456A", "Oak Avenue", "Apt 2B")),
        ("789", "First Blvd", "Suite 100", ("789", "First Boulevard", "Suite 100")),
        (None, "Central Pkwy", None, (None, "Central Parkway", None)),
        ("", "Park Dr", "", ("", "Park Drive", "")),
    ]
    
    print("🧪 Testing Full Address Component Standardization")
    print("=" * 60)
    
    all_passed = True
    
    for i, (street_number, street_name, unit, expected) in enumerate(test_cases, 1):
        result = standardize_full_address_components(street_number, street_name, unit)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Test {i:2d}: {status}")
        print(f"  Input:    ({street_number!r}, {street_name!r}, {unit!r})")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        
        if not passed:
            print(f"  ERROR: Expected {expected}, got {result}")
        print()
    
    return all_passed

def test_address_rebuilding():
    """Test address rebuilding from components"""
    
    test_cases = [
        # (street_number, street_name, unit) -> expected address
        ("123", "Main Street", None, "123 Main Street"),
        ("456A", "Oak Avenue", "Apt 2B", "456A Oak Avenue Apt 2B"),
        ("789", "First Boulevard", "Suite 100", "789 First Boulevard Suite 100"),
        (None, "Central Parkway", None, "Central Parkway"),
        ("123", "Main Street", "", "123 Main Street"),
        ("", "Oak Avenue", "Apt 5", "Oak Avenue Apt 5"),
    ]
    
    print("🧪 Testing Address Rebuilding")
    print("=" * 60)
    
    all_passed = True
    
    for i, (street_number, street_name, unit, expected) in enumerate(test_cases, 1):
        result = rebuild_street_address(street_number, street_name, unit)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Test {i:2d}: {status}")
        print(f"  Input:    ({street_number!r}, {street_name!r}, {unit!r})")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
        
        if not passed:
            print(f"  ERROR: Expected '{expected}', got '{result}'")
        print()
    
    return all_passed

def show_mapping_stats():
    """Show statistics about the street type mapping"""
    
    print("📊 Street Type Mapping Statistics")
    print("=" * 60)
    
    target_types = set(STREET_TYPE_MAPPING.values())
    print(f"Standard target types: {len(target_types)}")
    print(f"Total mapping variants: {len(STREET_TYPE_MAPPING)}")
    
    print("\nMappings by target type:")
    for target in sorted(target_types):
        variants = [k for k, v in STREET_TYPE_MAPPING.items() if v == target]
        print(f"  {target}: {len(variants)} variants")
        print(f"    {', '.join(sorted(variants))}")
    
    print()

def main():
    """Run all tests"""
    print("🚀 Street Type Standardization Test Suite")
    print("=" * 80)
    
    show_mapping_stats()
    
    try:
        test1_passed = test_street_standardization()
        test2_passed = test_full_address_standardization() 
        test3_passed = test_address_rebuilding()
        
        print("=" * 80)
        if all([test1_passed, test2_passed, test3_passed]):
            print("🎉 All tests passed successfully!")
            print("✅ Street type standardization is working correctly")
            return 0
        else:
            print("❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())