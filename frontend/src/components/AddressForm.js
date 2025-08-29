import React, { useState } from 'react';
import StateSelect from './StateSelect';
import MunicipalitySelect from './MunicipalitySelect';
import AddressAutocomplete from './AddressAutocomplete';

/**
 * Main address form component that orchestrates the multi-step selection process
 */
function AddressForm({ onSubmit, onReset }) {
  const [selectedState, setSelectedState] = useState(null);
  const [selectedMunicipality, setSelectedMunicipality] = useState(null);
  const [streetAddress, setStreetAddress] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleStateChange = (state) => {
    setSelectedState(state);
    // Reset municipality and address when state changes
    setSelectedMunicipality(null);
    setStreetAddress('');
  };

  const handleMunicipalityChange = (municipality) => {
    setSelectedMunicipality(municipality);
    // Reset address when municipality changes
    setStreetAddress('');
  };

  const handleAddressChange = (address) => {
    setStreetAddress(address);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!selectedState || !selectedMunicipality || !streetAddress.trim()) {
      alert('Please complete all required fields');
      return;
    }

    setSubmitting(true);
    
    const formData = {
      state: selectedState,
      municipality: selectedMunicipality,
      streetAddress: streetAddress.trim(),
    };

    try {
      if (onSubmit) {
        await onSubmit(formData);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      alert('Failed to submit form. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setSelectedState(null);
    setSelectedMunicipality(null);
    setStreetAddress('');
    
    if (onReset) {
      onReset();
    }
  };

  const isFormComplete = selectedState && selectedMunicipality && streetAddress.trim();

  return (
    <div className="address-form-container">
      <div className="form-header">
        <h2>Address Search</h2>
        <p>Please select a state, then a municipality, and finally enter a street address.</p>
      </div>

      <form onSubmit={handleSubmit} className="address-form">
        {/* Step 1: State Selection */}
        <div className="form-step">
          <div className="step-number">1</div>
          <StateSelect
            value={selectedState}
            onChange={handleStateChange}
            disabled={submitting}
          />
        </div>

        {/* Step 2: Municipality Selection */}
        {selectedState && (
          <div className="form-step">
            <div className="step-number">2</div>
            <MunicipalitySelect
              selectedState={selectedState}
              value={selectedMunicipality}
              onChange={handleMunicipalityChange}
              disabled={submitting}
            />
          </div>
        )}

        {/* Step 3: Address Autocomplete */}
        {selectedState && selectedMunicipality && (
          <div className="form-step">
            <div className="step-number">3</div>
            <AddressAutocomplete
              selectedState={selectedState}
              selectedMunicipality={selectedMunicipality}
              value={streetAddress}
              onChange={handleAddressChange}
              disabled={submitting}
            />
          </div>
        )}

        {/* Form Actions */}
        <div className="form-actions">
          <button
            type="button"
            onClick={handleReset}
            className="btn btn-secondary"
            disabled={submitting}
          >
            Reset Form
          </button>
          
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!isFormComplete || submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Address'}
          </button>
        </div>

        {/* Form Summary */}
        {isFormComplete && (
          <div className="form-summary">
            <h4>Selected Address:</h4>
            <div className="address-details">
              <div><strong>Street:</strong> {streetAddress}</div>
              <div><strong>Municipality:</strong> {selectedMunicipality.name} ({selectedMunicipality.type})</div>
              <div><strong>State:</strong> {selectedState.name} ({selectedState.code})</div>
              <div><strong>Full Address:</strong> {streetAddress}, {selectedMunicipality.name}, {selectedState.code}</div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}

export default AddressForm;