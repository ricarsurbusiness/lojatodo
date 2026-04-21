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
    const response = await api.get<SalesAnalytics>('/api/v1/analytics/sales');
    return response.data;
  },

  async getOrdersAnalytics(): Promise<OrdersAnalytics> {
    const response = await api.get<OrdersAnalytics>('/api/v1/analytics/orders');
    return response.data;
  },

  async getProductsAnalytics(): Promise<ProductsAnalytics> {
    const response = await api.get<ProductsAnalytics>('/api/v1/analytics/products');
    return response.data;
  },
};

export default analyticsService;