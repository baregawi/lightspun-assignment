import apiClient from './client';
import { API_ENDPOINTS } from '../../constants';

/**
 * States API service
 */
export const statesApi = {
  /**
   * Get all US states
   */
  async getAll() {
    const response = await apiClient.get(API_ENDPOINTS.STATES);
    return response.states || [];
  },

  /**
   * Get state by code
   */
  async getByCode(stateCode) {
    const response = await apiClient.get(`${API_ENDPOINTS.STATES}/${stateCode}`);
    return response;
  },

  /**
   * Create new state
   */
  async create(stateData) {
    const response = await apiClient.post(API_ENDPOINTS.STATES, stateData);
    return response;
  },

  /**
   * Update state
   */
  async update(stateId, stateData) {
    const response = await apiClient.put(`${API_ENDPOINTS.STATES}/${stateId}`, stateData);
    return response;
  },

  /**
   * Delete state
   */
  async delete(stateId) {
    const response = await apiClient.delete(`${API_ENDPOINTS.STATES}/${stateId}`);
    return response;
  },
};