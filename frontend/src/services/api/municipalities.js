import apiClient from './client';
import { API_ENDPOINTS } from '../../constants';

/**
 * Municipalities API service
 */
export const municipalitiesApi = {
  /**
   * Get municipalities by state code
   */
  async getByStateCode(stateCode) {
    const response = await apiClient.get(API_ENDPOINTS.MUNICIPALITIES(stateCode));
    return response.municipalities || [];
  },

  /**
   * Get municipality by ID
   */
  async getById(municipalityId) {
    const response = await apiClient.get(`/municipalities/${municipalityId}`);
    return response;
  },

  /**
   * Create new municipality
   */
  async create(municipalityData) {
    const response = await apiClient.post('/municipalities', municipalityData);
    return response;
  },

  /**
   * Update municipality
   */
  async update(municipalityId, municipalityData) {
    const response = await apiClient.put(`/municipalities/${municipalityId}`, municipalityData);
    return response;
  },

  /**
   * Delete municipality
   */
  async delete(municipalityId) {
    const response = await apiClient.delete(`/municipalities/${municipalityId}`);
    return response;
  },
};