# Test Suite Documentation

This directory contains comprehensive tests for the Lightspun Assignment API services. The test suite is organized into unit tests and integration tests with proper separation of concerns.

## Directory Structure

```
tests/
├── README.md                    # This documentation
├── pytest.ini                  # Pytest configuration
├── conftest.py                 # Global test fixtures and configuration
├── pytest_plugins.py          # Custom pytest plugins
├── requirements.txt            # Testing dependencies
├── fixtures/                   # Test data fixtures
│   ├── __init__.py
│   └── sample_data.py          # Sample data for testing
├── utils/                      # Test utilities and helpers
│   ├── __init__.py
│   └── test_helpers.py         # Testing helper functions
├── unit/                       # Unit tests
│   └── services/               # Service layer unit tests
│       ├── test_state_service.py
│       ├── test_municipality_service.py
│       └── test_address_service.py
└── integration/                # Integration tests
    └── api/                    # API endpoint integration tests
        ├── test_states_api.py
        ├── test_municipalities_api.py
        └── test_addresses_api.py
```

## Test Categories

### Unit Tests (`tests/unit/`)

Unit tests focus on testing individual service methods in isolation using mocking:

- **State Service Tests**: Test state CRUD operations, validation, and error handling
- **Municipality Service Tests**: Test municipality operations, relationships with states
- **Address Service Tests**: Test address operations, autocomplete functionality

#### Key Features:
- Comprehensive mocking of database operations
- Test all service methods including error scenarios
- Validate business logic and data transformations
- Test async operations properly

### Integration Tests (`tests/integration/`)

Integration tests verify API endpoints work correctly with the full application stack:

- **States API Tests**: Test all state-related endpoints
- **Municipalities API Tests**: Test municipality endpoints and state relationships
- **Addresses API Tests**: Test address endpoints and autocomplete functionality

#### Key Features:
- Test complete request/response cycles
- Validate HTTP status codes and response formats
- Test error handling and validation
- Performance and content-type verification

## Test Configuration

### Pytest Configuration (`pytest.ini`)

The test suite uses extensive pytest markers for organizing tests:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.state` - State-related tests
- `@pytest.mark.municipality` - Municipality-related tests
- `@pytest.mark.address` - Address-related tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.asyncio` - Async tests

### Global Fixtures (`conftest.py`)

Shared fixtures available to all tests:

- `test_client` - FastAPI test client
- `db_connection` - Database connection for tests
- `clean_db` - Clean database state
- `sample_states` - Pre-populated state data
- `sample_municipalities` - Pre-populated municipality data
- `sample_addresses` - Pre-populated address data
- Mock data fixtures for various test scenarios

## Running Tests

### Run All Tests
```bash
pytest
```

### Run by Category
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific service tests
pytest -m state
pytest -m municipality
pytest -m address
```

### Run with Coverage
```bash
pytest --cov=lightspun --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/unit/services/test_state_service.py
pytest tests/integration/api/test_states_api.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Fast Tests Only (exclude slow tests)
```bash
pytest -m "not slow"
```

## Test Utilities

### Helper Classes (`tests/utils/test_helpers.py`)

The test suite includes several helper classes:

- **DatabaseTestHelper**: Database operation helpers and assertions
- **APITestHelper**: API response validation helpers
- **MockDataBuilder**: Consistent mock data creation
- **AsyncTestHelper**: Async testing utilities
- **ValidationTestHelper**: Validation error testing
- **PerformanceTestHelper**: Performance measurement utilities
- **ErrorTestHelper**: Error scenario testing

### Sample Data (`tests/fixtures/sample_data.py`)

Comprehensive sample data for testing:

- **SampleDataFixtures**: Pre-defined test data
- State, municipality, and address sample data
- Test scenarios for different use cases
- Performance test data generation
- Validation test cases

## Testing Best Practices

### Unit Test Guidelines

1. **Mock External Dependencies**: All database calls are mocked
2. **Test Business Logic**: Focus on service method behavior
3. **Error Scenarios**: Test both success and failure cases
4. **Async Testing**: Properly handle async operations with pytest-asyncio
5. **Data Validation**: Test schema validation and transformations

### Integration Test Guidelines

1. **Real Database**: Use actual database connections with transaction rollback
2. **Full Request Cycle**: Test complete HTTP request/response
3. **Status Codes**: Verify correct HTTP status codes
4. **Response Format**: Validate JSON response structure
5. **Error Handling**: Test error responses and messages

### Test Data Management

1. **Fixtures**: Use pytest fixtures for consistent test data
2. **Isolation**: Each test should be independent
3. **Cleanup**: Automatic cleanup with database transactions
4. **Realistic Data**: Use realistic sample data that mirrors production

## Dependencies

The test suite requires additional dependencies specified in `requirements.txt`:

- `pytest` and plugins for test framework
- `httpx` and `requests` for HTTP testing
- `asyncpg` for async database testing
- `factory-boy` and `faker` for test data generation
- `pytest-benchmark` for performance testing
- Code quality tools (`flake8`, `black`, `mypy`)

## Coverage Goals

The test suite aims for high code coverage:

- **Unit Tests**: 90%+ coverage of service layer
- **Integration Tests**: 100% coverage of API endpoints
- **Error Paths**: Test all error scenarios and edge cases
- **Business Logic**: Comprehensive testing of business rules

## Continuous Integration

Tests are designed to run in CI/CD environments:

- Parallel execution support with `pytest-xdist`
- HTML and JSON reporting for CI systems
- Performance benchmarking
- Code quality checks

## Adding New Tests

When adding new functionality:

1. **Unit Tests**: Add corresponding unit tests for new service methods
2. **Integration Tests**: Add API endpoint tests for new routes
3. **Mock Data**: Update sample data fixtures if needed
4. **Documentation**: Update this README with new test information

### Example Unit Test Structure

```python
@pytest.mark.unit
@pytest.mark.service_name
class TestServiceName:
    \"\"\"Test suite for ServiceName.\"\"\"
    
    @pytest.mark.asyncio
    async def test_method_success(self, mock_data):
        \"\"\"Test successful method execution.\"\"\"
        # Arrange
        # Act  
        # Assert
    
    @pytest.mark.asyncio
    async def test_method_error_case(self):
        \"\"\"Test method error handling.\"\"\"
        # Test error scenarios
```

### Example Integration Test Structure

```python
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.service_name
class TestServiceAPI:
    \"\"\"Integration test suite for Service API endpoints.\"\"\"
    
    @pytest.mark.asyncio
    async def test_endpoint_success(self, test_client, sample_data):
        \"\"\"Test successful API endpoint.\"\"\"
        response = test_client.get(\"/endpoint\")
        assert response.status_code == 200
        # Validate response structure and content
    
    def test_endpoint_error_case(self, test_client):
        \"\"\"Test API endpoint error handling.\"\"\"
        # Test error responses
```

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure test database is available
2. **Async Issues**: Use `@pytest.mark.asyncio` for async tests
3. **Fixture Dependencies**: Check fixture scope and dependencies
4. **Mock Problems**: Verify mock paths and return values

### Debug Mode

Run tests with debugging:

```bash
pytest --pdb  # Drop into debugger on failure
pytest -s     # Show print statements
pytest --lf   # Run last failed tests only
```