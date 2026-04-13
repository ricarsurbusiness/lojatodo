import api from './api';

export interface CartItem {
  productId: string;
  productName: string;
  quantity: number;
  price: number;
  image?: string;
}

export interface Cart {
  id: string;
  userId: string;
  items: CartItem[];
  total: number;
  createdAt: string;
  updatedAt: string;
}

export interface AddToCartRequest {
  productId: string;
  quantity: number;
}

export interface UpdateCartItemRequest {
  quantity: number;
}

export const cartService = {
  async getCart(): Promise<Cart> {
    const response = await api.get<Cart>('/cart');
    return response.data;
  },

  async addItem(data: AddToCartRequest): Promise<Cart> {
    const response = await api.post<Cart>('/api/v1/cart/items', data);
    return response.data;
  },

  async updateItem(productId: string, data: UpdateCartItemRequest): Promise<Cart> {
    const response = await api.put<Cart>(`/api/v1/cart/items/${productId}`, data);
    return response.data;
  },

  async removeItem(productId: string): Promise<Cart> {
    const response = await api.delete<Cart>(`/api/v1/cart/items/${productId}`);
    return response.data;
  },

  async clearCart(): Promise<void> {
    await api.delete('/cart');
  },
};

export default cartService;