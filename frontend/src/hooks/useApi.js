import { useState, useCallback } from 'react';

/**
 * Custom hook for API calls with loading and error states
 */
export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiFunction, ...args) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction(...args);
      return result;
    } catch (err) {
      setError(err.message || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setLoading(false);
  }, []);

  return { loading, error, execute, reset };
}

/**
 * Custom hook for API calls with data caching
 */
export function useApiData(apiFunction, dependencies = []) {
  const [data, setData] = useState(null);
  const { loading, error, execute, reset } = useApi();

  const fetch = useCallback(async (...args) => {
    try {
      const result = await execute(apiFunction, ...args);
      setData(result);
      return result;
    } catch (err) {
      setData(null);
      throw err;
    }
  }, [execute, apiFunction]);

  const refetch = useCallback(() => {
    if (dependencies.length > 0) {
      return fetch(...dependencies);
    }
  }, [fetch, dependencies]);

  const clear = useCallback(() => {
    setData(null);
    reset();
  }, [reset]);

  return { 
    data, 
    loading, 
    error, 
    fetch, 
    refetch, 
    clear,
    hasData: data !== null 
  };
}