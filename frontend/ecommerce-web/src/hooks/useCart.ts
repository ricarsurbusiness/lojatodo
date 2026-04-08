import { useContext } from 'react';
import { CartContext } from '../context/CartContext';

export interface UseCartReturn {
  cart: import('../types').Cart | null;
  isLoading: boolean;
  error: string | null;
  fetchCart: () => Promise<void>;
  addItem: (data: import('../services/cartService').AddToCartRequest) => Promise<void>;
  updateItem: (productId: string, data: import('../services/cartService').UpdateCartItemRequest) => Promise<void>;
  removeItem: (productId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  getItemCount: () => number;
  getTotal: () => number;
}

export function useCart(): UseCartReturn {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context as UseCartReturn;
}
