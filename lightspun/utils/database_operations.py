"""
Database Operations Utilities Module

This module provides common db.database operation utilities including:
- Query building helpers
- Common CRUD operation patterns  
- Transaction management utilities
- Database connection helpers
- Query optimization utilities

This reduces code duplication across service classes.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from contextlib import asynccontextmanager

from .. import database as db
from ..logging_config import get_logger

# Initialize logger
db_logger = get_logger('lightspun.utils.database_operations')


class QueryBuilder:
    """Helper class for building dynamic SQL queries"""
    
    @staticmethod
    def build_select(
        table: str,
        fields: List[str] = None,
        where_conditions: List[str] = None,
        order_by: List[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> str:
        """
        Build a SELECT query dynamically.
        
        Args:
            table: Table name
            fields: List of fields to select (default: *)
            where_conditions: List of WHERE conditions
            order_by: List of ORDER BY clauses
            limit: LIMIT value
            offset: OFFSET value
            
        Returns:
            Complete SQL query string
        """
        # SELECT clause
        select_fields = "*" if not fields else ", ".join(fields)
        query = f"SELECT {select_fields} FROM {table}"
        
        # WHERE clause
        if where_conditions:
            query += f" WHERE {' AND '.join(where_conditions)}"
        
        # ORDER BY clause
        if order_by:
            query += f" ORDER BY {', '.join(order_by)}"
        
        # LIMIT clause
        if limit:
            query += f" LIMIT {limit}"
        
        # OFFSET clause  
        if offset:
            query += f" OFFSET {offset}"
        
        return query
    
    @staticmethod
    def build_insert(
        table: str,
        fields: List[str],
        returning: List[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Build an INSERT query with proper parameter placeholders.
        
        Args:
            table: Table name
            fields: List of field names to insert
            returning: List of fields to return
            
        Returns:
            Tuple of (query_string, parameter_names)
        """
        placeholders = [f":{field}" for field in fields]
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        
        if returning:
            query += f" RETURNING {', '.join(returning)}"
        
        return query, fields
    
    @staticmethod
    def build_update(
        table: str,
        fields: List[str],
        where_field: str,
        returning: List[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Build an UPDATE query with proper parameter placeholders.
        
        Args:
            table: Table name
            fields: List of fields to update
            where_field: Field name for WHERE condition
            returning: List of fields to return
            
        Returns:
            Tuple of (query_string, parameter_names)
        """
        set_clauses = [f"{field} = :{field}" for field in fields]
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where_field} = :{where_field}"
        
        if returning:
            query += f" RETURNING {', '.join(returning)}"
        
        parameter_names = fields + [where_field]
        return query, parameter_names


class DatabaseOperations:
    """Common db.database operation patterns"""
    
    @staticmethod
    async def get_by_id(
        table: str,
        id_value: Any,
        id_field: str = "id",
        fields: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single record by ID.
        
        Args:
            table: Table name
            id_value: ID value to search for
            id_field: ID field name (default: "id")
            fields: Fields to select (default: all)
            
        Returns:
            Record as dictionary or None
        """
        query = QueryBuilder.build_select(
            table=table,
            fields=fields,
            where_conditions=[f"{id_field} = :{id_field}"]
        )
        
        row = await db.database.fetch_one(query=query, values={id_field: id_value})
        return dict(row) if row else None
    
    @staticmethod
    async def get_all(
        table: str,
        fields: List[str] = None,
        order_by: List[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all records from a table.
        
        Args:
            table: Table name
            fields: Fields to select (default: all)
            order_by: ORDER BY clauses
            limit: Maximum number of records
            
        Returns:
            List of records as dictionaries
        """
        query = QueryBuilder.build_select(
            table=table,
            fields=fields,
            order_by=order_by,
            limit=limit
        )
        
        rows = await db.database.fetch_all(query=query)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def create(
        table: str,
        data: Dict[str, Any],
        returning: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new record.
        
        Args:
            table: Table name
            data: Field values to insert
            returning: Fields to return from created record
            
        Returns:
            Created record as dictionary or None
        """
        fields = list(data.keys())
        query, _ = QueryBuilder.build_insert(table, fields, returning)
        
        if returning:
            row = await db.database.fetch_one(query=query, values=data)
            return dict(row) if row else None
        else:
            await db.database.execute(query=query, values=data)
            return None
    
    @staticmethod
    async def update_by_id(
        table: str,
        id_value: Any,
        data: Dict[str, Any],
        id_field: str = "id",
        returning: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a record by ID.
        
        Args:
            table: Table name
            id_value: ID of record to update
            data: Field values to update
            id_field: ID field name (default: "id")
            returning: Fields to return from updated record
            
        Returns:
            Updated record as dictionary or None
        """
        fields = list(data.keys())
        query, _ = QueryBuilder.build_update(table, fields, id_field, returning)
        
        values = {**data, id_field: id_value}
        
        if returning:
            row = await db.database.fetch_one(query=query, values=values)
            return dict(row) if row else None
        else:
            result = await db.database.execute(query=query, values=values)
            return {"rows_affected": result}
    
    @staticmethod
    async def delete_by_id(
        table: str,
        id_value: Any,
        id_field: str = "id"
    ) -> bool:
        """
        Delete a record by ID.
        
        Args:
            table: Table name
            id_value: ID of record to delete
            id_field: ID field name (default: "id")
            
        Returns:
            True if record was deleted, False otherwise
        """
        query = f"DELETE FROM {table} WHERE {id_field} = :{id_field}"
        result = await db.database.execute(query=query, values={id_field: id_value})
        return result > 0
    
    @staticmethod
    async def count(
        table: str,
        where_conditions: List[str] = None,
        parameters: Dict[str, Any] = None
    ) -> int:
        """
        Count records in a table.
        
        Args:
            table: Table name
            where_conditions: Optional WHERE conditions
            parameters: Parameters for WHERE conditions
            
        Returns:
            Number of matching records
        """
        query = f"SELECT COUNT(*) FROM {table}"
        
        if where_conditions:
            query += f" WHERE {' AND '.join(where_conditions)}"
        
        params = parameters or {}
        result = await db.database.fetch_val(query=query, values=params)
        return result or 0
    
    @staticmethod
    async def exists(
        table: str,
        where_conditions: List[str],
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Check if records exist matching conditions.
        
        Args:
            table: Table name
            where_conditions: WHERE conditions
            parameters: Parameters for WHERE conditions
            
        Returns:
            True if matching records exist
        """
        count = await DatabaseOperations.count(table, where_conditions, parameters)
        return count > 0


class TransactionManager:
    """Transaction management utilities"""
    
    @staticmethod
    @asynccontextmanager
    async def transaction():
        """
        Context manager for db.database transactions.
        
        Usage:
            async with TransactionManager.transaction():
                # Database operations here
                # Will be committed automatically or rolled back on exception
        """
        transaction = await db.database.transaction()
        try:
            yield transaction
        except Exception:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()


class PaginationHelper:
    """Utilities for handling pagination"""
    
    @staticmethod
    def calculate_offset(page: int, page_size: int) -> int:
        """Calculate OFFSET value for pagination"""
        if page < 1:
            page = 1
        return (page - 1) * page_size
    
    @staticmethod
    async def paginate(
        table: str,
        page: int = 1,
        page_size: int = 20,
        fields: List[str] = None,
        where_conditions: List[str] = None,
        parameters: Dict[str, Any] = None,
        order_by: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get paginated results from a table.
        
        Args:
            table: Table name
            page: Page number (1-based)
            page_size: Number of records per page
            fields: Fields to select
            where_conditions: WHERE conditions
            parameters: Parameters for WHERE conditions
            order_by: ORDER BY clauses
            
        Returns:
            Dictionary with pagination metadata and results
        """
        # Calculate offset
        offset = PaginationHelper.calculate_offset(page, page_size)
        
        # Get total count
        total_count = await DatabaseOperations.count(table, where_conditions, parameters or {})
        
        # Get page data
        query = QueryBuilder.build_select(
            table=table,
            fields=fields,
            where_conditions=where_conditions,
            order_by=order_by,
            limit=page_size,
            offset=offset
        )
        
        rows = await db.database.fetch_all(query=query, values=parameters or {})
        records = [dict(row) for row in rows]
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "records": records,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }


class SearchHelper:
    """Utilities for building search queries"""
    
    @staticmethod
    def build_ilike_condition(field: str, search_term: str, param_name: str) -> Tuple[str, Dict[str, str]]:
        """
        Build ILIKE condition for text search.
        
        Args:
            field: Field name to search
            search_term: Search term
            param_name: Parameter name for the query
            
        Returns:
            Tuple of (condition_string, parameters_dict)
        """
        condition = f"{field} ILIKE :{param_name}"
        parameters = {param_name: f"%{search_term}%"}
        return condition, parameters
    
    @staticmethod
    def build_multi_field_search(
        fields: List[str],
        search_term: str,
        operator: str = "OR"
    ) -> Tuple[str, Dict[str, str]]:
        """
        Build search conditions across multiple fields.
        
        Args:
            fields: List of field names to search
            search_term: Search term
            operator: Logical operator (OR/AND)
            
        Returns:
            Tuple of (condition_string, parameters_dict)
        """
        conditions = []
        parameters = {}
        
        for i, field in enumerate(fields):
            param_name = f"search_term_{i}"
            condition, param_dict = SearchHelper.build_ilike_condition(field, search_term, param_name)
            conditions.append(condition)
            parameters.update(param_dict)
        
        combined_condition = f" {operator} ".join(conditions)
        return f"({combined_condition})", parameters