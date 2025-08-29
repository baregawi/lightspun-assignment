"""
Core Module

This module contains core functionality including address processing and fuzzy search.
"""

from .address_processing import AddressComponents, AddressParser, AddressValidator, AddressFormatter
from .fuzzy_search import FuzzySearchEngine, AddressFuzzySearch, FuzzySearchConfig, SearchStrategy

__all__ = [
    'AddressComponents', 'AddressParser', 'AddressValidator', 'AddressFormatter',
    'FuzzySearchEngine', 'AddressFuzzySearch', 'FuzzySearchConfig', 'SearchStrategy'
]