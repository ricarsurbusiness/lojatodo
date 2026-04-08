import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import productService, { Product, Category } from '../../services/productService';
import { useCart } from '../../context/CartContext';
import { Button } from '../../components/common/Button';
import { Loader } from '../../components/common/Loader';
import { Alert } from '../../components/common/Alert';

export const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { addItem, isLoading: cartLoading } = useCart();
  const [product, setProduct] = useState<Product | null>(null);
  const [category, setCategory] = useState<Category | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) return;
      
      setLoading(true);
      setError(null);
      try {
        const productData = await productService.getProduct(id);
        setProduct(productData);
        
        if (productData.categoryId) {
          const categoryData = await productService.getCategory(productData.categoryId);
          setCategory(categoryData);
        }
      } catch (err) {
        setError('Failed to load product');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [id]);

  const handleAddToCart = async () => {
    if (!product) return;
    
    try {
      await addItem({ productId: product.id, quantity });
      setSuccessMessage('Product added to cart!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError('Failed to add to cart');
    }
  };

  const handleQuantityChange = (delta: number) => {
    setQuantity((prev) => Math.max(1, Math.min(prev + delta, product?.stock || 1)));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {error || 'Product not found'}
          </h2>
          <Link to="/products" className="text-blue-600 hover:text-blue-500">
            Back to Products
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <nav className="flex items-center text-sm text-gray-500 mb-8">
          <Link to="/" className="hover:text-gray-900">Home</Link>
          <span className="mx-2">/</span>
          <Link to="/products" className="hover:text-gray-900">Products</Link>
          {category && (
            <>
              <span className="mx-2">/</span>
              <Link to={`/products?category=${category.id}`} className="hover:text-gray-900">
                {category.name}
              </Link>
            </>
          )}
          <span className="mx-2">/</span>
          <span className="text-gray-900">{product.name}</span>
        </nav>

        {successMessage && (
          <Alert variant="success" className="mb-4" onClose={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        )}

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
            <div className="aspect-w-1 aspect-h-1">
              <img
                src={product.image || 'https://via.placeholder.com/600x600?text=No+Image'}
                alt={product.name}
                className="w-full h-full object-cover rounded-lg"
              />
            </div>
            
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>
              {category && (
                <Link
                  to={`/products?category=${category.id}`}
                  className="text-sm text-blue-600 hover:text-blue-500"
                >
                  {category.name}
                </Link>
              )}
              
              <p className="text-3xl font-bold text-gray-900 mt-4">
                ${product.price.toFixed(2)}
              </p>
              
              <div className="mt-2">
                <span className={`text-sm ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                </span>
              </div>
              
              <div className="mt-6">
                <h2 className="text-lg font-semibold mb-2">Description</h2>
                <p className="text-gray-600">{product.description}</p>
              </div>
              
              {product.stock > 0 && (
                <div className="mt-6">
                  <h2 className="text-lg font-semibold mb-2">Quantity</h2>
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => handleQuantityChange(-1)}
                      disabled={quantity <= 1}
                      className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-100"
                    >
                      -
                    </button>
                    <span className="text-lg font-medium">{quantity}</span>
                    <button
                      onClick={() => handleQuantityChange(1)}
                      disabled={quantity >= product.stock}
                      className="px-3 py-1 border rounded-lg disabled:opacity-50 hover:bg-gray-100"
                    >
                      +
                    </button>
                  </div>
                </div>
              )}
              
              <div className="mt-6">
                <Button
                  onClick={handleAddToCart}
                  variant={product.stock > 0 ? 'primary' : 'outline'}
                  size="lg"
                  className="w-full"
                  disabled={product.stock <= 0}
                  isLoading={cartLoading}
                >
                  {product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;
