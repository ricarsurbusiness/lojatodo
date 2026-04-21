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

// Backend request format
interface OrderCreateItem {
  product_id: number;
  quantity: number;
  unit_price: number;
}

interface OrderCreateRequest {
  items: OrderCreateItem[];
  shipping_address: {
    street: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
  };
}

export interface CreateOrderRequest {
  items: Array<{
    productId: string;
    quantity: number;
  }>;
  shippingAddress: ShippingAddress;
}

// Backend response format
interface OrdersApiResponse {
  items: Order[];
  total: number;
  page: number;
  pages: number;
}

export interface GetOrdersResponse {
  orders: Order[];
  total: number;
  page: number;
  limit: number;
}

// Backend order response
interface OrderApiResponse {
  id: number;
  user_id: number;
  status: string;
  total_amount: string;
  shipping_address: {
    street: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
  };
  created_at: string;
  updated_at: string;
  items: Array<{
    id: number;
    product_id: number;
    quantity: number;
    unit_price: string;
  }>;
}

export const orderService = {
  async createOrder(data: CreateOrderRequest, cartItems?: Array<{ productId: string; price: number }>): Promise<Order> {
    // Transform frontend format to backend format
    const apiData: OrderCreateRequest = {
      items: data.items.map((item, index) => ({
        product_id: parseInt(item.productId),
        quantity: item.quantity,
        // Get price from cart items if available
        unit_price: cartItems && cartItems[index] ? cartItems[index].price : 0,
      })),
      shipping_address: {
        street: data.shippingAddress.street,
        city: data.shippingAddress.city,
        state: data.shippingAddress.state,
        zip_code: data.shippingAddress.zipCode,
        country: data.shippingAddress.country,
      },
    };
    
    const response = await api.post<OrderApiResponse>('/api/v1/orders', apiData);
    const orderData = response.data;
    
    // Transform backend response to frontend format
    return {
      id: String(orderData.id),
      userId: String(orderData.user_id),
      status: orderData.status,
      total: parseFloat(orderData.total_amount),
      shippingAddress: {
        street: orderData.shipping_address.street,
        city: orderData.shipping_address.city,
        state: orderData.shipping_address.state,
        zipCode: orderData.shipping_address.zip_code,
        country: orderData.shipping_address.country,
      },
      items: orderData.items.map((item) => ({
        productId: String(item.product_id),
        productName: '', // Not provided by backend
        quantity: item.quantity,
        price: parseFloat(item.unit_price),
      })),
      createdAt: orderData.created_at,
      updatedAt: orderData.updated_at,
    };
  },

  async getOrders(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Promise<GetOrdersResponse> {
    const response = await api.get<any>('/api/v1/orders', { params });
    const data = response.data;
    
    // Transform backend response to frontend format
    const orders = data.items.map((order: any) => ({
      id: String(order.id),
      userId: String(order.user_id),
      status: order.status,
      total: parseFloat(order.total_amount),
      shippingAddress: {
        street: order.shipping_address?.street || '',
        city: order.shipping_address?.city || '',
        state: order.shipping_address?.state || '',
        zipCode: order.shipping_address?.zip_code || '',
        country: order.shipping_address?.country || '',
      },
      items: order.items?.map((item: any) => ({
        productId: String(item.product_id),
        productName: '',
        quantity: item.quantity,
        price: parseFloat(item.unit_price),
      })) || [],
      createdAt: order.created_at,
      updatedAt: order.updated_at,
    }));
    
    return {
      orders,
      total: data.total,
      page: data.page,
      limit: 10,
    };
  },

  async getOrder(id: string): Promise<Order> {
    const response = await api.get<any>(`/api/v1/orders/${id}`);
    const orderData = response.data;
    
    return {
      id: String(orderData.id),
      userId: String(orderData.user_id),
      status: orderData.status,
      total: parseFloat(orderData.total_amount),
      shippingAddress: {
        street: orderData.shipping_address?.street || '',
        city: orderData.shipping_address?.city || '',
        state: orderData.shipping_address?.state || '',
        zipCode: orderData.shipping_address?.zip_code || '',
        country: orderData.shipping_address?.country || '',
      },
      items: orderData.items?.map((item: any) => ({
        productId: String(item.product_id),
        productName: '',
        quantity: item.quantity,
        price: parseFloat(item.unit_price),
      })) || [],
      createdAt: orderData.created_at,
      updatedAt: orderData.updated_at,
    };
  },

  async cancelOrder(id: string): Promise<Order> {
    const response = await api.put<any>(`/api/v1/orders/${id}/cancel`);
    const orderData = response.data;
    
    return {
      id: String(orderData.id),
      userId: String(orderData.user_id),
      status: orderData.status,
      total: parseFloat(orderData.total_amount),
      shippingAddress: {
        street: orderData.shipping_address?.street || '',
        city: orderData.shipping_address?.city || '',
        state: orderData.shipping_address?.state || '',
        zipCode: orderData.shipping_address?.zip_code || '',
        country: orderData.shipping_address?.country || '',
      },
      items: orderData.items?.map((item: any) => ({
        productId: String(item.product_id),
        productName: '',
        quantity: item.quantity,
        price: parseFloat(item.unit_price),
      })) || [],
      createdAt: orderData.created_at,
      updatedAt: orderData.updated_at,
    };
  },

  async confirmOrder(id: string): Promise<Order> {
    const response = await api.put<any>(`/api/v1/orders/${id}/confirm`);
    const orderData = response.data;
    
    return {
      id: String(orderData.id),
      userId: String(orderData.user_id),
      status: orderData.status,
      total: parseFloat(orderData.total_amount),
      shippingAddress: {
        street: orderData.shipping_address?.street || '',
        city: orderData.shipping_address?.city || '',
        state: orderData.shipping_address?.state || '',
        zipCode: orderData.shipping_address?.zip_code || '',
        country: orderData.shipping_address?.country || '',
      },
      items: orderData.items?.map((item: any) => ({
        productId: String(item.product_id),
        productName: '',
        quantity: item.quantity,
        price: parseFloat(item.unit_price),
      })) || [],
      createdAt: orderData.created_at,
      updatedAt: orderData.updated_at,
    };
  },

  async shipOrder(id: string): Promise<Order> {
    const response = await api.put<any>(`/api/v1/orders/${id}/ship`, {});
    const orderData = response.data;
    
    return {
      id: String(orderData.id),
      userId: String(orderData.user_id),
      status: orderData.status,
      total: parseFloat(orderData.total_amount),
      shippingAddress: {
        street: orderData.shipping_address?.street || '',
        city: orderData.shipping_address?.city || '',
        state: orderData.shipping_address?.state || '',
        zipCode: orderData.shipping_address?.zip_code || '',
        country: orderData.shipping_address?.country || '',
      },
      items: orderData.items?.map((item: any) => ({
        productId: String(item.product_id),
        productName: '',
        quantity: item.quantity,
        price: parseFloat(item.unit_price),
      })) || [],
      createdAt: orderData.created_at,
      updatedAt: orderData.updated_at,
    };
  },

  async deliverOrder(id: string): Promise<Order> {
    const response = await api.put<any>(`/api/v1/orders/${id}/deliver`);
    const orderData = response.data;
    
    return {
      id: String(orderData.id),
      userId: String(orderData.user_id),
      status: orderData.status,
      total: parseFloat(orderData.total_amount),
      shippingAddress: {
        street: orderData.shipping_address?.street || '',
        city: orderData.shipping_address?.city || '',
        state: orderData.shipping_address?.state || '',
        zipCode: orderData.shipping_address?.zip_code || '',
        country: orderData.shipping_address?.country || '',
      },
      items: orderData.items?.map((item: any) => ({
        productId: String(item.product_id),
        productName: '',
        quantity: item.quantity,
        price: parseFloat(item.unit_price),
      })) || [],
      createdAt: orderData.created_at,
      updatedAt: orderData.updated_at,
    };
  },
};

export default orderService;