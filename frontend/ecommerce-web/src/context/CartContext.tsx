import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { Cart, CartItem } from '../types';
import cartService, { AddToCartRequest, UpdateCartItemRequest } from '../services/cartService';

interface CartState {
  cart: Cart | null;
  isLoading: boolean;
  error: string | null;
}

type CartAction =
  | { type: 'CART_LOADING' }
  | { type: 'CART_SUCCESS'; payload: Cart }
  | { type: 'CART_FAILURE'; payload: string }
  | { type: 'CART_CLEAR' };

const initialState: CartState = {
  cart: null,
  isLoading: false,
  error: null,
};

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'CART_LOADING':
      return { ...state, isLoading: true, error: null };
    case 'CART_SUCCESS':
      return { ...state, cart: action.payload, isLoading: false, error: null };
    case 'CART_FAILURE':
      return { ...state, isLoading: false, error: action.payload };
    case 'CART_CLEAR':
      return { ...state, cart: null, isLoading: false, error: null };
    default:
      return state;
  }
}

interface CartContextType extends CartState {
  fetchCart: () => Promise<void>;
  addItem: (data: AddToCartRequest) => Promise<void>;
  updateItem: (productId: string, data: UpdateCartItemRequest) => Promise<void>;
  removeItem: (productId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  getItemCount: () => number;
  getTotal: () => number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, initialState);

  const fetchCart = async () => {
    dispatch({ type: 'CART_LOADING' });
    try {
      const cart = await cartService.getCart();
      dispatch({ type: 'CART_SUCCESS', payload: cart });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to fetch cart';
      dispatch({ type: 'CART_FAILURE', payload: message });
    }
  };

  const addItem = async (data: AddToCartRequest) => {
    dispatch({ type: 'CART_LOADING' });
    try {
      const cart = await cartService.addItem(data);
      dispatch({ type: 'CART_SUCCESS', payload: cart });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to add item';
      dispatch({ type: 'CART_FAILURE', payload: message });
      throw error;
    }
  };

  const updateItem = async (productId: string, data: UpdateCartItemRequest) => {
    dispatch({ type: 'CART_LOADING' });
    try {
      const cart = await cartService.updateItem(productId, data);
      dispatch({ type: 'CART_SUCCESS', payload: cart });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to update item';
      dispatch({ type: 'CART_FAILURE', payload: message });
      throw error;
    }
  };

  const removeItem = async (productId: string) => {
    dispatch({ type: 'CART_LOADING' });
    try {
      const cart = await cartService.removeItem(productId);
      dispatch({ type: 'CART_SUCCESS', payload: cart });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to remove item';
      dispatch({ type: 'CART_FAILURE', payload: message });
      throw error;
    }
  };

  const clearCart = async () => {
    dispatch({ type: 'CART_LOADING' });
    try {
      await cartService.clearCart();
      dispatch({ type: 'CART_CLEAR' });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to clear cart';
      dispatch({ type: 'CART_FAILURE', payload: message });
      throw error;
    }
  };

  const getItemCount = (): number => {
    if (!state.cart?.items) return 0;
    return state.cart.items.reduce((total: number, item: CartItem) => total + item.quantity, 0);
  };

  const getTotal = (): number => {
    return state.cart?.total ?? 0;
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchCart();
    }
  }, []);

  return (
    <CartContext.Provider
      value={{
        ...state,
        fetchCart,
        addItem,
        updateItem,
        removeItem,
        clearCart,
        getItemCount,
        getTotal,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart(): CartContextType {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
