"""
Production environment configuration.

This configuration is optimized for production deployment with:
- Environment variable based configuration
- Secure defaults
- JSON logging for machine parsing
- Performance optimizations
- Strict security settings
"""

import os
from typing import List
from .base import Config, DatabaseConfig, ServerConfig, LoggingConfig, SecurityConfig, APIConfig


class ProductionConfig(Config):
    """Production environment configuration"""
    
    def __init__(self):
        super().__init__()
        self.environment = "production"
    
    def load(self) -> None:
        """Load production configuration from environment variables"""
        self.database = DatabaseConfig(
            url=self._get_required_env("DATABASE_URL"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "20")),  # Larger pool for production
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "30")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
        
        self.server = ServerConfig(
            host=os.getenv("SERVER_HOST", "0.0.0.0"),
            port=int(os.getenv("SERVER_PORT", "8000")),
            reload=False,  # Never enable reload in production
            workers=int(os.getenv("SERVER_WORKERS", "4"))  # Multiple workers for production
        )
        
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format="json",  # JSON format for production log parsing
            file_enabled=os.getenv("LOG_FILE_ENABLED", "true").lower() == "true",
            file_path=os.getenv("LOG_FILE_PATH", "/var/log/app/app.log"),
            file_max_bytes=int(os.getenv("LOG_FILE_MAX_BYTES", "52428800")),  # 50MB
            file_backup_count=int(os.getenv("LOG_FILE_BACKUP_COUNT", "10")),
            console_enabled=os.getenv("LOG_CONSOLE_ENABLED", "true").lower() == "true"
        )
        
        self.security = SecurityConfig(
            secret_key=self._get_required_env("SECRET_KEY"),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")),  # Shorter in production
            cors_origins=self._get_cors_origins(),
            cors_allow_credentials=os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true",
            cors_allow_methods=self._get_list_env("CORS_ALLOW_METHODS", ["GET", "POST", "PUT", "DELETE"]),
            cors_allow_headers=self._get_list_env("CORS_ALLOW_HEADERS", ["Content-Type", "Authorization"])
        )
        
        self.api = APIConfig(
            title=os.getenv("API_TITLE", "US States and Addresses API"),
            description=os.getenv("API_DESCRIPTION", "FastAPI backend for US states, municipalities, and addresses"),
            version=os.getenv("API_VERSION", "1.0.0"),
            docs_url=os.getenv("API_DOCS_URL", None),  # Disable docs in production by default
            redoc_url=os.getenv("API_REDOC_URL", None),  # Disable redoc in production by default
            openapi_url=os.getenv("API_OPENAPI_URL", None),  # Disable openapi in production by default
            debug=False  # Never enable debug in production
        )
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _get_cors_origins(self) -> List[str]:
        """Get CORS origins from environment"""
        origins_str = os.getenv("CORS_ORIGINS", "")
        if not origins_str:
            return []
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    def _get_list_env(self, key: str, default: List[str]) -> List[str]:
        """Get list from environment variable"""
        value = os.getenv(key)
        if not value:
            return default
        return [item.strip() for item in value.split(",") if item.strip()]