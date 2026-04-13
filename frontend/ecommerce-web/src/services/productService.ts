import api from './api';

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  categoryId: string;
  stock: number;
}

export interface Category {
  id: string;
  name: string;
  description: string;
}

export interface GetProductsResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
}

export const productService = {
  async getProducts(params?: {
    page?: number;
    limit?: number;
    category?: string;
    search?: string;
  }): Promise<GetProductsResponse> {
    const response = await api.get<GetProductsResponse>('/api/v1/products', { params });
    return response.data;
  },

  async getProduct(id: string): Promise<Product> {
    const response = await api.get<Product>(`/api/v1/products/${id}`);
    return response.data;
  },

  async getCategories(): Promise<Category[]> {
    const response = await api.get<Category[]>('/api/v1/categories');
    return response.data;
  },

  async getCategories(): Promise<Category[]> {
    const response = await api.get<Category[]>('/api/v1/categories');
    return response.data;
  },

  async getCategory(id: string): Promise<Category> {
    const response = await api.get<Category>(`/api/v1/categories/${id}`);
    return response.data;
  },

  async createProduct(data: {
    name: string;
    description: string;
    price: number;
    image: string;
    categoryId: string;
    stock: number;
  }): Promise<Product> {
    const response = await api.post<Product>('/products', data);
    return response.data;
  },

  async updateProduct(id: string, data: {
    name?: string;
    description?: string;
    price?: number;
    image?: string;
    categoryId?: string;
    stock?: number;
  }): Promise<Product> {
    const response = await api.put<Product>(`/api/v1/products/${id}`, data);
    return response.data;
  },

  async deleteProduct(id: string): Promise<void> {
    await api.delete(`/api/v1/products/${id}`);
  },
};

export default productService;