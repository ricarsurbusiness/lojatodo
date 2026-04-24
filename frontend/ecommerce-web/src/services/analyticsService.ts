import api from './api';

export interface SalesAnalytics {
  today: number;
  week: number;
  month: number;
  todayChange: number;
  weekChange: number;
  monthChange: number;
}

export interface OrdersAnalytics {
  today: number;
  week: number;
  month: number;
  pending: number;
  processing: number;
  shipped: number;
  delivered: number;
  cancelled: number;
}

export interface ProductsAnalytics {
  totalProducts: number;
  lowStock: number;
  outOfStock: number;
  topProducts: Array<{
    id: string;
    name: string;
    sold: number;
    revenue: number;
    stock: number;
  }>;
}

export const analyticsService = {
  async getSalesAnalytics(): Promise<SalesAnalytics> {
    try {
      // Try admin dashboard first
      const response = await api.get<any>('/api/v1/admin/dashboard');
      const data = response.data;
      
      return {
        today: parseFloat(data.total_revenue) * 0.1 || 0,  // Simplified estimate
        week: parseFloat(data.total_revenue) * 0.3 || 0,
        month: parseFloat(data.total_revenue) || 0,
        todayChange: 0,
        weekChange: 0,
        monthChange: 0,
      };
    } catch {
      return {
        today: 0,
        week: 0,
        month: 0,
        todayChange: 0,
        weekChange: 0,
        monthChange: 0,
      };
    }
  },

  async getOrdersAnalytics(): Promise<OrdersAnalytics> {
    try {
      const response = await api.get<any>('/api/v1/admin/orders', { limit: 100 });
      const items = response.data.items || [];
      
      const byStatus: Record<string, number> = {};
      for (const order of items) {
        const status = order.status;
        byStatus[status] = (byStatus[status] || 0) + 1;
      }
      
      return {
        today: 0,
        week: 0,
        month: items.length,
        pending: byStatus.pendiente || 0,
        processing: byStatus.procesamiento || 0,
        shipped: byStatus.enviado || 0,
        delivered: byStatus.entregado || 0,
        cancelled: byStatus.cancelado || 0,
      };
    } catch {
      return {
        today: 0,
        week: 0,
        month: 0,
        pending: 0,
        processing: 0,
        shipped: 0,
        delivered: 0,
        cancelled: 0,
      };
    }
  },

  async getProductsAnalytics(): Promise<ProductsAnalytics> {
    try {
      const response = await api.get<any>('/api/v1/products', { limit: 100 });
      const products = response.data.products || [];
      
      return {
        totalProducts: products.length,
        lowStock: products.filter((p: any) => p.stock < 10).length,
        outOfStock: products.filter((p: any) => p.stock === 0).length,
        topProducts: products.slice(0, 10).map((p: any) => ({
          id: String(p.id),
          name: p.name,
          sold: p.stock || 0,
          revenue: parseFloat(p.price) * (p.stock || 0),
          stock: p.stock || 0,
        })),
      };
    } catch {
      return {
        totalProducts: 0,
        lowStock: 0,
        outOfStock: 0,
        topProducts: [],
      };
    }
  },
};

export default analyticsService;