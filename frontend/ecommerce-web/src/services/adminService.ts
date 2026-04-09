import api from './api';

export interface DashboardStats {
  totalRevenue: number;
  totalOrders: number;
  totalUsers: number;
  totalProducts: number;
  revenueByDay: Array<{ date: string; revenue: number }>;
  ordersByStatus: Record<string, number>;
  topProducts: Array<{
    productId: string;
    name: string;
    totalSold: number;
    revenue: number;
  }>;
}

export interface UsersResponse {
  users: Array<{
    id: string;
    email: string;
    name: string;
    role: string;
    createdAt: string;
  }>;
  total: number;
  page: number;
  limit: number;
}

export const adminService = {
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/admin/dashboard');
    return response.data;
  },

  async getUsers(params?: {
    page?: number;
    limit?: number;
    role?: string;
  }): Promise<UsersResponse> {
    const response = await api.get<UsersResponse>('/admin/users', { params });
    return response.data;
  },

  async getOrders(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Promise<{
    orders: Array<{
      id: string;
      userId: string;
      total: number;
      status: string;
      createdAt: string;
    }>;
    total: number;
    page: number;
    limit: number;
  }> {
    const response = await api.get('/admin/orders', { params });
    return response.data;
  },

  async updateOrderStatus(orderId: string, status: string): Promise<void> {
    await api.put(`/admin/orders/${orderId}/status`, { status });
  },

  async updateUserRole(userId: string, role: string): Promise<void> {
    await api.put(`/admin/users/${userId}/role`, { role });
  },
};

export default adminService;