/**
 * API service functions for communicating with the Lightspun backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

/**
 * Generic API request function
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
}

/**
 * Get all US states
 */
export async function getStates() {
  const response = await apiRequest('/states');
  return response.states || [];
}

/**
 * Get municipalities in a specific state
 */
export async function getMunicipalities(stateCode) {
  if (!stateCode) {
    throw new Error('State code is required');
  }
  
  const response = await apiRequest(`/states/${stateCode}/municipalities`);
  return response.municipalities || [];
}

/**
 * Get address autocomplete suggestions
 */
export async function getAddressAutocomplete(query, limit = 10) {
  if (!query || query.length < 2) {
    return [];
  }

  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
  });

  const response = await apiRequest(`/addresses/autocomplete?${params}`);
  return response.addresses || [];
}

/**
 * Get address by ID
 */
export async function getAddressById(addressId) {
  return await apiRequest(`/addresses/${addressId}`);
}

/**
 * Create a new address
 */
export async function createAddress(addressData) {
  return await apiRequest('/addresses', {
    method: 'POST',
    body: JSON.stringify(addressData),
  });
}

// Export API utilities
export const api = {
  getStates,
  getMunicipalities, 
  getAddressAutocomplete,
  getAddressById,
  createAddress,
};