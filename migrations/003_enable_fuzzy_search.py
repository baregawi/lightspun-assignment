#!/usr/bin/env python3
"""
Database migration: Enable fuzzy search with PostgreSQL extensions

This migration enables advanced fuzzy search capabilities for address autocomplete:
1. pg_trgm extension - Trigram similarity matching for typos and partial matches
2. fuzzystrmatch extension - Soundex and other fuzzy string matching algorithms
3. GIN trigram indexes - High-performance fuzzy search indexes
4. Similarity operators (%) and functions (similarity, soundex)

These enable:
- Typo-tolerant search ("Main Stret" finds "Main Street")  
- Phonetic matching (soundex-based matching for similar-sounding words)
- Fast fuzzy search with proper indexing
- Configurable similarity thresholds

Migration: 003_enable_fuzzy_search
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
logger = get_logger('migration.003')

async def migrate_up():
    """Apply the migration - enable fuzzy search extensions and create indexes"""
    logger.info("Starting migration 003: Enabling fuzzy search capabilities")
    
    try:
        # Connect to database
        await connect_db()
        
        # Enable PostgreSQL extensions
        logger.info("Enabling PostgreSQL extensions...")
        
        # Enable pg_trgm for trigram similarity
        await database.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        logger.info("✅ Enabled extension: pg_trgm (trigram similarity)")
        
        # Enable fuzzystrmatch for soundex and other fuzzy algorithms
        await database.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch")
        logger.info("✅ Enabled extension: fuzzystrmatch (soundex, metaphone, etc.)")
        
        # Create GIN trigram indexes for fast fuzzy search
        logger.info("Creating trigram indexes for fuzzy search...")
        
        # Index for street_name fuzzy search
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_street_name_trgm 
            ON addresses USING GIN (street_name gin_trgm_ops)
        """)
        logger.info("✅ Created trigram index: ix_addresses_street_name_trgm")
        
        # Index for street_number fuzzy search
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_street_number_trgm 
            ON addresses USING GIN (street_number gin_trgm_ops)
        """)
        logger.info("✅ Created trigram index: ix_addresses_street_number_trgm")
        
        # Index for full street_address fuzzy search
        await database.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_addresses_street_address_trgm 
            ON addresses USING GIN (street_address gin_trgm_ops)
        """)
        logger.info("✅ Created trigram index: ix_addresses_street_address_trgm")
        
        # Test the fuzzy search functionality
        logger.info("Testing fuzzy search functionality...")
        
        # Test trigram similarity
        test_result = await database.fetch_one("""
            SELECT 
                COUNT(*) as total_addresses,
                COUNT(CASE WHEN street_name % 'Main Street' THEN 1 END) as main_street_matches,
                AVG(similarity('Main Street', street_name)) as avg_similarity
            FROM addresses
            WHERE street_name IS NOT NULL
        """)
        
        logger.info(f"📊 Fuzzy search test results:")
        logger.info(f"   Total addresses: {test_result['total_addresses']}")
        logger.info(f"   'Main Street' similarity matches: {test_result['main_street_matches']}")
        logger.info(f"   Average similarity to 'Main Street': {test_result['avg_similarity']:.4f}")
        
        # Test soundex functionality
        soundex_test = await database.fetch_one("""
            SELECT COUNT(DISTINCT soundex(street_name)) as unique_soundex_codes
            FROM addresses 
            WHERE street_name IS NOT NULL
        """)
        
        logger.info(f"   Unique soundex codes: {soundex_test['unique_soundex_codes']}")
        
        # Show available fuzzy search functions
        logger.info("📋 Available fuzzy search functions:")
        logger.info("   - similarity(text, text) -> float")
        logger.info("   - text % text -> boolean (similarity operator)")
        logger.info("   - soundex(text) -> text")
        logger.info("   - metaphone(text, int) -> text")
        logger.info("   - dmetaphone(text) -> text")
        logger.info("   - levenshtein(text, text) -> int")
        
        logger.info("✅ Migration 003 completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration 003 failed: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def migrate_down():
    """Rollback the migration - remove fuzzy search indexes and extensions"""
    logger.info("Rolling back migration 003: Removing fuzzy search capabilities")
    
    try:
        # Connect to database
        await connect_db()
        
        # Remove trigram indexes
        logger.info("Removing trigram indexes...")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_street_address_trgm")
        logger.info("✅ Removed index: ix_addresses_street_address_trgm")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_street_number_trgm")
        logger.info("✅ Removed index: ix_addresses_street_number_trgm")
        
        await database.execute("DROP INDEX CONCURRENTLY IF EXISTS ix_addresses_street_name_trgm")
        logger.info("✅ Removed index: ix_addresses_street_name_trgm")
        
        # Note: We don't drop extensions as they might be used by other applications
        logger.info("ℹ️  Extensions (pg_trgm, fuzzystrmatch) left installed for other applications")
        
        logger.info("✅ Migration 003 rollback completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration 003 rollback failed: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def test_fuzzy_search():
    """Test fuzzy search functionality with sample queries"""
    logger.info("Testing fuzzy search functionality...")
    
    try:
        await connect_db()
        
        # Test cases with different types of fuzzy matching
        test_cases = [
            ("Main Street", "Exact match"),
            ("Main Stret", "Typo in street name"),
            ("Oak Avenu", "Typo in street type"),
            ("Lincon Boulevard", "Typo in street name"),
            ("123 Main", "Partial address"),
        ]
        
        for search_term, description in test_cases:
            logger.info(f"\n🔍 Testing: {description}")
            logger.info(f"   Search term: '{search_term}'")
            
            # Test trigram similarity
            trgm_result = await database.fetch_all("""
                SELECT street_address, street_name, city,
                       similarity(street_name, :search_term) as sim_score
                FROM addresses 
                WHERE street_name % :search_term
                ORDER BY similarity(street_name, :search_term) DESC
                LIMIT 3
            """, {"search_term": search_term})
            
            logger.info(f"   Trigram matches: {len(trgm_result)}")
            for row in trgm_result:
                logger.info(f"     {row['street_address']}, {row['city']} (similarity: {row['sim_score']:.3f})")
            
            # Test soundex matching for street names
            if " " in search_term:
                street_part = search_term.split()[-1]  # Get the street name part
                soundex_result = await database.fetch_all("""
                    SELECT street_address, street_name, city
                    FROM addresses 
                    WHERE soundex(street_name) = soundex(:street_part)
                    LIMIT 3
                """, {"street_part": street_part})
                
                logger.info(f"   Soundex matches for '{street_part}': {len(soundex_result)}")
                for row in soundex_result[:2]:  # Show fewer results
                    logger.info(f"     {row['street_address']}, {row['city']}")
        
        logger.info("\n✅ Fuzzy search testing completed")
        
    except Exception as e:
        logger.error(f"❌ Fuzzy search test failed: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def check_extensions():
    """Check installed extensions and available functions"""
    logger.info("Checking fuzzy search extensions and functions...")
    
    try:
        await connect_db()
        
        # Check installed extensions
        extensions = await database.fetch_all("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname IN ('pg_trgm', 'fuzzystrmatch')
        """)
        
        logger.info("📦 Installed extensions:")
        for ext in extensions:
            logger.info(f"   {ext['extname']} v{ext['extversion']}")
        
        # Check trigram indexes
        indexes = await database.fetch_all("""
            SELECT indexname, tablename
            FROM pg_indexes 
            WHERE indexname LIKE '%trgm%'
        """)
        
        logger.info("🔍 Trigram indexes:")
        for idx in indexes:
            logger.info(f"   {idx['tablename']}.{idx['indexname']}")
        
        # Test a simple similarity query
        if extensions:
            sample = await database.fetch_one("""
                SELECT 
                    similarity('Main Street', 'Main Stret') as typo_similarity,
                    similarity('Oak Avenue', 'Oak Ave') as abbrev_similarity
            """)
            
            logger.info("🧪 Sample similarity scores:")
            logger.info(f"   'Main Street' vs 'Main Stret': {sample['typo_similarity']:.3f}")
            logger.info(f"   'Oak Avenue' vs 'Oak Ave': {sample['abbrev_similarity']:.3f}")
        
    except Exception as e:
        logger.error(f"❌ Extension check failed: {e}", exc_info=True)
        raise
    finally:
        await disconnect_db()

async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration: Enable fuzzy search')
    parser.add_argument('--up', action='store_true', help='Apply migration')
    parser.add_argument('--down', action='store_true', help='Rollback migration') 
    parser.add_argument('--test', action='store_true', help='Test fuzzy search functionality')
    parser.add_argument('--check', action='store_true', help='Check extensions and indexes')
    
    args = parser.parse_args()
    
    # Load configuration and initialize database
    config = get_config()
    init_database(config)
    
    if args.up:
        await migrate_up()
    elif args.down:
        await migrate_down()
    elif args.test:
        await test_fuzzy_search()
    elif args.check:
        await check_extensions()
    else:
        print("Usage: python 003_enable_fuzzy_search.py [--up|--down|--test|--check]")
        print("  --up     Apply migration (enable fuzzy search)")
        print("  --down   Rollback migration (remove fuzzy indexes)")
        print("  --test   Test fuzzy search functionality")
        print("  --check  Check extensions and indexes")

if __name__ == "__main__":
    asyncio.run(main())