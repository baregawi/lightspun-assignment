"""
State Service Module

This module handles all state-related business logic and database operations.
Provides CRUD operations and specialized queries for states.
"""

from typing import List, Optional

from ..database import database
from ..schemas import State, StateCreate, StateUpdate
from ..logging_config import get_logger
from ..utils.database_operations import DatabaseOperations

# Initialize logger
state_logger = get_logger('lightspun.services.state')


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
        state_logger.debug(f"Fetching state by ID: {state_id}")
        
        result = await DatabaseOperations.get_by_id(
            table="states",
            id_value=state_id,
            fields=["id", "code", "name"]
        )
        
        if result:
            state_logger.debug(f"Found state: {result['name']} ({result['code']})")
            return State.model_validate(result)
        else:
            state_logger.warning(f"State not found for ID: {state_id}")
            return None

    @staticmethod
    async def create_state(state_data: StateCreate) -> State:
        """Create a new state"""
        state_logger.info(f"Creating new state: {state_data.name} ({state_data.code})")
        
        result = await DatabaseOperations.create(
            table="states",
            data=state_data.model_dump(),
            returning=["id", "code", "name"]
        )
        
        if result:
            state_logger.info(f"Created state: {result['name']} ({result['code']}) with ID {result['id']}")
            return State.model_validate(result)
        else:
            raise RuntimeError("Failed to create state")

    @staticmethod
    async def update_state(state_id: int, state_data: StateUpdate) -> Optional[State]:
        """Update a state"""
        update_data = state_data.model_dump(exclude_unset=True)
        if not update_data:
            state_logger.debug(f"No updates provided for state {state_id}, returning current state")
            return await StateService.get_state_by_id(state_id)
        
        state_logger.info(f"Updating state {state_id} with data: {update_data}")
        
        result = await DatabaseOperations.update_by_id(
            table="states",
            id_value=state_id,
            data=update_data,
            returning=["id", "code", "name"]
        )
        
        if result:
            state_logger.info(f"Updated state: {result['name']} ({result['code']})")
            return State.model_validate(result)
        else:
            state_logger.warning(f"State {state_id} not found for update")
            return None

    @staticmethod
    async def delete_state(state_id: int) -> bool:
        """Delete a state"""
        state_logger.warning(f"Attempting to delete state {state_id}")
        
        # Check if state exists and has dependencies
        state = await StateService.get_state_by_id(state_id)
        if not state:
            state_logger.warning(f"State {state_id} not found for deletion")
            return False
        
        # Check for dependent municipalities
        municipality_count = await database.fetch_val(
            query="SELECT COUNT(*) FROM municipalities WHERE state_id = :state_id",
            values={"state_id": state_id}
        )
        
        if municipality_count > 0:
            state_logger.error(f"Cannot delete state {state_id}: has {municipality_count} municipalities")
            raise ValueError(f"Cannot delete state {state.name}: has {municipality_count} associated municipalities")
        
        success = await DatabaseOperations.delete_by_id("states", state_id)
        
        if success:
            state_logger.info(f"Deleted state: {state.name} ({state.code})")
        else:
            state_logger.error(f"Failed to delete state {state_id}")
        
        return success

    @staticmethod
    async def get_states_with_municipality_count() -> List[dict]:
        """Get all states with their municipality counts"""
        state_logger.debug("Fetching states with municipality counts")
        
        query = """
            SELECT s.id, s.code, s.name, COUNT(m.id) as municipality_count
            FROM states s
            LEFT JOIN municipalities m ON s.id = m.state_id
            GROUP BY s.id, s.code, s.name
            ORDER BY s.name
        """
        
        rows = await database.fetch_all(query=query)
        
        results = []
        for row in rows:
            state_dict = dict(row)
            state_dict['municipality_count'] = int(state_dict['municipality_count'])
            results.append(state_dict)
        
        state_logger.debug(f"Retrieved {len(results)} states with municipality counts")
        return results

    @staticmethod
    async def search_states_by_name(name_query: str) -> List[State]:
        """Search states by name (case-insensitive partial match)"""
        state_logger.debug(f"Searching states by name: {name_query}")
        
        query = """
            SELECT id, code, name 
            FROM states 
            WHERE LOWER(name) LIKE LOWER(:name_pattern)
               OR LOWER(code) LIKE LOWER(:code_pattern)
            ORDER BY 
                CASE WHEN LOWER(name) LIKE LOWER(:exact_name) THEN 1 ELSE 2 END,
                name
        """
        
        name_pattern = f"%{name_query}%"
        code_pattern = f"%{name_query}%"
        exact_name = name_query.lower()
        
        rows = await database.fetch_all(
            query=query,
            values={
                "name_pattern": name_pattern,
                "code_pattern": code_pattern,
                "exact_name": exact_name
            }
        )
        
        results = [State.model_validate(dict(row)) for row in rows]
        state_logger.debug(f"Found {len(results)} states matching '{name_query}'")
        return results

    @staticmethod
    async def validate_state_code(state_code: str) -> bool:
        """Validate if a state code exists"""
        state_logger.debug(f"Validating state code: {state_code}")
        
        exists = await DatabaseOperations.exists(
            table="states",
            where_conditions=["code = :code"],
            parameters={"code": state_code.upper()}
        )
        
        state_logger.debug(f"State code {state_code} {'exists' if exists else 'does not exist'}")
        return exists