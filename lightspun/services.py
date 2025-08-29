from typing import List, Optional
from .database import database
from .schemas import (
    State, StateCreate, StateUpdate,
    Municipality, MunicipalityCreate, MunicipalityUpdate,
    Address, AddressCreate, AddressUpdate
)

class StateService:
    """Service class for state operations"""

    @staticmethod
    async def get_all_states() -> List[State]:
        """Get all states"""
        query = "SELECT id, code, name FROM states ORDER BY name"
        rows = await database.fetch_all(query=query)
        return [State.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_state_by_code(state_code: str) -> Optional[State]:
        """Get state by code"""
        query = "SELECT id, code, name FROM states WHERE code = :code"
        row = await database.fetch_one(query=query, values={"code": state_code.upper()})
        return State.model_validate(dict(row)) if row else None

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
        """Get municipalities by state code"""
        query = """
            SELECT m.id, m.name, m.type, m.state_id 
            FROM municipalities m
            JOIN states s ON m.state_id = s.id
            WHERE s.code = :state_code
            ORDER BY m.name
        """
        rows = await database.fetch_all(query=query, values={"state_code": state_code.upper()})
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
        """Search addresses by query string"""
        query = """
            SELECT full_address 
            FROM addresses 
            WHERE LOWER(full_address) LIKE LOWER(:search_term)
            ORDER BY full_address
            LIMIT :limit
        """
        search_term = f"%{search_query}%"
        rows = await database.fetch_all(
            query=query, 
            values={"search_term": search_term, "limit": limit}
        )
        return [row["full_address"] for row in rows]

    @staticmethod
    async def get_all_addresses() -> List[Address]:
        """Get all addresses"""
        query = "SELECT id, street_address, city, state_code, full_address FROM addresses ORDER BY full_address"
        rows = await database.fetch_all(query=query)
        return [Address.model_validate(dict(row)) for row in rows]

    @staticmethod
    async def get_address_by_id(address_id: int) -> Optional[Address]:
        """Get address by ID"""
        query = "SELECT id, street_address, city, state_code, full_address FROM addresses WHERE id = :id"
        row = await database.fetch_one(query=query, values={"id": address_id})
        return Address.model_validate(dict(row)) if row else None

    @staticmethod
    async def create_address(address_data: AddressCreate) -> Address:
        """Create a new address"""
        full_address = f"{address_data.street_address}, {address_data.city}, {address_data.state_code}"
        query = """
            INSERT INTO addresses (street_address, city, state_code, full_address) 
            VALUES (:street_address, :city, :state_code, :full_address) 
            RETURNING id, street_address, city, state_code, full_address
        """
        values = {
            **address_data.model_dump(),
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
        
        # If any address component is updated, regenerate full address
        current_address = await AddressService.get_address_by_id(address_id)
        if not current_address:
            return None
        
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
            RETURNING id, street_address, city, state_code, full_address
        """
        values = {**update_data, "id": address_id}
        row = await database.fetch_one(query=query, values=values)
        return Address.model_validate(dict(row)) if row else None

    @staticmethod
    async def delete_address(address_id: int) -> bool:
        """Delete an address"""
        query = "DELETE FROM addresses WHERE id = :id"
        result = await database.execute(query=query, values={"id": address_id})
        return result > 0