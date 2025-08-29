import React, { useState, useEffect } from 'react';
import { getMunicipalities } from '../services/api';

/**
 * Municipality selection dropdown component
 */
function MunicipalitySelect({ selectedState, value, onChange, disabled = false }) {
  const [municipalities, setMunicipalities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (selectedState && selectedState.code) {
      loadMunicipalities(selectedState.code);
    } else {
      setMunicipalities([]);
      setError(null);
    }
  }, [selectedState]);

  const loadMunicipalities = async (stateCode) => {
    try {
      setLoading(true);
      setError(null);
      const municipalitiesData = await getMunicipalities(stateCode);
      setMunicipalities(municipalitiesData);
    } catch (err) {
      setError('Failed to load municipalities. Please try again.');
      console.error('Error loading municipalities:', err);
      setMunicipalities([]);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event) => {
    const selectedMunicipalityId = parseInt(event.target.value);
    const selectedMunicipality = municipalities.find(
      municipality => municipality.id === selectedMunicipalityId
    );
    onChange(selectedMunicipality);
  };

  const handleRetry = () => {
    if (selectedState && selectedState.code) {
      loadMunicipalities(selectedState.code);
    }
  };

  // Don't render if no state is selected
  if (!selectedState) {
    return null;
  }

  if (loading) {
    return (
      <div className="form-group">
        <label htmlFor="municipality-select">Municipality:</label>
        <select id="municipality-select" disabled className="form-control">
          <option>Loading municipalities...</option>
        </select>
      </div>
    );
  }

  if (error) {
    return (
      <div className="form-group">
        <label htmlFor="municipality-select">Municipality:</label>
        <select id="municipality-select" disabled className="form-control error">
          <option>Error loading municipalities</option>
        </select>
        <div className="error-message">{error}</div>
        <button 
          type="button" 
          onClick={handleRetry}
          className="retry-button"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="form-group">
      <label htmlFor="municipality-select">
        Municipality in {selectedState.name}: <span className="required">*</span>
      </label>
      <select
        id="municipality-select"
        value={value ? value.id : ''}
        onChange={handleChange}
        disabled={disabled}
        className="form-control"
        required
      >
        <option value="">Select a municipality...</option>
        {municipalities.map((municipality) => (
          <option key={municipality.id} value={municipality.id}>
            {municipality.name} {municipality.type && `(${municipality.type})`}
          </option>
        ))}
      </select>
      {municipalities.length > 0 && (
        <small className="form-text">
          {municipalities.length} municipalities available in {selectedState.name}
        </small>
      )}
      {municipalities.length === 0 && !loading && !error && (
        <small className="form-text text-muted">
          No municipalities found for {selectedState.name}
        </small>
      )}
    </div>
  );
}

export default MunicipalitySelect;