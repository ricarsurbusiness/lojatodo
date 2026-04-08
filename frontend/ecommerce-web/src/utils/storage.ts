const TOKEN_KEY = 'token';
const CART_KEY = 'cart';

export const storage = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken(): void {
    localStorage.removeItem(TOKEN_KEY);
  },

  getCart<T>(): T | null {
    const data = localStorage.getItem(CART_KEY);
    if (!data) return null;
    try {
      return JSON.parse(data) as T;
    } catch {
      return null;
    }
  },

  setCart<T>(cart: T): void {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
  },

  removeCart(): void {
    localStorage.removeItem(CART_KEY);
  },

  clear(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(CART_KEY);
  },
};