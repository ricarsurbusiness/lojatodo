export interface ApiResponse<T> {
  data: T;
  message?: string;
  success?: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages?: number;
}

export interface ErrorResponse {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
  statusCode?: number;
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ErrorResponseWithValidation extends ErrorResponse {
  validationErrors?: ValidationError[];
}