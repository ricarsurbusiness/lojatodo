import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService, { DashboardStats } from '../../services/adminService';
import { useAuth } from '../../context/AuthContext';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const isSuperAdmin = user?.roles?.includes('superAdmin');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await adminService.getDashboardStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
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
        <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-gray-500 text-sm">Total Revenue</div>
            <div className="text-2xl font-bold text-green-600">
              ${stats?.totalRevenue.toLocaleString() || '0'}
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-gray-500 text-sm">Total Orders</div>
            <div className="text-2xl font-bold text-blue-600">
              {stats?.totalOrders || 0}
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-gray-500 text-sm">Total Users</div>
            <div className="text-2xl font-bold text-purple-600">
              {stats?.totalUsers || 0}
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-gray-500 text-sm">Total Products</div>
            <div className="text-2xl font-bold text-orange-600">
              {stats?.totalProducts || 0}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Revenue by Day</h2>
            <div className="space-y-2">
              {stats?.revenueByDay.slice(-7).map((item) => (
                <div key={item.date} className="flex justify-between items-center">
                  <span className="text-gray-600">{item.date}</span>
                  <span className="font-semibold">${item.revenue.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Orders by Status</h2>
            <div className="space-y-2">
              {stats?.ordersByStatus && Object.entries(stats.ordersByStatus).map(([status, count]) => (
                <div key={status} className="flex justify-between items-center">
                  <span className="text-gray-600 capitalize">{status}</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm mt-6">
          <h2 className="text-xl font-semibold mb-4">Top Products</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Product</th>
                  <th className="text-right py-2">Sold</th>
                  <th className="text-right py-2">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {stats?.topProducts.map((product) => (
                  <tr key={product.productId} className="border-b">
                    <td className="py-2">{product.name}</td>
                    <td className="text-right">{product.totalSold}</td>
                    <td className="text-right">${product.revenue.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <Link
            to="/admin/products"
            className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <h3 className="font-semibold text-lg mb-2">Products</h3>
            <p className="text-gray-500 text-sm">Manage products inventory</p>
          </Link>
          <Link
            to="/admin/orders"
            className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <h3 className="font-semibold text-lg mb-2">Orders</h3>
            <p className="text-gray-500 text-sm">View and manage orders</p>
          </Link>
          {isSuperAdmin && (
            <Link
              to="/admin/users"
              className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <h3 className="font-semibold text-lg mb-2">Users</h3>
              <p className="text-gray-500 text-sm">Manage user accounts</p>
            </Link>
          )}
          <Link
            to="/admin/analytics"
            className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <h3 className="font-semibold text-lg mb-2">Analytics</h3>
            <p className="text-gray-500 text-sm">View sales and performance analytics</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;