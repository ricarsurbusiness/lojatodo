import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import { OrderProvider } from './context/OrderContext'
import { Layout } from './components/layout/Layout'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import ProfilePage from './pages/auth/ProfilePage'
import HomePage from './pages/shop/HomePage'
import ProductListPage from './pages/shop/ProductListPage'
import ProductDetailPage from './pages/shop/ProductDetailPage'
import CartPage from './pages/cart/CartPage'
import CheckoutPage from './pages/checkout/CheckoutPage'
import OrderHistoryPage from './pages/orders/OrderHistoryPage'
import OrderDetailPage from './pages/orders/OrderDetailPage'
import DashboardPage from './pages/admin/DashboardPage'
import ProductsPage from './pages/admin/ProductsPage'
import AdminOrdersPage from './pages/admin/AdminOrdersPage'
import UsersPage from './pages/admin/UsersPage'
import AnalyticsPage from './pages/admin/AnalyticsPage'
import CategoriesPage from './pages/admin/CategoriesPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <OrderProvider>
            <Layout>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/products" element={<ProductListPage />} />
                <Route path="/products/:id" element={<ProductDetailPage />} />
                <Route path="/cart" element={<CartPage />} />
                <Route path="/checkout" element={<CheckoutPage />} />
                <Route path="/orders" element={<OrderHistoryPage />} />
                <Route path="/orders/:id" element={<OrderDetailPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                
                {/* Admin Routes - wrapped individually */}
                <Route path="/admin" element={
                  <ProtectedRoute requiredRole="admin">
                    <DashboardPage />
                  </ProtectedRoute>
                } />
                <Route path="/admin/products" element={
                  <ProtectedRoute requiredRole="admin">
                    <ProductsPage />
                  </ProtectedRoute>
                } />
                <Route path="/admin/orders" element={
                  <ProtectedRoute requiredRole="admin">
                    <AdminOrdersPage />
                  </ProtectedRoute>
                } />
                <Route path="/admin/users" element={
                  <ProtectedRoute requiredRole="superAdmin">
                    <UsersPage />
                  </ProtectedRoute>
                } />
                <Route path="/admin/analytics" element={
                  <ProtectedRoute requiredRole="admin">
                    <AnalyticsPage />
                  </ProtectedRoute>
                } />
                <Route path="/admin/categories" element={
                  <ProtectedRoute requiredRole="superAdmin">
                    <CategoriesPage />
                  </ProtectedRoute>
                } />
                
                {/* Catch all - redirect to home */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Layout>
          </OrderProvider>
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
