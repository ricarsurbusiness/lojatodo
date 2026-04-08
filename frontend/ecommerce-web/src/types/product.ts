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

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
}

export interface GetProductsParams {
  page?: number;
  limit?: number;
  category?: string;
  search?: string;
}