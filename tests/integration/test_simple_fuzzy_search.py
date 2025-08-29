#!/usr/bin/env python3
"""
Simple test script for fuzzy search functionality
"""

import asyncio
import asyncpg

async def test_basic_fuzzy_search():
    """Test basic fuzzy search capabilities"""
    
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        print("\n🔍 Basic Fuzzy Search Tests")
        print("=" * 50)
        
        # Test 1: Exact match
        print("\n1. Exact Match Test")
        result = await conn.fetch("""
            SELECT street_address, city
            FROM addresses 
            WHERE street_name % 'Main Street'
            ORDER BY similarity(street_name, 'Main Street') DESC
            LIMIT 3
        """)
        print(f"   'Main Street' exact: {len(result)} matches")
        for row in result:
            print(f"     {row['street_address']}, {row['city']}")
        
        # Test 2: Typo tolerance
        print("\n2. Typo Tolerance Test")
        result = await conn.fetch("""
            SELECT street_address, street_name, city,
                   similarity(street_name, 'Main Stret') as sim
            FROM addresses 
            WHERE street_name % 'Main Stret'
            ORDER BY similarity(street_name, 'Main Stret') DESC
            LIMIT 3
        """)
        print(f"   'Main Stret' (typo): {len(result)} matches")
        for row in result:
            print(f"     {row['street_address']} {row['street_name']}, {row['city']} (sim: {row['sim']:.3f})")
        
        # Test 3: Soundex matching
        print("\n3. Soundex Test")
        result = await conn.fetch("""
            SELECT street_address, street_name, city
            FROM addresses 
            WHERE soundex(street_name) = soundex('Johnson Avenue')
            LIMIT 3
        """)
        print(f"   'Johnson Avenue' soundex: {len(result)} matches")
        for row in result:
            print(f"     {row['street_address']} {row['street_name']}, {row['city']}")
        
        # Test 4: Autocomplete scenario
        print("\n4. Autocomplete Test")
        search_terms = ["Ma", "Main", "Main St", "Oak Av", "123 M"]
        
        for term in search_terms:
            result = await conn.fetch("""
                SELECT full_address
                FROM addresses 
                WHERE street_address % $1 OR full_address % $1
                ORDER BY similarity(COALESCE(street_address, ''), $1) DESC
                LIMIT 3
            """, term)
            
            print(f"   '{term}': {len(result)} matches")
            if result:
                print(f"     Top result: {result[0]['full_address']}")
        
        # Test 5: Performance with indexes
        print("\n5. Index Usage Test")
        
        # Check if trigram indexes are being used
        explain_result = await conn.fetch("""
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT street_name
            FROM addresses 
            WHERE street_name % 'Main Street'
            LIMIT 10
        """)
        
        print("   Query plan for trigram search:")
        uses_index = False
        for row in explain_result:
            plan = row[0]
            if 'gin' in plan.lower() or 'index scan' in plan.lower():
                uses_index = True
                print(f"     ✅ {plan}")
            elif 'time' in plan.lower() or 'cost' in plan.lower():
                print(f"     📊 {plan}")
        
        if uses_index:
            print("   ✅ Trigram indexes are being used!")
        else:
            print("   ⚠️  Query not using trigram indexes")
        
        # Test 6: Different similarity thresholds
        print("\n6. Similarity Threshold Test")
        
        test_query = "Main Stret"  # Intentional typo
        for threshold in [0.2, 0.3, 0.5, 0.7]:
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM addresses 
                WHERE similarity(street_name, $1) >= $2
            """, test_query, threshold)
            print(f"   Threshold {threshold}: {count} matches for '{test_query}'")
        
        # Test 7: Combined fuzzy + exact search
        print("\n7. Combined Search Test")
        
        search_query = "Oak Ave"
        
        # Traditional approach
        exact_count = await conn.fetchval("""
            SELECT COUNT(*) FROM addresses 
            WHERE street_name ILIKE $1 OR street_address ILIKE $1
        """, f"%{search_query}%")
        
        # Fuzzy approach
        fuzzy_count = await conn.fetchval("""
            SELECT COUNT(*) FROM addresses 
            WHERE street_name % $1 OR street_address % $1
        """, search_query)
        
        print(f"   '{search_query}' exact/ILIKE: {exact_count} matches")
        print(f"   '{search_query}' fuzzy: {fuzzy_count} matches")
        
        print("\n🎉 Basic fuzzy search tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()
        print("✅ Disconnected from database")

def main():
    """Run basic fuzzy search tests"""
    print("🚀 Simple Fuzzy Search Test")
    print("=" * 50)
    
    try:
        asyncio.run(test_basic_fuzzy_search())
        return 0
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())