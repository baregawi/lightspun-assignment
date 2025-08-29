import React from 'react';
import LoadingState from './LoadingState';
import ErrorState from './ErrorState';

/**
 * Reusable select component with loading and error states
 */
function Select({
  id,
  value,
  onChange,
  options = [],
  placeholder = 'Select an option...',
  disabled = false,
  loading = false,
  error,
  onRetry,
  formatOption = (option) => option,
  getOptionValue = (option) => option,
  getOptionLabel = (option) => option,
  required = false,
  ...props
}) {
  const handleChange = (event) => {
    const selectedValue = event.target.value;
    const selectedOption = options.find(option => 
      getOptionValue(option).toString() === selectedValue
    );
    onChange(selectedOption);
  };

  if (loading) {
    return (
      <select id={id} disabled className="form-control">
        <option>Loading...</option>
      </select>
    );
  }

  if (error) {
    return (
      <>
        <select id={id} disabled className="form-control error">
          <option>Error loading options</option>
        </select>
        <ErrorState 
          message={error} 
          onRetry={onRetry}
          showRetry={!!onRetry}
        />
      </>
    );
  }

  return (
    <select
      id={id}
      value={value ? getOptionValue(value).toString() : ''}
      onChange={handleChange}
      disabled={disabled}
      className="form-control"
      required={required}
      {...props}
    >
      <option value="">{placeholder}</option>
      {options.map((option, index) => {
        const optionValue = getOptionValue(option);
        const optionLabel = getOptionLabel(option);
        return (
          <option key={index} value={optionValue.toString()}>
            {optionLabel}
          </option>
        );
      })}
    </select>
  );
}

export default Select;