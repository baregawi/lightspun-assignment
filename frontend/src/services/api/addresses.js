import apiClient from './client';
import { API_ENDPOINTS, API_DEFAULTS } from '../../constants';
import { createQueryString } from '../../utils';

/**
 * Addresses API service
 */
export const addressesApi = {
  /**
   * Get address autocomplete suggestions
   */
  async autocomplete(query, limit = API_DEFAULTS.AUTOCOMPLETE_LIMIT) {
    if (!query || query.length < API_DEFAULTS.AUTOCOMPLETE_MIN_LENGTH) {
      return [];
    }

    const params = createQueryString({
      q: query,
      limit: limit,
    });

    const response = await apiClient.get(`${API_ENDPOINTS.ADDRESSES_AUTOCOMPLETE}?${params}`);
    return response.addresses || [];
  },

  /**
   * Get all addresses
   */
  async getAll(limit = 1000) {
    const params = createQueryString({ limit });
    const response = await apiClient.get(`${API_ENDPOINTS.ADDRESSES}?${params}`);
    return response || [];
  },

  /**
   * Get address by ID
   */
  async getById(addressId) {
    const response = await apiClient.get(API_ENDPOINTS.ADDRESS_BY_ID(addressId));
    return response;
  },

  /**
   * Create new address
   */
  async create(addressData) {
    const response = await apiClient.post(API_ENDPOINTS.ADDRESSES, addressData);
    return response;
  },

  /**
   * Update address
   */
  async update(addressId, addressData) {
    const response = await apiClient.put(API_ENDPOINTS.ADDRESS_BY_ID(addressId), addressData);
    return response;
  },

  /**
   * Delete address
   */
  async delete(addressId) {
    const response = await apiClient.delete(API_ENDPOINTS.ADDRESS_BY_ID(addressId));
    return response;
  },
};