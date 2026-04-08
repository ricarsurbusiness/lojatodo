import React, { useState, FormEvent, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { Card, CardContent, CardFooter, CardHeader } from '../../components/common/Card';
import { Alert } from '../../components/common/Alert';

export const ProfilePage: React.FC = () => {
  const { user, updateProfile, isLoading, error, clearError } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (user) {
      setName(user.name);
      setEmail(user.email);
    }
  }, [user]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    setSuccessMessage('');

    try {
      await updateProfile({ name, email });
      setSuccessMessage('Profile updated successfully');
    } catch {
      // Error is handled by AuthContext
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-600">Please log in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-gray-900">Your Profile</h2>
          <p className="mt-2 text-sm text-gray-600">
            Manage your account information
          </p>
        </div>

        <Card variant="bordered" padding="lg">
          <form onSubmit={handleSubmit}>
            <CardHeader className="text-xl">Account Details</CardHeader>
            <CardContent>
              {error && (
                <Alert variant="error" className="mb-4" onClose={clearError}>
                  {error}
                </Alert>
              )}

              {successMessage && (
                <Alert variant="success" className="mb-4" onClose={() => setSuccessMessage('')}>
                  {successMessage}
                </Alert>
              )}

              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-md mb-4">
                  <p className="text-sm text-gray-500">Role</p>
                  <p className="font-medium text-gray-900 capitalize">{user.role}</p>
                </div>

                <Input
                  id="name"
                  name="name"
                  type="text"
                  label="Full name"
                  autoComplete="name"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                />

                <Input
                  id="email"
                  name="email"
                  type="email"
                  label="Email address"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                />

                <Input
                  id="id"
                  name="id"
                  type="text"
                  label="User ID"
                  value={user.id}
                  disabled
                  helperText="Your unique user identifier"
                />
              </div>
            </CardContent>

            <CardFooter>
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                isLoading={isLoading}
                disabled={isLoading}
              >
                Save changes
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default ProfilePage;
