import api from './api';
import inventoryService from './inventoryService';

export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: string;
  image: string | null;
  category_id: number | null;
  stock: number | null;
  available_quantity?: number; // From inventory service
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
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
    const response = await api.get<Product[]>('/api/v1/products', { params });
    const products = response.data;
    
    // Fetch inventory for each product and add available_quantity
    if (products.length > 0) {
      const productIds = products.map(p => p.id);
      const inventoryMap = await inventoryService.getInventoryForProducts(productIds);
      
      // Add available_quantity to each product
      products.forEach(product => {
        const inv = inventoryMap.get(product.id);
        if (inv) {
          product.available_quantity = inv.available_quantity;
          // Also update stock for backwards compatibility
          product.stock = inv.available_quantity;
        }
      });
    }
    
    return {
      products,
      total: products.length,
      page: params?.page || 1,
      limit: params?.limit || products.length
    };
  },

  async getProduct(id: string): Promise<Product> {
    const response = await api.get<Product>(`/api/v1/products/${id}`);
    const product = response.data;
    
    // Fetch inventory for this product
    try {
      const inventory = await inventoryService.getInventory(id);
      product.available_quantity = inventory.available_quantity;
      product.stock = inventory.available_quantity;
    } catch {
      // Product might not have inventory
    }
    
    return product;
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
    // Transform camelCase to snake_case for backend
    const payload = {
      name: data.name,
      description: data.description,
      price: data.price,
      image: data.image,
      category_id: data.categoryId ? parseInt(data.categoryId) : null,
      stock: data.stock,
    };
    const response = await api.post<Product>('/api/v1/products', payload);
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
    // Transform camelCase to snake_case for backend
    const payload: Record<string, any> = {};
    if (data.name !== undefined) payload.name = data.name;
    if (data.description !== undefined) payload.description = data.description;
    if (data.price !== undefined) payload.price = data.price;
    if (data.image !== undefined) payload.image = data.image;
    if (data.categoryId !== undefined && data.categoryId !== '') {
      payload.category_id = parseInt(data.categoryId);
    }
    if (data.stock !== undefined) payload.stock = data.stock;
    
    const response = await api.put<Product>(`/api/v1/products/${id}`, payload);
    return response.data;
  },

  async deleteProduct(id: string): Promise<void> {
    await api.delete(`/api/v1/products/${id}`);
  },
};

export default productService;
