import React from 'react';
import { FormGroup, LoadingState, AutocompleteDropdown, StepIndicator } from '../../../components/ui';
import { useAutocomplete } from '../../../hooks';
import { addressesApi } from '../../../services/api';
import { FORM_LABELS, LOADING_MESSAGES, API_DEFAULTS } from '../../../constants';
import { formatError } from '../../../utils';

/**
 * Address autocomplete component with step indicator
 */
function AddressAutocomplete({ 
  selectedState, 
  selectedMunicipality, 
  value, 
  onChange, 
  disabled = false,
  step = 3 
}) {
  const {
    query,
    suggestions,
    loading,
    error,
    showDropdown,
    selectedIndex,
    inputRef,
    dropdownRef,
    handleInputChange,
    handleInputFocus,
    handleSuggestionSelect,
    handleKeyDown,
    setSelectedIndex,
  } = useAutocomplete({
    fetchSuggestions: addressesApi.autocomplete,
    debounceDelay: API_DEFAULTS.DEBOUNCE_DELAY,
    minQueryLength: API_DEFAULTS.AUTOCOMPLETE_MIN_LENGTH,
    onSelect: (suggestion) => {
      onChange(suggestion);
    },
  });

  // Update query when value changes externally
  React.useEffect(() => {
    if (value !== query) {
      handleInputChange(value || '');
    }
  }, [value, query, handleInputChange]);

  const handleChange = (event) => {
    const newValue = event.target.value;
    handleInputChange(newValue);
    onChange(newValue);
  };

  const getLabel = () => {
    if (selectedMunicipality && selectedState) {
      return `${FORM_LABELS.ADDRESS} in ${selectedMunicipality.name}, ${selectedState.code}`;
    }
    return FORM_LABELS.ADDRESS;
  };

  const getHelpText = () => {
    return 'Start typing to see address suggestions. Use arrow keys to navigate and Enter to select.';
  };

  // Don't render if no state and municipality are selected
  if (!selectedState || !selectedMunicipality) {
    return null;
  }

  return (
    <div className="form-step">
      <StepIndicator 
        step={step} 
        active={!!selectedState && !!selectedMunicipality && !value} 
        completed={!!value} 
      />
      
      <FormGroup
        label={getLabel()}
        required
        error={error ? formatError(error) : null}
        helpText={getHelpText()}
        id="address-input"
      >
        <div className="autocomplete-container">
          <div className="autocomplete-wrapper">
            <input
              ref={inputRef}
              id="address-input"
              type="text"
              value={query}
              onChange={handleChange}
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
                <LoadingState message="Searching..." inline />
              </div>
            )}
            
            {showDropdown && (
              <AutocompleteDropdown
                suggestions={suggestions}
                selectedIndex={selectedIndex}
                onSuggestionClick={handleSuggestionSelect}
                onSuggestionHover={setSelectedIndex}
                dropdownRef={dropdownRef}
              />
            )}
          </div>
        </div>
      </FormGroup>
    </div>
  );
}

export default AddressAutocomplete;