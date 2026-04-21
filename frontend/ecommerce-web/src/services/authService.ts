import api from './api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
    roles?: string[];
  };
}

// Backend response types
interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface RegisterResponse {
  id: number;
  email: string;
  name: string;
  roles: string[];
  created_at: string;
}

interface VerifyResponse {
  user_id: number;
  email: string;
  roles: string[];
}

export interface VerifyTokenResponse {
  valid: boolean;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
    roles?: string[];
  };
}

export interface UpdateProfileRequest {
  name: string;
  email?: string;
}

export interface UpdateProfileResponse {
  id: string;
  email: string;
  name: string;
  role: string;
}

export const authService = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<LoginResponse>('/api/v1/auth/login', data);
    const loginData = response.data;
    
    // Store token first so subsequent requests include it
    localStorage.setItem('token', loginData.access_token);
    
    // Get user info from verify endpoint
    const verifyResponse = await api.get<VerifyResponse>('/api/v1/auth/verify');
    const verifyData = verifyResponse.data;
    
    return {
      token: loginData.access_token,
      user: {
        id: String(verifyData.user_id),
        email: verifyData.email,
        name: '', // Will be fetched later if needed
        role: verifyData.roles[0] || 'cliente',
        roles: verifyData.roles || []
      }
    };
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<RegisterResponse>('/api/v1/auth/register', data);
    const registerData = response.data;
    
    // Login after register
    const loginResponse = await api.post<LoginResponse>('/api/v1/auth/login', {
      email: data.email,
      password: data.password
    });
    
    // Store token first
    localStorage.setItem('token', loginResponse.data.access_token);
    
    return {
      token: loginResponse.data.access_token,
      user: {
        id: String(registerData.id),
        email: registerData.email,
        name: registerData.name,
        role: registerData.roles[0] || 'cliente',
        roles: registerData.roles || []
      }
    };
  },

  async verifyToken(): Promise<VerifyTokenResponse> {
    const response = await api.get<VerifyResponse>('/api/v1/auth/verify');
    const data = response.data;
    
    return {
      valid: true,
      user: {
        id: String(data.user_id),
        email: data.email,
        name: '',
        role: data.roles[0] || 'cliente',
        roles: data.roles || []
      }
    };
  },

  async logout(): Promise<void> {
    // No backend logout endpoint, just clear local token
    localStorage.removeItem('token');
  },

  async updateProfile(data: UpdateProfileRequest): Promise<UpdateProfileResponse> {
    const response = await api.put<UpdateProfileResponse>('/api/v1/auth/profile', data);
    return response.data;
  },
};

export default authService;