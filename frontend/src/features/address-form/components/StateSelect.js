import React, { useEffect } from 'react';
import { FormGroup, Select, StepIndicator } from '../../../components/ui';
import { useApiData } from '../../../hooks';
import { statesApi } from '../../../services/api';
import { FORM_LABELS, LOADING_MESSAGES, ERROR_MESSAGES, PLACEHOLDERS } from '../../../constants';
import { formatState, formatCount } from '../../../utils';

/**
 * State selection component with step indicator
 */
function StateSelect({ value, onChange, disabled = false, step = 1 }) {
  const { 
    data: states, 
    loading, 
    error, 
    fetch: fetchStates,
    hasData 
  } = useApiData(statesApi.getAll);

  useEffect(() => {
    fetchStates();
  }, [fetchStates]);

  const handleChange = (selectedState) => {
    onChange(selectedState);
  };

  const getHelpText = () => {
    if (hasData && states.length > 0) {
      return formatCount(states.length, 'state');
    }
    return null;
  };

  return (
    <div className="form-step">
      <StepIndicator step={step} active={!value} completed={!!value} />
      
      <FormGroup
        label={FORM_LABELS.STATE}
        required
        error={error}
        helpText={getHelpText()}
        id="state-select"
      >
        <Select
          id="state-select"
          value={value}
          onChange={handleChange}
          options={states || []}
          placeholder={PLACEHOLDERS.STATE_SELECT}
          disabled={disabled}
          loading={loading}
          error={error ? ERROR_MESSAGES.STATES_LOAD_FAILED : null}
          onRetry={fetchStates}
          getOptionValue={(state) => state.code}
          getOptionLabel={(state) => formatState(state)}
          required
        />
      </FormGroup>
    </div>
  );
}

export default StateSelect;