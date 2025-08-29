#!/usr/bin/env python3
"""
Test script for street address parsing functionality
"""

import sys
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent))

from lightspun.services import parse_street_address

def test_address_parsing():
    """Test the address parsing function with various examples"""
    
    test_cases = [
        # Basic cases
        ("1070 Pierce Pl", ("1070", "Pierce Pl", None)),
        ("1077 Roosevelt Ct", ("1077", "Roosevelt Ct", None)),
        ("1201 East Dr", ("1201", "East Dr", None)),
        ("148 West Rd", ("148", "West Rd", None)),
        
        # Cases with apartment/unit
        ("123 Main Street Apt 2B", ("123", "Main Street", "Apt 2B")),
        ("456A Oak Avenue Suite 100", ("456A", "Oak Avenue", "Suite 100")),
        ("789 First Street Unit 5", ("789", "First Street", "Unit 5")),
        ("1000 Broadway #205", ("1000", "Broadway", "# 205")),
        
        # Cases with different formats
        ("42A Lincoln Blvd", ("42A", "Lincoln Blvd", None)),
        ("5555 Central Park Ave", ("5555", "Central Park Ave", None)),
        
        # Edge cases
        ("Main Street", (None, "Main Street", None)),  # No number
        ("", (None, "", None)),  # Empty string
        ("123", ("123", "", None)),  # Just number
    ]
    
    print("🧪 Testing Street Address Parsing")
    print("=" * 50)
    
    all_passed = True
    
    for i, (input_addr, expected) in enumerate(test_cases, 1):
        result = parse_street_address(input_addr)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Test {i:2d}: {status}")
        print(f"  Input:    '{input_addr}'")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        
        if not passed:
            print(f"  ERROR: Expected {expected}, got {result}")
        print()
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = test_address_parsing()
    sys.exit(0 if success else 1)