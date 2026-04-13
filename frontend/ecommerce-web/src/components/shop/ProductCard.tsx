import React from 'react';
import { Link } from 'react-router-dom';
import { Product } from '../../types/product';
import { Button } from '../common/Button';

interface ProductCardProps {
  product: Product;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <Link to={`/products/${product.id}`}>
        <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden bg-gray-200 xl:aspect-w-8 xl:aspect-h-7">
          <img
            src={product.image || 'https://via.placeholder.com/400x400?text=No+Image'}
            alt={product.name}
            className="h-full w-full object-cover object-center group-hover:opacity-75"
          />
        </div>
      </Link>
      <div className="p-4">
        <Link to={`/products/${product.id}`}>
          <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 truncate">
            {product.name}
          </h3>
        </Link>
        <p className="mt-1 text-sm text-gray-500 line-clamp-2">{product.description}</p>
        <div className="mt-4 flex items-center justify-between">
          <p className="text-xl font-bold text-gray-900">${typeof product.price === 'string' ? product.price : product.price.toFixed(2)}</p>
          <span className={`text-sm ${(product.stock || 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {(product.stock || 0) > 0 ? `${product.stock} in stock` : 'Out of stock'}
          </span>
        </div>
        <div className="mt-4">
          <Button
            variant={(product.stock || 0) > 0 ? 'primary' : 'outline'}
            size="sm"
            className="w-full"
            disabled={(product.stock || 0) <= 0}
          >
            {product.stock > 0 ? 'Add to Cart' : 'Out of Stock'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
