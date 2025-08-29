# Professional Configuration Management System

This document describes the comprehensive, fully-integrated configuration management system implemented for the Lightspun FastAPI application.

## Overview

The configuration system provides:
- ✅ **Environment-specific configurations** (development, production, testing)
- ✅ **Secure handling of sensitive data** via environment variables
- ✅ **Configuration validation** using Pydantic models
- ✅ **Type-safe configuration access** throughout the application
- ✅ **Fully integrated logging system** - automatic setup with configuration loading
- ✅ **Professional logging configuration** with different formats per environment
- ✅ **CORS and security settings** management
- ✅ **Database connection pooling** configuration
- ✅ **API documentation** control per environment
- ✅ **Zero-configuration startup** - everything configured with single `get_config()` call

## Architecture

```
lightspun/config/
├── __init__.py          # Public interface
├── base.py             # Abstract base classes and utilities
├── development.py      # Development environment config
├── production.py       # Production environment config (uses .env)
└── testing.py          # Testing environment config
```

## Configuration Classes

### DatabaseConfig
- Connection URL with credentials
- Connection pooling settings (size, overflow, timeout, recycle)
- Query logging control

### ServerConfig
- Host and port settings
- Worker process configuration
- Hot reload settings
- Port validation (1-65535)

### LoggingConfig
- Log level with validation (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Log format (colored, json, simple) 
- File logging configuration with rotation
- Console logging control

### SecurityConfig
- JWT secret key and algorithm
- Token expiration settings
- CORS origins, methods, and headers
- Credential handling

### APIConfig
- API title, description, version
- Documentation URLs (can be disabled in production)
- Debug mode control

## Environment Configurations

### Development (`ENVIRONMENT=development`)
```python
{
    "database_url": "postgresql://user:password@postgres:5432/lightspun_db",
    "log_level": "DEBUG",
    "log_format": "colored",
    "api_debug": True,
    "server_reload": True,
    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
    "docs_enabled": True
}
```

### Production (`ENVIRONMENT=production`)
```python
{
    "database_url": "${DATABASE_URL}",  # From environment
    "log_level": "${LOG_LEVEL:-INFO}",  # Defaults to INFO
    "log_format": "json",               # Machine-readable
    "api_debug": False,                 # Never debug in prod
    "server_reload": False,             # Never reload in prod
    "server_workers": 4,                # Multiple workers
    "cors_origins": "${CORS_ORIGINS}",  # From environment
    "docs_enabled": False               # Disabled by default
}
```

### Testing (`ENVIRONMENT=testing`)
```python
{
    "database_url": "postgresql://user:password@localhost:5432/lightspun_test_db",
    "log_level": "WARNING",             # Minimal logging
    "log_format": "simple",
    "file_logging": False,              # No file logs in tests
    "server_port": 8001,                # Different port
    "docs_enabled": False
}
```

## Environment Variables

For production deployment, create a `.env` file based on `.env.example`:

```bash
# Core Settings
ENVIRONMENT=production
DATABASE_URL=postgresql://user:secure_password@postgres:5432/lightspun_db
SECRET_KEY=your-super-secure-secret-key

# Database Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Server Settings  
SERVER_WORKERS=4
SERVER_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=/var/log/app/app.log

# Security
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ACCESS_TOKEN_EXPIRE_MINUTES=15

# API Control (empty = disabled)
API_DOCS_URL=
API_REDOC_URL=
```

## Usage Examples

### Basic Usage (Fully Integrated)
```python
from lightspun.config import get_config
from lightspun.logging_config import get_logger

# Single call loads configuration AND sets up logging automatically
config = get_config()
logger = get_logger('my.module')

# Logging is now fully configured based on environment
logger.info("Application started")  # Colored in dev, JSON in prod

print(f"Environment: {config.environment}")
print(f"Database URL: {config.get_database_url(hide_password=True)}")
print(f"Log Level: {config.logging.level}")
```

### Zero-Configuration Startup
```python
# Before: Required multiple manual setup steps
# setup_logging(config)
# init_database(config) 
# configure_cors(config)

# After: Single call does everything
config = get_config()  # ← Automatically sets up logging!
```

### Application Integration (Simplified)
```python
# FastAPI app with integrated configuration
from lightspun.config import get_config

# Everything configured automatically
config = get_config()  # ← Logging setup happens here automatically

app = FastAPI(
    title=config.api.title,
    version=config.api.version,
    docs_url=config.api.docs_url,
    debug=config.api.debug
)

# CORS automatically configured from environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.cors_origins,
    allow_credentials=config.security.cors_allow_credentials
)
```

### Database Integration (Simplified)
```python
from lightspun.config import get_config
from lightspun.database import init_database

config = get_config()  # ← Logging already configured!
init_database(config)  # Database gets properly configured logger
```

### Module-Level Usage
```python
from lightspun.config import get_config
from lightspun.logging_config import get_logger

# Get configuration (with automatic logging setup)
config = get_config()

# Get logger - automatically configured with request IDs and formatting
logger = get_logger(__name__)

logger.info("Module initialized")  # Perfect formatting per environment
```

## Configuration Validation

All configuration values are validated using Pydantic:

```python
# Port validation
ServerConfig(port=99999)  # ❌ ValueError: Port must be between 1 and 65535

# Log level validation  
LoggingConfig(level="INVALID")  # ❌ ValueError: Log level must be one of [DEBUG, INFO, ...]

# Log format validation
LoggingConfig(format="invalid")  # ❌ ValueError: Log format must be one of [colored, json, simple]
```

## Security Features

- **Password masking**: Database URLs hide passwords in logs
- **Secret key management**: Production secrets from environment variables
- **CORS configuration**: Environment-specific allowed origins
- **Documentation control**: Can disable API docs in production
- **Validation**: All inputs validated for security

## Testing

Run the configuration test suite:
```bash
python test_config.py
```

This validates:
- ✅ All three environment configurations load correctly
- ✅ Environment variable overrides work in production
- ✅ Configuration validation catches invalid values
- ✅ Type safety and error handling

## Integration Benefits

### Before Integration
```python
# Multiple manual steps required
from lightspun.config import get_config
from lightspun.logging_config import setup_logging
from lightspun.database import init_database

config = get_config()
setup_logging(config)          # ← Manual step
init_database(config)          # ← Manual step  
logger = get_logger(__name__)  # ← Might not be configured properly
```

### After Integration
```python
# Single call handles everything
from lightspun.config import get_config
from lightspun.logging_config import get_logger

config = get_config()          # ← Automatically sets up logging
logger = get_logger(__name__)  # ← Always properly configured
```

## Key Benefits

1. **Zero-Configuration Startup**: Single `get_config()` call sets up everything
2. **Environment Isolation**: Each environment has appropriate defaults
3. **Automatic Logging Integration**: No manual logging setup required
4. **Security**: Sensitive data via environment variables, not code
5. **Type Safety**: Pydantic models prevent configuration errors
6. **Validation**: Catch invalid configurations at startup
7. **Consistent Logging**: All modules get properly formatted logs
8. **Request Tracing**: Automatic request ID injection for API calls
9. **Professional Output**: 
   - Development: Colored console logs
   - Production: Structured JSON logs  
   - Testing: Minimal simple logs
10. **Documentation**: Self-documenting configuration with descriptions
11. **Flexibility**: Easy to add new settings or environments
12. **Professional**: Follows industry best practices

## Best Practices

1. **Never commit `.env` files** - they contain secrets
2. **Use `.env.example`** as a template for deployment
3. **Validate early** - configuration loads at application startup  
4. **Hide passwords** in logs using `get_database_url(hide_password=True)`
5. **Use environment-specific defaults** rather than hardcoding
6. **Document all settings** with Pydantic Field descriptions