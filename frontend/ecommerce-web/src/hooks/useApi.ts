import { useState, useCallback } from 'react';
import api from '../services/api';

export interface UseApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

export interface UseApiOptions {
  immediate?: boolean;
}

export function useApi<T>(
  fetchFn: () => Promise<T>,
  options: UseApiOptions = {}
): UseApiState<T> & {
  execute: () => Promise<T | null>;
  reset: () => void;
} {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(options.immediate ?? false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (): Promise<T | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
      return result;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [fetchFn]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    isLoading,
    error,
    execute,
    reset,
  };
}

export function useApiPost<TRequest, TResponse>(
  url: string,
  options: UseApiOptions = {}
): UseApiState<TResponse> & {
  execute: (data: TRequest) => Promise<TResponse | null>;
  reset: () => void;
} {
  const [data, setData] = useState<TResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (requestData: TRequest): Promise<TResponse | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.post<TResponse>(url, requestData);
      setData(response.data);
      return response.data;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [url]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    isLoading,
    error,
    execute,
    reset,
  };
}

export function useApiGet<TResponse>(
  url: string,
  options: UseApiOptions = {}
): UseApiState<TResponse> & {
  execute: () => Promise<TResponse | null>;
  reset: () => void;
} {
  const [data, setData] = useState<TResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(options.immediate ?? false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (): Promise<TResponse | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<TResponse>(url);
      setData(response.data);
      return response.data;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [url]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    isLoading,
    error,
    execute,
    reset,
  };
}
