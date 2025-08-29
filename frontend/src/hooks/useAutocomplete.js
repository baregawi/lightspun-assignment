import { useState, useCallback, useRef, useEffect } from 'react';
import { useDebounce } from './useDebounce';

/**
 * Custom hook for autocomplete functionality with keyboard navigation
 */
export function useAutocomplete({
  fetchSuggestions,
  debounceDelay = 300,
  minQueryLength = 2,
  onSelect,
}) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Debounce the query to avoid excessive API calls
  const debouncedQuery = useDebounce(query, debounceDelay);

  // Fetch suggestions when debounced query changes
  useEffect(() => {
    if (debouncedQuery && debouncedQuery.length >= minQueryLength) {
      searchSuggestions(debouncedQuery);
    } else {
      setSuggestions([]);
      setShowDropdown(false);
    }
  }, [debouncedQuery, minQueryLength]);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        inputRef.current &&
        dropdownRef.current &&
        !inputRef.current.contains(event.target) &&
        !dropdownRef.current.contains(event.target)
      ) {
        setShowDropdown(false);
        setSelectedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const searchSuggestions = useCallback(async (searchQuery) => {
    try {
      setLoading(true);
      setError(null);
      
      const results = await fetchSuggestions(searchQuery);
      setSuggestions(results);
      setShowDropdown(results.length > 0);
      setSelectedIndex(-1);
    } catch (err) {
      setError(err.message || 'Failed to load suggestions');
      setSuggestions([]);
      setShowDropdown(false);
    } finally {
      setLoading(false);
    }
  }, [fetchSuggestions]);

  const handleInputChange = useCallback((value) => {
    setQuery(value);
  }, []);

  const handleInputFocus = useCallback(() => {
    if (suggestions.length > 0) {
      setShowDropdown(true);
    }
  }, [suggestions.length]);

  const handleSuggestionSelect = useCallback((suggestion, index) => {
    setQuery(suggestion);
    setSuggestions([]);
    setShowDropdown(false);
    setSelectedIndex(-1);
    
    if (onSelect) {
      onSelect(suggestion, index);
    }
    
    inputRef.current?.blur();
  }, [onSelect]);

  const handleKeyDown = useCallback((event) => {
    if (!showDropdown || suggestions.length === 0) {
      return;
    }

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        event.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        event.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSuggestionSelect(suggestions[selectedIndex], selectedIndex);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
      default:
        break;
    }
  }, [showDropdown, suggestions, selectedIndex, handleSuggestionSelect]);

  const clear = useCallback(() => {
    setQuery('');
    setSuggestions([]);
    setShowDropdown(false);
    setSelectedIndex(-1);
    setError(null);
  }, []);

  return {
    // State
    query,
    suggestions,
    loading,
    error,
    showDropdown,
    selectedIndex,
    
    // Refs
    inputRef,
    dropdownRef,
    
    // Handlers
    handleInputChange,
    handleInputFocus,
    handleSuggestionSelect,
    handleKeyDown,
    
    // Actions
    clear,
    setSelectedIndex,
  };
}