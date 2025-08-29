"""
Development environment configuration.

This configuration is optimized for development work with:
- Local database connections
- Debug logging enabled
- Hot reloading enabled
- Relaxed security settings
- Colored console logging
"""

from .base import Config, DatabaseConfig, ServerConfig, LoggingConfig, SecurityConfig, APIConfig


class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    def __init__(self):
        super().__init__()
        self.environment = "development"
    
    def load(self) -> None:
        """Load development configuration"""
        self.database = DatabaseConfig(
            url="postgresql://user:password@postgres:5432/lightspun_db",
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            echo=False  # Set to True to see SQL queries in development
        )
        
        self.server = ServerConfig(
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable hot reloading in development
            workers=1
        )
        
        self.logging = LoggingConfig(
            level="DEBUG",  # More verbose logging in development
            format="colored",  # Colored output for better readability
            file_enabled=True,
            file_path="logs/app.log",
            file_max_bytes=10485760,
            file_backup_count=5,
            console_enabled=True
        )
        
        self.security = SecurityConfig(
            secret_key="dev-secret-key-change-in-production",
            algorithm="HS256",
            access_token_expire_minutes=60,  # Longer expiration in dev
            cors_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Common frontend ports
            cors_allow_credentials=True,
            cors_allow_methods=["*"],
            cors_allow_headers=["*"]
        )
        
        self.api = APIConfig(
            title="US States and Addresses API (Development)",
            description="FastAPI backend for US states, municipalities, and addresses - Development Environment",
            version="1.0.0-dev",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            debug=True  # Enable debug mode in development
        )