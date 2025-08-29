import { API_BASE_URL, API_DEFAULTS } from '../../constants';
import { getApiErrorMessage, retryWithBackoff } from '../../utils';

/**
 * Base API client with error handling and retry logic
 */
class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = new Error(`API request failed: ${response.status} ${response.statusText}`);
        error.status = response.status;
        throw error;
      }

      return await response.json();
    } catch (error) {
      // Add user-friendly error message
      error.userMessage = getApiErrorMessage(error);
      throw error;
    }
  }

  async requestWithRetry(endpoint, options = {}, maxRetries = API_DEFAULTS.MAX_RETRIES) {
    return retryWithBackoff(
      () => this.request(endpoint, options),
      maxRetries
    );
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

export default new ApiClient();