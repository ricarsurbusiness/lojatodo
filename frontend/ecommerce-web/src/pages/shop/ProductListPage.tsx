import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import productService, { Product, Category } from '../../services/productService';
import { ProductGrid } from '../../components/shop/ProductGrid';
import { CategoryFilter } from '../../components/shop/CategoryFilter';
import { SearchBar } from '../../components/shop/SearchBar';

const ITEMS_PER_PAGE = 12;

export const ProductListPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  
  const selectedCategory = searchParams.get('category') || null;
  const searchQuery = searchParams.get('search') || '';

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await productService.getCategories();
        setCategories(data);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const params = {
          page: currentPage,
          limit: ITEMS_PER_PAGE,
          ...(selectedCategory && { category: selectedCategory }),
          ...(searchQuery && { search: searchQuery }),
        };
        const data = await productService.getProducts(params);
        setProducts(data.products);
        setTotal(data.total);
      } catch (error) {
        console.error('Failed to fetch products:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [currentPage, selectedCategory, searchQuery]);

  const handleCategorySelect = (categoryId: string | null) => {
    setCurrentPage(1);
    const newParams = new URLSearchParams(searchParams);
    if (categoryId) {
      newParams.set('category', categoryId);
    } else {
      newParams.delete('category');
    }
    setSearchParams(newParams);
  };

  const handleSearch = (query: string) => {
    setCurrentPage(1);
    const newParams = new URLSearchParams(searchParams);
    if (query) {
      newParams.set('search', query);
    } else {
      newParams.delete('search');
    }
    setSearchParams(newParams);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Products</h1>
        
        <div className="flex flex-col lg:flex-row gap-8">
          <aside className="lg:w-1/4">
            <SearchBar onSearch={handleSearch} />
            <CategoryFilter
              categories={categories}
              selectedCategory={selectedCategory}
              onSelectCategory={handleCategorySelect}
            />
          </aside>
          
          <main className="lg:w-3/4">
            <div className="mb-4">
              <p className="text-gray-600">
                Showing {products.length} of {total} products
              </p>
            </div>
            
            <ProductGrid products={products} loading={loading} />
            
            {totalPages > 1 && (
              <div className="mt-8 flex justify-center">
                <nav className="flex gap-2">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                  >
                    Previous
                  </button>
                  
                  {[...Array(totalPages)].map((_, i) => (
                    <button
                      key={i + 1}
                      onClick={() => handlePageChange(i + 1)}
                      className={`px-4 py-2 border rounded-lg ${
                        currentPage === i + 1
                          ? 'bg-blue-600 text-white'
                          : 'hover:bg-gray-100'
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                  
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                  >
                    Next
                  </button>
                </nav>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default ProductListPage;
