#!/usr/bin/env python3
"""
Database migration: Add performance indexes

This migration adds database indexes to improve query performance for:
1. Municipality lookups by state_id
2. Municipality lookups by name  
3. Address lookups by city
4. Address lookups by state_code
5. Address lookups by city+state combination
6. Address autocomplete by street_address

Migration: 001_add_performance_indexes
Created: 2025-08-29
"""

import asyncio
import sys
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent.parent))

from lightspun.config import get_config
from lightspun.logging_config import get_logger
from lightspun.database import init_database, database, connect_db, disconnect_db

# Initialize logger
logger = get_logger('migration.001')

async def migrate_up():
    """Apply the migration - add performance indexes"""
    logger.info("Starting migration 001: Adding performance indexes")
    
    try:
        # Connect to database
        await connect_db()
        
        # Create indexes for municipalities table
        logger.info("Adding indexes for municipalities table...")
        
        # Index for state_id lookups (if not exists)
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_municipalities_state_id 
            ON municipalities (state_id)
        """)
        logger.info("✅ Added index: ix_municipalities_state_id")
        
        # Index for municipality name searches
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_municipalities_name 
            ON municipalities (name)
        """)
        logger.info("✅ Added index: ix_municipalities_name")
        
        # Create indexes for addresses table
        logger.info("Adding indexes for addresses table...")
        
        # Index for city lookups
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_city 
            ON addresses (city)
        """)
        logger.info("✅ Added index: ix_addresses_city")
        
        # Index for state_code lookups
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_state_code 
            ON addresses (state_code)
        """)
        logger.info("✅ Added index: ix_addresses_state_code")
        
        # Composite index for city+state searches
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_city_state 
            ON addresses (city, state_code)
        """)
        logger.info("✅ Added index: ix_addresses_city_state")
        
        # Index for address autocomplete (street_address searches)
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_street_address 
            ON addresses (street_address)
        """)
        logger.info("✅ Added index: ix_addresses_street_address")
        
        logger.info("✅ Migration 001 completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration 001 failed: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def migrate_down():
    """Rollback the migration - remove performance indexes"""
    logger.info("Rolling back migration 001: Removing performance indexes")
    
    try:
        # Connect to database
        await connect_db()
        
        # Remove indexes for addresses table
        logger.info("Removing indexes from addresses table...")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_street_address")
        logger.info("✅ Removed index: ix_addresses_street_address")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_city_state")
        logger.info("✅ Removed index: ix_addresses_city_state")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_state_code")
        logger.info("✅ Removed index: ix_addresses_state_code")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_city")
        logger.info("✅ Removed index: ix_addresses_city")
        
        # Remove indexes for municipalities table
        logger.info("Removing indexes from municipalities table...")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_municipalities_name")
        logger.info("✅ Removed index: ix_municipalities_name")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_municipalities_state_id")
        logger.info("✅ Removed index: ix_municipalities_state_id")
        
        logger.info("✅ Migration 001 rollback completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration 001 rollback failed: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def check_indexes():
    """Check which indexes currently exist"""
    logger.info("Checking existing indexes...")
    
    try:
        await connect_db()
        
        # Check indexes on municipalities table
        result = await database.fetch_all("""
            SELECT indexname, tablename, indexdef 
            FROM pg_indexes 
            WHERE tablename IN ('municipalities', 'addresses')
            ORDER BY tablename, indexname
        """)
        
        logger.info("Current indexes:")
        for row in result:
            logger.info(f"  {row['tablename']}.{row['indexname']}: {row['indexdef']}")
            
    except Exception as e:
        logger.error(f"❌ Failed to check indexes: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration: Add performance indexes')
    parser.add_argument('--up', action='store_true', help='Apply migration')
    parser.add_argument('--down', action='store_true', help='Rollback migration')
    parser.add_argument('--check', action='store_true', help='Check existing indexes')
    
    args = parser.parse_args()
    
    # Load configuration and initialize database
    config = get_config()
    init_database(config)
    
    if args.up:
        await migrate_up()
    elif args.down:
        await migrate_down()
    elif args.check:
        await check_indexes()
    else:
        print("Usage: python 001_add_performance_indexes.py [--up|--down|--check]")
        print("  --up    Apply migration (add indexes)")
        print("  --down  Rollback migration (remove indexes)")
        print("  --check Check existing indexes")

if __name__ == "__main__":
    asyncio.run(main())