import React, { useState } from 'react';
import { Button } from '../../components/ui';
import { 
  StateSelect, 
  MunicipalitySelect, 
  AddressAutocomplete, 
  AddressFormSummary 
} from './components';
import { validateFormData } from '../../utils';
import { FORM_LABELS, ERROR_MESSAGES, SUCCESS_MESSAGES } from '../../constants';

/**
 * Main address form component that orchestrates the multi-step selection process
 */
function AddressForm({ onSubmit, onReset, className = 'address-form-container' }) {
  const [selectedState, setSelectedState] = useState(null);
  const [selectedMunicipality, setSelectedMunicipality] = useState(null);
  const [streetAddress, setStreetAddress] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const handleStateChange = (state) => {
    setSelectedState(state);
    // Reset dependent fields when state changes
    setSelectedMunicipality(null);
    setStreetAddress('');
    setSubmitError(null);
  };

  const handleMunicipalityChange = (municipality) => {
    setSelectedMunicipality(municipality);
    // Reset address when municipality changes
    setStreetAddress('');
    setSubmitError(null);
  };

  const handleAddressChange = (address) => {
    setStreetAddress(address);
    setSubmitError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    const formData = {
      state: selectedState,
      municipality: selectedMunicipality,
      streetAddress: streetAddress.trim(),
    };

    // Validate form data
    const validation = validateFormData(formData);
    if (!validation.isValid) {
      setSubmitError(validation.errors.join(', '));
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      if (onSubmit) {
        await onSubmit(formData);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setSubmitError(error.message || ERROR_MESSAGES.FORM_SUBMIT_FAILED);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setSelectedState(null);
    setSelectedMunicipality(null);
    setStreetAddress('');
    setSubmitError(null);
    
    if (onReset) {
      onReset();
    }
  };

  const isFormComplete = selectedState && selectedMunicipality && streetAddress.trim();

  return (
    <div className={className}>
      <div className="form-header">
        <h2>Address Search</h2>
        <p>Please select a state, then a municipality, and finally enter a street address.</p>
      </div>

      <form onSubmit={handleSubmit} className="address-form">
        {/* Step 1: State Selection */}
        <StateSelect
          value={selectedState}
          onChange={handleStateChange}
          disabled={submitting}
          step={1}
        />

        {/* Step 2: Municipality Selection */}
        <MunicipalitySelect
          selectedState={selectedState}
          value={selectedMunicipality}
          onChange={handleMunicipalityChange}
          disabled={submitting}
          step={2}
        />

        {/* Step 3: Address Autocomplete */}
        <AddressAutocomplete
          selectedState={selectedState}
          selectedMunicipality={selectedMunicipality}
          value={streetAddress}
          onChange={handleAddressChange}
          disabled={submitting}
          step={3}
        />

        {/* Form Actions */}
        <div className="form-actions">
          <Button
            type="button"
            variant="secondary"
            onClick={handleReset}
            disabled={submitting}
          >
            {FORM_LABELS.RESET}
          </Button>
          
          <Button
            type="submit"
            variant="primary"
            disabled={!isFormComplete}
            loading={submitting}
          >
            {FORM_LABELS.SUBMIT}
          </Button>
        </div>

        {/* Submit Error */}
        {submitError && (
          <div className="error-message" role="alert">
            {submitError}
          </div>
        )}

        {/* Form Summary */}
        <AddressFormSummary
          selectedState={selectedState}
          selectedMunicipality={selectedMunicipality}
          streetAddress={streetAddress}
        />
      </form>
    </div>
  );
}

export default AddressForm;