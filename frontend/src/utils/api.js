/**
 * API utility functions
 */

/**
 * Check if error is a network error
 */
export function isNetworkError(error) {
  return error.name === 'TypeError' && error.message.includes('fetch');
}

/**
 * Check if error is a timeout error
 */
export function isTimeoutError(error) {
  return error.name === 'AbortError' || error.message.includes('timeout');
}

/**
 * Get user-friendly error message from API error
 */
export function getApiErrorMessage(error) {
  if (isNetworkError(error)) {
    return 'Network connection failed. Please check your internet connection.';
  }
  
  if (isTimeoutError(error)) {
    return 'Request timed out. Please try again.';
  }
  
  if (error.status) {
    switch (error.status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 404:
        return 'The requested resource was not found.';
      case 500:
        return 'Server error. Please try again later.';
      case 503:
        return 'Service temporarily unavailable. Please try again later.';
      default:
        return `Request failed with status ${error.status}`;
    }
  }
  
  return error.message || 'An unexpected error occurred';
}

/**
 * Create query string from parameters
 */
export function createQueryString(params) {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      searchParams.append(key, value.toString());
    }
  });
  
  return searchParams.toString();
}

/**
 * Retry function with exponential backoff
 */
export async function retryWithBackoff(fn, maxRetries = 3, baseDelay = 1000) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Don't retry client errors (4xx)
      if (error.status >= 400 && error.status < 500) {
        throw error;
      }
      
      // Wait before retrying (exponential backoff)
      if (i < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, i);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError;
}