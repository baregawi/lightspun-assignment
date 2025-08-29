/**
 * Validation utilities
 */

/**
 * Check if a value is required and not empty
 */
export function isRequired(value) {
  return value !== null && value !== undefined && value !== '';
}

/**
 * Validate form data structure
 */
export function validateFormData(data) {
  const errors = [];

  if (!data.state) {
    errors.push('State is required');
  }

  if (!data.municipality) {
    errors.push('Municipality is required');
  }

  if (!isRequired(data.streetAddress)) {
    errors.push('Street address is required');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Validate state selection
 */
export function validateState(state) {
  return state && state.code && state.name;
}

/**
 * Validate municipality selection
 */
export function validateMunicipality(municipality) {
  return municipality && municipality.id && municipality.name;
}

/**
 * Validate street address
 */
export function validateStreetAddress(address) {
  return isRequired(address) && address.trim().length >= 2;
}