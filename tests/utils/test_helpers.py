"""
Test utilities and helper functions.
"""

import asyncio
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock
import pytest


class DatabaseTestHelper:
    """Helper class for database-related test operations."""
    
    @staticmethod
    def create_mock_row(data: Dict[str, Any]) -> MagicMock:
        """Create a mock database row object."""
        mock_row = MagicMock()
        for key, value in data.items():
            setattr(mock_row, key, value)
        return mock_row
    
    @staticmethod
    def create_mock_rows(data_list: List[Dict[str, Any]]) -> List[MagicMock]:
        """Create a list of mock database row objects."""
        return [DatabaseTestHelper.create_mock_row(data) for data in data_list]
    
    @staticmethod
    def assert_database_call(mock_db, method_name: str, expected_query_contains: str = None):
        """Assert that a database method was called with expected parameters."""
        method = getattr(mock_db, method_name)
        assert method.called, f"Expected {method_name} to be called"
        
        if expected_query_contains:
            call_args = method.call_args
            query = call_args[1].get('query', '')
            assert expected_query_contains in query, f"Expected query to contain '{expected_query_contains}'"


class APITestHelper:
    """Helper class for API testing operations."""
    
    @staticmethod
    def assert_api_response_structure(response_data: Dict[str, Any], required_fields: List[str]):
        """Assert that API response has required fields."""
        for field in required_fields:
            assert field in response_data, f"Expected field '{field}' in response"
    
    @staticmethod
    def assert_error_response(response_data: Dict[str, Any], expected_status: int = None):
        """Assert that response is a proper error response."""
        assert "detail" in response_data, "Error response should contain 'detail' field"
        if expected_status:
            assert response_data.get("status_code") == expected_status
    
    @staticmethod
    def create_test_pagination_data(total_items: int, page_size: int = 10):
        """Create test data for pagination testing."""
        return {
            "total_count": total_items,
            "page_size": page_size,
            "total_pages": (total_items + page_size - 1) // page_size
        }


class MockDataBuilder:
    """Builder class for creating consistent mock data."""
    
    @staticmethod
    def build_state_data(
        id: int = 1,
        code: str = "CA", 
        name: str = "California"
    ) -> Dict[str, Any]:
        """Build mock state data."""
        return {
            "id": id,
            "code": code,
            "name": name
        }
    
    @staticmethod
    def build_municipality_data(
        id: int = 1,
        name: str = "Los Angeles",
        type: str = "city",
        state_id: int = 1
    ) -> Dict[str, Any]:
        """Build mock municipality data."""
        return {
            "id": id,
            "name": name,
            "type": type,
            "state_id": state_id
        }
    
    @staticmethod
    def build_address_data(
        id: int = 1,
        street_address: str = "123 Main Street",
        municipality_id: int = 1
    ) -> Dict[str, Any]:
        """Build mock address data."""
        return {
            "id": id,
            "street_address": street_address,
            "municipality_id": municipality_id
        }
    
    @staticmethod
    def build_multiple_states(count: int = 3) -> List[Dict[str, Any]]:
        """Build multiple states for testing."""
        states_data = [
            {"id": 1, "code": "CA", "name": "California"},
            {"id": 2, "code": "NY", "name": "New York"},
            {"id": 3, "code": "TX", "name": "Texas"},
            {"id": 4, "code": "FL", "name": "Florida"},
            {"id": 5, "code": "WA", "name": "Washington"}
        ]
        return states_data[:count]
    
    @staticmethod
    def build_multiple_municipalities(state_id: int = 1, count: int = 3) -> List[Dict[str, Any]]:
        """Build multiple municipalities for testing."""
        municipalities_data = [
            {"id": 1, "name": "Los Angeles", "type": "city", "state_id": state_id},
            {"id": 2, "name": "San Francisco", "type": "city", "state_id": state_id},
            {"id": 3, "name": "Sacramento", "type": "city", "state_id": state_id},
            {"id": 4, "name": "Oakland", "type": "city", "state_id": state_id},
            {"id": 5, "name": "San Diego", "type": "city", "state_id": state_id}
        ]
        return municipalities_data[:count]
    
    @staticmethod
    def build_multiple_addresses(municipality_id: int = 1, count: int = 5) -> List[Dict[str, Any]]:
        """Build multiple addresses for testing."""
        addresses_data = [
            {"id": 1, "street_address": "123 Main Street", "municipality_id": municipality_id},
            {"id": 2, "street_address": "456 Oak Avenue", "municipality_id": municipality_id},
            {"id": 3, "street_address": "789 Pine Road", "municipality_id": municipality_id},
            {"id": 4, "street_address": "321 Elm Street", "municipality_id": municipality_id},
            {"id": 5, "street_address": "654 Maple Drive", "municipality_id": municipality_id}
        ]
        return addresses_data[:count]


class AsyncTestHelper:
    """Helper class for async testing operations."""
    
    @staticmethod
    def create_async_mock(return_value=None):
        """Create an async mock function."""
        async def async_mock(*args, **kwargs):
            return return_value
        return AsyncMock(side_effect=async_mock)
    
    @staticmethod
    def run_async_test(async_func, *args, **kwargs):
        """Run an async function in a test environment."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_func(*args, **kwargs))


class ValidationTestHelper:
    """Helper class for validation testing."""
    
    @staticmethod
    def assert_validation_error(response, field_name: str, error_message: str = None):
        """Assert that a validation error occurred for a specific field."""
        assert response.status_code == 422
        detail = response.json()["detail"]
        
        field_errors = [error for error in detail if field_name in error["loc"]]
        assert len(field_errors) > 0, f"No validation error found for field '{field_name}'"
        
        if error_message:
            field_error = field_errors[0]
            assert error_message.lower() in field_error["msg"].lower()
    
    @staticmethod
    def create_invalid_data_cases() -> List[Dict[str, Any]]:
        """Create common invalid data cases for testing."""
        return [
            {"case": "empty_string", "value": ""},
            {"case": "whitespace_only", "value": "   "},
            {"case": "null_value", "value": None},
            {"case": "wrong_type", "value": 123},
            {"case": "too_long", "value": "a" * 1000}
        ]


class PerformanceTestHelper:
    """Helper class for performance testing."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        return result, duration
    
    @staticmethod
    async def measure_async_execution_time(async_func, *args, **kwargs):
        """Measure execution time of an async function."""
        import time
        start_time = time.time()
        result = await async_func(*args, **kwargs)
        duration = time.time() - start_time
        return result, duration
    
    @staticmethod
    def assert_performance_threshold(duration: float, threshold: float):
        """Assert that execution time is within threshold."""
        assert duration < threshold, f"Execution took {duration:.3f}s, expected < {threshold}s"


class ErrorTestHelper:
    """Helper class for error handling testing."""
    
    @staticmethod
    def create_database_error(error_type: str = "connection"):
        """Create mock database errors for testing."""
        error_messages = {
            "connection": "Connection to database failed",
            "timeout": "Database query timeout",
            "constraint": "Database constraint violation",
            "not_found": "Record not found"
        }
        
        error = Exception(error_messages.get(error_type, "Database error"))
        error.error_type = error_type
        return error
    
    @staticmethod
    def create_api_error(status_code: int = 500, message: str = "Internal server error"):
        """Create mock API errors for testing."""
        error = Exception(message)
        error.status_code = status_code
        return error