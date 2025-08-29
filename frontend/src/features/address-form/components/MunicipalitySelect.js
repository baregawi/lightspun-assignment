import React, { useEffect } from 'react';
import { FormGroup, Select, StepIndicator } from '../../../components/ui';
import { useApiData } from '../../../hooks';
import { municipalitiesApi } from '../../../services/api';
import { FORM_LABELS, ERROR_MESSAGES, PLACEHOLDERS } from '../../../constants';
import { formatMunicipality, formatCount } from '../../../utils';

/**
 * Municipality selection component with step indicator
 */
function MunicipalitySelect({ 
  selectedState, 
  value, 
  onChange, 
  disabled = false, 
  step = 2 
}) {
  const { 
    data: municipalities, 
    loading, 
    error, 
    fetch: fetchMunicipalities,
    clear,
    hasData 
  } = useApiData(municipalitiesApi.getByStateCode);

  useEffect(() => {
    if (selectedState && selectedState.code) {
      fetchMunicipalities(selectedState.code);
    } else {
      clear();
    }
  }, [selectedState, fetchMunicipalities, clear]);

  const handleChange = (selectedMunicipality) => {
    onChange(selectedMunicipality);
  };

  const handleRetry = () => {
    if (selectedState && selectedState.code) {
      fetchMunicipalities(selectedState.code);
    }
  };

  const getLabel = () => {
    return selectedState 
      ? `${FORM_LABELS.MUNICIPALITY} in ${selectedState.name}`
      : FORM_LABELS.MUNICIPALITY;
  };

  const getHelpText = () => {
    if (!selectedState) return null;
    
    if (hasData) {
      if (municipalities && municipalities.length > 0) {
        return `${formatCount(municipalities.length, 'municipality', 'municipalities')} available in ${selectedState.name}`;
      } else if (!loading && !error) {
        return `No municipalities found for ${selectedState.name}`;
      }
    }
    return null;
  };

  // Don't render if no state is selected
  if (!selectedState) {
    return null;
  }

  return (
    <div className="form-step">
      <StepIndicator 
        step={step} 
        active={!!selectedState && !value} 
        completed={!!value} 
      />
      
      <FormGroup
        label={getLabel()}
        required
        error={error}
        helpText={getHelpText()}
        id="municipality-select"
      >
        <Select
          id="municipality-select"
          value={value}
          onChange={handleChange}
          options={municipalities || []}
          placeholder={PLACEHOLDERS.MUNICIPALITY_SELECT}
          disabled={disabled}
          loading={loading}
          error={error ? ERROR_MESSAGES.MUNICIPALITIES_LOAD_FAILED : null}
          onRetry={handleRetry}
          getOptionValue={(municipality) => municipality.id}
          getOptionLabel={(municipality) => formatMunicipality(municipality)}
          required
        />
      </FormGroup>
    </div>
  );
}

export default MunicipalitySelect;