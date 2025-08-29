"""
Unit tests for StateService.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from lightspun.services.state_service import StateService
from lightspun.schemas import State, StateCreate, StateUpdate


@pytest.mark.unit
@pytest.mark.state
class TestStateService:
    """Test suite for StateService."""

    @pytest.mark.asyncio
    async def test_get_all_states_success(self, mock_state_data):
        """Test successful retrieval of all states."""
        # Mock database response
        mock_rows = [MagicMock(**state) for state in mock_state_data]
        
        with patch('lightspun.services.state_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await StateService.get_all_states()
            
            # Assertions
            assert len(result) == 3
            assert all(isinstance(state, State) for state in result)
            assert result[0].code == "CA"
            assert result[0].name == "California"
            
            # Verify database call
            mock_db.fetch_all.assert_called_once()
            call_args = mock_db.fetch_all.call_args
            assert "SELECT id, code, name FROM states ORDER BY name" in call_args[1]['query']

    @pytest.mark.asyncio
    async def test_get_all_states_empty(self):
        """Test retrieval when no states exist."""
        with patch('lightspun.services.state_service.database') as mock_db:
            mock_db.fetch_all.return_value = []
            
            result = await StateService.get_all_states()
            
            assert result == []

    @pytest.mark.asyncio
    async def test_get_state_by_code_success(self, mock_state_data):
        """Test successful retrieval of state by code."""
        mock_row = MagicMock(**mock_state_data[0])
        
        with patch('lightspun.services.state_service.database') as mock_db:
            mock_db.fetch_one.return_value = mock_row
            
            result = await StateService.get_state_by_code("CA")
            
            assert isinstance(result, State)
            assert result.code == "CA"
            assert result.name == "California"
            
            # Verify database call with uppercase code
            mock_db.fetch_one.assert_called_once()
            call_args = mock_db.fetch_one.call_args
            assert call_args[1]['values']['code'] == "CA"

    @pytest.mark.asyncio
    async def test_get_state_by_code_not_found(self):
        """Test retrieval of non-existent state."""
        with patch('lightspun.services.state_service.database') as mock_db:
            mock_db.fetch_one.return_value = None
            
            result = await StateService.get_state_by_code("XX")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_state_by_code_lowercase(self, mock_state_data):
        """Test that lowercase state codes are converted to uppercase."""
        mock_row = MagicMock(**mock_state_data[0])
        
        with patch('lightspun.services.state_service.database') as mock_db:
            mock_db.fetch_one.return_value = mock_row
            
            result = await StateService.get_state_by_code("ca")
            
            # Verify the code was converted to uppercase in the query
            call_args = mock_db.fetch_one.call_args
            assert call_args[1]['values']['code'] == "CA"

    @pytest.mark.asyncio
    async def test_get_state_by_id_success(self, mock_state_data):
        """Test successful retrieval of state by ID."""
        mock_result = mock_state_data[0]
        
        with patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.get_by_id.return_value = mock_result
            
            result = await StateService.get_state_by_id(1)
            
            assert isinstance(result, State)
            assert result.id == 1
            assert result.code == "CA"
            
            # Verify DatabaseOperations call
            mock_db_ops.get_by_id.assert_called_once_with(
                table="states",
                id_value=1,
                fields=["id", "code", "name"]
            )

    @pytest.mark.asyncio
    async def test_get_state_by_id_not_found(self):
        """Test retrieval of non-existent state by ID."""
        with patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.get_by_id.return_value = None
            
            result = await StateService.get_state_by_id(999)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_create_state_success(self, mock_state_data):
        """Test successful state creation."""
        state_data = StateCreate(code="WA", name="Washington")
        mock_result = {"id": 4, "code": "WA", "name": "Washington"}
        
        with patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.create.return_value = mock_result
            
            result = await StateService.create_state(state_data)
            
            assert isinstance(result, State)
            assert result.code == "WA"
            assert result.name == "Washington"
            
            # Verify DatabaseOperations call
            mock_db_ops.create.assert_called_once_with(
                table="states",
                data=state_data.model_dump(),
                returning=["id", "code", "name"]
            )

    @pytest.mark.asyncio
    async def test_create_state_failure(self):
        """Test state creation failure."""
        state_data = StateCreate(code="WA", name="Washington")
        
        with patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.create.return_value = None
            
            with pytest.raises(RuntimeError, match="Failed to create state"):
                await StateService.create_state(state_data)

    @pytest.mark.asyncio
    async def test_update_state_success(self, mock_state_data):
        """Test successful state update."""
        state_data = StateUpdate(name="New California")
        mock_result = {"id": 1, "code": "CA", "name": "New California"}
        
        with patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.update_by_id.return_value = mock_result
            
            result = await StateService.update_state(1, state_data)
            
            assert isinstance(result, State)
            assert result.name == "New California"
            
            # Verify DatabaseOperations call
            mock_db_ops.update_by_id.assert_called_once_with(
                table="states",
                id_value=1,
                data=state_data.model_dump(exclude_unset=True),
                returning=["id", "code", "name"]
            )

    @pytest.mark.asyncio
    async def test_update_state_no_changes(self):
        """Test state update with no changes."""
        state_data = StateUpdate()  # No fields set
        mock_current_state = State(id=1, code="CA", name="California")
        
        with patch.object(StateService, 'get_state_by_id', return_value=mock_current_state):
            result = await StateService.update_state(1, state_data)
            
            assert result == mock_current_state

    @pytest.mark.asyncio
    async def test_update_state_not_found(self):
        """Test updating non-existent state."""
        state_data = StateUpdate(name="New Name")
        
        with patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.update_by_id.return_value = None
            
            result = await StateService.update_state(999, state_data)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_state_success(self):
        """Test successful state deletion."""
        mock_state = State(id=1, code="CA", name="California")
        
        with patch.object(StateService, 'get_state_by_id', return_value=mock_state), \
             patch('lightspun.services.state_service.database') as mock_db, \
             patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            
            # Mock no dependent municipalities
            mock_db.fetch_val.return_value = 0
            mock_db_ops.delete_by_id.return_value = True
            
            result = await StateService.delete_state(1)
            
            assert result is True
            
            # Verify dependency check
            mock_db.fetch_val.assert_called_once()
            # Verify deletion
            mock_db_ops.delete_by_id.assert_called_once_with("states", 1)

    @pytest.mark.asyncio
    async def test_delete_state_with_municipalities(self):
        """Test deletion of state with dependent municipalities."""
        mock_state = State(id=1, code="CA", name="California")
        
        with patch.object(StateService, 'get_state_by_id', return_value=mock_state), \
             patch('lightspun.services.state_service.database') as mock_db:
            
            # Mock dependent municipalities exist
            mock_db.fetch_val.return_value = 5
            
            with pytest.raises(ValueError, match="Cannot delete state California: has 5 associated municipalities"):
                await StateService.delete_state(1)

    @pytest.mark.asyncio
    async def test_delete_state_not_found(self):
        """Test deletion of non-existent state."""
        with patch.object(StateService, 'get_state_by_id', return_value=None):
            result = await StateService.delete_state(999)
            assert result is False

    @pytest.mark.asyncio
    async def test_get_states_with_municipality_count(self):
        """Test retrieval of states with municipality counts."""
        mock_rows = [
            {"id": 1, "code": "CA", "name": "California", "municipality_count": 5},
            {"id": 2, "code": "NY", "name": "New York", "municipality_count": 3},
            {"id": 3, "code": "TX", "name": "Texas", "municipality_count": 0}
        ]
        
        with patch('lightspun.services.state_service.database') as mock_db:
            mock_db.fetch_all.return_value = [MagicMock(**row) for row in mock_rows]
            
            result = await StateService.get_states_with_municipality_count()
            
            assert len(result) == 3
            assert result[0]['municipality_count'] == 5
            assert isinstance(result[0]['municipality_count'], int)

    @pytest.mark.asyncio
    async def test_search_states_by_name(self):
        """Test searching states by name."""
        mock_rows = [
            MagicMock(id=1, code="CA", name="California"),
            MagicMock(id=2, code="SC", name="South Carolina")
        ]
        
        with patch('lightspun.services.state_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await StateService.search_states_by_name("carolina")
            
            assert len(result) == 2
            assert all(isinstance(state, State) for state in result)
            
            # Verify the query was called with proper patterns
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert "carolina" in values['name_pattern'].lower()

    @pytest.mark.asyncio
    async def test_validate_state_code_exists(self):
        """Test validation of existing state code."""
        with patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.exists.return_value = True
            
            result = await StateService.validate_state_code("CA")
            
            assert result is True
            
            # Verify the exists call with uppercase code
            mock_db_ops.exists.assert_called_once_with(
                table="states",
                where_conditions=["code = :code"],
                parameters={"code": "CA"}
            )

    @pytest.mark.asyncio
    async def test_validate_state_code_not_exists(self):
        """Test validation of non-existent state code."""
        with patch('lightspun.services.state_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.exists.return_value = False
            
            result = await StateService.validate_state_code("XX")
            
            assert result is False