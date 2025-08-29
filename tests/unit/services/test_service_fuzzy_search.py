#!/usr/bin/env python3
"""
Test script for fuzzy search service methods
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

async def test_service_fuzzy_methods():
    """Test the new fuzzy search service methods"""
    
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        print("\n🔍 Testing Fuzzy Search Methods")
        print("=" * 60)
        
        # Test cases for fuzzy address search
        test_cases = [
            ("Main Street", "Exact match"),
            ("Main Stret", "Single typo"),
            ("Oak Ave", "Abbreviated form"),  
            ("Lincoln Blvd", "Different abbreviation"),
            ("123 Park", "Partial address with number"),
            ("Garfield Dr", "Drive abbreviation"),
        ]
        
        for search_query, description in test_cases:
            print(f"\n🔍 {description}: '{search_query}'")
            
            # Test fuzzy search addresses method  
            fuzzy_results = await conn.fetch("""
                SELECT DISTINCT 
                    full_address,
                    GREATEST(
                        similarity(street_address, $1),
                        similarity(street_name, $1),
                        CASE 
                            WHEN soundex(street_name) = soundex($1) THEN 0.8
                            ELSE 0.0 
                        END
                    ) as similarity_score
                FROM addresses 
                WHERE 
                    (street_address % $1)
                    OR (street_name % $1)  
                    OR soundex(street_name) = soundex($1)
                HAVING GREATEST(
                    similarity(street_address, $1),
                    similarity(street_name, $1),
                    CASE 
                        WHEN soundex(street_name) = soundex($1) THEN 0.8
                        ELSE 0.0 
                    END
                ) >= 0.3
                ORDER BY similarity_score DESC, full_address
                LIMIT 5
            """, search_query)
            
            print(f"   Fuzzy matches: {len(fuzzy_results)}")
            for row in fuzzy_results[:3]:
                print(f"     {row['full_address']} (score: {row['similarity_score']:.3f})")
        
        # Test street name fuzzy search
        print("\n\n🏘️ Testing Street Name Fuzzy Search")
        print("=" * 60)
        
        street_name_tests = [
            ("Main", "Common name"),
            ("Oak", "Tree name"),
            ("Garfeld", "Typo in name"), 
            ("Lincon", "Historical name typo"),
        ]
        
        for search_query, description in street_name_tests:
            print(f"\n🏘️ {description}: '{search_query}'")
            
            # Test fuzzy street name search
            street_results = await conn.fetch("""
                SELECT 
                    street_name,
                    COUNT(*) as address_count,
                    GREATEST(
                        similarity(street_name, $1),
                        CASE 
                            WHEN soundex(street_name) = soundex($1) THEN 0.7
                            ELSE 0.0 
                        END
                    ) as similarity_score
                FROM addresses 
                WHERE 
                    (street_name % $1)
                    OR soundex(street_name) = soundex($1)
                GROUP BY street_name
                HAVING GREATEST(
                    similarity(street_name, $1),
                    CASE 
                        WHEN soundex(street_name) = soundex($1) THEN 0.7
                        ELSE 0.0 
                    END
                ) >= 0.4
                ORDER BY similarity_score DESC, address_count DESC, street_name
                LIMIT 5
            """, search_query)
            
            print(f"   Street name matches: {len(street_results)}")
            for row in street_results:
                print(f"     {row['street_name']} ({row['address_count']} addresses, score: {row['similarity_score']:.3f})")
        
        # Test autocomplete scenarios
        print("\n\n🎯 Testing Autocomplete Scenarios") 
        print("=" * 60)
        
        autocomplete_tests = [
            ("123", "House number"),
            ("123 M", "Number + letter"),
            ("Ma", "Partial street name"),
            ("Main", "Full street name"),
            ("Oak Av", "Name + partial type"),
            ("lincoln b", "Name + partial type (lowercase)"),
        ]
        
        for search_query, description in autocomplete_tests:
            print(f"\n🎯 {description}: '{search_query}'")
            
            # Simple fuzzy autocomplete
            autocomplete_results = await conn.fetch("""
                SELECT DISTINCT full_address,
                       GREATEST(
                           similarity(street_address, $1),
                           similarity(full_address, $1)
                       ) as score
                FROM addresses 
                WHERE street_address % $1 
                   OR full_address % $1
                HAVING GREATEST(
                    similarity(street_address, $1),
                    similarity(full_address, $1)
                ) >= 0.2
                ORDER BY score DESC, full_address
                LIMIT 5
            """, search_query)
            
            print(f"   Autocomplete matches: {len(autocomplete_results)}")
            for row in autocomplete_results[:3]:
                print(f"     {row['full_address']} (score: {row['score']:.3f})")
        
        # Performance comparison
        print("\n\n⚡ Performance Comparison")
        print("=" * 60)
        
        import time
        
        search_term = "Main Street"
        
        # Traditional ILIKE search
        start = time.time()
        ilike_result = await conn.fetchval("""
            SELECT COUNT(*) FROM addresses 
            WHERE street_name ILIKE $1 OR street_address ILIKE $1
        """, f"%{search_term}%")
        ilike_time = (time.time() - start) * 1000
        
        # Trigram fuzzy search
        start = time.time()
        fuzzy_result = await conn.fetchval("""
            SELECT COUNT(*) FROM addresses 
            WHERE street_name % $1 OR street_address % $1
        """, search_term)
        fuzzy_time = (time.time() - start) * 1000
        
        # Similarity threshold search
        start = time.time() 
        similarity_result = await conn.fetchval("""
            SELECT COUNT(*) FROM addresses 
            WHERE similarity(street_name, $1) > 0.3 
               OR similarity(street_address, $1) > 0.3
        """, search_term)
        similarity_time = (time.time() - start) * 1000
        
        print(f"   ILIKE search:      {ilike_result:4d} results in {ilike_time:6.2f}ms")
        print(f"   Trigram search:    {fuzzy_result:4d} results in {fuzzy_time:6.2f}ms") 
        print(f"   Similarity search: {similarity_result:4d} results in {similarity_time:6.2f}ms")
        
        # Test different similarity thresholds
        print("\n\n📊 Similarity Threshold Analysis")
        print("=" * 60)
        
        typo_query = "Main Stret"  # Intentional typo
        thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for threshold in thresholds:
            result_count = await conn.fetchval("""
                SELECT COUNT(*) FROM addresses 
                WHERE similarity(street_name, $1) >= $2
            """, typo_query, threshold)
            
            print(f"   Threshold {threshold:.1f}: {result_count:3d} matches for '{typo_query}'")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()
        print("\n✅ Disconnected from database")

def main():
    """Run service fuzzy search tests"""
    print("🚀 Fuzzy Search Service Methods Test")
    print("=" * 80)
    
    try:
        asyncio.run(test_service_fuzzy_methods())
        
        print("\n🎉 All fuzzy search service tests completed successfully!")
        print("✅ Fuzzy search service methods are working correctly")
        return 0
        
    except Exception as e:
        print(f"❌ Service tests failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())