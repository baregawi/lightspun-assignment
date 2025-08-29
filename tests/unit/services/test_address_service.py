"""
Unit tests for AddressService.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from lightspun.services.address_service import AddressService
from lightspun.schemas import Address, AddressCreate, AddressUpdate, AddressCreateMinimal
from lightspun.core.address_processing import AddressComponents


@pytest.mark.unit
@pytest.mark.address
class TestAddressService:
    """Test suite for AddressService."""

    @pytest.mark.asyncio
    async def test_get_address_by_id_success(self, mock_address_data):
        """Test successful retrieval of address by ID."""
        mock_result = mock_address_data[0]
        
        with patch('lightspun.services.address_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.get_by_id.return_value = mock_result
            
            result = await AddressService.get_address_by_id(1)
            
            assert isinstance(result, Address)
            assert result.street_address == "123 Main Street"
            assert result.city == "Los Angeles"
            
            # Verify DatabaseOperations call
            mock_db_ops.get_by_id.assert_called_once_with(
                table="addresses",
                id_value=1,
                fields=["id", "street_number", "street_name", "unit", "street_address", "city", "state_code", "full_address"]
            )

    @pytest.mark.asyncio
    async def test_get_address_by_id_not_found(self):
        """Test retrieval of non-existent address by ID."""
        with patch('lightspun.services.address_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.get_by_id.return_value = None
            
            result = await AddressService.get_address_by_id(999)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_search_addresses_by_city(self, mock_address_data):
        """Test searching addresses by city."""
        # Filter addresses for Los Angeles
        la_addresses = [addr for addr in mock_address_data if addr["city"] == "Los Angeles"]
        mock_rows = [MagicMock(**addr) for addr in la_addresses]
        
        with patch('lightspun.services.address_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await AddressService.search_addresses_by_city("Los Angeles", limit=10)
            
            assert len(result) == 1
            assert all(isinstance(addr, Address) for addr in result)
            assert all(addr.city == "Los Angeles" for addr in result)
            
            # Verify database call
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert values['city'] == "Los Angeles"
            assert values['limit'] == 10

    @pytest.mark.asyncio
    async def test_search_addresses_by_city_default_limit(self):
        """Test searching addresses by city with default limit."""
        with patch('lightspun.services.address_service.database') as mock_db:
            mock_db.fetch_all.return_value = []
            
            await AddressService.search_addresses_by_city("Test City")
            
            call_args = mock_db.fetch_all.call_args
            assert call_args[1]['values']['limit'] == 50  # Default limit

    @pytest.mark.asyncio
    async def test_search_addresses_by_state(self, mock_address_data):
        """Test searching addresses by state code."""
        mock_rows = [MagicMock(**addr) for addr in mock_address_data]
        
        with patch('lightspun.services.address_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await AddressService.search_addresses_by_state("ca", limit=25)
            
            assert len(result) == 2
            assert all(isinstance(addr, Address) for addr in result)
            
            # Verify state code was converted to uppercase
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert values['state_code'] == "CA"
            assert values['limit'] == 25

    @pytest.mark.asyncio
    async def test_create_address_success(self):
        """Test successful address creation."""
        address_data = AddressCreate(
            street_number="123",
            street_name="Main St",
            unit=None,
            street_address="123 Main St",
            city="Los Angeles",
            state_code="CA"
        )
        
        mock_result = {
            "id": 1,
            "street_number": "123",
            "street_name": "Main Street",
            "unit": None,
            "street_address": "123 Main Street",
            "city": "Los Angeles",
            "state_code": "CA",
            "full_address": "123 Main Street, Los Angeles, CA"
        }
        
        mock_components = AddressComponents(
            street_number="123",
            street_name="Main Street",
            unit=None
        )
        
        with patch('lightspun.services.address_service.AddressParser') as mock_parser, \
             patch('lightspun.services.address_service.AddressValidator') as mock_validator, \
             patch('lightspun.services.address_service.AddressFormatter') as mock_formatter, \
             patch('lightspun.services.address_service.DatabaseOperations') as mock_db_ops, \
             patch('lightspun.services.address_service.standardize_street_type', return_value="Main Street"):
            
            # Mock parser
            mock_parser_instance = mock_parser.return_value
            mock_parser_instance.parse_street_address.return_value = mock_components
            
            # Mock validator
            mock_validator_instance = mock_validator.return_value
            mock_validator_instance.validate_complete_address.return_value = MagicMock(is_valid=True)
            
            # Mock formatter
            mock_formatter_instance = mock_formatter.return_value
            mock_formatter_instance.format_full_address.return_value = "123 Main Street, Los Angeles, CA"
            
            # Mock database operation
            mock_db_ops.create.return_value = mock_result
            
            result = await AddressService.create_address(address_data)
            
            assert isinstance(result, Address)
            assert result.street_name == "Main Street"
            assert result.full_address == "123 Main Street, Los Angeles, CA"

    @pytest.mark.asyncio
    async def test_create_address_validation_failure(self):
        """Test address creation with validation failure."""
        address_data = AddressCreate(
            street_address="",
            city="",
            state_code=""
        )
        
        with patch('lightspun.services.address_service.AddressParser') as mock_parser, \
             patch('lightspun.services.address_service.AddressValidator') as mock_validator:
            
            # Mock parser
            mock_parser_instance = mock_parser.return_value
            mock_parser_instance.parse_street_address.return_value = AddressComponents()
            
            # Mock validator failure
            mock_validator_instance = mock_validator.return_value
            mock_validator_instance.validate_complete_address.return_value = MagicMock(
                is_valid=False,
                errors=["Street address is required", "City is required"]
            )
            
            with pytest.raises(ValueError, match="Invalid address: Street address is required; City is required"):
                await AddressService.create_address(address_data)

    @pytest.mark.asyncio
    async def test_create_address_minimal_success(self):
        """Test successful minimal address creation."""
        address_data = AddressCreateMinimal(
            street_address="123 Main St",
            city="Los Angeles",
            state_code="CA"
        )
        
        mock_result = {
            "id": 1,
            "street_number": "123",
            "street_name": "Main Street",
            "unit": None,
            "street_address": "123 Main St",
            "city": "Los Angeles", 
            "state_code": "CA",
            "full_address": "123 Main St, Los Angeles, CA"
        }
        
        mock_components = AddressComponents(
            street_number="123",
            street_name="Main Street",
            unit=None
        )
        
        with patch('lightspun.services.address_service.AddressParser') as mock_parser, \
             patch('lightspun.services.address_service.AddressFormatter') as mock_formatter, \
             patch('lightspun.services.address_service.DatabaseOperations') as mock_db_ops:
            
            # Mock parser
            mock_parser_instance = mock_parser.return_value
            mock_parser_instance.parse_street_address.return_value = mock_components
            
            # Mock formatter
            mock_formatter_instance = mock_formatter.return_value
            mock_formatter_instance.format_full_address.return_value = "123 Main St, Los Angeles, CA"
            
            # Mock database operation
            mock_db_ops.create.return_value = mock_result
            
            result = await AddressService.create_address_minimal(address_data)
            
            assert isinstance(result, Address)
            assert result.street_address == "123 Main St"

    @pytest.mark.asyncio
    async def test_update_address_success(self, mock_address_data):
        """Test successful address update."""
        address_data = AddressUpdate(street_name="New Street Name")
        mock_current_address = Address(**mock_address_data[0])
        
        mock_result = {
            **mock_address_data[0],
            "street_name": "New Street Name"
        }
        
        with patch.object(AddressService, 'get_address_by_id', return_value=mock_current_address), \
             patch('lightspun.services.address_service.AddressFormatter') as mock_formatter, \
             patch('lightspun.services.address_service.DatabaseOperations') as mock_db_ops, \
             patch('lightspun.services.address_service.standardize_street_type', return_value="New Street Name"):
            
            # Mock formatter
            mock_formatter_instance = mock_formatter.return_value
            mock_formatter_instance.format_full_address.return_value = "123 New Street Name, Los Angeles, CA"
            
            mock_db_ops.update_by_id.return_value = mock_result
            
            result = await AddressService.update_address(1, address_data)
            
            assert isinstance(result, Address)
            assert result.street_name == "New Street Name"

    @pytest.mark.asyncio
    async def test_update_address_no_changes(self):
        """Test address update with no changes."""
        address_data = AddressUpdate()  # No fields set
        mock_current_address = Address(
            id=1,
            street_address="123 Main Street",
            city="Los Angeles",
            state_code="CA",
            full_address="123 Main Street, Los Angeles, CA"
        )
        
        with patch.object(AddressService, 'get_address_by_id', return_value=mock_current_address):
            result = await AddressService.update_address(1, address_data)
            
            assert result == mock_current_address

    @pytest.mark.asyncio
    async def test_delete_address_success(self, mock_address_data):
        """Test successful address deletion."""
        mock_address = Address(**mock_address_data[0])
        
        with patch.object(AddressService, 'get_address_by_id', return_value=mock_address), \
             patch('lightspun.services.address_service.DatabaseOperations') as mock_db_ops:
            
            mock_db_ops.delete_by_id.return_value = True
            
            result = await AddressService.delete_address(1)
            
            assert result is True
            mock_db_ops.delete_by_id.assert_called_once_with("addresses", 1)

    @pytest.mark.asyncio
    async def test_delete_address_not_found(self):
        """Test deletion of non-existent address."""
        with patch.object(AddressService, 'get_address_by_id', return_value=None):
            result = await AddressService.delete_address(999)
            assert result is False

    @pytest.mark.asyncio
    async def test_search_addresses_by_street_name(self, mock_address_data):
        """Test searching addresses by street name."""
        # Filter for Main Street addresses
        main_street_addresses = [addr for addr in mock_address_data if "Main" in addr["street_name"]]
        mock_rows = [MagicMock(**addr) for addr in main_street_addresses]
        
        with patch('lightspun.services.address_service.database') as mock_db, \
             patch('lightspun.services.address_service.standardize_street_type', return_value="Main Street"):
            
            mock_db.fetch_all.return_value = mock_rows
            
            result = await AddressService.search_addresses_by_street_name("Main St", limit=10)
            
            assert len(result) == 1
            assert all(isinstance(addr, Address) for addr in result)
            
            # Verify standardization was applied
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert "Main Street" in values['street_name']

    @pytest.mark.asyncio
    async def test_search_addresses_by_street_number(self, mock_address_data):
        """Test searching addresses by street number."""
        # Filter for addresses with number "123"
        filtered_addresses = [addr for addr in mock_address_data if addr["street_number"] == "123"]
        mock_rows = [MagicMock(**addr) for addr in filtered_addresses]
        
        with patch('lightspun.services.address_service.database') as mock_db:
            mock_db.fetch_all.return_value = mock_rows
            
            result = await AddressService.search_addresses_by_street_number("123", limit=15)
            
            assert len(result) == 1
            assert result[0].street_number == "123"
            
            # Verify query parameters
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert values['street_number'] == "123"
            assert values['limit'] == 15

    @pytest.mark.asyncio
    async def test_fuzzy_search_addresses(self):
        """Test fuzzy address search."""
        mock_suggestions = ["123 Main Street, Los Angeles, CA", "124 Main Street, Los Angeles, CA"]
        
        with patch('lightspun.services.address_service.FuzzySearchConfig') as mock_config, \
             patch('lightspun.services.address_service.AddressFuzzySearch') as mock_searcher:
            
            mock_searcher_instance = mock_searcher.return_value
            mock_searcher_instance.search_addresses.return_value = mock_suggestions
            
            result = await AddressService.fuzzy_search_addresses("Main St", limit=5, min_similarity=0.4)
            
            assert result == mock_suggestions
            
            # Verify configuration
            mock_config.assert_called_once_with(min_similarity=0.4, limit=5)
            mock_searcher_instance.search_addresses.assert_called_once_with("Main St", 5)

    @pytest.mark.asyncio
    async def test_autocomplete_addresses_with_fuzzy(self):
        """Test address autocomplete with fuzzy search enabled."""
        mock_suggestions = ["123 Main Street, Los Angeles, CA"]
        
        with patch('lightspun.services.address_service.FuzzySearchConfig') as mock_config, \
             patch('lightspun.services.address_service.AddressFuzzySearch') as mock_searcher:
            
            mock_searcher_instance = mock_searcher.return_value
            mock_searcher_instance.autocomplete.return_value = mock_suggestions
            
            result = await AddressService.autocomplete_addresses("Main", limit=8, use_fuzzy=True)
            
            assert result == mock_suggestions
            mock_searcher_instance.autocomplete.assert_called_once_with("Main", 8)

    @pytest.mark.asyncio
    async def test_autocomplete_addresses_without_fuzzy(self):
        """Test address autocomplete with fuzzy search disabled."""
        mock_rows = [
            MagicMock(full_address="123 Main Street, Los Angeles, CA"),
            MagicMock(full_address="124 Main Street, Los Angeles, CA")
        ]
        
        with patch('lightspun.services.address_service.database') as mock_db, \
             patch('lightspun.services.address_service.standardize_street_type', return_value="Main Street"):
            
            mock_db.fetch_all.return_value = mock_rows
            
            result = await AddressService.autocomplete_addresses("Main", limit=5, use_fuzzy=False)
            
            assert len(result) == 2
            assert "123 Main Street, Los Angeles, CA" in result
            
            # Verify exact matching query was used
            call_args = mock_db.fetch_all.call_args
            values = call_args[1]['values']
            assert values['prefix_term'] == "Main%"
            assert values['std_prefix_term'] == "Main Street%"

    @pytest.mark.asyncio
    async def test_autocomplete_addresses_short_query(self):
        """Test address autocomplete with query too short."""
        result = await AddressService.autocomplete_addresses("M", limit=10)
        assert result == []
        
        result = await AddressService.autocomplete_addresses("", limit=10)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_addresses(self, mock_address_data):
        """Test retrieving all addresses."""
        mock_results = mock_address_data
        
        with patch('lightspun.services.address_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.get_all.return_value = mock_results
            
            result = await AddressService.get_all_addresses(limit=500)
            
            assert len(result) == 2
            assert all(isinstance(addr, Address) for addr in result)
            
            # Verify call parameters
            mock_db_ops.get_all.assert_called_once_with(
                table="addresses",
                fields=["id", "street_number", "street_name", "unit", "street_address", "city", "state_code", "full_address"],
                order_by=["state_code", "city", "street_name", "street_number"],
                limit=500
            )

    @pytest.mark.asyncio
    async def test_get_all_addresses_default_limit(self):
        """Test retrieving all addresses with default limit."""
        with patch('lightspun.services.address_service.DatabaseOperations') as mock_db_ops:
            mock_db_ops.get_all.return_value = []
            
            await AddressService.get_all_addresses()
            
            call_args = mock_db_ops.get_all.call_args
            assert call_args[1]['limit'] == 1000  # Default limit

    @pytest.mark.asyncio
    async def test_search_addresses_alias(self):
        """Test that search_addresses is an alias for autocomplete_addresses."""
        mock_suggestions = ["123 Main Street, Los Angeles, CA"]
        
        with patch.object(AddressService, 'autocomplete_addresses', return_value=mock_suggestions) as mock_autocomplete:
            result = await AddressService.search_addresses("Main", limit=5)
            
            assert result == mock_suggestions
            mock_autocomplete.assert_called_once_with("Main", 5, use_fuzzy=True)