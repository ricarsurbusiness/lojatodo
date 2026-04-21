import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import orderService from '../../services/orderService';

interface Order {
  id: string;
  userId: string;
  total: number;
  status: string;
  createdAt: string;
}

const statusColors: Record<string, string> = {
  pendiente: 'bg-yellow-100 text-yellow-800',
  confirmado: 'bg-blue-100 text-blue-800',
  procesamiento: 'bg-blue-100 text-blue-800',
  enviado: 'bg-purple-100 text-purple-800',
  entregado: 'bg-green-100 text-green-800',
  cancelado: 'bg-red-100 text-red-800',
  fallido: 'bg-red-100 text-red-800',
};

// Spanish status options from backend
const statusOptions = ['pendiente', 'confirmado', 'procesamiento', 'enviado', 'entregado', 'cancelado', 'fallido'];

export const AdminOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 10;

  useEffect(() => {
    fetchOrders();
  }, [page]);

  const fetchOrders = async () => {
    try {
      const data = await adminService.getOrders({ page, limit });
      setOrders(data.orders);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (orderId: string, status: string) => {
    try {
      await adminService.updateOrderStatus(orderId, status);
      setOrders(orders.map((o) => (o.id === orderId ? { ...o, status } : o)));
    } catch (error) {
      console.error('Failed to update order status:', error);
    }
  };

  const handleConfirmOrder = async (orderId: string) => {
    try {
      const updated = await orderService.confirmOrder(orderId);
      setOrders(orders.map((o) => (o.id === orderId ? { ...o, status: updated.status } : o)));
    } catch (error) {
      console.error('Failed to confirm order:', error);
    }
  };

  const handleShipOrder = async (orderId: string) => {
    try {
      const updated = await orderService.shipOrder(orderId);
      setOrders(orders.map((o) => (o.id === orderId ? { ...o, status: updated.status } : o)));
    } catch (error) {
      console.error('Failed to ship order:', error);
    }
  };

  const handleDeliverOrder = async (orderId: string) => {
    try {
      const updated = await orderService.deliverOrder(orderId);
      setOrders(orders.map((o) => (o.id === orderId ? { ...o, status: updated.status } : o)));
    } catch (error) {
      console.error('Failed to deliver order:', error);
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    try {
      const updated = await orderService.cancelOrder(orderId);
      setOrders(orders.map((o) => (o.id === orderId ? { ...o, status: updated.status } : o)));
    } catch (error) {
      console.error('Failed to cancel order:', error);
    }
  };

  const getActionsForStatus = (status: string): { label: string; handler: (id: string) => Promise<void>; action: string }[] => {
    // Handle Spanish status names
    switch (status) {
      case 'pendiente': // pending
        return [
          { label: 'Confirm', handler: handleConfirmOrder, action: 'confirm' },
          { label: 'Cancel', handler: handleCancelOrder, action: 'cancel' },
        ];
      case 'confirmado': // confirmed
        return [
          { label: 'Ship', handler: handleShipOrder, action: 'ship' },
          { label: 'Cancel', handler: handleCancelOrder, action: 'cancel' },
        ];
      case 'enviado': // shipped
        return [
          { label: 'Deliver', handler: handleDeliverOrder, action: 'deliver' },
        ];
      case 'procesamiento': // processing
        return [
          { label: 'Ship', handler: handleShipOrder, action: 'ship' },
        ];
      case 'entregado': // delivered - no actions
        return [];
      case 'cancelado': // cancelled - no actions
        return [];
      case 'fallido': // failed - no actions
        return [];
      default:
        return [];
    }
  };

  const totalPages = Math.ceil(total / limit);

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
        <h1 className="text-3xl font-bold mb-8">Order Management</h1>

        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left py-3 px-4">Order ID</th>
                <th className="text-left py-3 px-4">Date</th>
                <th className="text-right py-3 px-4">Total</th>
                <th className="text-left py-3 px-4">Status</th>
                <th className="text-right py-3 px-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id} className="border-t hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <Link to={`/orders/${order.id}`} className="text-blue-600 hover:underline">
                      {order.id.substring(0, 8)}...
                    </Link>
                  </td>
                  <td className="py-3 px-4">{new Date(order.createdAt).toLocaleDateString()}</td>
                  <td className="py-3 px-4 text-right">${order.total.toFixed(2)}</td>
                  <td className="py-3 px-4">
                    <select
                      value={order.status}
                      onChange={(e) => handleStatusChange(order.id, e.target.value)}
                      className={`px-2 py-1 rounded-full text-sm font-medium ${statusColors[order.status] || 'bg-gray-100'}`}
                    >
                      {statusOptions.map((status) => (
                        <option key={status} value={status}>
                          {status.charAt(0).toUpperCase() + status.slice(1)}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex justify-end gap-2">
                      {getActionsForStatus(order.status).map((action) => (
                        <button
                          key={action.action}
                          onClick={() => action.handler(order.id)}
                          className={`px-2 py-1 text-xs rounded ${
                            action.action === 'cancel'
                              ? 'bg-red-100 text-red-700 hover:bg-red-200'
                              : action.action === 'confirm'
                              ? 'bg-green-100 text-green-700 hover:bg-green-200'
                              : action.action === 'ship'
                              ? 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                          }`}
                        >
                          {action.label}
                        </button>
                      ))}
                      <Link to={`/orders/${order.id}`} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                        View
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-6">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-gray-600">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page === totalPages}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminOrdersPage;