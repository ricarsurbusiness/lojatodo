import React from 'react';
import { Button } from '../common/Button';
import { Link } from 'react-router-dom';

interface CartSummaryProps {
  subtotal: number;
  shipping: number;
  total: number;
  itemCount: number;
  onCheckout?: () => void;
  isAuthenticated?: boolean;
}

export const CartSummary: React.FC<CartSummaryProps> = ({
  subtotal,
  shipping,
  total,
  itemCount,
  onCheckout,
  isAuthenticated = false,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
      
      <div className="space-y-3 border-b border-gray-200 pb-4 mb-4">
        <div className="flex justify-between text-gray-600">
          <span>Subtotal ({itemCount} {itemCount === 1 ? 'item' : 'items'})</span>
          <span>${subtotal.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-gray-600">
          <span>Shipping</span>
          <span>{shipping === 0 ? 'Free' : `$${shipping.toFixed(2)}`}</span>
        </div>
      </div>
      
      <div className="flex justify-between text-lg font-semibold mb-6">
        <span>Total</span>
        <span>${total.toFixed(2)}</span>
      </div>
      
      {onCheckout && (
        isAuthenticated ? (
          <Button variant="primary" size="lg" className="w-full" onClick={onCheckout}>
            Proceed to Checkout
          </Button>
        ) : (
          <Link to="/login" className="block">
            <Button variant="primary" size="lg" className="w-full">
              Login to Checkout
            </Button>
          </Link>
        )
      )}
      
      <div className="mt-4 text-center text-sm text-gray-500">
        <p>Secure checkout powered by Stripe</p>
      </div>
    </div>
  );
};

export default CartSummary;
