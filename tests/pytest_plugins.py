"""
Custom pytest plugins for test configuration.
"""

import pytest
import asyncio
from typing import Generator


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "external: marks tests that require external services"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests that measure performance"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add slow marker to tests that take a long time
        if "performance" in item.keywords:
            item.add_marker(pytest.mark.slow)
        
        # Add external marker to tests that use external services
        if any(keyword in item.keywords for keyword in ["database", "api"]):
            if "integration" in item.keywords:
                item.add_marker(pytest.mark.external)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class DatabaseTransactionManager:
    """Context manager for database transactions in tests."""
    
    def __init__(self, connection):
        self.connection = connection
        self.transaction = None
    
    async def __aenter__(self):
        self.transaction = self.connection.transaction()
        await self.transaction.start()
        return self.connection
    
    async def __aexist__(self, exc_type, exc_val, exc_tb):
        if self.transaction:
            await self.transaction.rollback()


@pytest.fixture
async def db_transaction(db_connection):
    """Provide a database connection with automatic rollback."""
    async with DatabaseTransactionManager(db_connection) as conn:
        yield conn