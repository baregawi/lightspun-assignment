"""
Testing environment configuration.

This configuration is optimized for automated testing with:
- In-memory or test database
- Minimal logging
- Fast execution settings
- Test-specific overrides
"""

from .base import Config, DatabaseConfig, ServerConfig, LoggingConfig, SecurityConfig, APIConfig


class TestingConfig(Config):
    """Testing environment configuration"""
    
    def __init__(self):
        super().__init__()
        self.environment = "testing"
    
    def load(self) -> None:
        """Load testing configuration"""
        self.database = DatabaseConfig(
            url="postgresql://user:password@localhost:5432/lightspun_test_db",
            pool_size=1,  # Minimal pool for testing
            max_overflow=2,
            pool_timeout=5,  # Shorter timeouts for faster test failures
            pool_recycle=300,  # Shorter recycle time
            echo=False  # Disable query logging in tests unless debugging
        )
        
        self.server = ServerConfig(
            host="127.0.0.1",
            port=8001,  # Different port to avoid conflicts
            reload=False,
            workers=1
        )
        
        self.logging = LoggingConfig(
            level="WARNING",  # Minimal logging in tests
            format="simple",
            file_enabled=False,  # No file logging in tests
            file_path="",
            file_max_bytes=0,
            file_backup_count=0,
            console_enabled=True
        )
        
        self.security = SecurityConfig(
            secret_key="test-secret-key-not-secure",
            algorithm="HS256",
            access_token_expire_minutes=5,  # Very short expiration for tests
            cors_origins=["http://localhost"],
            cors_allow_credentials=True,
            cors_allow_methods=["*"],
            cors_allow_headers=["*"]
        )
        
        self.api = APIConfig(
            title="US States and Addresses API (Testing)",
            description="FastAPI backend for US states, municipalities, and addresses - Testing Environment",
            version="1.0.0-test",
            docs_url=None,  # Disable docs in testing
            redoc_url=None,  # Disable redoc in testing
            openapi_url=None,  # Disable openapi in testing
            debug=False
        )