"""
Professional logging configuration for the Lightspun FastAPI application.

This module provides centralized logging configuration with:
- Structured JSON logging for production
- Colored console output for development
- Configurable log levels via environment variables
- Request ID tracking for API requests
- File rotation for persistent logs
"""

import logging
import logging.config
import os
import sys
from typing import Dict, Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
            
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
            
        if hasattr(record, 'duration'):
            log_obj['duration_ms'] = record.duration
            
        return json.dumps(log_obj)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output in development."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green  
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Build log message
        log_parts = [
            f"{color}{record.levelname:<8}{reset}",
            f"{timestamp}",
            f"{record.name:<20}",
            f"{record.getMessage()}"
        ]
        
        # Add request ID if present
        if hasattr(record, 'request_id'):
            log_parts.insert(-1, f"[{record.request_id}]")
            
        return " ".join(log_parts)


def setup_logging(config) -> None:
    """Setup professional logging configuration.
    
    Args:
        config: Configuration object containing logging settings
    """
    if config is None:
        raise ValueError("Configuration object is required for logging setup")
    
    log_config = config.logging
    environment = config.environment
    
    # Base configuration
    logging_config_dict: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JSONFormatter,
            },
            'colored': {
                '()': ColoredFormatter,
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {},
        'loggers': {
            # Application loggers
            'lightspun': {
                'level': log_config.level,
                'handlers': [],
                'propagate': False
            },
            'load_data': {
                'level': log_config.level, 
                'handlers': [],
                'propagate': False
            },
            
            # Third-party loggers (reduce noise)
            'uvicorn': {
                'level': 'INFO',
                'handlers': [],
                'propagate': False
            },
            'uvicorn.access': {
                'level': 'INFO',
                'handlers': [],
                'propagate': False
            },
            'sqlalchemy.engine': {
                'level': 'WARNING',
                'handlers': [],
                'propagate': False
            },
            'databases': {
                'level': 'WARNING',
                'handlers': [],
                'propagate': False
            }
        },
        'root': {
            'level': log_config.level,
            'handlers': []
        }
    }
    
    # Add console handler if enabled
    if log_config.console_enabled:
        logging_config_dict['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'level': log_config.level,
            'stream': sys.stdout,
        }
        # Add console to all logger handlers
        for logger in logging_config_dict['loggers'].values():
            logger['handlers'].append('console')
        logging_config_dict['root']['handlers'].append('console')
    
    # Add file handler if enabled
    if log_config.file_enabled:
        logging_config_dict['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_config.level,
            'filename': log_config.file_path,
            'maxBytes': log_config.file_max_bytes,
            'backupCount': log_config.file_backup_count,
            'formatter': 'json'
        }
        # Add file to application logger handlers only
        logging_config_dict['loggers']['lightspun']['handlers'].append('file')
        logging_config_dict['loggers']['load_data']['handlers'].append('file')
    
    # Choose formatter based on log format configuration
    console_formatter = log_config.format if log_config.console_enabled else 'simple'
    
    if 'console' in logging_config_dict['handlers']:
        logging_config_dict['handlers']['console']['formatter'] = console_formatter
    
    # Create logs directory if file logging is enabled
    if log_config.file_enabled:
        os.makedirs(os.path.dirname(log_config.file_path), exist_ok=True)
    
    # Apply configuration
    logging.config.dictConfig(logging_config_dict)
    
    # Log startup message
    logger = logging.getLogger('lightspun.logging')
    logger.info(
        f"Logging initialized - Environment: {environment}, Level: {log_config.level}"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Name of the logger (usually module name)
        
    Returns:
        Logger instance configured according to the logging system
    """
    logger = logging.getLogger(name)
    
    # Add request ID filter if not already present
    if not any(isinstance(f, RequestIDFilter) for f in logger.filters):
        logger.addFilter(RequestIDFilter())
    
    return logger


# Request ID context management for FastAPI
import contextvars

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('request_id')


def set_request_id(request_id: str) -> None:
    """Set request ID in context."""
    request_id_var.set(request_id)


def get_request_id() -> str:
    """Get request ID from context."""
    try:
        return request_id_var.get()
    except LookupError:
        return "no-request-id"


class RequestIDFilter(logging.Filter):
    """Filter to add request ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


# Logging will be initialized by the configuration system
# No automatic initialization to avoid circular imports