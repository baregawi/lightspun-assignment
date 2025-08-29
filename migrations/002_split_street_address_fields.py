#!/usr/bin/env python3
"""
Database migration: Split street address into components

This migration adds separate fields for street address components:
1. street_number - The house/building number (e.g., "123", "456A")
2. street_name - The street name (e.g., "Main Street", "Oak Avenue") 
3. unit - The unit/apartment/suite (e.g., "Apt 2B", "Suite 100")

The original street_address field is kept for backward compatibility.

Migration: 002_split_street_address_fields
Created: 2025-08-29
"""

import asyncio
import sys
import re
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent.parent))

from lightspun.config import get_config
from lightspun.logging_config import get_logger
from lightspun.database import init_database, database, connect_db, disconnect_db

# Initialize logger
logger = get_logger('migration.002')

def parse_street_address(street_address: str) -> tuple:
    """
    Parse a street address into components (street_number, street_name, unit).
    
    Examples:
    - "123 Main Street" -> ("123", "Main Street", None)
    - "456A Oak Avenue Apt 2B" -> ("456A", "Oak Avenue", "Apt 2B")
    - "789 First Street Suite 100" -> ("789", "First Street", "Suite 100")
    """
    if not street_address:
        return (None, street_address or "", None)
    
    # Pattern to match: [number] [street name] [optional unit]
    # Unit patterns: Apt, Suite, Unit, #, etc.
    unit_pattern = r'\s+(apt|apartment|suite|unit|#|ste|bldg|building)\s*\.?\s*(.+)$'
    
    # First, extract unit if present (case insensitive)
    unit_match = re.search(unit_pattern, street_address, re.IGNORECASE)
    unit = None
    base_address = street_address
    
    if unit_match:
        unit = f"{unit_match.group(1).title()} {unit_match.group(2)}"
        base_address = street_address[:unit_match.start()].strip()
    
    # Now extract street number from the remaining address
    number_pattern = r'^(\d+[A-Za-z]?)\s+(.+)$'
    number_match = re.match(number_pattern, base_address.strip())
    
    if number_match:
        street_number = number_match.group(1)
        street_name = number_match.group(2).strip()
    else:
        # No number found, treat entire base address as street name
        street_number = None
        street_name = base_address.strip()
    
    return (street_number, street_name, unit)

async def migrate_up():
    """Apply the migration - add street address component fields"""
    logger.info("Starting migration 002: Splitting street address fields")
    
    try:
        # Connect to database
        await connect_db()
        
        # Add new columns to addresses table
        logger.info("Adding new columns to addresses table...")
        
        # Add street_number column
        await database.execute("""
            ALTER TABLE addresses 
            ADD COLUMN IF NOT EXISTS street_number VARCHAR(10)
        """)
        logger.info("✅ Added column: street_number")
        
        # Add street_name column
        await database.execute("""
            ALTER TABLE addresses 
            ADD COLUMN IF NOT EXISTS street_name VARCHAR(150)
        """)
        logger.info("✅ Added column: street_name")
        
        # Add unit column
        await database.execute("""
            ALTER TABLE addresses 
            ADD COLUMN IF NOT EXISTS unit VARCHAR(20)
        """)
        logger.info("✅ Added column: unit")
        
        # Populate the new fields by parsing existing street_address data
        logger.info("Parsing existing street addresses...")
        
        # Get all existing addresses
        rows = await database.fetch_all("""
            SELECT id, street_address 
            FROM addresses 
            WHERE street_number IS NULL
        """)
        
        logger.info(f"Found {len(rows)} addresses to parse")
        
        # Process each address
        for row in rows:
            street_number, street_name, unit = parse_street_address(row['street_address'])
            
            await database.execute("""
                UPDATE addresses 
                SET street_number = :street_number,
                    street_name = :street_name,
                    unit = :unit
                WHERE id = :id
            """, {
                "street_number": street_number,
                "street_name": street_name,
                "unit": unit,
                "id": row['id']
            })
        
        logger.info("✅ Parsed and populated street address components")
        
        # Make street_name NOT NULL after populating data
        await database.execute("""
            ALTER TABLE addresses 
            ALTER COLUMN street_name SET NOT NULL
        """)
        logger.info("✅ Set street_name as NOT NULL")
        
        # Create indexes for new fields
        logger.info("Creating indexes for new fields...")
        
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_street_name 
            ON addresses (street_name)
        """)
        logger.info("✅ Added index: ix_addresses_street_name")
        
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_street_number 
            ON addresses (street_number)
        """)
        logger.info("✅ Added index: ix_addresses_street_number")
        
        logger.info("✅ Migration 002 completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration 002 failed: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def migrate_down():
    """Rollback the migration - remove street address component fields"""
    logger.info("Rolling back migration 002: Removing street address component fields")
    
    try:
        # Connect to database
        await connect_db()
        
        # Remove indexes
        logger.info("Removing indexes...")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_street_number")
        logger.info("✅ Removed index: ix_addresses_street_number")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_street_name")
        logger.info("✅ Removed index: ix_addresses_street_name")
        
        # Remove columns
        logger.info("Removing columns from addresses table...")
        
        await database.execute("ALTER TABLE addresses DROP COLUMN IF EXISTS unit")
        logger.info("✅ Removed column: unit")
        
        await database.execute("ALTER TABLE addresses DROP COLUMN IF EXISTS street_name")
        logger.info("✅ Removed column: street_name")
        
        await database.execute("ALTER TABLE addresses DROP COLUMN IF EXISTS street_number")
        logger.info("✅ Removed column: street_number")
        
        logger.info("✅ Migration 002 rollback completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration 002 rollback failed: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def check_migration():
    """Check the current state of the migration"""
    logger.info("Checking migration 002 status...")
    
    try:
        await connect_db()
        
        # Check if columns exist
        result = await database.fetch_all("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'addresses' 
              AND column_name IN ('street_number', 'street_name', 'unit', 'street_address')
            ORDER BY column_name
        """)
        
        logger.info("Address table columns:")
        for row in result:
            nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
            logger.info(f"  {row['column_name']}: {row['data_type']} {nullable}")
        
        # Check indexes
        result = await database.fetch_all("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'addresses' 
              AND indexname LIKE '%street%'
            ORDER BY indexname
        """)
        
        logger.info("Street-related indexes:")
        for row in result:
            logger.info(f"  {row['indexname']}")
        
        # Sample data
        result = await database.fetch_all("""
            SELECT street_address, street_number, street_name, unit
            FROM addresses 
            LIMIT 5
        """)
        
        logger.info("Sample address data:")
        for row in result:
            logger.info(f"  Original: {row['street_address']}")
            logger.info(f"  Parsed: #{row['street_number']} | {row['street_name']} | {row['unit']}")
            logger.info("")
            
    except Exception as e:
        logger.error(f"❌ Failed to check migration status: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration: Split street address fields')
    parser.add_argument('--up', action='store_true', help='Apply migration')
    parser.add_argument('--down', action='store_true', help='Rollback migration')
    parser.add_argument('--check', action='store_true', help='Check migration status')
    
    args = parser.parse_args()
    
    # Load configuration and initialize database
    config = get_config()
    init_database(config)
    
    if args.up:
        await migrate_up()
    elif args.down:
        await migrate_down()
    elif args.check:
        await check_migration()
    else:
        print("Usage: python 002_split_street_address_fields.py [--up|--down|--check]")
        print("  --up    Apply migration (split street address fields)")
        print("  --down  Rollback migration (remove street address component fields)")
        print("  --check Check migration status")

if __name__ == "__main__":
    asyncio.run(main())