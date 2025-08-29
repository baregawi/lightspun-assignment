import React from 'react';

/**
 * Reusable autocomplete dropdown component
 */
function AutocompleteDropdown({
  suggestions = [],
  selectedIndex = -1,
  onSuggestionClick,
  onSuggestionHover,
  dropdownRef,
  formatSuggestion = (suggestion) => suggestion,
  className = 'autocomplete-dropdown',
}) {
  if (suggestions.length === 0) {
    return null;
  }

  return (
    <div ref={dropdownRef} className={className}>
      {suggestions.map((suggestion, index) => (
        <div
          key={index}
          className={`autocomplete-item ${
            index === selectedIndex ? 'selected' : ''
          }`}
          onClick={() => onSuggestionClick(suggestion, index)}
          onMouseEnter={() => onSuggestionHover && onSuggestionHover(index)}
        >
          {formatSuggestion(suggestion)}
        </div>
      ))}
    </div>
  );
}

export default AutocompleteDropdown;