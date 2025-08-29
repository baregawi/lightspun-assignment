#!/usr/bin/env python3
"""
Test script for standardized address search functionality
"""

import asyncio
import asyncpg
import sys
from pathlib import Path

# Add the lightspun package to the path
sys.path.append(str(Path(__file__).parent))

from lightspun.utils.street_standardization import standardize_street_type

async def test_standardized_search():
    """Test address search with various street type formats"""
    
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Test cases: (search_term, description)
        test_cases = [
            ("Main St", "Abbreviated street search"),
            ("Main Street", "Full street search"),
            ("Oak Ave", "Abbreviated avenue search"),
            ("Oak Avenue", "Full avenue search"),
            ("Lincoln Blvd", "Abbreviated boulevard search"),
            ("Lincoln Boulevard", "Full boulevard search"),
            ("Park Dr", "Abbreviated drive search"),
            ("Park Drive", "Full drive search"),
        ]
        
        print("\n🔍 Testing Address Search with Standardization")
        print("=" * 80)
        
        for search_term, description in test_cases:
            standardized_term = standardize_street_type(search_term)
            
            # Search for addresses using the original term
            result = await conn.fetch("""
                SELECT street_address, street_name, city, full_address
                FROM addresses 
                WHERE street_address ILIKE $1
                   OR street_name ILIKE $1
                LIMIT 5
            """, f"%{search_term}%")
            
            # Also search using standardized term
            std_result = await conn.fetch("""
                SELECT street_address, street_name, city, full_address
                FROM addresses 
                WHERE street_address ILIKE $1
                   OR street_name ILIKE $1
                LIMIT 5
            """, f"%{standardized_term}%")
            
            print(f"\n🔍 {description}")
            print(f"   Search term: '{search_term}' -> Standardized: '{standardized_term}'")
            print(f"   Original search results: {len(result)}")
            print(f"   Standardized search results: {len(std_result)}")
            
            # Show results
            if std_result:
                print("   Sample standardized results:")
                for row in std_result[:3]:
                    print(f"     {row['street_address']}, {row['city']}")
            else:
                print("     No results found")
                
            # Check if searching for old abbreviations still works with standardization
            if search_term != standardized_term:
                hybrid_result = await conn.fetch("""
                    SELECT street_address, street_name, city, full_address
                    FROM addresses 
                    WHERE street_address ILIKE $1
                       OR street_address ILIKE $2
                       OR street_name ILIKE $1
                       OR street_name ILIKE $2
                    LIMIT 5
                """, f"%{search_term}%", f"%{standardized_term}%")
                
                print(f"   Hybrid search (both terms): {len(hybrid_result)} results")
        
        # Test some edge cases
        print("\n🧪 Testing Edge Cases")
        print("=" * 80)
        
        edge_cases = [
            "St",          # Just the abbreviation
            "Street",      # Just the full form
            "Main",        # No street type
            "123 Main",    # Number + street name
        ]
        
        for search_term in edge_cases:
            result = await conn.fetch("""
                SELECT street_address, street_name, city
                FROM addresses 
                WHERE street_address ILIKE $1
                   OR street_name ILIKE $1
                LIMIT 3
            """, f"%{search_term}%")
            
            standardized_term = standardize_street_type(search_term)
            
            print(f"\n🔍 Edge case: '{search_term}' -> '{standardized_term}'")
            print(f"   Results: {len(result)}")
            
            if result:
                for row in result:
                    print(f"     {row['street_address']}, {row['city']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()
        print("\n✅ Disconnected from database")

async def test_search_performance():
    """Test search performance with indexes"""
    
    DATABASE_URL = "postgresql://user:password@localhost:5432/lightspun_db"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("\n⚡ Testing Search Performance")
        print("=" * 80)
        
        # Test search with EXPLAIN ANALYZE
        search_terms = ["Main Street", "Oak Avenue", "Lincoln Boulevard"]
        
        for term in search_terms:
            result = await conn.fetch("""
                EXPLAIN ANALYZE
                SELECT street_address, street_name, city
                FROM addresses 
                WHERE street_name ILIKE $1
                LIMIT 10
            """, f"%{term}%")
            
            print(f"\n🔍 Performance for '{term}':")
            for row in result:
                if 'time' in row[0].lower() or 'cost' in row[0].lower():
                    print(f"   {row[0]}")
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    finally:
        await conn.close()

def main():
    """Run search tests"""
    print("🚀 Standardized Address Search Test Suite")
    print("=" * 80)
    
    try:
        asyncio.run(test_standardized_search())
        asyncio.run(test_search_performance())
        
        print("\n🎉 All search tests completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Search tests failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())