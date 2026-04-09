import React from 'react';
import { Link } from 'react-router-dom';
import { Order, OrderStatus } from '../../types/order';

interface OrderCardProps {
  order: Order;
}

const statusColors: Record<OrderStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  processing: 'bg-indigo-100 text-indigo-800',
  shipped: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const OrderCard: React.FC<OrderCardProps> = ({ order }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
        <div>
          <p className="text-sm text-gray-500">Order ID</p>
          <p className="font-medium text-gray-900">#{order.id}</p>
        </div>
        <div className="mt-2 sm:mt-0">
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[order.status]}`}
          >
            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
          </span>
        </div>
      </div>

      <div className="border-t border-gray-100 pt-4 mb-4">
        <p className="text-sm text-gray-500 mb-2">
          {order.items.length} {order.items.length === 1 ? 'item' : 'items'}
        </p>
        <div className="flex flex-wrap gap-2">
          {order.items.slice(0, 3).map((item, index) => (
            <span key={index} className="text-sm text-gray-600 bg-gray-50 px-2 py-1 rounded">
              {item.productName} x{item.quantity}
            </span>
          ))}
          {order.items.length > 3 && (
            <span className="text-sm text-gray-500 bg-gray-50 px-2 py-1 rounded">
              +{order.items.length - 3} more
            </span>
          )}
        </div>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pt-4 border-t border-gray-100">
        <div className="text-sm text-gray-500 mb-2 sm:mb-0">
          <span>Ordered on {formatDate(order.createdAt)}</span>
        </div>
        <div className="flex items-center justify-between sm:justify-end">
          <p className="text-lg font-bold text-gray-900 mr-4">${order.total.toFixed(2)}</p>
          <Link
            to={`/orders/${order.id}`}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View Details →
          </Link>
        </div>
      </div>
    </div>
  );
};

export default OrderCard;