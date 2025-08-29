/**
 * API-related constants
 */

export const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

export const API_ENDPOINTS = {
  STATES: '/states',
  MUNICIPALITIES: (stateCode) => `/states/${stateCode}/municipalities`,
  ADDRESSES_AUTOCOMPLETE: '/addresses/autocomplete',
  ADDRESSES: '/addresses',
  ADDRESS_BY_ID: (id) => `/addresses/${id}`,
};

export const API_DEFAULTS = {
  AUTOCOMPLETE_LIMIT: 10,
  AUTOCOMPLETE_MIN_LENGTH: 2,
  DEBOUNCE_DELAY: 300,
  REQUEST_TIMEOUT: 10000,
  MAX_RETRIES: 3,
};