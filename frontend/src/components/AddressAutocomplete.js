import React, { useState, useEffect, useRef } from 'react';
import { getAddressAutocomplete } from '../services/api';

/**
 * Address autocomplete input component
 */
function AddressAutocomplete({ selectedState, selectedMunicipality, value, onChange, disabled = false }) {
  const [query, setQuery] = useState(value || '');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [debounceTimeout, setDebounceTimeout] = useState(null);
  
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  useEffect(() => {
    setQuery(value || '');
  }, [value]);

  useEffect(() => {
    // Close dropdown when clicking outside
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
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const searchAddresses = async (searchQuery) => {
    if (!searchQuery || searchQuery.length < 2) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const results = await getAddressAutocomplete(searchQuery, 10);
      setSuggestions(results);
      setShowDropdown(results.length > 0);
      setSelectedIndex(-1);
    } catch (err) {
      setError('Failed to load address suggestions');
      console.error('Error loading address suggestions:', err);
      setSuggestions([]);
      setShowDropdown(false);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (event) => {
    const newQuery = event.target.value;
    setQuery(newQuery);
    onChange(newQuery);

    // Clear existing debounce timeout
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }

    // Set new debounce timeout
    const newTimeout = setTimeout(() => {
      searchAddresses(newQuery);
    }, 300); // 300ms delay

    setDebounceTimeout(newTimeout);
  };

  const handleInputFocus = () => {
    if (suggestions.length > 0) {
      setShowDropdown(true);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    onChange(suggestion);
    setSuggestions([]);
    setShowDropdown(false);
    setSelectedIndex(-1);
    inputRef.current?.blur();
  };

  const handleKeyDown = (event) => {
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
          handleSuggestionClick(suggestions[selectedIndex]);
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
  };

  // Don't render if no state and municipality are selected
  if (!selectedState || !selectedMunicipality) {
    return null;
  }

  return (
    <div className="form-group autocomplete-container">
      <label htmlFor="address-input">
        Street Address in {selectedMunicipality.name}, {selectedState.code}: <span className="required">*</span>
      </label>
      
      <div className="autocomplete-wrapper">
        <input
          ref={inputRef}
          id="address-input"
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className="form-control"
          placeholder="Start typing an address..."
          required
          autoComplete="off"
        />
        
        {loading && (
          <div className="autocomplete-loading">
            <small>Searching...</small>
          </div>
        )}
        
        {error && (
          <div className="error-message">{error}</div>
        )}
        
        {showDropdown && suggestions.length > 0 && (
          <div ref={dropdownRef} className="autocomplete-dropdown">
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className={`autocomplete-item ${
                  index === selectedIndex ? 'selected' : ''
                }`}
                onClick={() => handleSuggestionClick(suggestion)}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                {suggestion}
              </div>
            ))}
          </div>
        )}
      </div>
      
      <small className="form-text">
        Start typing to see address suggestions. Use arrow keys to navigate and Enter to select.
      </small>
    </div>
  );
}

export default AddressAutocomplete;