#!/usr/bin/env python3
"""
Script to standardize street types in all existing addresses.

This script will:
1. Get all street types currently in the database
2. Show statistics of what needs to be standardized
3. Update all addresses with standardized street types
4. Update both street_name and street_address fields
5. Update full_address field to reflect changes
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent))

from lightspun.utils.street_standardization import (
    standardize_street_type,
    get_street_type_statistics,
    rebuild_street_address,
    STREET_TYPE_MAPPING
)

async def analyze_current_street_types():
    """Analyze current street types in the database"""
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Get all street names
        rows = await conn.fetch("SELECT street_name FROM addresses WHERE street_name IS NOT NULL")
        street_names = [row['street_name'] for row in rows]
        
        print(f"📊 Total addresses with street names: {len(street_names)}")
        
        # Analyze street types
        stats = get_street_type_statistics(street_names)
        
        print("\n📋 Current street type distribution:")
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        
        standardizable = 0
        for street_type, count in sorted_stats:
            needs_standardization = any(
                variant.lower() != target.lower() 
                for variant, target in STREET_TYPE_MAPPING.items() 
                if target == street_type
            )
            marker = "🔄" if needs_standardization else "✅"
            print(f"  {marker} {street_type}: {count}")
            if needs_standardization:
                standardizable += count
        
        print(f"\n📈 Addresses that will be standardized: {standardizable}")
        print(f"📈 Addresses already standardized: {len(street_names) - standardizable}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()

async def standardize_database_addresses():
    """Standardize all addresses in the database"""
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Get all addresses that need standardization
        rows = await conn.fetch("""
            SELECT id, street_number, street_name, unit, street_address, city, state_code
            FROM addresses 
            WHERE street_name IS NOT NULL
        """)
        
        print(f"📊 Found {len(rows)} addresses to process")
        
        processed = 0
        standardized = 0
        
        for row in rows:
            original_street_name = row['street_name']
            standardized_street_name = standardize_street_type(original_street_name)
            
            # Only update if standardization changed something
            if original_street_name != standardized_street_name:
                # Rebuild street address with standardized name
                new_street_address = rebuild_street_address(
                    row['street_number'], 
                    standardized_street_name, 
                    row['unit']
                )
                
                new_full_address = f"{new_street_address}, {row['city']}, {row['state_code']}"
                
                # Update the database
                await conn.execute("""
                    UPDATE addresses 
                    SET street_name = $1,
                        street_address = $2,
                        full_address = $3
                    WHERE id = $4
                """, standardized_street_name, new_street_address, new_full_address, row['id'])
                
                standardized += 1
            
            processed += 1
            
            if processed % 100 == 0:
                print(f"  Processed {processed}/{len(rows)} addresses ({standardized} standardized)")
        
        print(f"✅ Processing complete!")
        print(f"📊 Total processed: {processed}")
        print(f"🔄 Total standardized: {standardized}")
        print(f"✅ Already standard: {processed - standardized}")
        
        # Show some examples of standardized addresses
        if standardized > 0:
            print("\n📋 Sample standardized addresses:")
            sample_rows = await conn.fetch("""
                SELECT street_address, street_name, city
                FROM addresses 
                ORDER BY RANDOM()
                LIMIT 10
            """)
            
            for row in sample_rows:
                print(f"  {row['street_address']}, {row['city']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()

async def verify_standardization():
    """Verify that standardization was successful"""
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Get all street names again
        rows = await conn.fetch("SELECT street_name FROM addresses WHERE street_name IS NOT NULL")
        street_names = [row['street_name'] for row in rows]
        
        # Analyze street types after standardization
        stats = get_street_type_statistics(street_names)
        
        print("\n📋 Street types after standardization:")
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        
        non_standard = 0
        for street_type, count in sorted_stats[:20]:  # Show top 20
            # Check if this type appears as a key (needs standardization) vs target (already standard)
            is_target = street_type in set(STREET_TYPE_MAPPING.values())
            is_variant = street_type in STREET_TYPE_MAPPING.keys() and STREET_TYPE_MAPPING[street_type] != street_type
            
            if is_variant:
                marker = "❌"
                non_standard += count
            elif is_target:
                marker = "✅"
            else:
                marker = "❓"
            
            print(f"  {marker} {street_type}: {count}")
        
        if non_standard == 0:
            print(f"\n🎉 All {len(street_names)} addresses have standardized street types!")
        else:
            print(f"\n⚠️  {non_standard} addresses still need standardization")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Standardize street types in address database')
    parser.add_argument('--analyze', action='store_true', help='Analyze current street types')
    parser.add_argument('--standardize', action='store_true', help='Standardize all addresses')
    parser.add_argument('--verify', action='store_true', help='Verify standardization results')
    parser.add_argument('--all', action='store_true', help='Run analysis, standardization, and verification')
    
    args = parser.parse_args()
    
    if args.all:
        print("🚀 Running complete street type standardization process...")
        print("\n" + "="*60)
        print("STEP 1: ANALYZING CURRENT STREET TYPES")
        print("="*60)
        await analyze_current_street_types()
        
        print("\n" + "="*60)
        print("STEP 2: STANDARDIZING ADDRESSES")
        print("="*60)
        await standardize_database_addresses()
        
        print("\n" + "="*60)
        print("STEP 3: VERIFYING RESULTS")
        print("="*60)
        await verify_standardization()
        
    elif args.analyze:
        await analyze_current_street_types()
    elif args.standardize:
        await standardize_database_addresses()
    elif args.verify:
        await verify_standardization()
    else:
        print("Usage: python standardize_street_types.py [--analyze|--standardize|--verify|--all]")
        print("  --analyze      Analyze current street types")
        print("  --standardize  Standardize all addresses")  
        print("  --verify       Verify standardization results")
        print("  --all          Run complete process")

if __name__ == "__main__":
    asyncio.run(main())