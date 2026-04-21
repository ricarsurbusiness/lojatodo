import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { CartItem as CartItemType } from '../../types/cart';
import { Button } from '../common/Button';

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  items: CartItemType[];
  total: number;
  onUpdateQuantity: (productId: string, quantity: number) => void;
  onRemove: (productId: string) => void;
  onCheckout?: () => void;
}

export const CartDrawer: React.FC<CartDrawerProps> = ({
  isOpen,
  onClose,
  items,
  total,
  onUpdateQuantity,
  onRemove,
  onCheckout,
}) => {
  const drawerRef = useRef<HTMLDivElement>(null);
  const [isClosing, setIsClosing] = useState(false);

  // Convert total to number if it's a string
  const totalNum = typeof total === 'string' ? parseFloat(total) : total;
  const shipping = totalNum > 100 ? 0 : 9.99;
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (drawerRef.current && !drawerRef.current.contains(event.target as Node)) {
        handleClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsClosing(false);
      onClose();
    }, 300);
  };

  if (!isOpen && !isClosing) return null;

  return (
    <div
      className={`fixed inset-0 z-50 transition-opacity duration-300 ${
        isClosing ? 'opacity-0' : 'opacity-100'
      }`}
    >
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={handleClose} />
      
      <div
        ref={drawerRef}
        className={`absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-xl transform transition-transform duration-300 ${
          isClosing ? 'translate-x-full' : 'translate-x-0'
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">Shopping Cart ({itemCount})</h2>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            {items.length === 0 ? (
              <div className="text-center py-12">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <p className="text-gray-500 mb-4">Your cart is empty</p>
                <Link
                  to="/products"
                  onClick={handleClose}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Continue Shopping
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {items.map((item) => (
                  <div key={item.productId} className="flex gap-3 py-3 border-b border-gray-100">
                    <img
                      src={item.image || 'https://via.placeholder.com/80x80?text=No+Image'}
                      alt={item.productName}
                      className="w-20 h-20 object-cover rounded-lg"
                    />
                    <div className="flex-1 min-w-0">
                      <Link
                        to={`/products/${item.productId}`}
                        onClick={handleClose}
                        className="text-sm font-medium text-gray-900 hover:text-blue-600 line-clamp-2"
                      >
                        {item.productName}
                      </Link>
                      <p className="text-gray-500 text-sm mt-1">
                        ${typeof item.price === 'string' ? item.price : item.price.toFixed(2)}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <button
                          onClick={() => onUpdateQuantity(item.productId, item.quantity - 1)}
                          disabled={item.quantity <= 1}
                          className="w-6 h-6 flex items-center justify-center border rounded hover:bg-gray-50 disabled:opacity-50"
                        >
                          -
                        </button>
                        <span className="w-8 text-center text-sm">{item.quantity}</span>
                        <button
                          onClick={() => onUpdateQuantity(item.productId, item.quantity + 1)}
                          className="w-6 h-6 flex items-center justify-center border rounded hover:bg-gray-50"
                        >
                          +
                        </button>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">
                        ${typeof item.price === 'string' 
                          ? (parseFloat(item.price) * item.quantity).toFixed(2)
                          : (item.price * item.quantity).toFixed(2)}
                      </p>
                      <button
                        onClick={() => onRemove(item.productId)}
                        className="text-red-600 text-sm hover:text-red-700 mt-1"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {items.length > 0 && (
            <div className="border-t border-gray-200 p-4 space-y-4">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span>${totalNum.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-600 text-sm">
                <span>Shipping</span>
                <span>{shipping === 0 ? 'Free' : `$${shipping.toFixed(2)}`}</span>
              </div>
              <div className="flex justify-between font-semibold text-lg">
                <span>Total</span>
                <span>${(totalNum + shipping).toFixed(2)}</span>
              </div>
              
              <div className="space-y-2">
                {onCheckout && (
                  <Button variant="primary" className="w-full" onClick={() => { handleClose(); onCheckout(); }}>
                    Checkout
                  </Button>
                )}
                <Link
                  to="/cart"
                  onClick={handleClose}
                  className="block"
                >
                  <Button variant="outline" className="w-full">
                    View Cart
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CartDrawer;