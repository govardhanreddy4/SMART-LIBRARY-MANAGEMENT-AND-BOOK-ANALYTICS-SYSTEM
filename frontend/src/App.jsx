import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import AppLayout from './components/layout/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import BooksPage from './pages/BooksPage';
import MembersPage from './pages/MembersPage';
import CirculationPage from './pages/CirculationPage';
import AnalyticsPage from './pages/AnalyticsPage';
import BookDiscoveryPage from './pages/BookDiscoveryPage';
import ConcurrencyPage from './pages/ConcurrencyPage';

// Simple Route Protection
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-400 text-sm">
        Initializing Smart Library Application...
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="books" element={<BooksPage />} />
            <Route path="members" element={<MembersPage />} />
            <Route path="loans" element={<CirculationPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="discovery" element={<BookDiscoveryPage />} />
            <Route path="concurrency" element={<ConcurrencyPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
