"""
Address Service Module

This module handles all address-related business logic and db.database operations.
Provides CRUD operations, fuzzy search, and address validation/parsing.
"""

from typing import List, Optional

from .. import database as db
from ..schemas import Address, AddressCreate, AddressUpdate, AddressCreateMinimal
from ..logging_config import get_logger
from ..utils.database_operations import DatabaseOperations
from ..core.address_processing import AddressParser, AddressValidator, AddressFormatter
from ..core.fuzzy_search import AddressFuzzySearch, FuzzySearchConfig
from ..utils.street_standardization import standardize_street_type, rebuild_street_address

# Initialize logger
address_logger = get_logger('lightspun.services.address')


class AddressService:
    """Service class for address operations"""

    @staticmethod
    async def get_address_by_id(address_id: int) -> Optional[Address]:
        """Get address by ID"""
        address_logger.debug(f"Fetching address by ID: {address_id}")
        
        result = await DatabaseOperations.get_by_id(
            table="addresses",
            id_value=address_id,
            fields=["id", "street_number", "street_name", "unit", "street_address", "city", "state_code", "full_address"]
        )
        
        if result:
            address_logger.debug(f"Found address: {result['full_address']}")
            return Address.model_validate(result)
        else:
            address_logger.warning(f"Address not found for ID: {address_id}")
            return None

    @staticmethod
    async def search_addresses_by_city(city: str, limit: int = 50) -> List[Address]:
        """Search addresses by city (optimized with city index)"""
        address_logger.debug(f"Fetching addresses for city: {city}")
        
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE LOWER(city) = LOWER(:city)
            ORDER BY street_name, street_number
            LIMIT :limit
        """
        rows = await db.database.fetch_all(query=query, values={"city": city, "limit": limit})
        address_logger.debug(f"Found {len(rows)} addresses in {city}")
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def search_addresses_by_state(state_code: str, limit: int = 50) -> List[Address]:
        """Search addresses by state code"""
        address_logger.debug(f"Fetching addresses for state: {state_code}")
        
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE state_code = :state_code
            ORDER BY city, street_name, street_number
            LIMIT :limit
        """
        rows = await db.database.fetch_all(
            query=query, 
            values={"state_code": state_code.upper(), "limit": limit}
        )
        address_logger.debug(f"Found {len(rows)} addresses in state {state_code}")
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def create_address(address_data: AddressCreate) -> Address:
        """Create a new address with comprehensive validation"""
        address_logger.info(f"Creating new address: {address_data.street_address}, {address_data.city}")
        
        # Parse and validate address components
        parser = AddressParser()
        validator = AddressValidator()
        formatter = AddressFormatter()
        
        # If components aren't provided, parse from street_address
        street_number = address_data.street_number
        street_name = address_data.street_name  
        unit = address_data.unit
        
        if not all([street_number, street_name]) and address_data.street_address:
            address_components = parser.parse_street_address(address_data.street_address)
            street_number = street_number or address_components.street_number
            street_name = street_name or address_components.street_name
            unit = unit or address_components.unit
        
        # Standardize street name
        if street_name:
            street_name = standardize_street_type(street_name)
        
        # Build final address components
        standardized_street_address = rebuild_street_address(street_number, street_name, unit)
        full_address = formatter.format_full_address(
            street_number, street_name, unit, address_data.city, address_data.state_code
        )
        
        # Validate the complete address
        validation_result = validator.validate_complete_address(
            street_number, street_name, unit, address_data.city, address_data.state_code
        )
        
        if not validation_result.is_valid:
            raise ValueError(f"Invalid address: {'; '.join(validation_result.errors)}")
        
        result = await DatabaseOperations.create(
            table="addresses",
            data={
                "street_number": street_number,
                "street_name": street_name,
                "unit": unit,
                "street_address": standardized_street_address,
                "city": address_data.city,
                "state_code": address_data.state_code,
                "full_address": full_address
            },
            returning=["id", "street_number", "street_name", "unit", "street_address", "city", "state_code", "full_address"]
        )
        
        if result:
            address_logger.info(f"Created address: {result['full_address']}")
            return Address.model_validate(result)
        else:
            raise RuntimeError("Failed to create address")
    
    @staticmethod
    async def create_address_minimal(address_data: AddressCreateMinimal) -> Address:
        """Create a new address with automatic street address parsing"""
        address_logger.info(f"Creating minimal address: {address_data.street_address}")
        
        # Parse the street address into components using new parser
        parser = AddressParser()
        formatter = AddressFormatter()
        
        address_components = parser.parse_street_address(address_data.street_address)
        
        full_address = formatter.format_full_address(
            address_components.street_number,
            address_components.street_name, 
            address_components.unit,
            address_data.city,
            address_data.state_code
        )
        
        result = await DatabaseOperations.create(
            table="addresses",
            data={
                "street_number": address_components.street_number,
                "street_name": address_components.street_name,
                "unit": address_components.unit,
                "street_address": address_data.street_address,
                "city": address_data.city,
                "state_code": address_data.state_code,
                "full_address": full_address
            },
            returning=["id", "street_number", "street_name", "unit", "street_address", "city", "state_code", "full_address"]
        )
        
        if result:
            address_logger.info(f"Created minimal address: {result['full_address']}")
            return Address.model_validate(result)
        else:
            raise RuntimeError("Failed to create address")

    @staticmethod
    async def update_address(address_id: int, address_data: AddressUpdate) -> Optional[Address]:
        """Update an address"""
        update_data = address_data.model_dump(exclude_unset=True)
        if not update_data:
            address_logger.debug(f"No updates provided for address {address_id}")
            return await AddressService.get_address_by_id(address_id)
        
        address_logger.info(f"Updating address {address_id} with data: {update_data}")
        
        # Get current address
        current_address = await AddressService.get_address_by_id(address_id)
        if not current_address:
            address_logger.warning(f"Address {address_id} not found for update")
            return None
        
        # Handle street address parsing if street_address is updated but components aren't
        if "street_address" in update_data:
            street_address = update_data["street_address"]
            
            # If individual components weren't provided, parse the new street address
            if not any(field in update_data for field in ["street_number", "street_name", "unit"]):
                parser = AddressParser()
                address_components = parser.parse_street_address(street_address)
                update_data["street_number"] = address_components.street_number
                update_data["street_name"] = address_components.street_name  
                update_data["unit"] = address_components.unit
        
        # Standardize street name if provided
        if "street_name" in update_data and update_data["street_name"]:
            update_data["street_name"] = standardize_street_type(update_data["street_name"])
        
        # If any address component is updated, regenerate full address
        street_address = update_data.get("street_address", current_address.street_address)
        city = update_data.get("city", current_address.city)
        state_code = update_data.get("state_code", current_address.state_code)
        
        formatter = AddressFormatter()
        street_number = update_data.get("street_number", current_address.street_number)
        street_name = update_data.get("street_name", current_address.street_name)
        unit = update_data.get("unit", current_address.unit)
        
        full_address = formatter.format_full_address(street_number, street_name, unit, city, state_code)
        update_data["full_address"] = full_address
        
        result = await DatabaseOperations.update_by_id(
            table="addresses",
            id_value=address_id,
            data=update_data,
            returning=["id", "street_number", "street_name", "unit", "street_address", "city", "state_code", "full_address"]
        )
        
        if result:
            address_logger.info(f"Updated address: {result['full_address']}")
            return Address.model_validate(result)
        else:
            address_logger.warning(f"Address {address_id} not found for update")
            return None

    @staticmethod
    async def delete_address(address_id: int) -> bool:
        """Delete an address"""
        address_logger.warning(f"Attempting to delete address {address_id}")
        
        # Check if address exists
        address = await AddressService.get_address_by_id(address_id)
        if not address:
            address_logger.warning(f"Address {address_id} not found for deletion")
            return False
        
        success = await DatabaseOperations.delete_by_id("addresses", address_id)
        
        if success:
            address_logger.info(f"Deleted address: {address.full_address}")
        else:
            address_logger.error(f"Failed to delete address {address_id}")
        
        return success

    @staticmethod
    async def search_addresses_by_street_name(street_name: str, limit: int = 20) -> List[Address]:
        """Search addresses by street name with standardization (optimized with street_name index)"""
        address_logger.debug(f"Searching addresses on street: {street_name}")
        
        # Standardize the search term before querying
        standardized_street_name = standardize_street_type(street_name.strip())
        
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE LOWER(street_name) LIKE LOWER(:street_name)
            ORDER BY city, street_number
            LIMIT :limit
        """
        rows = await db.database.fetch_all(
            query=query, 
            values={"street_name": f"%{standardized_street_name}%", "limit": limit}
        )
        address_logger.debug(f"Found {len(rows)} addresses on {standardized_street_name}")
        return [Address.model_validate(dict(row)) for row in rows]
    
    @staticmethod
    async def search_addresses_by_street_number(street_number: str, limit: int = 20) -> List[Address]:
        """Search addresses by street number (optimized with street_number index)"""
        address_logger.debug(f"Searching addresses with number: {street_number}")
        
        query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses 
            WHERE street_number = :street_number
            ORDER BY city, street_name
            LIMIT :limit
        """
        rows = await db.database.fetch_all(
            query=query, 
            values={"street_number": street_number, "limit": limit}
        )
        address_logger.debug(f"Found {len(rows)} addresses with number {street_number}")
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def fuzzy_search_addresses(search_query: str, limit: int = 10, min_similarity: float = 0.3) -> List[str]:
        """
        Fuzzy search addresses using the new fuzzy search engine.
        
        Args:
            search_query: Search term (can contain typos or similar sounds)
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
        
        Returns:
            List of matching full addresses
        """
        address_logger.debug(f"Fuzzy searching addresses with query: {search_query}")
        
        # Use the new fuzzy search engine
        config = FuzzySearchConfig(min_similarity=min_similarity, limit=limit)
        fuzzy_searcher = AddressFuzzySearch(config)
        
        results = await fuzzy_searcher.search_addresses(search_query, limit)
        address_logger.debug(f"Found {len(results)} fuzzy matches for '{search_query}'")
        
        return results

    @staticmethod
    async def autocomplete_addresses(search_query: str, limit: int = 10, use_fuzzy: bool = True, state_code: Optional[str] = None, city: Optional[str] = None) -> List[str]:
        """
        Enhanced address autocomplete with optional fuzzy search and location filtering.
        
        Args:
            search_query: Partial address to search for
            limit: Maximum number of suggestions
            use_fuzzy: Whether to include fuzzy matching for typos
            state_code: Optional state code filter (e.g., 'CA', 'NY')
            city: Optional city filter
            
        Returns:
            List of matching address suggestions filtered by location if provided
        """
        address_logger.debug(f"Autocompleting addresses for: {search_query}, fuzzy: {use_fuzzy}")
        
        if not search_query or len(search_query.strip()) < 2:
            return []
        
        if use_fuzzy:
            # Use the new fuzzy search engine
            config = FuzzySearchConfig(limit=limit)
            fuzzy_searcher = AddressFuzzySearch(config)
            return await fuzzy_searcher.autocomplete(search_query, limit, state_code=state_code, city=city)
        else:
            # Use traditional exact/prefix matching (faster)
            search_query = search_query.strip()
            standardized_query = standardize_street_type(search_query)
            
            # Build WHERE clauses for location filtering
            where_conditions = [
                "(street_address ILIKE :prefix_term OR street_address ILIKE :std_prefix_term OR LOWER(full_address) LIKE LOWER(:contains_term) OR LOWER(full_address) LIKE LOWER(:std_contains_term))"
            ]
            values = {
                "prefix_term": f"{search_query}%",
                "std_prefix_term": f"{standardized_query}%", 
                "contains_term": f"%{search_query}%",
                "std_contains_term": f"%{standardized_query}%",
                "limit": limit
            }
            
            if state_code:
                where_conditions.append("state_code = :state_code")
                values["state_code"] = state_code.upper()
                
            if city:
                where_conditions.append("LOWER(city) = LOWER(:city)")
                values["city"] = city
            
            query = f"""
                SELECT DISTINCT full_address,
                    CASE 
                        WHEN street_address ILIKE :prefix_term THEN 1 
                        WHEN street_address ILIKE :std_prefix_term THEN 2
                        ELSE 3 
                    END as priority
                FROM addresses 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY priority, full_address
                LIMIT :limit
            """
            
            rows = await db.database.fetch_all(
                query=query,
                values=values
            )
            
            address_logger.debug(f"Found {len(rows)} exact matches for '{search_query}'")
            return [row["full_address"] for row in rows]

    @staticmethod
    async def fuzzy_search_street_names(search_query: str, limit: int = 20, min_similarity: float = 0.4) -> List[dict]:
        """
        Fuzzy search for street names with similarity scores using the new fuzzy search engine.
        
        Args:
            search_query: Street name to search for (can have typos)
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of dicts with street_name, similarity_score, and address_count
        """
        address_logger.debug(f"Fuzzy searching street names for: {search_query}")
        
        # Use the new fuzzy search engine
        config = FuzzySearchConfig(min_similarity=min_similarity, limit=limit)
        fuzzy_searcher = AddressFuzzySearch(config)
        
        results = await fuzzy_searcher.search_street_names(search_query, limit)
        address_logger.debug(f"Found {len(results)} fuzzy street name matches")
        
        return results

    @staticmethod
    async def get_address_statistics() -> dict:
        """Get statistics about addresses"""
        address_logger.debug("Fetching address statistics")
        
        # Get total count
        total_count = await DatabaseOperations.count("addresses")
        
        # Get count by state
        state_stats = await db.database.fetch_all("""
            SELECT state_code, COUNT(*) as address_count
            FROM addresses
            GROUP BY state_code
            ORDER BY address_count DESC
            LIMIT 10
        """)
        
        # Get count by city (top 10)
        city_stats = await db.database.fetch_all("""
            SELECT city, state_code, COUNT(*) as address_count
            FROM addresses
            GROUP BY city, state_code
            ORDER BY address_count DESC
            LIMIT 10
        """)
        
        # Get most common street names
        street_stats = await db.database.fetch_all("""
            SELECT street_name, COUNT(*) as address_count
            FROM addresses
            WHERE street_name IS NOT NULL
            GROUP BY street_name
            ORDER BY address_count DESC
            LIMIT 10
        """)
        
        statistics = {
            "total_addresses": total_count,
            "by_state": [
                {"state_code": row["state_code"], "address_count": row["address_count"]}
                for row in state_stats
            ],
            "top_cities": [
                {
                    "city": row["city"],
                    "state_code": row["state_code"],
                    "address_count": row["address_count"]
                }
                for row in city_stats
            ],
            "top_street_names": [
                {"street_name": row["street_name"], "address_count": row["address_count"]}
                for row in street_stats
            ]
        }
        
        address_logger.debug(f"Retrieved address statistics: {total_count} total addresses")
        return statistics

    @staticmethod
    async def advanced_address_search(
        street_name: Optional[str] = None,
        city: Optional[str] = None,
        state_code: Optional[str] = None,
        street_number: Optional[str] = None,
        use_fuzzy: bool = False,
        limit: int = 20
    ) -> List[Address]:
        """
        Advanced search for addresses with multiple filters and optional fuzzy matching.
        
        Args:
            street_name: Street name to search for
            city: City to search in
            state_code: State code to search in  
            street_number: Street number to search for
            use_fuzzy: Whether to use fuzzy matching
            limit: Maximum results
            
        Returns:
            List of matching addresses
        """
        address_logger.debug(f"Advanced address search: street='{street_name}', city='{city}', state='{state_code}', number='{street_number}', fuzzy={use_fuzzy}")
        
        # Build dynamic query conditions
        where_conditions = []
        parameters = {}
        
        if street_name:
            if use_fuzzy:
                where_conditions.append("(street_name % :street_name OR similarity(street_name, :street_name) >= 0.3)")
            else:
                street_name = standardize_street_type(street_name.strip())
                where_conditions.append("LOWER(street_name) LIKE LOWER(:street_name)")
                parameters["street_name"] = f"%{street_name}%"
        
        if city:
            where_conditions.append("LOWER(city) = LOWER(:city)")
            parameters["city"] = city
        
        if state_code:
            where_conditions.append("state_code = :state_code")
            parameters["state_code"] = state_code.upper()
        
        if street_number:
            where_conditions.append("street_number = :street_number")
            parameters["street_number"] = street_number
        
        parameters["limit"] = limit
        
        # Build the complete query
        base_query = """
            SELECT id, street_number, street_name, unit, street_address, 
                   city, state_code, full_address
            FROM addresses
        """
        
        if where_conditions:
            base_query += f" WHERE {' AND '.join(where_conditions)}"
        
        base_query += " ORDER BY city, street_name, street_number LIMIT :limit"
        
        rows = await db.database.fetch_all(query=base_query, values=parameters)
        
        results = [Address.model_validate(dict(row)) for row in rows]
        address_logger.debug(f"Advanced search found {len(results)} addresses")
        return results

    @staticmethod
    async def search_addresses(query: str, limit: int = 10, state_code: Optional[str] = None, city: Optional[str] = None) -> List[str]:
        """
        Search addresses for autocomplete functionality.
        
        Args:
            query: Address search query
            limit: Maximum number of results
            state_code: Optional state code filter (e.g., 'CA', 'NY')
            city: Optional city filter
            
        Returns:
            List of matching full addresses filtered by state/city if provided
        """
        return await AddressService.autocomplete_addresses(query, limit, use_fuzzy=False, state_code=state_code, city=city)

    @staticmethod
    async def get_all_addresses(limit: int = 1000) -> List[Address]:
        """Get all addresses with optional limit"""
        address_logger.debug(f"Fetching all addresses (limit: {limit})")
        
        results = await DatabaseOperations.get_all(
            table="addresses",
            fields=["id", "street_number", "street_name", "unit", "street_address", "city", "state_code", "full_address"],
            order_by=["state_code", "city", "street_name", "street_number"],
            limit=limit
        )
        
        addresses = [Address.model_validate(result) for result in results]
        address_logger.debug(f"Retrieved {len(addresses)} addresses")
        return addresses