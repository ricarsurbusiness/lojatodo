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

// Backend request format
interface AddToCartApiRequest {
  product_id: number;
  quantity: number;
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
    const response = await api.get<any>('/api/v1/cart');
    const data = response.data;
    
    // Transform backend response to frontend format
    return {
      id: String(data.user_id),
      userId: String(data.user_id),
      items: data.items.map((item: any) => ({
        productId: String(item.product_id),
        productName: item.name,
        quantity: item.quantity,
        price: typeof item.price === 'string' ? parseFloat(item.price) : Number(item.price),
        image: undefined,
      })),
      total: typeof data.total === 'string' ? parseFloat(data.total) : Number(data.total),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  },

  async addItem(data: AddToCartRequest): Promise<Cart> {
    // Convert to backend format: product_id (number), quantity
    const productIdNum = parseInt(data.productId);
    console.log('Adding to cart:', { productId: data.productId, parsed: productIdNum, quantity: data.quantity });
    
    const apiData: AddToCartApiRequest = {
      product_id: productIdNum,
      quantity: parseInt(String(data.quantity))
    };
    console.log('API data:', apiData);
    const response = await api.post<any>('/api/v1/cart/add', apiData);
    const dataRes = response.data;
    
    // Transform backend response
    return {
      id: String(dataRes.user_id),
      userId: String(dataRes.user_id),
      items: dataRes.items.map((item: any) => ({
        productId: String(item.product_id),
        productName: item.name,
        quantity: item.quantity,
        price: typeof item.price === 'string' ? parseFloat(item.price) : Number(item.price),
        image: undefined,
      })),
      total: typeof dataRes.total === 'string' ? parseFloat(dataRes.total) : Number(dataRes.total),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  },

  async updateItem(productId: string, data: UpdateCartItemRequest): Promise<Cart> {
    const apiData = { 
      product_id: parseInt(productId),
      quantity: parseInt(String(data.quantity))
    };
    console.log('Updating cart:', apiData);
    const response = await api.post<any>('/api/v1/cart/update', apiData);
    const dataRes = response.data;
    
    // Transform backend response
    return {
      id: String(dataRes.user_id),
      userId: String(dataRes.user_id),
      items: dataRes.items.map((item: any) => ({
        productId: String(item.product_id),
        productName: item.name,
        quantity: item.quantity,
        price: typeof item.price === 'string' ? parseFloat(item.price) : Number(item.price),
        image: undefined,
      })),
      total: typeof dataRes.total === 'string' ? parseFloat(dataRes.total) : Number(dataRes.total),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  },

  async removeItem(productId: string): Promise<Cart> {
    // Remove uses query parameter: /cart/remove?product_id=3
    const response = await api.post<any>(`/api/v1/cart/remove?product_id=${parseInt(productId)}`);
    const dataRes = response.data;
    
    // Transform backend response
    return {
      id: String(dataRes.user_id),
      userId: String(dataRes.user_id),
      items: dataRes.items.map((item: any) => ({
        productId: String(item.product_id),
        productName: item.name,
        quantity: item.quantity,
        price: typeof item.price === 'string' ? parseFloat(item.price) : Number(item.price),
        image: undefined,
      })),
      total: typeof dataRes.total === 'string' ? parseFloat(dataRes.total) : Number(dataRes.total),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  },

  async clearCart(): Promise<void> {
    await api.delete('/api/v1/cart');
  },
};

export default cartService;