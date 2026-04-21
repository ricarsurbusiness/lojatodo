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
    const response = await api.get<any>('/api/v1/admin/dashboard');
    const data = response.data;
    
    // Transform backend snake_case to frontend camelCase
    return {
      totalRevenue: parseFloat(data.total_revenue) || 0,
      totalOrders: data.total_orders || 0,
      totalUsers: data.total_users || 0,
      totalProducts: data.total_products || 0,
      revenueByDay: data.revenue_by_day || [],
      ordersByStatus: data.orders_by_status || {},
      topProducts: (data.top_products || []).map((p: any) => ({
        productId: String(p.product_id),
        name: p.name,
        totalSold: p.total_sold,
        revenue: parseFloat(p.revenue)
      }))
    };
  },

  async getUsers(params?: {
    page?: number;
    limit?: number;
    role?: string;
  }): Promise<UsersResponse> {
    const response = await api.get('/api/v1/admin/users', { params });
    const data = response.data;
    
    // Transform backend snake_case to frontend camelCase
    return {
      users: (data.items || []).map((user: any) => ({
        id: String(user.id),
        email: user.email,
        name: user.name || '',
        role: user.role || user.roles?.[0] || 'cliente',
        roles: user.roles || [user.role || 'cliente'],
        createdAt: user.created_at
      })),
      total: data.total || 0,
      page: data.page || 1,
      limit: data.limit || 20
    };
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
    const response = await api.get('/api/v1/admin/orders', { params });
    const data = response.data;
    
    // Transform backend snake_case to frontend camelCase
    return {
      orders: (data.items || []).map((order: any) => ({
        id: String(order.id),
        userId: String(order.user_id),
        total: parseFloat(order.total_amount) || 0,
        status: order.status,
        createdAt: order.created_at
      })),
      total: data.total || 0,
      page: data.page || 1,
      limit: data.limit || 20
    };
  },

  async updateOrderStatus(orderId: string, status: string): Promise<void> {
    // Map status to the format expected by order-service
    const statusMap: Record<string, string> = {
      'pendiente': 'pendiente',
      'confirmado': 'confirmado', 
      'procesamiento': 'procesamiento',
      'enviado': 'enviado',
      'entregado': 'entregado',
      'cancelado': 'cancelado',
      'fallido': 'fallido',
    };
    
    const mappedStatus = statusMap[status] || status;
    await api.put(`/api/v1/orders/${orderId}/status`, { status: mappedStatus });
  },

  async addUserRole(userId: string, role: string): Promise<void> {
    // Note: admin role can only be assigned by superAdmin
    await api.post('/api/v1/assign-role', { user_id: parseInt(userId), role });
  },

  async removeUserRole(userId: string, role: string): Promise<void> {
    await api.post('/api/v1/remove-role', { user_id: parseInt(userId), role });
  },

  async updateUserRole(userId: string, role: string): Promise<void> {
    await api.put(`/api/v1/admin/users/${userId}/role`, { role });
  },
};

export default adminService;