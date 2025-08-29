"""
Unit tests for MunicipalityService.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from lightspun.services.municipality_service import MunicipalityService
from lightspun.schemas import Municipality, MunicipalityCreate, MunicipalityUpdate


@pytest.mark.unit
@pytest.mark.municipality
class TestMunicipalityService:
    """Test suite for MunicipalityService."""

    @pytest.mark.asyncio
    async def test_get_municipalities_by_state_code_success(self, mock_municipality_data):
        """Test successful retrieval of municipalities by state code."""
        mock_rows = [MagicMock(**municipality) for municipality in mock_municipality_data]
        
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await MunicipalityService.get_municipalities_by_state_code("CA")
            
            assert len(result) == 3
            assert all(isinstance(municipality, Municipality) for municipality in result)
            assert result[0].name == "Los Angeles"
            
            # Verify database call with uppercase state code
            call_args = mock_db.fetch_all.call_args
            assert call_args[1]['values']['state_code'] == "CA"

    @pytest.mark.asyncio
    async def test_get_municipalities_by_state_code_empty(self):
        """Test retrieval when no municipalities exist for state."""
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = []
            
            result = await MunicipalityService.get_municipalities_by_state_code("XX")
            
            assert result == []

    @pytest.mark.asyncio
    async def test_get_municipalities_by_state_id_success(self, mock_municipality_data):
        """Test successful retrieval of municipalities by state ID."""
        mock_rows = [MagicMock(**municipality) for municipality in mock_municipality_data]
        
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await MunicipalityService.get_municipalities_by_state_id(1)
            
            assert len(result) == 3
            assert all(isinstance(municipality, Municipality) for municipality in result)
            
            # Verify database call
            call_args = mock_db.fetch_all.call_args
            assert call_args[1]['values']['state_id'] == 1

    @pytest.mark.asyncio
    async def test_search_municipalities_by_name(self, mock_municipality_data):
        """Test searching municipalities by name."""
        filtered_data = [mock_municipality_data[0]]  # Only Los Angeles
        mock_rows = [MagicMock(**municipality) for municipality in filtered_data]
        
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await MunicipalityService.search_municipalities_by_name("angeles", limit=10)
            
            assert len(result) == 1
            assert result[0].name == "Los Angeles"
            
            # Verify query parameters
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert "angeles%" in values['prefix_term']
            assert "%angeles%" in values['contains_term']
            assert values['limit'] == 10

    @pytest.mark.asyncio
    async def test_search_municipalities_by_name_default_limit(self):
        """Test searching municipalities by name with default limit."""
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = []
            
            await MunicipalityService.search_municipalities_by_name("test")
            
            call_args = mock_db.fetch_all.call_args
            assert call_args[1]['values']['limit'] == 20  # Default limit

    @pytest.mark.asyncio
    async def test_get_municipality_by_id_success(self, mock_municipality_data):
        """Test successful retrieval of municipality by ID."""
        mock_result = mock_municipality_data[0]
        
        with patch('lightspun.services.municipality_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.get_by_id.return_value = mock_result
            
            result = await MunicipalityService.get_municipality_by_id(1)
            
            assert isinstance(result, Municipality)
            assert result.name == "Los Angeles"
            
            # Verify DatabaseOperations call
            mock_db_ops.get_by_id.assert_called_once_with(
                table="municipalities",
                id_value=1,
                fields=["id", "name", "type", "state_id"]
            )

    @pytest.mark.asyncio
    async def test_get_municipality_by_id_not_found(self):
        """Test retrieval of non-existent municipality by ID."""
        with patch('lightspun.services.municipality_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.get_by_id.return_value = None
            
            result = await MunicipalityService.get_municipality_by_id(999)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_create_municipality_success(self, mock_state_data):
        """Test successful municipality creation."""
        municipality_data = MunicipalityCreate(name="Oakland", type="city", state_id=1)
        mock_result = {"id": 4, "name": "Oakland", "type": "city", "state_id": 1}
        mock_state = mock_state_data[0]
        
        with patch('lightspun.services.municipality_service.StateService') as mock_state_service, \
             patch('lightspun.services.municipality_service.DatabaseOperations') as mock_db_ops:
            
            mock_state_service.get_state_by_id.return_value = MagicMock(**mock_state)
            mock_db_ops.create.return_value = mock_result
            
            result = await MunicipalityService.create_municipality(municipality_data)
            
            assert isinstance(result, Municipality)
            assert result.name == "Oakland"
            
            # Verify state validation
            mock_state_service.get_state_by_id.assert_called_once_with(1)
            
            # Verify creation
            mock_db_ops.create.assert_called_once_with(
                table="municipalities",
                data=municipality_data.model_dump(),
                returning=["id", "name", "type", "state_id"]
            )

    @pytest.mark.asyncio
    async def test_create_municipality_invalid_state(self):
        """Test municipality creation with invalid state."""
        municipality_data = MunicipalityCreate(name="Oakland", type="city", state_id=999)
        
        with patch('lightspun.services.municipality_service.StateService') as mock_state_service:
            mock_state_service.get_state_by_id.return_value = None
            
            with pytest.raises(ValueError, match="State with ID 999 does not exist"):
                await MunicipalityService.create_municipality(municipality_data)

    @pytest.mark.asyncio
    async def test_create_municipality_failure(self, mock_state_data):
        """Test municipality creation failure."""
        municipality_data = MunicipalityCreate(name="Oakland", type="city", state_id=1)
        mock_state = mock_state_data[0]
        
        with patch('lightspun.services.municipality_service.StateService') as mock_state_service, \
             patch('lightspun.services.municipality_service.DatabaseOperations') as mock_db_ops:
            
            mock_state_service.get_state_by_id.return_value = MagicMock(**mock_state)
            mock_db_ops.create.return_value = None
            
            with pytest.raises(RuntimeError, match="Failed to create municipality"):
                await MunicipalityService.create_municipality(municipality_data)

    @pytest.mark.asyncio
    async def test_update_municipality_success(self, mock_municipality_data):
        """Test successful municipality update."""
        municipality_data = MunicipalityUpdate(name="New Los Angeles")
        mock_result = {"id": 1, "name": "New Los Angeles", "type": "city", "state_id": 1}
        
        with patch('lightspun.services.municipality_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.update_by_id.return_value = mock_result
            
            result = await MunicipalityService.update_municipality(1, municipality_data)
            
            assert isinstance(result, Municipality)
            assert result.name == "New Los Angeles"

    @pytest.mark.asyncio
    async def test_update_municipality_no_changes(self):
        """Test municipality update with no changes."""
        municipality_data = MunicipalityUpdate()  # No fields set
        mock_current_municipality = Municipality(id=1, name="Los Angeles", type="city", state_id=1)
        
        with patch.object(MunicipalityService, 'get_municipality_by_id', return_value=mock_current_municipality):
            result = await MunicipalityService.update_municipality(1, municipality_data)
            
            assert result == mock_current_municipality

    @pytest.mark.asyncio
    async def test_update_municipality_not_found(self):
        """Test updating non-existent municipality."""
        municipality_data = MunicipalityUpdate(name="New Name")
        
        with patch('lightspun.services.municipality_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.update_by_id.return_value = None
            
            result = await MunicipalityService.update_municipality(999, municipality_data)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_municipality_success(self):
        """Test successful municipality deletion."""
        mock_municipality = Municipality(id=1, name="Los Angeles", type="city", state_id=1)
        
        with patch.object(MunicipalityService, 'get_municipality_by_id', return_value=mock_municipality), \
             patch('lightspun.services.municipality_service.DatabaseOperations') as mock_db_ops:
            
            mock_db_ops.delete_by_id.return_value = True
            
            result = await MunicipalityService.delete_municipality(1)
            
            assert result is True
            mock_db_ops.delete_by_id.assert_called_once_with("municipalities", 1)

    @pytest.mark.asyncio
    async def test_delete_municipality_not_found(self):
        """Test deletion of non-existent municipality."""
        with patch.object(MunicipalityService, 'get_municipality_by_id', return_value=None):
            result = await MunicipalityService.delete_municipality(999)
            assert result is False

    @pytest.mark.asyncio
    async def test_get_municipalities_by_type(self, mock_municipality_data):
        """Test retrieval of municipalities by type."""
        # Filter for cities only
        city_data = [m for m in mock_municipality_data if m['type'] == 'city']
        mock_rows = [MagicMock(**municipality) for municipality in city_data]
        
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await MunicipalityService.get_municipalities_by_type("city", limit=50)
            
            assert len(result) == 3
            assert all(municipality.type == "city" for municipality in result)
            
            # Verify query parameters
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert values['municipality_type'] == "city"
            assert values['limit'] == 50

    @pytest.mark.asyncio
    async def test_get_municipalities_by_type_default_limit(self):
        """Test retrieval of municipalities by type with default limit."""
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = []
            
            await MunicipalityService.get_municipalities_by_type("city")
            
            call_args = mock_db.fetch_all.call_args
            assert call_args[1]['values']['limit'] == 50  # Default limit

    @pytest.mark.asyncio
    async def test_get_municipality_statistics(self):
        """Test retrieval of municipality statistics."""
        mock_total_count = 100
        mock_type_stats = [
            {"type": "city", "count": 80},
            {"type": "town", "count": 20}
        ]
        mock_state_stats = [
            {"state_name": "California", "state_code": "CA", "municipality_count": 50},
            {"state_name": "Texas", "state_code": "TX", "municipality_count": 30}
        ]
        
        with patch('lightspun.services.municipality_service.DatabaseOperations') as mock_db_ops, \
             patch('lightspun.services.municipality_service.database') as mock_db:
            
            mock_db_ops.count.return_value = mock_total_count
            mock_db.fetch_all.side_effect = [
                [MagicMock(**stat) for stat in mock_type_stats],
                [MagicMock(**stat) for stat in mock_state_stats]
            ]
            
            result = await MunicipalityService.get_municipality_statistics()
            
            assert result['total_municipalities'] == 100
            assert len(result['by_type']) == 2
            assert result['by_type'][0]['type'] == 'city'
            assert result['by_type'][0]['count'] == 80
            assert len(result['top_states']) == 2
            assert result['top_states'][0]['state_name'] == 'California'

    @pytest.mark.asyncio
    async def test_search_municipalities_advanced_all_filters(self):
        """Test advanced municipality search with all filters."""
        mock_rows = [MagicMock(id=1, name="Los Angeles", type="city", state_id=1)]
        
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await MunicipalityService.search_municipalities_advanced(
                name_query="angeles",
                municipality_type="city", 
                state_code="CA",
                limit=10
            )
            
            assert len(result) == 1
            assert result[0].name == "Los Angeles"
            
            # Verify query parameters
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert "angeles" in values['name_pattern']
            assert values['municipality_type'] == "city"
            assert values['state_code'] == "CA"
            assert values['limit'] == 10

    @pytest.mark.asyncio
    async def test_search_municipalities_advanced_partial_filters(self):
        """Test advanced municipality search with partial filters."""
        mock_rows = []
        
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await MunicipalityService.search_municipalities_advanced(
                name_query="angeles",
                municipality_type=None,
                state_code=None,
                limit=20
            )
            
            assert result == []
            
            # Verify only name filter was applied
            call_args = mock_db.fetch_all.call_args
            query = call_args[1]['query']
            values = call_args[1]['values']
            
            assert "name_pattern" in values
            assert "municipality_type" not in values
            assert "state_code" not in values

    @pytest.mark.asyncio
    async def test_search_municipalities_advanced_no_filters(self):
        """Test advanced municipality search with no filters."""
        mock_rows = [MagicMock(id=i, name=f"City {i}", type="city", state_id=1) for i in range(5)]
        
        with patch('lightspun.services.municipality_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await MunicipalityService.search_municipalities_advanced(
                name_query=None,
                municipality_type=None,
                state_code=None,
                limit=20
            )
            
            assert len(result) == 5
            
            # Verify no WHERE conditions were added
            call_args = mock_db.fetch_all.call_args
            query = call_args[1]['query']
            assert "WHERE" not in query