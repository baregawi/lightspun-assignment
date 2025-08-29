"""
Professional configuration management for the Lightspun FastAPI application.

This package provides centralized configuration management with:
- Environment-specific configurations (development, production, testing)
- Secure handling of sensitive data via environment variables
- Configuration validation using Pydantic
- Type-safe configuration access
"""

from .base import get_config, Config

__all__ = ["get_config", "Config"]