import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import { CartItemComponent } from '../../components/cart/CartItem';
import { CartSummary } from '../../components/cart/CartSummary';
import { Loader } from '../../components/common/Loader';

export const CartPage: React.FC = () => {
  const { cart, isLoading, error, fetchCart, updateItem, removeItem } = useCart();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!cart) {
      fetchCart();
    }
  }, [cart, fetchCart]);

  const handleUpdateQuantity = async (productId: string, quantity: number) => {
    await updateItem(productId, { quantity });
  };

  const handleRemove = async (productId: string) => {
    await removeItem(productId);
  };

  const handleCheckout = () => {
    navigate('/checkout');
  };

  if (isLoading && !cart) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            <p>{error}</p>
            <button onClick={fetchCart} className="underline mt-2 hover:text-red-800">
              Try again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const items = cart?.items || [];
  const subtotal = cart?.total ?? 0;
  const shipping = subtotal > 100 ? 0 : 9.99;
  const total = subtotal + shipping;
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>
        
        {items.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-20 w-20 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p className="text-xl text-gray-600 mb-4">Your cart is empty</p>
            <Link
              to="/products"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Continue Shopping
            </Link>
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row gap-8">
            <div className="lg:w-2/3">
              <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="p-4 border-b border-gray-200 bg-gray-50">
                  <p className="text-sm text-gray-600">
                    {itemCount} {itemCount === 1 ? 'item' : 'items'} in your cart
                  </p>
                </div>
                
                <div className="divide-y divide-gray-200">
                  {items.map((item) => (
                    <div key={item.productId} className="p-4">
                      <CartItemComponent
                        item={item}
                        onUpdateQuantity={handleUpdateQuantity}
                        onRemove={handleRemove}
                      />
                    </div>
                  ))}
                </div>
                
                <div className="p-4 border-t border-gray-200 bg-gray-50">
                  <Link
                    to="/products"
                    className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                    </svg>
                    Continue Shopping
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="lg:w-1/3">
              <div className="sticky top-4">
                <CartSummary
                  subtotal={subtotal}
                  shipping={shipping}
                  total={total}
                  itemCount={itemCount}
                  onCheckout={handleCheckout}
                  isAuthenticated={isAuthenticated}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartPage;
