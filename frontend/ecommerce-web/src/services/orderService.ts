import api from './api';

export interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  price: number;
}

export interface ShippingAddress {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

export interface Order {
  id: string;
  userId: string;
  items: OrderItem[];
  total: number;
  status: string;
  shippingAddress: ShippingAddress;
  createdAt: string;
  updatedAt: string;
}

export interface CreateOrderRequest {
  items: Array<{
    productId: string;
    quantity: number;
  }>;
  shippingAddress: ShippingAddress;
}

export interface GetOrdersResponse {
  orders: Order[];
  total: number;
  page: number;
  limit: number;
}

export const orderService = {
  async createOrder(data: CreateOrderRequest): Promise<Order> {
    const response = await api.post<Order>('/orders', data);
    return response.data;
  },

  async getOrders(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Promise<GetOrdersResponse> {
    const response = await api.get<GetOrdersResponse>('/orders', { params });
    return response.data;
  },

  async getOrder(id: string): Promise<Order> {
    const response = await api.get<Order>(`/orders/${id}`);
    return response.data;
  },

  async cancelOrder(id: string): Promise<Order> {
    const response = await api.post<Order>(`/orders/${id}/cancel`);
    return response.data;
  },
};

export default orderService;