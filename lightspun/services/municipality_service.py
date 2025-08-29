"""
Municipality Service Module

This module handles all municipality-related business logic and db.database operations.
Provides CRUD operations and specialized queries for municipalities.
"""

from typing import List, Optional

from .. import database as db
from ..schemas import Municipality, MunicipalityCreate, MunicipalityUpdate
from ..logging_config import get_logger
from ..utils.database_operations import DatabaseOperations

# Initialize logger
municipality_logger = get_logger('lightspun.services.municipality')


class MunicipalityService:
    """Service class for municipality operations"""

    @staticmethod
    async def get_municipalities_by_state_code(state_code: str) -> List[Municipality]:
        """Get municipalities by state code (optimized with state_id index)"""
        municipality_logger.debug(f"Fetching municipalities for state: {state_code}")
        
        # Optimized query that uses the ix_municipalities_state_id index
        # Use ROW_NUMBER to get unique municipalities by name per state
        query = """
            SELECT m.id, m.name, m.type, m.state_id 
            FROM (
                SELECT id, name, type, state_id,
                       ROW_NUMBER() OVER (PARTITION BY name, state_id ORDER BY id) as rn
                FROM municipalities
                WHERE state_id = (SELECT id FROM states WHERE code = :state_code)
            ) m
            WHERE m.rn = 1
            ORDER BY m.name
        """
        
        rows = await db.database.fetch_all(query=query, values={"state_code": state_code.upper()})
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
        
        rows = await db.database.fetch_all(query=query, values={"state_id": state_id})
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
        
        rows = await db.database.fetch_all(
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
    async def get_municipality_by_id(municipality_id: int) -> Optional[Municipality]:
        """Get municipality by ID"""
        municipality_logger.debug(f"Fetching municipality by ID: {municipality_id}")
        
        result = await DatabaseOperations.get_by_id(
            table="municipalities",
            id_value=municipality_id,
            fields=["id", "name", "type", "state_id"]
        )
        
        if result:
            municipality_logger.debug(f"Found municipality: {result['name']}")
            return Municipality.model_validate(result)
        else:
            municipality_logger.warning(f"Municipality not found for ID: {municipality_id}")
            return None

    @staticmethod
    async def create_municipality(municipality_data: MunicipalityCreate) -> Municipality:
        """Create a new municipality"""
        municipality_logger.info(f"Creating new municipality: {municipality_data.name}")
        
        # Validate state exists
        from .state_service import StateService
        state = await StateService.get_state_by_id(municipality_data.state_id)
        if not state:
            raise ValueError(f"State with ID {municipality_data.state_id} does not exist")
        
        result = await DatabaseOperations.create(
            table="municipalities",
            data=municipality_data.model_dump(),
            returning=["id", "name", "type", "state_id"]
        )
        
        if result:
            municipality_logger.info(f"Created municipality: {result['name']} in {state.name}")
            return Municipality.model_validate(result)
        else:
            raise RuntimeError("Failed to create municipality")

    @staticmethod
    async def update_municipality(municipality_id: int, municipality_data: MunicipalityUpdate) -> Optional[Municipality]:
        """Update a municipality"""
        update_data = municipality_data.model_dump(exclude_unset=True)
        if not update_data:
            municipality_logger.debug(f"No updates provided for municipality {municipality_id}")
            return await MunicipalityService.get_municipality_by_id(municipality_id)
        
        municipality_logger.info(f"Updating municipality {municipality_id} with data: {update_data}")
        
        result = await DatabaseOperations.update_by_id(
            table="municipalities",
            id_value=municipality_id,
            data=update_data,
            returning=["id", "name", "type", "state_id"]
        )
        
        if result:
            municipality_logger.info(f"Updated municipality: {result['name']}")
            return Municipality.model_validate(result)
        else:
            municipality_logger.warning(f"Municipality {municipality_id} not found for update")
            return None

    @staticmethod
    async def delete_municipality(municipality_id: int) -> bool:
        """Delete a municipality"""
        municipality_logger.warning(f"Attempting to delete municipality {municipality_id}")
        
        # Check if municipality exists
        municipality = await MunicipalityService.get_municipality_by_id(municipality_id)
        if not municipality:
            municipality_logger.warning(f"Municipality {municipality_id} not found for deletion")
            return False
        
        success = await DatabaseOperations.delete_by_id("municipalities", municipality_id)
        
        if success:
            municipality_logger.info(f"Deleted municipality: {municipality.name}")
        else:
            municipality_logger.error(f"Failed to delete municipality {municipality_id}")
        
        return success

    @staticmethod
    async def get_municipalities_by_type(municipality_type: str, limit: int = 50) -> List[Municipality]:
        """Get municipalities by type"""
        municipality_logger.debug(f"Fetching municipalities of type: {municipality_type}")
        
        query = """
            SELECT id, name, type, state_id
            FROM municipalities 
            WHERE type = :municipality_type
            ORDER BY name
            LIMIT :limit
        """
        
        rows = await db.database.fetch_all(
            query=query, 
            values={"municipality_type": municipality_type, "limit": limit}
        )
        
        municipality_logger.debug(f"Found {len(rows)} municipalities of type {municipality_type}")
        return [Municipality.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_municipality_statistics() -> dict:
        """Get statistics about municipalities"""
        municipality_logger.debug("Fetching municipality statistics")
        
        # Get total count
        total_count = await DatabaseOperations.count("municipalities")
        
        # Get count by type
        type_stats = await db.database.fetch_all("""
            SELECT type, COUNT(*) as count
            FROM municipalities
            GROUP BY type
            ORDER BY count DESC
        """)
        
        # Get count by state
        state_stats = await db.database.fetch_all("""
            SELECT s.name as state_name, s.code as state_code, COUNT(m.id) as municipality_count
            FROM states s
            LEFT JOIN municipalities m ON s.id = m.state_id
            GROUP BY s.id, s.name, s.code
            HAVING COUNT(m.id) > 0
            ORDER BY municipality_count DESC
            LIMIT 10
        """)
        
        statistics = {
            "total_municipalities": total_count,
            "by_type": [{"type": row["type"], "count": row["count"]} for row in type_stats],
            "top_states": [
                {
                    "state_name": row["state_name"],
                    "state_code": row["state_code"], 
                    "municipality_count": row["municipality_count"]
                }
                for row in state_stats
            ]
        }
        
        municipality_logger.debug(f"Retrieved municipality statistics: {total_count} total municipalities")
        return statistics

    @staticmethod
    async def search_municipalities_advanced(
        name_query: Optional[str] = None,
        municipality_type: Optional[str] = None,
        state_code: Optional[str] = None,
        limit: int = 20
    ) -> List[Municipality]:
        """Advanced search for municipalities with multiple filters"""
        municipality_logger.debug(f"Advanced municipality search: name='{name_query}', type='{municipality_type}', state='{state_code}'")
        
        # Build dynamic query
        where_conditions = []
        parameters = {}
        
        if name_query:
            where_conditions.append("(m.name ILIKE :name_pattern)")
            parameters["name_pattern"] = f"%{name_query}%"
        
        if municipality_type:
            where_conditions.append("m.type = :municipality_type")
            parameters["municipality_type"] = municipality_type
        
        if state_code:
            where_conditions.append("s.code = :state_code")
            parameters["state_code"] = state_code.upper()
        
        parameters["limit"] = limit
        
        # Build the complete query
        base_query = """
            SELECT m.id, m.name, m.type, m.state_id
            FROM municipalities m
            JOIN states s ON m.state_id = s.id
        """
        
        if where_conditions:
            base_query += f" WHERE {' AND '.join(where_conditions)}"
        
        base_query += " ORDER BY m.name LIMIT :limit"
        
        rows = await db.database.fetch_all(query=base_query, values=parameters)
        
        results = [Municipality.model_validate(dict(row)) for row in rows]
        municipality_logger.debug(f"Advanced search found {len(results)} municipalities")
        return results