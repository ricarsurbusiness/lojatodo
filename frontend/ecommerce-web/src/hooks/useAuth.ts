import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export interface UseAuthReturn {
  user: import('../types').User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: import('../services/authService').LoginRequest) => Promise<void>;
  register: (data: import('../services/authService').RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export function useAuth(): UseAuthReturn {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context as UseAuthReturn;
}
