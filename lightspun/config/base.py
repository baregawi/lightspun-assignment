"""
Base configuration classes and configuration loading logic.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = Field(..., description="Database connection URL")
    pool_size: int = Field(5, description="Connection pool size")
    max_overflow: int = Field(10, description="Maximum connection overflow")
    pool_timeout: int = Field(30, description="Connection pool timeout in seconds")
    pool_recycle: int = Field(3600, description="Connection recycle time in seconds")
    echo: bool = Field(False, description="Enable SQLAlchemy query logging")


class ServerConfig(BaseModel):
    """Server configuration"""
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port")
    reload: bool = Field(False, description="Enable auto-reload")
    workers: int = Field(1, description="Number of worker processes")
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field("INFO", description="Log level")
    format: str = Field("colored", description="Log format (colored/json/simple)")
    file_enabled: bool = Field(True, description="Enable file logging")
    file_path: str = Field("logs/app.log", description="Log file path")
    file_max_bytes: int = Field(10485760, description="Max log file size (10MB)")
    file_backup_count: int = Field(5, description="Number of log file backups")
    console_enabled: bool = Field(True, description="Enable console logging")
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        valid_formats = ['colored', 'json', 'simple']
        if v not in valid_formats:
            raise ValueError(f'Log format must be one of {valid_formats}')
        return v


class SecurityConfig(BaseModel):
    """Security configuration"""
    secret_key: Optional[str] = Field(None, description="Application secret key")
    algorithm: str = Field("HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(30, description="Access token expiration")
    cors_origins: List[str] = Field(["*"], description="CORS allowed origins")
    cors_allow_credentials: bool = Field(True, description="CORS allow credentials")
    cors_allow_methods: List[str] = Field(["*"], description="CORS allowed methods")
    cors_allow_headers: List[str] = Field(["*"], description="CORS allowed headers")


class APIConfig(BaseModel):
    """API configuration"""
    title: str = Field("US States and Addresses API", description="API title")
    description: str = Field("FastAPI backend for US states, municipalities, and addresses", description="API description")
    version: str = Field("1.0.0", description="API version")
    docs_url: Optional[str] = Field("/docs", description="OpenAPI docs URL")
    redoc_url: Optional[str] = Field("/redoc", description="ReDoc URL")
    openapi_url: Optional[str] = Field("/openapi.json", description="OpenAPI schema URL")
    debug: bool = Field(False, description="Enable debug mode")


class Config(ABC):
    """Abstract base configuration class"""
    
    def __init__(self):
        self.database: DatabaseConfig
        self.server: ServerConfig
        self.logging: LoggingConfig
        self.security: SecurityConfig
        self.api: APIConfig
        self.environment: str
        
    @abstractmethod
    def load(self) -> None:
        """Load configuration from appropriate sources"""
        pass
    
    def get_database_url(self, hide_password: bool = False) -> str:
        """Get database URL, optionally hiding the password"""
        if hide_password:
            return self.database.url.replace(
                self.database.url.split('@')[0].split(':')[-1], 
                '***'
            )
        return self.database.url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment,
            'database': self.database.dict(),
            'server': self.server.dict(),
            'logging': self.logging.dict(),
            'security': {**self.security.dict(), 'secret_key': '***' if self.security.secret_key else None},
            'api': self.api.dict()
        }


def get_environment() -> str:
    """Get current environment from ENV variable"""
    return os.getenv('ENVIRONMENT', 'development').lower()


def get_config(setup_logging: bool = True) -> Config:
    """Get configuration instance based on environment
    
    Args:
        setup_logging: Whether to automatically setup logging with the config
        
    Returns:
        Configured Config instance
    """
    environment = get_environment()
    
    if environment == 'production':
        from .production import ProductionConfig
        config = ProductionConfig()
    elif environment == 'testing':
        from .testing import TestingConfig
        config = TestingConfig()
    else:
        from .development import DevelopmentConfig
        config = DevelopmentConfig()
    
    config.load()
    
    # Automatically setup logging with the loaded configuration
    if setup_logging:
        try:
            from ..logging_config import setup_logging as setup_logging_func
            setup_logging_func(config)
        except ImportError:
            # Fallback to basic logging if logging_config is not available
            import logging
            logging.basicConfig(
                level=getattr(config.logging, 'level', 'INFO'),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    return config