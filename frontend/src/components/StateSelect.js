import React, { useState, useEffect } from 'react';
import { getStates } from '../services/api';

/**
 * State selection dropdown component
 */
function StateSelect({ value, onChange, disabled = false }) {
  const [states, setStates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStates();
  }, []);

  const loadStates = async () => {
    try {
      setLoading(true);
      setError(null);
      const statesData = await getStates();
      setStates(statesData);
    } catch (err) {
      setError('Failed to load states. Please try again.');
      console.error('Error loading states:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event) => {
    const selectedStateCode = event.target.value;
    const selectedState = states.find(state => state.code === selectedStateCode);
    onChange(selectedState);
  };

  if (loading) {
    return (
      <div className="form-group">
        <label htmlFor="state-select">State:</label>
        <select id="state-select" disabled className="form-control">
          <option>Loading states...</option>
        </select>
      </div>
    );
  }

  if (error) {
    return (
      <div className="form-group">
        <label htmlFor="state-select">State:</label>
        <select id="state-select" disabled className="form-control error">
          <option>Error loading states</option>
        </select>
        <div className="error-message">{error}</div>
        <button 
          type="button" 
          onClick={loadStates}
          className="retry-button"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="form-group">
      <label htmlFor="state-select">
        State: <span className="required">*</span>
      </label>
      <select
        id="state-select"
        value={value ? value.code : ''}
        onChange={handleChange}
        disabled={disabled}
        className="form-control"
        required
      >
        <option value="">Select a state...</option>
        {states.map((state) => (
          <option key={state.code} value={state.code}>
            {state.name} ({state.code})
          </option>
        ))}
      </select>
      {states.length > 0 && (
        <small className="form-text">
          {states.length} states available
        </small>
      )}
    </div>
  );
}

export default StateSelect;