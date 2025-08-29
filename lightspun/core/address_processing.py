"""
Address Processing Module

This module handles all address-related processing including:
- Address parsing and component extraction
- Street type standardization
- Address validation and formatting
- Address component reconstruction

This centralizes address logic that was previously scattered across services.
"""

import re
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

from ..utils.street_standardization import (
    standardize_street_type,
    rebuild_street_address,
    STREET_TYPE_MAPPING
)


@dataclass
class AddressComponents:
    """Structured representation of address components"""
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    unit: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    full_address: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if address has minimum required components"""
        return bool(self.street_name and self.city and self.state_code)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations"""
        return {
            'street_number': self.street_number,
            'street_name': self.street_name, 
            'unit': self.unit,
            'street_address': self.street_address,
            'city': self.city,
            'state_code': self.state_code,
            'full_address': self.full_address
        }


class AddressParser:
    """Handles parsing addresses into components"""
    
    @staticmethod
    def parse_street_address(street_address: str) -> AddressComponents:
        """
        Parse a street address into components (street_number, street_name, unit) with standardization.
        
        Examples:
        - "123 Main St" -> ("123", "Main Street", None)
        - "456A Oak Ave Apt 2B" -> ("456A", "Oak Avenue", "Apt 2B")
        - "789 First Blvd Suite 100" -> ("789", "First Boulevard", "Suite 100")
        """
        if not street_address:
            return (None, street_address or "", None)
        
        # Pattern to match: [number] [street name] [optional unit]
        # Unit patterns: Apt, Suite, Unit, #, etc.
        unit_pattern = r'\s+(apt|apartment|suite|unit|#|ste|bldg|building)\s*\.?\s*(.+)$'
        
        # First, extract unit if present (case insensitive)
        unit_match = re.search(unit_pattern, street_address, re.IGNORECASE)
        unit = None
        base_address = street_address
        
        if unit_match:
            unit = f"{unit_match.group(1).title()} {unit_match.group(2)}"
            base_address = street_address[:unit_match.start()].strip()
        
        # Now extract street number from the remaining address
        number_pattern = r'^(\d+[A-Za-z]?)\s+(.+)$'
        number_match = re.match(number_pattern, base_address.strip())
        
        if number_match:
            street_number = number_match.group(1)
            street_name = number_match.group(2).strip()
        else:
            # No number found, treat entire base address as street name
            street_number = None
            street_name = base_address.strip()
        
        # Standardize the street name (standardize street type suffixes)
        if street_name:
            street_name = standardize_street_type(street_name)
        
        return AddressComponents(
            street_number=street_number,
            street_name=street_name,
            unit=unit
        )
    
    @staticmethod
    def parse_full_address(
        street_number: Optional[str] = None,
        street_name: Optional[str] = None, 
        unit: Optional[str] = None,
        street_address: Optional[str] = None,
        city: Optional[str] = None,
        state_code: Optional[str] = None
    ) -> AddressComponents:
        """
        Parse and standardize a complete address into components.
        
        Can work with either individual components or a full street_address that needs parsing.
        """
        # If we have a street_address but missing components, parse it
        if street_address and not street_name:
            parsed_number, parsed_name, parsed_unit = AddressParser.parse_street_address(street_address)
            street_number = street_number or parsed_number
            street_name = street_name or parsed_name  
            unit = unit or parsed_unit
        
        # Standardize street name if provided
        if street_name:
            street_name = standardize_street_type(street_name)
        
        # Rebuild street address from components
        if street_number or street_name or unit:
            street_address = rebuild_street_address(street_number, street_name, unit)
        
        # Build full address
        full_address = None
        if street_address and city and state_code:
            full_address = f"{street_address}, {city}, {state_code}"
        
        return AddressComponents(
            street_number=street_number,
            street_name=street_name,
            unit=unit, 
            street_address=street_address,
            city=city,
            state_code=state_code,
            full_address=full_address
        )


class AddressValidator:
    """Handles address validation and normalization"""
    
    @staticmethod
    def validate_state_code(state_code: str) -> str:
        """Validate and normalize state code"""
        if not state_code:
            raise ValueError("State code is required")
        
        normalized = state_code.strip().upper()
        if len(normalized) != 2:
            raise ValueError("State code must be exactly 2 characters")
        
        return normalized
    
    @staticmethod
    def validate_city(city: str) -> str:
        """Validate and normalize city name"""
        if not city:
            raise ValueError("City is required")
        
        normalized = city.strip()
        if len(normalized) < 1:
            raise ValueError("City name cannot be empty")
        
        return normalized
    
    @staticmethod 
    def validate_street_name(street_name: str) -> str:
        """Validate and normalize street name"""
        if not street_name:
            raise ValueError("Street name is required")
        
        normalized = street_name.strip()
        if len(normalized) < 1:
            raise ValueError("Street name cannot be empty")
        
        return normalized
    
    @staticmethod
    def validate_address_components(components: AddressComponents) -> AddressComponents:
        """Validate all address components and return normalized version"""
        validated_components = AddressComponents()
        
        # Copy over street number and unit as-is (optional fields)
        validated_components.street_number = components.street_number
        validated_components.unit = components.unit
        
        # Validate required fields
        if components.street_name:
            validated_components.street_name = AddressValidator.validate_street_name(components.street_name)
        
        if components.city:
            validated_components.city = AddressValidator.validate_city(components.city)
            
        if components.state_code:
            validated_components.state_code = AddressValidator.validate_state_code(components.state_code)
        
        # Rebuild derived fields
        if validated_components.street_number or validated_components.street_name or validated_components.unit:
            validated_components.street_address = rebuild_street_address(
                validated_components.street_number,
                validated_components.street_name,
                validated_components.unit
            )
        
        if validated_components.street_address and validated_components.city and validated_components.state_code:
            validated_components.full_address = f"{validated_components.street_address}, {validated_components.city}, {validated_components.state_code}"
        
        return validated_components


class AddressFormatter:
    """Handles address formatting and display"""
    
    @staticmethod
    def format_address_line(components: AddressComponents, include_unit: bool = True) -> str:
        """Format address as a single line"""
        parts = []
        
        if components.street_number:
            parts.append(components.street_number)
        
        if components.street_name:
            parts.append(components.street_name)
        
        if include_unit and components.unit:
            parts.append(components.unit)
        
        return ' '.join(parts)
    
    @staticmethod  
    def format_full_address(components: AddressComponents) -> str:
        """Format complete address with city and state"""
        street_line = AddressFormatter.format_address_line(components)
        
        if components.city and components.state_code:
            return f"{street_line}, {components.city}, {components.state_code}"
        
        return street_line
    
    @staticmethod
    def format_for_display(components: AddressComponents) -> Dict[str, str]:
        """Format address for UI display with multiple representations"""
        return {
            'street_line': AddressFormatter.format_address_line(components),
            'street_line_no_unit': AddressFormatter.format_address_line(components, include_unit=False),
            'full_address': AddressFormatter.format_full_address(components),
            'city_state': f"{components.city}, {components.state_code}" if components.city and components.state_code else ""
        }


# Convenience functions for backward compatibility
def parse_street_address(street_address: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Convenience function for backward compatibility"""
    components = AddressParser.parse_street_address(street_address)
    return (components.street_number, components.street_name, components.unit)


def standardize_full_address_components(
    street_number: Optional[str], 
    street_name: Optional[str], 
    unit: Optional[str]
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Convenience function for backward compatibility"""
    components = AddressParser.parse_full_address(
        street_number=street_number,
        street_name=street_name,
        unit=unit
    )
    return (components.street_number, components.street_name, components.unit)