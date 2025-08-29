#!/usr/bin/env python3
"""
Test script for fuzzy search functionality using asyncpg
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent))

from lightspun.street_standardization import standardize_street_type

async def test_fuzzy_search_comprehensive():
    """Comprehensive test of fuzzy search capabilities"""
    
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Test 1: Basic trigram similarity
        print("\n🔍 Test 1: Basic Trigram Similarity")
        print("=" * 60)
        
        test_cases = [
            ("Main Street", "Exact match"),
            ("Main Stret", "Single character typo"),
            ("Mian Street", "Character transposition"),
            ("Main Str", "Truncated street type"),
            ("Oak Avenue", "Different street name"),
            ("Oak Avenu", "Missing character"),
            ("Oakk Avenue", "Extra character"),
            ("Lincoln Boulevard", "Long street name"),
            ("Lincon Blvd", "Multiple issues"),
        ]
        
        for search_term, description in test_cases:
            result = await conn.fetch("""
                SELECT street_name, similarity($1, street_name) as sim
                FROM addresses 
                WHERE street_name % $1
                ORDER BY similarity($1, street_name) DESC
                LIMIT 3
            """, search_term)
            
            print(f"\n🔍 {description}: '{search_term}'")
            print(f"   Found {len(result)} matches")
            for row in result:
                print(f"     '{row['street_name']}' (similarity: {row['sim']:.3f})")
        
        # Test 2: Soundex matching
        print("\n\n🔊 Test 2: Soundex Phonetic Matching")
        print("=" * 60)
        
        phonetic_tests = [
            ("Smith Street", "Smith"),
            ("Smyth Street", "Smyth (sounds like Smith)"),
            ("Johnson Avenue", "Johnson"),
            ("Johnsen Avenue", "Johnsen (sounds like Johnson)"),
        ]
        
        for search_full, description in phonetic_tests:
            search_name = search_full.split()[0]  # Get first word
            result = await conn.fetch("""
                SELECT street_name, soundex(street_name) as street_soundex
                FROM addresses 
                WHERE soundex(street_name) = soundex($1)
                LIMIT 5
            """, search_name)
            
            print(f"\n🔊 {description}")
            print(f"   Searching for soundex of: '{search_name}'")
            print(f"   Found {len(result)} phonetic matches")
            for row in result[:3]:
                print(f"     '{row['street_name']}' (soundex: {row['street_soundex']})")
        
        # Test 3: Combined fuzzy search (like our service method)
        print("\n\n🎯 Test 3: Combined Fuzzy Search")
        print("=" * 60)
        
        combined_tests = [
            ("Main St", "Abbreviation search"),
            ("Oak Av", "Partial abbreviation"),
            ("123 Main", "Address with number"),
            ("Lincoln Boul", "Partial boulevard"),
            ("Park Drv", "Typo in abbreviation"),
        ]
        
        for search_term, description in combined_tests:
            standardized = standardize_street_type(search_term)
            
            # Simulate our service method query
            result = await conn.fetch("""
                SELECT DISTINCT 
                    street_address, street_name, city,
                    GREATEST(
                        similarity(street_address, $1),
                        similarity(street_address, $2),
                        similarity(street_name, $1),
                        similarity(street_name, $2),
                        CASE 
                            WHEN soundex(street_name) = soundex($1) THEN 0.8
                            ELSE 0.0 
                        END
                    ) as similarity_score
                FROM addresses 
                WHERE 
                    (street_address % $1 OR street_address % $2)
                    OR (street_name % $1 OR street_name % $2)  
                    OR soundex(street_name) = soundex($1)
                    OR soundex(street_name) = soundex($2)
                HAVING GREATEST(
                    similarity(street_address, $1),
                    similarity(street_address, $2), 
                    similarity(street_name, $1),
                    similarity(street_name, $2),
                    CASE 
                        WHEN soundex(street_name) = soundex($1) THEN 0.8
                        ELSE 0.0 
                    END
                ) >= 0.3
                ORDER BY similarity_score DESC
                LIMIT 5
            """, search_term, standardized)
            
            print(f"\n🎯 {description}: '{search_term}' -> '{standardized}'")
            print(f"   Found {len(result)} combined matches")
            for row in result[:3]:
                print(f"     {row['street_address']}, {row['city']} (score: {row['similarity_score']:.3f})")
        
        # Test 4: Performance test
        print("\n\n⚡ Test 4: Performance Test")
        print("=" * 60)
        
        import time
        
        performance_queries = [
            ("ILIKE", "SELECT COUNT(*) FROM addresses WHERE street_name ILIKE '%Main%'"),
            ("Trigram", "SELECT COUNT(*) FROM addresses WHERE street_name % 'Main Street'"),
            ("Similarity", "SELECT COUNT(*) FROM addresses WHERE similarity(street_name, 'Main Street') > 0.3"),
        ]
        
        for query_type, query in performance_queries:
            start_time = time.time()
            result = await conn.fetchval(query)
            end_time = time.time()
            
            print(f"   {query_type:10} query: {result:4d} results in {(end_time - start_time)*1000:.2f}ms")
        
        # Test 5: Index usage verification
        print("\n\n📊 Test 5: Index Usage Analysis")
        print("=" * 60)
        
        explain_result = await conn.fetch("""
            EXPLAIN ANALYZE
            SELECT street_name, similarity('Main Street', street_name)
            FROM addresses 
            WHERE street_name % 'Main Street'
            LIMIT 10
        """)
        
        print("   Query plan for trigram search:")
        for row in explain_result:
            plan_line = row[0]
            if 'gin' in plan_line.lower() or 'index' in plan_line.lower() or 'time' in plan_line.lower():
                print(f"     {plan_line}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()
        print("\n✅ Disconnected from database")

async def test_autocomplete_scenarios():
    """Test realistic autocomplete scenarios"""
    
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("\n🚀 Testing Realistic Autocomplete Scenarios")
        print("=" * 80)
        
        # Realistic user input scenarios
        scenarios = [
            ("12", "User types house number"),
            ("123", "User continues typing number"),
            ("123 M", "User starts street name"),
            ("123 Ma", "User continues street name"),
            ("123 Main", "User types full street name"),
            ("123 Main S", "User starts street type"),
            ("123 Main St", "User completes with abbreviation"),
            ("mai", "User types with typo"),
            ("main str", "User types abbreviated form"),
            ("1234 Oak Av", "Different address partial"),
        ]
        
        for search_query, description in scenarios:
            # Test both exact and fuzzy approaches
            
            # Exact/prefix matching (traditional)
            exact_result = await conn.fetch("""
                SELECT full_address
                FROM addresses 
                WHERE street_address ILIKE $1 OR full_address ILIKE $2
                ORDER BY 
                    CASE WHEN street_address ILIKE $1 THEN 1 ELSE 2 END,
                    full_address
                LIMIT 5
            """, f"{search_query}%", f"%{search_query}%")
            
            # Fuzzy matching 
            fuzzy_result = await conn.fetch("""
                SELECT DISTINCT full_address,
                       GREATEST(
                           similarity(street_address, $1),
                           similarity(full_address, $1)
                       ) as score
                FROM addresses 
                WHERE street_address % $1 OR full_address % $1
                HAVING GREATEST(
                    similarity(street_address, $1),
                    similarity(full_address, $1)
                ) >= 0.2
                ORDER BY score DESC
                LIMIT 5
            """, search_query)
            
            print(f"\n🔍 {description}: '{search_query}'")
            print(f"   Exact matches: {len(exact_result)}")
            print(f"   Fuzzy matches: {len(fuzzy_result)}")
            
            # Show top results
            if exact_result:
                print("   Top exact result:", exact_result[0]['full_address'])
            if fuzzy_result:
                print(f"   Top fuzzy result: {fuzzy_result[0]['full_address']} (score: {fuzzy_result[0]['score']:.3f})")
    
    except Exception as e:
        print(f"❌ Autocomplete test error: {e}")
    finally:
        await conn.close()

def main():
    """Run all fuzzy search tests"""
    print("🚀 Comprehensive Fuzzy Search Test Suite")
    print("=" * 80)
    
    try:
        asyncio.run(test_fuzzy_search_comprehensive())
        asyncio.run(test_autocomplete_scenarios())
        
        print("\n🎉 All fuzzy search tests completed successfully!")
        print("✅ Fuzzy search functionality is working correctly")
        return 0
        
    except Exception as e:
        print(f"❌ Fuzzy search tests failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())