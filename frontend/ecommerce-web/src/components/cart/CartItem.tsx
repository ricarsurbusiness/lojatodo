import React from 'react';
import { Link } from 'react-router-dom';
import { CartItem } from '../../types/cart';
import { Button } from '../common/Button';

interface CartItemProps {
  item: CartItem;
  onUpdateQuantity: (productId: string, quantity: number) => void;
  onRemove: (productId: string) => void;
}

export const CartItemComponent: React.FC<CartItemProps> = ({ item, onUpdateQuantity, onRemove }) => {
  const handleQuantityChange = (delta: number) => {
    const newQuantity = item.quantity + delta;
    if (newQuantity > 0) {
      onUpdateQuantity(item.productId, newQuantity);
    }
  };

  return (
    <div className="flex items-center gap-4 py-4 border-b border-gray-200">
      <Link to={`/products/${item.productId}`} className="flex-shrink-0">
        <img
          src={item.image || 'https://via.placeholder.com/100x100?text=No+Image'}
          alt={item.productName}
          className="w-20 h-20 object-cover rounded-lg"
        />
      </Link>
      
      <div className="flex-1 min-w-0">
        <Link to={`/products/${item.productId}`} className="text-lg font-semibold text-gray-900 hover:text-blue-600 truncate block">
          {item.productName}
        </Link>
        <p className="text-gray-500 mt-1">${item.price.toFixed(2)}</p>
      </div>
      
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleQuantityChange(-1)}
          disabled={item.quantity <= 1}
        >
          -
        </Button>
        <span className="w-12 text-center font-medium">{item.quantity}</span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleQuantityChange(1)}
        >
          +
        </Button>
      </div>
      
      <div className="text-right min-w-[80px]">
        <p className="font-semibold text-gray-900">${(item.price * item.quantity).toFixed(2)}</p>
      </div>
      
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onRemove(item.productId)}
        className="text-red-600 hover:text-red-700 hover:bg-red-50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      </Button>
    </div>
  );
};

export default CartItemComponent;
