import React, { useState, useEffect } from 'react';
import analyticsService, { SalesAnalytics, OrdersAnalytics, ProductsAnalytics } from '../../services/analyticsService';

export const AnalyticsPage: React.FC = () => {
  const [sales, setSales] = useState<SalesAnalytics | null>(null);
  const [orders, setOrders] = useState<OrdersAnalytics | null>(null);
  const [products, setProducts] = useState<ProductsAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [salesData, ordersData, productsData] = await Promise.all([
          analyticsService.getSalesAnalytics(),
          analyticsService.getOrdersAnalytics(),
          analyticsService.getProductsAnalytics(),
        ]);
        setSales(salesData);
        setOrders(ordersData);
        setProducts(productsData);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Analytics</h1>

        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Revenue</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-gray-500 text-sm">Today</div>
              <div className="text-2xl font-bold text-green-600">
                ${sales?.today.toLocaleString() || 0}
              </div>
              {sales?.todayChange !== undefined && (
                <div className={`text-sm ${sales.todayChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {sales.todayChange >= 0 ? '+' : ''}{sales.todayChange}%
                </div>
              )}
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-gray-500 text-sm">This Week</div>
              <div className="text-2xl font-bold text-green-600">
                ${sales?.week.toLocaleString() || 0}
              </div>
              {sales?.weekChange !== undefined && (
                <div className={`text-sm ${sales.weekChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {sales.weekChange >= 0 ? '+' : ''}{sales.weekChange}%
                </div>
              )}
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-gray-500 text-sm">This Month</div>
              <div className="text-2xl font-bold text-green-600">
                ${sales?.month.toLocaleString() || 0}
              </div>
              {sales?.monthChange !== undefined && (
                <div className={`text-sm ${sales.monthChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {sales.monthChange >= 0 ? '+' : ''}{sales.monthChange}%
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Orders by Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-gray-500 text-sm">Pending</div>
              <div className="text-2xl font-bold text-yellow-600">
                {orders?.pending || 0}
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-gray-500 text-sm">Processing</div>
              <div className="text-2xl font-bold text-blue-600">
                {orders?.processing || 0}
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-gray-500 text-sm">Shipped</div>
              <div className="text-2xl font-bold text-purple-600">
                {orders?.shipped || 0}
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-gray-500 text-sm">Delivered</div>
              <div className="text-2xl font-bold text-green-600">
                {orders?.delivered || 0}
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="text-gray-500 text-sm">Cancelled</div>
              <div className="text-2xl font-bold text-red-600">
                {orders?.cancelled || 0}
              </div>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Top Products</h2>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Product</th>
                    <th className="text-right py-2">Sold</th>
                    <th className="text-right py-2">Revenue</th>
                    <th className="text-right py-2">Stock</th>
                  </tr>
                </thead>
                <tbody>
                  {products?.topProducts.map((product) => (
                    <tr key={product.id} className="border-b">
                      <td className="py-2">{product.name}</td>
                      <td className="text-right">{product.sold}</td>
                      <td className="text-right">${product.revenue.toLocaleString()}</td>
                      <td className="text-right">
                        <span className={product.stock < 10 ? 'text-red-600' : ''}>
                          {product.stock}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;