import React, { useState, useEffect } from 'react';
import adminService, { UsersResponse } from '../../services/adminService';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  roles: string[];
  createdAt: string;
}

const ALL_ROLES = ['cliente', 'admin', 'superAdmin'];

const roleColors: Record<string, string> = {
  cliente: 'bg-blue-100 text-blue-800',
  admin: 'bg-purple-100 text-purple-800',
  superAdmin: 'bg-red-100 text-red-800',
};

const roleLabels: Record<string, string> = {
  cliente: 'Cliente',
  admin: 'Admin',
  superAdmin: 'Super Admin',
};

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [roleFilter, setRoleFilter] = useState<string>('');
  const limit = 10;

  useEffect(() => {
    fetchUsers();
  }, [page, roleFilter]);

  const fetchUsers = async () => {
    try {
      const data: UsersResponse = await adminService.getUsers({
        page,
        limit,
        role: roleFilter || undefined,
      });
      setUsers(data.users);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRole = async (userId: string, roleToAdd: string) => {
    try {
      await adminService.addUserRole(userId, roleToAdd);
      setUsers(users.map((u) => 
        u.id === userId 
          ? { ...u, roles: [...u.roles, roleToAdd], role: roleToAdd } 
          : u
      ));
    } catch (error) {
      console.error('Failed to add role:', error);
    }
  };

  const handleRemoveRole = async (userId: string, roleToRemove: string) => {
    try {
      await adminService.removeUserRole(userId, roleToRemove);
      const updatedUsers = users.map((u) => {
        if (u.id === userId) {
          const newRoles = u.roles.filter(r => r !== roleToRemove);
          return { 
            ...u, 
            roles: newRoles,
            role: newRoles[0] || 'cliente'
          };
        }
        return u;
      });
      setUsers(updatedUsers);
    } catch (error) {
      console.error('Failed to remove role:', error);
    }
  };

  const getAvailableRoles = (userRoles: string[]) => {
    return ALL_ROLES.filter(role => !userRoles.includes(role));
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
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">User Management</h1>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="">All Roles</option>
            <option value="cliente">Clientes</option>
            <option value="admin">Admins</option>
          </select>
        </div>

        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left py-3 px-4">Name</th>
                <th className="text-left py-3 px-4">Email</th>
                <th className="text-left py-3 px-4">Roles</th>
                <th className="text-left py-3 px-4">Joined</th>
                <th className="text-right py-3 px-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-t hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium">{user.name || '-'}</td>
                  <td className="py-3 px-4">{user.email}</td>
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {user.roles.map((role) => (
                        <span
                          key={role}
                          className={`px-2 py-1 rounded-full text-xs font-medium ${roleColors[role] || 'bg-gray-100 text-gray-800'}`}
                        >
                          {roleLabels[role] || role}
                          {user.roles.length > 1 && (
                            <button
                              onClick={() => handleRemoveRole(user.id, role)}
                              className="ml-1 text-red-600 hover:text-red-800"
                              title={`Remove ${roleLabels[role] || role}`}
                            >
                              ×
                            </button>
                          )}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-4">{new Date(user.createdAt).toLocaleDateString()}</td>
                  <td className="py-3 px-4 text-right">
                    {getAvailableRoles(user.roles).length > 0 && (
                      <div className="flex gap-1 justify-end">
                        {getAvailableRoles(user.roles).map((role) => (
                          <button
                            key={role}
                            onClick={() => handleAddRole(user.id, role)}
                            className={`px-2 py-1 text-xs rounded border ${roleColors[role]} hover:opacity-80`}
                            title={`Add ${roleLabels[role] || role}`}
                          >
                            +{roleLabels[role] || role}
                          </button>
                        ))}
                      </div>
                    )}
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

export default UsersPage;