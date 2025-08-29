/**
 * Formatting utilities
 */

/**
 * Format state display text
 */
export function formatState(state) {
  if (!state || !state.name || !state.code) return '';
  return `${state.name} (${state.code})`;
}

/**
 * Format municipality display text
 */
export function formatMunicipality(municipality) {
  if (!municipality || !municipality.name) return '';
  return municipality.type 
    ? `${municipality.name} (${municipality.type})`
    : municipality.name;
}

/**
 * Format full address
 */
export function formatFullAddress(streetAddress, municipality, state) {
  const parts = [];
  
  if (streetAddress && streetAddress.trim()) {
    parts.push(streetAddress.trim());
  }
  
  if (municipality && municipality.name) {
    parts.push(municipality.name);
  }
  
  if (state && state.code) {
    parts.push(state.code);
  }
  
  return parts.join(', ');
}

/**
 * Format error message for display
 */
export function formatError(error) {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error && error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
}

/**
 * Format count text (singular/plural)
 */
export function formatCount(count, singular, plural = null) {
  const pluralForm = plural || `${singular}s`;
  return count === 1 ? `${count} ${singular}` : `${count} ${pluralForm}`;
}