"""
Fuzzy Search Module

This module provides fuzzy search capabilities using PostgreSQL's
pg_trgm and fuzzystrmatch extensions for intelligent address matching.

Features:
- Trigram similarity matching for typo tolerance
- Soundex phonetic matching for similar-sounding names  
- Configurable similarity thresholds
- Performance-optimized queries with proper indexing
- Multiple search strategies (exact, fuzzy, combined)
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..database import database
from ..logging_config import get_logger
from ..utils.street_standardization import standardize_street_type

# Initialize logger
fuzzy_logger = get_logger('lightspun.core.fuzzy_search')


class SearchStrategy(Enum):
    """Available search strategies"""
    EXACT = "exact"          # Traditional ILIKE/exact matching
    FUZZY = "fuzzy"          # Trigram similarity matching
    SOUNDEX = "soundex"      # Phonetic matching
    COMBINED = "combined"    # All strategies combined


@dataclass  
class FuzzySearchConfig:
    """Configuration for fuzzy search operations"""
    min_similarity: float = 0.3
    soundex_boost: float = 0.8  # Boost score for soundex matches
    limit: int = 10
    strategy: SearchStrategy = SearchStrategy.COMBINED
    
    def __post_init__(self):
        if not 0.0 <= self.min_similarity <= 1.0:
            raise ValueError("min_similarity must be between 0.0 and 1.0")


@dataclass
class SearchResult:
    """Represents a search result with scoring"""
    content: str
    similarity_score: float
    match_type: str  # "trigram", "soundex", "exact"
    
    def __lt__(self, other):
        return self.similarity_score > other.similarity_score  # Higher scores first


class FuzzySearchEngine:
    """Core fuzzy search functionality"""
    
    @staticmethod
    async def trigram_similarity_search(
        search_query: str, 
        field_name: str,
        table_name: str = "addresses",
        min_similarity: float = 0.3,
        limit: int = 10,
        additional_where: str = "",
        additional_params: List[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform trigram similarity search on a specific field.
        
        Args:
            search_query: Text to search for
            field_name: Database field to search in
            table_name: Database table to search
            min_similarity: Minimum similarity threshold (0.0-1.0)
            limit: Maximum number of results
            additional_where: Additional WHERE conditions
            additional_params: Parameters for additional WHERE conditions
            
        Returns:
            List of matching records with similarity scores
        """
        fuzzy_logger.debug(f"Trigram search for '{search_query}' in {table_name}.{field_name}")
        
        # Prepare parameters
        params = [search_query, search_query, min_similarity, limit]
        if additional_params:
            params.extend(additional_params)
        
        where_clause = f"WHERE {field_name} % ${len(params) - 3}"
        if additional_where:
            where_clause += f" AND {additional_where}"
        
        query = f"""
            SELECT *, similarity({field_name}, $1) as similarity_score
            FROM {table_name}
            {where_clause}
            HAVING similarity({field_name}, $2) >= ${len(params) - 2}
            ORDER BY similarity_score DESC, {field_name}
            LIMIT ${len(params) - 1}
        """
        
        rows = await database.fetch_all(query=query, values=params)
        fuzzy_logger.debug(f"Found {len(rows)} trigram matches")
        
        return [dict(row) for row in rows]
    
    @staticmethod
    async def soundex_search(
        search_query: str,
        field_name: str, 
        table_name: str = "addresses",
        limit: int = 10,
        additional_where: str = "",
        additional_params: List[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform soundex phonetic matching search.
        
        Args:
            search_query: Text to search for (phonetic matching)
            field_name: Database field to search in
            table_name: Database table to search
            limit: Maximum number of results
            additional_where: Additional WHERE conditions
            additional_params: Parameters for additional WHERE conditions
            
        Returns:
            List of matching records
        """
        fuzzy_logger.debug(f"Soundex search for '{search_query}' in {table_name}.{field_name}")
        
        params = [search_query, limit]
        if additional_params:
            params.extend(additional_params)
        
        where_clause = f"WHERE soundex({field_name}) = soundex($1)"
        if additional_where:
            where_clause += f" AND {additional_where}"
        
        query = f"""
            SELECT *, soundex({field_name}) as soundex_code
            FROM {table_name} 
            {where_clause}
            ORDER BY {field_name}
            LIMIT $2
        """
        
        rows = await database.fetch_all(query=query, values=params)
        fuzzy_logger.debug(f"Found {len(rows)} soundex matches")
        
        return [dict(row) for row in rows]
    
    @staticmethod
    async def combined_fuzzy_search(
        search_query: str,
        config: FuzzySearchConfig,
        fields: List[str],
        table_name: str = "addresses",
        return_fields: List[str] = None,
        additional_where: str = "",
        additional_params: List[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform combined fuzzy search using multiple strategies.
        
        Args:
            search_query: Text to search for
            config: Search configuration
            fields: List of fields to search in
            table_name: Database table to search
            return_fields: Fields to return (default: all)
            additional_where: Additional WHERE conditions  
            additional_params: Parameters for additional WHERE conditions
            
        Returns:
            List of matching records with combined similarity scores
        """
        fuzzy_logger.debug(f"Combined fuzzy search for '{search_query}' in fields: {fields}")
        
        # Standardize the search query
        standardized_query = standardize_street_type(search_query.strip())
        
        # Build field similarity expressions
        similarity_expressions = []
        trigram_conditions = []
        soundex_conditions = []
        
        for field in fields:
            # Trigram similarity for both original and standardized queries
            similarity_expressions.extend([
                f"similarity({field}, $1)",
                f"similarity({field}, $2)"
            ])
            
            # Trigram matching conditions
            trigram_conditions.extend([
                f"{field} % $1",
                f"{field} % $2"
            ])
            
            # Soundex conditions
            soundex_conditions.extend([
                f"soundex({field}) = soundex($1)",
                f"soundex({field}) = soundex($2)"
            ])
        
        # Build the GREATEST expression for similarity scoring
        similarity_score_expr = f"GREATEST({', '.join(similarity_expressions)}"
        
        # Add soundex boost if any soundex conditions match
        if soundex_conditions:
            soundex_case = f"""
                CASE WHEN ({' OR '.join(soundex_conditions)}) 
                     THEN {config.soundex_boost} 
                     ELSE 0.0 
                END
            """
            similarity_score_expr += f", {soundex_case}"
        
        similarity_score_expr += ") as similarity_score"
        
        # Build WHERE conditions
        all_conditions = trigram_conditions + soundex_conditions
        where_conditions = f"({' OR '.join(all_conditions)})"
        
        if additional_where:
            where_conditions = f"({where_conditions}) AND {additional_where}"
        
        # Select fields
        select_fields = "*" if not return_fields else ", ".join(return_fields)
        
        # Prepare parameters
        params = [search_query, standardized_query, config.min_similarity, config.limit]
        if additional_params:
            params.extend(additional_params)
        
        query = f"""
            SELECT {select_fields}, {similarity_score_expr}
            FROM {table_name}
            WHERE {where_conditions}
            HAVING GREATEST({', '.join(similarity_expressions)}) >= $3
                OR ({' OR '.join(soundex_conditions)})
            ORDER BY similarity_score DESC, {fields[0]}
            LIMIT $4
        """
        
        rows = await database.fetch_all(query=query, values=params)
        fuzzy_logger.debug(f"Found {len(rows)} combined fuzzy matches")
        
        return [dict(row) for row in rows]


class AddressFuzzySearch:
    """Specialized fuzzy search for address data"""
    
    def __init__(self, config: Optional[FuzzySearchConfig] = None):
        self.config = config or FuzzySearchConfig()
    
    async def search_addresses(self, search_query: str, limit: Optional[int] = None) -> List[str]:
        """
        Fuzzy search for full addresses.
        
        Args:
            search_query: Address search term
            limit: Maximum results (overrides config)
            
        Returns:
            List of matching full addresses
        """
        search_limit = limit or self.config.limit
        
        results = await FuzzySearchEngine.combined_fuzzy_search(
            search_query=search_query,
            config=self.config,
            fields=["street_address", "street_name", "full_address"],
            return_fields=["full_address"],
            table_name="addresses"
        )
        
        # Extract unique full addresses
        addresses = []
        seen = set()
        
        for result in results[:search_limit]:
            addr = result["full_address"]
            if addr and addr not in seen:
                addresses.append(addr)
                seen.add(addr)
        
        return addresses
    
    async def search_street_names(self, search_query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fuzzy search for street names with statistics.
        
        Args:
            search_query: Street name search term
            limit: Maximum results (overrides config)
            
        Returns:
            List of dicts with street_name, similarity_score, and address_count
        """
        search_limit = limit or self.config.limit
        
        # Use a specialized query for street names with grouping
        standardized_query = standardize_street_type(search_query.strip())
        
        query = """
            SELECT 
                street_name,
                COUNT(*) as address_count,
                GREATEST(
                    similarity(street_name, $1),
                    similarity(street_name, $2),
                    CASE 
                        WHEN soundex(street_name) = soundex($1) THEN $4
                        WHEN soundex(street_name) = soundex($2) THEN $4
                        ELSE 0.0 
                    END
                ) as similarity_score
            FROM addresses 
            WHERE 
                (street_name % $1 OR street_name % $2)
                OR soundex(street_name) = soundex($1)
                OR soundex(street_name) = soundex($2)
            GROUP BY street_name
            HAVING GREATEST(
                similarity(street_name, $1),
                similarity(street_name, $2),
                CASE 
                    WHEN soundex(street_name) = soundex($1) THEN $4
                    WHEN soundex(street_name) = soundex($2) THEN $4
                    ELSE 0.0 
                END
            ) >= $3
            ORDER BY similarity_score DESC, address_count DESC, street_name
            LIMIT $5
        """
        
        rows = await database.fetch_all(query=query, values=[
            search_query, 
            standardized_query, 
            self.config.min_similarity,
            self.config.soundex_boost,
            search_limit
        ])
        
        return [
            {
                "street_name": row["street_name"],
                "similarity_score": float(row["similarity_score"]),
                "address_count": row["address_count"]
            }
            for row in rows
        ]
    
    async def autocomplete(self, search_query: str, limit: Optional[int] = None) -> List[str]:
        """
        Autocomplete addresses with fuzzy matching.
        
        Args:
            search_query: Partial address to autocomplete
            limit: Maximum suggestions (overrides config)
            
        Returns:
            List of address suggestions
        """
        if not search_query or len(search_query.strip()) < 2:
            return []
        
        return await self.search_addresses(search_query, limit)
    
    async def get_performance_stats(self, search_query: str) -> Dict[str, Any]:
        """
        Get performance statistics for different search strategies.
        
        Args:
            search_query: Query to analyze
            
        Returns:
            Dictionary with performance metrics
        """
        import time
        
        stats = {}
        
        # Test exact search
        start = time.time()
        exact_count = await database.fetch_val("""
            SELECT COUNT(*) FROM addresses 
            WHERE street_name ILIKE $1 OR street_address ILIKE $1
        """, f"%{search_query}%")
        stats["exact"] = {
            "count": exact_count,
            "time_ms": round((time.time() - start) * 1000, 2)
        }
        
        # Test trigram search  
        start = time.time()
        fuzzy_count = await database.fetch_val("""
            SELECT COUNT(*) FROM addresses 
            WHERE street_name % $1 OR street_address % $1
        """, search_query)
        stats["trigram"] = {
            "count": fuzzy_count,
            "time_ms": round((time.time() - start) * 1000, 2)
        }
        
        # Test similarity search
        start = time.time()
        similarity_count = await database.fetch_val("""
            SELECT COUNT(*) FROM addresses 
            WHERE similarity(street_name, $1) > $2
        """, search_query, self.config.min_similarity)
        stats["similarity"] = {
            "count": similarity_count, 
            "time_ms": round((time.time() - start) * 1000, 2)
        }
        
        return stats


# Convenience functions for backward compatibility and easy access
async def fuzzy_search_addresses(search_query: str, limit: int = 10, min_similarity: float = 0.3) -> List[str]:
    """Convenience function for fuzzy address search"""
    config = FuzzySearchConfig(min_similarity=min_similarity, limit=limit)
    searcher = AddressFuzzySearch(config)
    return await searcher.search_addresses(search_query)


async def autocomplete_addresses(search_query: str, limit: int = 10, use_fuzzy: bool = True) -> List[str]:
    """Convenience function for address autocomplete"""
    if not use_fuzzy:
        # Fall back to exact matching
        standardized_query = standardize_street_type(search_query.strip())
        
        query = """
            SELECT DISTINCT full_address
            FROM addresses 
            WHERE street_address ILIKE $1
               OR street_address ILIKE $2
               OR LOWER(full_address) LIKE LOWER($3)
               OR LOWER(full_address) LIKE LOWER($4)
            ORDER BY 
                CASE 
                    WHEN street_address ILIKE $1 THEN 1 
                    WHEN street_address ILIKE $2 THEN 2
                    ELSE 3 
                END,
                full_address
            LIMIT $5
        """
        
        rows = await database.fetch_all(query=query, values=[
            f"{search_query}%",
            f"{standardized_query}%", 
            f"%{search_query}%",
            f"%{standardized_query}%",
            limit
        ])
        
        return [row["full_address"] for row in rows]
    else:
        config = FuzzySearchConfig(limit=limit)
        searcher = AddressFuzzySearch(config)
        return await searcher.autocomplete(search_query)