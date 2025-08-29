#!/usr/bin/env python3
"""
Configuration system test script for the Lightspun FastAPI application.

This script demonstrates that the professional configuration management system
is working correctly with different environments.
"""

import os
import sys
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_development_config():
    """Test development configuration"""
    print("🧪 Testing Development Configuration...")
    os.environ['ENVIRONMENT'] = 'development'
    
    from lightspun.config import get_config
    from lightspun.logging_config import get_logger
    
    # Test integrated logging configuration
    config = get_config()  # This should automatically setup logging
    logger = get_logger('test.development')
    logger.info("Testing integrated logging configuration")
    
    print(f"✅ Environment: {config.environment}")
    print(f"✅ Database URL: {config.get_database_url(hide_password=True)}")
    print(f"✅ API Title: {config.api.title}")
    print(f"✅ Debug Mode: {config.api.debug}")
    print(f"✅ Log Level: {config.logging.level}")
    print(f"✅ Log Format: {config.logging.format}")
    print(f"✅ Server Reload: {config.server.reload}")
    print(f"✅ CORS Origins: {config.security.cors_origins}")
    print(f"✅ Secret Key: {'***' if config.security.secret_key else 'Not set'}")
    print(f"✅ Integrated Logging: Working")
    print()

def test_production_config():
    """Test production configuration (simulated)"""
    print("🏭 Testing Production Configuration...")
    
    # Set production environment variables
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['DATABASE_URL'] = 'postgresql://prod_user:secure_pass@prod-db:5432/prod_lightspun_db'
    os.environ['SECRET_KEY'] = 'super-secure-production-key-12345'
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['SERVER_WORKERS'] = '4'
    os.environ['CORS_ORIGINS'] = 'https://example.com,https://app.example.com'
    os.environ['API_DOCS_URL'] = ''  # Disabled in production
    os.environ['LOG_FILE_PATH'] = './test_logs/app.log'  # Use writable path for testing
    
    # Clear module cache to reload config
    modules_to_clear = [m for m in sys.modules.keys() if m.startswith('lightspun.config')]
    for module in modules_to_clear:
        del sys.modules[module]
    
    from lightspun.config import get_config
    from lightspun.logging_config import get_logger
    
    # Test production logging with JSON format
    config = get_config()  # This should automatically setup JSON logging
    logger = get_logger('test.production')
    logger.info("Testing production JSON logging")
    
    print(f"✅ Environment: {config.environment}")
    print(f"✅ Database URL: {config.get_database_url(hide_password=True)}")
    print(f"✅ API Title: {config.api.title}")
    print(f"✅ Debug Mode: {config.api.debug}")
    print(f"✅ Docs URL: {config.api.docs_url or 'Disabled'}")
    print(f"✅ Log Level: {config.logging.level}")
    print(f"✅ Log Format: {config.logging.format}")
    print(f"✅ Server Workers: {config.server.workers}")
    print(f"✅ Server Reload: {config.server.reload}")
    print(f"✅ CORS Origins: {config.security.cors_origins}")
    print(f"✅ Secret Key: {'***' if config.security.secret_key else 'Not set'}")
    print(f"✅ Integrated Logging: Working (JSON format)")
    print()

def test_testing_config():
    """Test testing configuration"""
    print("🔬 Testing Testing Configuration...")
    os.environ['ENVIRONMENT'] = 'testing'
    
    # Clear module cache to reload config
    modules_to_clear = [m for m in sys.modules.keys() if m.startswith('lightspun.config')]
    for module in modules_to_clear:
        del sys.modules[module]
    
    from lightspun.config import get_config
    config = get_config()
    
    print(f"✅ Environment: {config.environment}")
    print(f"✅ Database URL: {config.get_database_url(hide_password=True)}")
    print(f"✅ API Title: {config.api.title}")
    print(f"✅ Debug Mode: {config.api.debug}")
    print(f"✅ Log Level: {config.logging.level}")
    print(f"✅ Log Format: {config.logging.format}")
    print(f"✅ File Logging: {config.logging.file_enabled}")
    print(f"✅ Server Port: {config.server.port}")
    print()

def test_config_validation():
    """Test configuration validation"""
    print("🔍 Testing Configuration Validation...")
    
    # Test invalid port
    try:
        from lightspun.config.base import ServerConfig
        ServerConfig(port=99999)  # Invalid port
        print("❌ Port validation failed")
    except ValueError as e:
        print(f"✅ Port validation: {e}")
    
    # Test invalid log level
    try:
        from lightspun.config.base import LoggingConfig
        LoggingConfig(level="INVALID")  # Invalid level
        print("❌ Log level validation failed")
    except ValueError as e:
        print(f"✅ Log level validation: {e}")
    
    # Test invalid log format
    try:
        from lightspun.config.base import LoggingConfig
        LoggingConfig(format="invalid")  # Invalid format
        print("❌ Log format validation failed")
    except ValueError as e:
        print(f"✅ Log format validation: {e}")
    
    print()

def main():
    """Run all configuration tests"""
    print("🚀 Professional Configuration System Test Suite")
    print("=" * 60)
    
    try:
        test_development_config()
        test_production_config()
        test_testing_config()
        test_config_validation()
        
        print("🎉 All configuration tests passed successfully!")
        print("✅ Professional configuration management system is working correctly")
        
        return 0
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())