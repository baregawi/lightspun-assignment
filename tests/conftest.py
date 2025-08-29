"""
Pytest configuration and shared fixtures for all tests.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Any
from fastapi.testclient import TestClient
import asyncpg
from lightspun.app import app
from lightspun.config import get_config
from lightspun.database import database


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def config():
    """Get test configuration."""
    return get_config()


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def db_connection(config):
    """Create a database connection for tests."""
    connection = await asyncpg.connect(
        host=config.database.host,
        port=config.database.port,
        user=config.database.user,
        password=config.database.password,
        database=config.database.name
    )
    yield connection
    await connection.close()


@pytest_asyncio.fixture(scope="function")
async def clean_db(db_connection):
    """Clean database before each test."""
    # Start transaction
    await db_connection.execute("BEGIN")
    
    # Clean tables in correct order (respecting foreign keys)
    await db_connection.execute("DELETE FROM addresses")
    await db_connection.execute("DELETE FROM municipalities")
    await db_connection.execute("DELETE FROM states")
    
    # Reset sequences
    await db_connection.execute("ALTER SEQUENCE states_id_seq RESTART WITH 1")
    await db_connection.execute("ALTER SEQUENCE municipalities_id_seq RESTART WITH 1") 
    await db_connection.execute("ALTER SEQUENCE addresses_id_seq RESTART WITH 1")
    
    yield
    
    # Rollback transaction
    await db_connection.execute("ROLLBACK")


@pytest_asyncio.fixture(scope="function")
async def sample_states(db_connection):
    """Create sample states for testing."""
    states = [
        {"code": "CA", "name": "California"},
        {"code": "NY", "name": "New York"},
        {"code": "TX", "name": "Texas"},
        {"code": "FL", "name": "Florida"},
        {"code": "WA", "name": "Washington"}
    ]
    
    inserted_states = []
    for state in states:
        result = await db_connection.fetchrow(
            "INSERT INTO states (code, name) VALUES ($1, $2) RETURNING id, code, name",
            state["code"], state["name"]
        )
        inserted_states.append(dict(result))
    
    return inserted_states


@pytest_asyncio.fixture(scope="function")
async def sample_municipalities(db_connection, sample_states):
    """Create sample municipalities for testing."""
    municipalities = [
        {"name": "Los Angeles", "type": "city", "state_code": "CA"},
        {"name": "San Francisco", "type": "city", "state_code": "CA"},
        {"name": "Sacramento", "type": "city", "state_code": "CA"},
        {"name": "New York", "type": "city", "state_code": "NY"},
        {"name": "Buffalo", "type": "city", "state_code": "NY"},
        {"name": "Houston", "type": "city", "state_code": "TX"},
        {"name": "Dallas", "type": "city", "state_code": "TX"},
        {"name": "Miami", "type": "city", "state_code": "FL"},
        {"name": "Seattle", "type": "city", "state_code": "WA"},
    ]
    
    # Get state IDs
    state_lookup = {state["code"]: state["id"] for state in sample_states}
    
    inserted_municipalities = []
    for municipality in municipalities:
        state_id = state_lookup[municipality["state_code"]]
        result = await db_connection.fetchrow(
            "INSERT INTO municipalities (name, type, state_id) VALUES ($1, $2, $3) RETURNING id, name, type, state_id",
            municipality["name"], municipality["type"], state_id
        )
        inserted_municipalities.append(dict(result))
    
    return inserted_municipalities


@pytest_asyncio.fixture(scope="function")
async def sample_addresses(db_connection, sample_states):
    """Create sample addresses for testing."""
    # Get California state for addresses
    ca_state = next(state for state in sample_states if state["code"] == "CA")
    
    addresses = [
        {
            "street_number": "123",
            "street_name": "Main Street", 
            "unit": None,
            "street_address": "123 Main Street",
            "city": "Los Angeles",
            "state_code": "CA",
            "full_address": "123 Main Street, Los Angeles, CA"
        },
        {
            "street_number": "456",
            "street_name": "Oak Avenue",
            "unit": "Apt 2B", 
            "street_address": "456 Oak Avenue",
            "city": "San Francisco",
            "state_code": "CA",
            "full_address": "456 Oak Avenue Apt 2B, San Francisco, CA"
        },
        {
            "street_number": "789",
            "street_name": "Pine Road",
            "unit": None,
            "street_address": "789 Pine Road", 
            "city": "Sacramento",
            "state_code": "CA",
            "full_address": "789 Pine Road, Sacramento, CA"
        },
        {
            "street_number": "101",
            "street_name": "First Boulevard",
            "unit": "Suite 100",
            "street_address": "101 First Boulevard",
            "city": "Los Angeles", 
            "state_code": "CA",
            "full_address": "101 First Boulevard Suite 100, Los Angeles, CA"
        },
        {
            "street_number": "202",
            "street_name": "Second Drive",
            "unit": None,
            "street_address": "202 Second Drive",
            "city": "Los Angeles",
            "state_code": "CA", 
            "full_address": "202 Second Drive, Los Angeles, CA"
        }
    ]
    
    inserted_addresses = []
    for address in addresses:
        result = await db_connection.fetchrow(
            """INSERT INTO addresses (street_number, street_name, unit, street_address, city, state_code, full_address) 
               VALUES ($1, $2, $3, $4, $5, $6, $7) 
               RETURNING id, street_number, street_name, unit, street_address, city, state_code, full_address""",
            address["street_number"], address["street_name"], address["unit"],
            address["street_address"], address["city"], address["state_code"], address["full_address"]
        )
        inserted_addresses.append(dict(result))
    
    return inserted_addresses


@pytest.fixture
def mock_state_data():
    """Mock state data for unit tests."""
    return [
        {"id": 1, "code": "CA", "name": "California"},
        {"id": 2, "code": "NY", "name": "New York"},
        {"id": 3, "code": "TX", "name": "Texas"}
    ]


@pytest.fixture
def mock_municipality_data():
    """Mock municipality data for unit tests.""" 
    return [
        {"id": 1, "name": "Los Angeles", "type": "city", "state_id": 1},
        {"id": 2, "name": "San Francisco", "type": "city", "state_id": 1},
        {"id": 3, "name": "Sacramento", "type": "city", "state_id": 1}
    ]


@pytest.fixture
def mock_address_data():
    """Mock address data for unit tests."""
    return [
        {
            "id": 1,
            "street_number": "123",
            "street_name": "Main Street",
            "unit": None,
            "street_address": "123 Main Street", 
            "city": "Los Angeles",
            "state_code": "CA",
            "full_address": "123 Main Street, Los Angeles, CA"
        },
        {
            "id": 2,
            "street_number": "456", 
            "street_name": "Oak Avenue",
            "unit": "Apt 2B",
            "street_address": "456 Oak Avenue",
            "city": "San Francisco", 
            "state_code": "CA",
            "full_address": "456 Oak Avenue Apt 2B, San Francisco, CA"
        }
    ]