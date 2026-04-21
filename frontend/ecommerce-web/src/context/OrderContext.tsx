import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Order, CreateOrderRequest, ShippingAddress } from '../types';
import orderService, { GetOrdersResponse } from '../services/orderService';

interface OrderState {
  orders: Order[];
  currentOrder: Order | null;
  isLoading: boolean;
  error: string | null;
  total: number;
  page: number;
  limit: number;
}

type OrderAction =
  | { type: 'ORDER_LOADING' }
  | { type: 'ORDER_SUCCESS'; payload: { orders: Order[]; total: number; page: number; limit: number } }
  | { type: 'CURRENT_ORDER_SUCCESS'; payload: Order }
  | { type: 'ORDER_FAILURE'; payload: string }
  | { type: 'ORDER_CLEAR' };

const initialState: OrderState = {
  orders: [] as Order[],
  currentOrder: null,
  isLoading: false,
  error: null,
  total: 0,
  page: 1,
  limit: 10,
};

function orderReducer(state: OrderState, action: OrderAction): OrderState {
  switch (action.type) {
    case 'ORDER_LOADING':
      return { ...state, isLoading: true, error: null };
    case 'ORDER_SUCCESS':
      return {
        ...state,
        orders: action.payload.orders,
        total: action.payload.total,
        page: action.payload.page,
        limit: action.payload.limit,
        isLoading: false,
        error: null,
      };
    case 'CURRENT_ORDER_SUCCESS':
      return {
        ...state,
        currentOrder: action.payload,
        isLoading: false,
        error: null,
      };
    case 'ORDER_FAILURE':
      return { ...state, isLoading: false, error: action.payload };
    case 'ORDER_CLEAR':
      return { ...state, currentOrder: null, isLoading: false, error: null };
    default:
      return state;
  }
}

interface OrderContextType extends OrderState {
  createOrder: (data: CreateOrderRequest) => Promise<Order>;
  fetchOrders: (params?: { page?: number; limit?: number; status?: string }) => Promise<void>;
  fetchOrder: (id: string) => Promise<void>;
  cancelOrder: (id: string) => Promise<void>;
  clearCurrentOrder: () => void;
}

const OrderContext = createContext<OrderContextType | undefined>(undefined);

export function OrderProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(orderReducer, initialState);

  const createOrder = async (data: CreateOrderRequest, cartItems?: Array<{ productId: string; price: number }>): Promise<Order> => {
    dispatch({ type: 'ORDER_LOADING' });
    try {
      const order = await orderService.createOrder(data, cartItems);
      dispatch({ type: 'CURRENT_ORDER_SUCCESS', payload: order });
      return order;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to create order';
      dispatch({ type: 'ORDER_FAILURE', payload: message });
      throw error;
    }
  };

  const fetchOrders = async (params?: { page?: number; limit?: number; status?: string }) => {
    dispatch({ type: 'ORDER_LOADING' });
    try {
      const response: GetOrdersResponse = await orderService.getOrders(params);
      dispatch({
        type: 'ORDER_SUCCESS',
        payload: {
          orders: response.orders,
          total: response.total,
          page: response.page,
          limit: response.limit,
        },
      });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to fetch orders';
      dispatch({ type: 'ORDER_FAILURE', payload: message });
    }
  };

  const fetchOrder = async (id: string) => {
    dispatch({ type: 'ORDER_LOADING' });
    try {
      const order = await orderService.getOrder(id);
      dispatch({ type: 'CURRENT_ORDER_SUCCESS', payload: order });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to fetch order';
      dispatch({ type: 'ORDER_FAILURE', payload: message });
    }
  };

  const cancelOrder = async (id: string) => {
    dispatch({ type: 'ORDER_LOADING' });
    try {
      const order = await orderService.cancelOrder(id);
      dispatch({ type: 'CURRENT_ORDER_SUCCESS', payload: order });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to cancel order';
      dispatch({ type: 'ORDER_FAILURE', payload: message });
      throw error;
    }
  };

  const clearCurrentOrder = () => {
    dispatch({ type: 'ORDER_CLEAR' });
  };

  return (
    <OrderContext.Provider
      value={{
        ...state,
        createOrder,
        fetchOrders,
        fetchOrder,
        cancelOrder,
        clearCurrentOrder,
      }}
    >
      {children}
    </OrderContext.Provider>
  );
}

export function useOrder(): OrderContextType {
  const context = useContext(OrderContext);
  if (!context) {
    throw new Error('useOrder must be used within an OrderProvider');
  }
  return context;
}
