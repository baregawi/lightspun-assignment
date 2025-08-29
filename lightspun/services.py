import re
from typing import List, Optional
from .database import database
from .schemas import (
    State, StateCreate, StateUpdate,
    Municipality, MunicipalityCreate, MunicipalityUpdate,
    Address, AddressCreate, AddressUpdate, AddressCreateMinimal
)
from .logging_config import get_logger
from .street_standardization import (
    standardize_street_type, 
    standardize_full_address_components,
    rebuild_street_address
)

# Initialize loggers for each service
state_logger = get_logger('lightspun.services.state')
municipality_logger = get_logger('lightspun.services.municipality')
address_logger = get_logger('lightspun.services.address')

def parse_street_address(street_address: str) -> tuple:
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
    
    return (street_number, street_name, unit)

class StateService:
    """Service class for state operations"""

    @staticmethod
    async def get_all_states() -> List[State]:
        """Get all states"""
        state_logger.debug("Fetching all states from database")
        query = "SELECT id, code, name FROM states ORDER BY name"
        rows = await database.fetch_all(query=query)
        state_logger.debug(f"Retrieved {len(rows)} states from database")
        return [State.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_state_by_code(state_code: str) -> Optional[State]:
        """Get state by code"""
        state_logger.debug(f"Fetching state by code: {state_code}")
        query = "SELECT id, code, name FROM states WHERE code = :code"
        row = await database.fetch_one(query=query, values={"code": state_code.upper()})
        if row:
            state_logger.debug(f"Found state: {row['name']} ({row['code']})")
            return State.model_validate(dict(row))
        else:
            state_logger.warning(f"State not found for code: {state_code}")
            return None

    @staticmethod
    async def get_state_by_id(state_id: int) -> Optional[State]:
        """Get state by ID"""
        query = "SELECT id, code, name FROM states WHERE id = :id"
        row = await database.fetch_one(query=query, values={"id": state_id})
        return State.model_validate(dict(row)) if row else None

    @staticmethod
    async def create_state(state_data: StateCreate) -> State:
        """Create a new state"""
        query = """
            INSERT INTO states (code, name) 
            VALUES (:code, :name) 
            RETURNING id, code, name
        """
        values = state_data.model_dump()
        row = await database.fetch_one(query=query, values=values)
        return State.model_validate(dict(row))

    @staticmethod
    async def update_state(state_id: int, state_data: StateUpdate) -> Optional[State]:
        """Update a state"""
        update_data = state_data.model_dump(exclude_unset=True)
        if not update_data:
            return await StateService.get_state_by_id(state_id)
        
        set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        query = f"""
            UPDATE states 
            SET {set_clause} 
            WHERE id = :id 
            RETURNING id, code, name
        """
        values = {**update_data, "id": state_id}
        row = await database.fetch_one(query=query, values=values)
        return State.model_validate(dict(row)) if row else None

    @staticmethod
    async def delete_state(state_id: int) -> bool:
        """Delete a state"""
        query = "DELETE FROM states WHERE id = :id"
        result = await database.execute(query=query, values={"id": state_id})
        return result > 0

class MunicipalityService:
    """Service class for municipality operations"""

    @staticmethod
    async def get_municipalities_by_state_code(state_code: str) -> List[Municipality]:
        """Get municipalities by state code (optimized with state_id index)"""
        municipality_logger.debug(f"Fetching municipalities for state: {state_code}")
        
        # Optimized query that uses the ix_municipalities_state_id index
        query = """
            SELECT m.id, m.name, m.type, m.state_id 
            FROM municipalities m
            JOIN states s ON m.state_id = s.id
            WHERE s.code = :state_code
            ORDER BY m.name
        """
        rows = await database.fetch_all(query=query, values={"state_code": state_code.upper()})
        municipality_logger.debug(f"Found {len(rows)} municipalities in state {state_code}")
        return [Municipality.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_municipalities_by_state_id(state_id: int) -> List[Municipality]:
        """Get municipalities by state ID (optimized with state_id index)"""
        municipality_logger.debug(f"Fetching municipalities for state_id: {state_id}")
        
        # This query will directly use the ix_municipalities_state_id index
        query = """
            SELECT id, name, type, state_id 
            FROM municipalities
            WHERE state_id = :state_id
            ORDER BY name
        """
        rows = await database.fetch_all(query=query, values={"state_id": state_id})
        municipality_logger.debug(f"Found {len(rows)} municipalities for state_id {state_id}")
        return [Municipality.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def search_municipalities_by_name(name_query: str, limit: int = 20) -> List[Municipality]:
        """Search municipalities by name (optimized with name index)"""
        municipality_logger.debug(f"Searching municipalities with name: {name_query}")
        
        # This query will use the ix_municipalities_name index for prefix searches
        query = """
            SELECT id, name, type, state_id 
            FROM municipalities
            WHERE name ILIKE :prefix_term
               OR name ILIKE :contains_term
            ORDER BY 
                CASE WHEN name ILIKE :prefix_term THEN 1 ELSE 2 END,
                name
            LIMIT :limit
        """
        prefix_term = f"{name_query}%"    # Prefix search can use index
        contains_term = f"%{name_query}%" # Fallback for substring search
        
        rows = await database.fetch_all(
            query=query, 
            values={
                "prefix_term": prefix_term,
                "contains_term": contains_term,
                "limit": limit
            }
        )
        municipality_logger.debug(f"Found {len(rows)} municipalities matching '{name_query}'")
        return [Municipality.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_municipalities_by_state_id(state_id: int) -> List[Municipality]:
        """Get municipalities by state ID"""
        query = """
            SELECT id, name, type, state_id 
            FROM municipalities 
            WHERE state_id = :state_id
            ORDER BY name
        """
        rows = await database.fetch_all(query=query, values={"state_id": state_id})
        return [Municipality.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_municipality_by_id(municipality_id: int) -> Optional[Municipality]:
        """Get municipality by ID"""
        query = "SELECT id, name, type, state_id FROM municipalities WHERE id = :id"
        row = await database.fetch_one(query=query, values={"id": municipality_id})
        return Municipality.model_validate(dict(row)) if row else None

    @staticmethod
    async def create_municipality(municipality_data: MunicipalityCreate) -> Municipality:
        """Create a new municipality"""
        query = """
            INSERT INTO municipalities (name, type, state_id) 
            VALUES (:name, :type, :state_id) 
            RETURNING id, name, type, state_id
        """
        values = municipality_data.model_dump()
        row = await database.fetch_one(query=query, values=values)
        return Municipality.model_validate(dict(row))

    @staticmethod
    async def update_municipality(municipality_id: int, municipality_data: MunicipalityUpdate) -> Optional[Municipality]:
        """Update a municipality"""
        update_data = municipality_data.model_dump(exclude_unset=True)
        if not update_data:
            return await MunicipalityService.get_municipality_by_id(municipality_id)
        
        set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        query = f"""
            UPDATE municipalities 
            SET {set_clause} 
            WHERE id = :id 
            RETURNING id, name, type, state_id
        """
        values = {**update_data, "id": municipality_id}
        row = await database.fetch_one(query=query, values=values)
        return Municipality.model_validate(dict(row)) if row else None

    @staticmethod
    async def delete_municipality(municipality_id: int) -> bool:
        """Delete a municipality"""
        query = "DELETE FROM municipalities WHERE id = :id"
        result = await database.execute(query=query, values={"id": municipality_id})
        return result > 0

class AddressService:
    """Service class for address operations"""

    @staticmethod
    async def search_addresses(search_query: str, limit: int = 10) -> List[str]:
        """Search addresses by query string with standardization (optimized with indexes)"""
        address_logger.debug(f"Searching addresses with query: {search_query}")
        
        # Standardize the search query for better matching
        standardized_query = standardize_street_type(search_query.strip())
        
        # Optimized query that can use the street_address index for prefix searches
        query = """
            SELECT full_address 
            FROM addresses 
            WHERE street_address ILIKE :prefix_term
               OR street_address ILIKE :std_prefix_term
               OR LOWER(full_address) LIKE LOWER(:full_term)
               OR LOWER(full_address) LIKE LOWER(:std_full_term)
            ORDER BY 
                CASE 
                    WHEN street_address ILIKE :prefix_term THEN 1 
                    WHEN street_address ILIKE :std_prefix_term THEN 2
                    ELSE 3 
                END,
                full_address
            LIMIT :limit
        """
        prefix_term = f"{search_query}%"  # Original prefix search
        std_prefix_term = f"{standardized_query}%"  # Standardized prefix search
        full_term = f"%{search_query}%"   # Original fallback search
        std_full_term = f"%{standardized_query}%"   # Standardized fallback search
        
        rows = await database.fetch_all(
            query=query, 
            values={
                "prefix_term": prefix_term,
                "std_prefix_term": std_prefix_term,
                "full_term": full_term,
                "std_full_term": std_full_term,
                "limit": limit
            }
        )
        address_logger.debug(f"Found {len(rows)} matching addresses for '{search_query}' (standardized: '{standardized_query}')")
        return [row["full_address"] for row in rows]

    @staticmethod
    async def search_addresses_by_city(city: str, limit: int = 10) -> List[Address]:
        """Search addresses by city (optimized with city index)"""
        address_logger.debug(f"Searching addresses in city: {city}")
        
        # This query will use the ix_addresses_city index for fast city lookups
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE LOWER(city) = LOWER(:city)
            ORDER BY street_address
            LIMIT :limit
        """
        rows = await database.fetch_all(query=query, values={"city": city, "limit": limit})
        address_logger.debug(f"Found {len(rows)} addresses in {city}")
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def search_addresses_by_state(state_code: str, limit: int = 50) -> List[Address]:
        """Search addresses by state code (optimized with state_code index)"""
        address_logger.debug(f"Searching addresses in state: {state_code}")
        
        # This query will use the ix_addresses_state_code index for fast state lookups
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE state_code = UPPER(:state_code)
            ORDER BY city, street_address
            LIMIT :limit
        """
        rows = await database.fetch_all(
            query=query, 
            values={"state_code": state_code, "limit": limit}
        )
        address_logger.debug(f"Found {len(rows)} addresses in state {state_code}")
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def search_addresses_by_city_and_state(
        city: str, 
        state_code: str, 
        limit: int = 20
    ) -> List[Address]:
        """Search addresses by city and state (optimized with composite index)"""
        address_logger.debug(f"Searching addresses in {city}, {state_code}")
        
        # This query will use the ix_addresses_city_state composite index
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE LOWER(city) = LOWER(:city) 
              AND state_code = UPPER(:state_code)
            ORDER BY street_address
            LIMIT :limit
        """
        rows = await database.fetch_all(
            query=query, 
            values={"city": city, "state_code": state_code, "limit": limit}
        )
        address_logger.debug(f"Found {len(rows)} addresses in {city}, {state_code}")
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_all_addresses() -> List[Address]:
        """Get all addresses"""
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address 
            FROM addresses 
            ORDER BY full_address
        """
        rows = await database.fetch_all(query=query)
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_address_by_id(address_id: int) -> Optional[Address]:
        """Get address by ID"""
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address 
            FROM addresses 
            WHERE id = :id
        """
        row = await database.fetch_one(query=query, values={"id": address_id})
        return Address.model_validate(dict(row)) if row else None

    @staticmethod
    async def create_address(address_data: AddressCreate) -> Address:
        """Create a new address with street type standardization"""
        # Parse street address if components are not provided
        street_number = address_data.street_number
        street_name = address_data.street_name  
        unit = address_data.unit
        
        # If street components are missing but street_address is provided, parse it
        if not street_name and address_data.street_address:
            parsed_number, parsed_name, parsed_unit = parse_street_address(address_data.street_address)
            street_number = street_number or parsed_number
            street_name = street_name or parsed_name
            unit = unit or parsed_unit
        
        # Standardize street type if street_name is provided directly
        if street_name:
            street_name = standardize_street_type(street_name)
        
        # Rebuild standardized street address
        standardized_street_address = rebuild_street_address(street_number, street_name, unit)
        full_address = f"{standardized_street_address}, {address_data.city}, {address_data.state_code}"
        
        query = """
            INSERT INTO addresses (street_number, street_name, unit, street_address, city, state_code, full_address) 
            VALUES (:street_number, :street_name, :unit, :street_address, :city, :state_code, :full_address) 
            RETURNING id, street_number, street_name, unit, street_address, city, state_code, full_address
        """
        values = {
            "street_number": street_number,
            "street_name": street_name,
            "unit": unit,
            "street_address": standardized_street_address,
            "city": address_data.city,
            "state_code": address_data.state_code,
            "full_address": full_address
        }
        row = await database.fetch_one(query=query, values=values)
        return Address.model_validate(dict(row))
    
    @staticmethod
    async def create_address_minimal(address_data: AddressCreateMinimal) -> Address:
        """Create a new address with automatic street address parsing"""
        # Parse the street address into components
        street_number, street_name, unit = parse_street_address(address_data.street_address)
        
        full_address = f"{address_data.street_address}, {address_data.city}, {address_data.state_code}"
        
        query = """
            INSERT INTO addresses (street_number, street_name, unit, street_address, city, state_code, full_address) 
            VALUES (:street_number, :street_name, :unit, :street_address, :city, :state_code, :full_address) 
            RETURNING id, street_number, street_name, unit, street_address, city, state_code, full_address
        """
        values = {
            "street_number": street_number,
            "street_name": street_name,
            "unit": unit,
            "street_address": address_data.street_address,
            "city": address_data.city,
            "state_code": address_data.state_code,
            "full_address": full_address
        }
        row = await database.fetch_one(query=query, values=values)
        return Address.model_validate(dict(row))

    @staticmethod
    async def update_address(address_id: int, address_data: AddressUpdate) -> Optional[Address]:
        """Update an address"""
        update_data = address_data.model_dump(exclude_unset=True)
        if not update_data:
            return await AddressService.get_address_by_id(address_id)
        
        # Get current address
        current_address = await AddressService.get_address_by_id(address_id)
        if not current_address:
            return None
        
        # Handle street address parsing if street_address is updated but components aren't
        if "street_address" in update_data:
            street_address = update_data["street_address"]
            
            # If individual components weren't provided, parse the new street address
            if not any(field in update_data for field in ["street_number", "street_name", "unit"]):
                street_number, street_name, unit = parse_street_address(street_address)
                update_data["street_number"] = street_number
                update_data["street_name"] = street_name  
                update_data["unit"] = unit
        
        # If any address component is updated, regenerate full address
        street_address = update_data.get("street_address", current_address.street_address)
        city = update_data.get("city", current_address.city)
        state_code = update_data.get("state_code", current_address.state_code)
        full_address = f"{street_address}, {city}, {state_code}"
        
        update_data["full_address"] = full_address
        
        set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        query = f"""
            UPDATE addresses 
            SET {set_clause} 
            WHERE id = :id 
            RETURNING id, street_number, street_name, unit, street_address, city, state_code, full_address
        """
        values = {**update_data, "id": address_id}
        row = await database.fetch_one(query=query, values=values)
        return Address.model_validate(dict(row)) if row else None

    @staticmethod
    async def search_addresses_by_street_name(street_name: str, limit: int = 20) -> List[Address]:
        """Search addresses by street name with standardization (optimized with street_name index)"""
        address_logger.debug(f"Searching addresses on street: {street_name}")
        
        # Standardize the search term before querying
        standardized_street_name = standardize_street_type(street_name.strip())
        
        # This query will use the ix_addresses_street_name index for street name lookups
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE LOWER(street_name) LIKE LOWER(:street_name)
            ORDER BY city, street_number
            LIMIT :limit
        """
        rows = await database.fetch_all(
            query=query, 
            values={"street_name": f"%{standardized_street_name}%", "limit": limit}
        )
        address_logger.debug(f"Found {len(rows)} addresses on {standardized_street_name}")
        return [Address.model_validate(dict(row)) for row in rows]
    
    @staticmethod
    async def search_addresses_by_street_number(street_number: str, limit: int = 20) -> List[Address]:
        """Search addresses by street number (optimized with street_number index)"""
        address_logger.debug(f"Searching addresses with number: {street_number}")
        
        # This query will use the ix_addresses_street_number index for street number lookups
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE street_number = :street_number
            ORDER BY city, street_name
            LIMIT :limit
        """
        rows = await database.fetch_all(
            query=query, 
            values={"street_number": street_number, "limit": limit}
        )
        address_logger.debug(f"Found {len(rows)} addresses with number {street_number}")
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def delete_address(address_id: int) -> bool:
        """Delete an address"""
        query = "DELETE FROM addresses WHERE id = :id"
        result = await database.execute(query=query, values={"id": address_id})
        return result > 0