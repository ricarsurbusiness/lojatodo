import api from './api';

export interface Category {
  id: number;
  name: string;
  description: string | null;
}

export const categoryService = {
  async getCategories(): Promise<Category[]> {
    const response = await api.get<Category[]>('/api/v1/categories');
    return response.data;
  },

  async getCategory(id: string): Promise<Category> {
    const response = await api.get<Category>(`/api/v1/categories/${id}`);
    return response.data;
  },

  async createCategory(data: {
    name: string;
    description: string;
  }): Promise<Category> {
    const response = await api.post<Category>('/api/v1/categories', data);
    return response.data;
  },

  async updateCategory(id: string, data: {
    name?: string;
    description?: string;
  }): Promise<Category> {
    const response = await api.put<Category>(`/api/v1/categories/${id}`, data);
    return response.data;
  },

  async deleteCategory(id: string): Promise<void> {
    await api.delete(`/api/v1/categories/${id}`);
  },
};

export default categoryService;