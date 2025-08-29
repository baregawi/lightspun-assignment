#!/usr/bin/env python3
"""
Script to update address table with parsed street components
This script connects directly to PostgreSQL and updates the street components
"""

import asyncio
import asyncpg
import re
import os

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

async def update_address_components():
    """Update all addresses with parsed street components"""
    
    # Connect to PostgreSQL
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Get all addresses that need parsing
        rows = await conn.fetch("""
            SELECT id, street_address 
            FROM addresses 
            WHERE street_name IS NULL
        """)
        
        print(f"📊 Found {len(rows)} addresses to parse")
        
        # Process each address
        processed = 0
        for row in rows:
            street_number, street_name, unit = parse_street_address(row['street_address'])
            
            await conn.execute("""
                UPDATE addresses 
                SET street_number = $1,
                    street_name = $2,
                    unit = $3
                WHERE id = $4
            """, street_number, street_name, unit, row['id'])
            
            processed += 1
            
            if processed % 100 == 0:
                print(f"  Processed {processed}/{len(rows)} addresses")
        
        print(f"✅ Processed {processed} addresses")
        
        # Set street_name as NOT NULL after populating data
        await conn.execute("ALTER TABLE addresses ALTER COLUMN street_name SET NOT NULL")
        print("✅ Set street_name as NOT NULL")
        
        # Create indexes for new fields
        await conn.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_street_name 
            ON addresses (street_name)
        """)
        print("✅ Created index: ix_addresses_street_name")
        
        await conn.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_street_number 
            ON addresses (street_number)
        """)
        print("✅ Created index: ix_addresses_street_number")
        
        # Show sample results
        sample_rows = await conn.fetch("""
            SELECT street_address, street_number, street_name, unit
            FROM addresses 
            LIMIT 10
        """)
        
        print("\n📋 Sample parsed addresses:")
        for row in sample_rows:
            print(f"  '{row['street_address']}' -> #{row['street_number']} | {row['street_name']} | {row['unit']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        try:
            await conn.close()
            print("✅ Disconnected from database")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(update_address_components())