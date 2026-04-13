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
  };
}

export interface VerifyTokenResponse {
  valid: boolean;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
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
    const response = await api.post<AuthResponse>('/api/v1/auth/login', data);
    return response.data;
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/v1/auth/register', data);
    return response.data;
  },

  async verifyToken(): Promise<VerifyTokenResponse> {
    const response = await api.get<VerifyTokenResponse>('/api/v1/auth/verify');
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/api/v1/auth/logout');
    } finally {
      localStorage.removeItem('token');
    }
  },

  async updateProfile(data: UpdateProfileRequest): Promise<UpdateProfileResponse> {
    const response = await api.put<UpdateProfileResponse>('/api/v1/auth/profile', data);
    return response.data;
  },
};

export default authService;