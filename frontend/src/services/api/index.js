/**
 * API Services module - Centralized API service layer
 */

// Import APIs for backward compatibility functions
import { statesApi } from './states';
import { municipalitiesApi } from './municipalities';
import { addressesApi } from './addresses';

export { default as apiClient } from './client';
export { statesApi } from './states';
export { municipalitiesApi } from './municipalities';
export { addressesApi } from './addresses';

// Backward compatibility - re-export main functions with original names
export const getStates = () => statesApi.getAll();
export const getMunicipalities = (stateCode) => municipalitiesApi.getByStateCode(stateCode);
export const getAddressAutocomplete = (query, limit) => addressesApi.autocomplete(query, limit);
export const getAddressById = (addressId) => addressesApi.getById(addressId);
export const createAddress = (addressData) => addressesApi.create(addressData);