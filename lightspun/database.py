import os
from databases import Database
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Logger will be initialized when needed
db_logger = None

# Global variables to be initialized by init_database
database = None
engine = None
SessionLocal = None

Base = declarative_base()
metadata = MetaData()


def init_database(config):
    """Initialize database connections with configuration"""
    global database, engine, SessionLocal, db_logger
    
    # Initialize logger now that configuration is available
    if db_logger is None:
        from .logging_config import get_logger
        db_logger = get_logger('lightspun.database')
    
    db_config = config.database
    db_logger.info(f"Initializing database with URL: {config.get_database_url(hide_password=True)}")
    
    # Create database connection
    database = Database(db_config.url)
    
    # Create SQLAlchemy engine with connection pooling
    engine = create_engine(
        db_config.url,
        pool_size=db_config.pool_size,
        max_overflow=db_config.max_overflow,
        pool_timeout=db_config.pool_timeout,
        pool_recycle=db_config.pool_recycle,
        echo=db_config.echo
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db_logger.info("Database initialization completed")


async def connect_db():
    """Connect to the database"""
    global db_logger
    if database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    # Ensure logger is available
    if db_logger is None:
        from .logging_config import get_logger
        db_logger = get_logger('lightspun.database')
    
    try:
        db_logger.info("Connecting to database...")
        await database.connect()
        db_logger.info("Successfully connected to database")
    except Exception as e:
        db_logger.error(f"Failed to connect to database: {e}", exc_info=True)
        raise


async def disconnect_db():
    """Disconnect from the database"""
    global db_logger
    if database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    # Ensure logger is available
    if db_logger is None:
        from .logging_config import get_logger
        db_logger = get_logger('lightspun.database')
    
    try:
        db_logger.info("Disconnecting from database...")
        await database.disconnect()
        db_logger.info("Successfully disconnected from database")
    except Exception as e:
        db_logger.error(f"Failed to disconnect from database: {e}", exc_info=True)
        raise