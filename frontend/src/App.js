/**
 * Main App Component
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Agents from './components/Agents';
import './index.css';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  return user ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/agents"
            element={
              <PrivateRoute>
                <Agents />
              </PrivateRoute>
            }
          />
          <Route
            path="/pipelines"
            element={
              <PrivateRoute>
                <div className="container"><h1>Pipelines (Coming Soon)</h1></div>
              </PrivateRoute>
            }
          />
          <Route
            path="/monitoring"
            element={
              <PrivateRoute>
                <div className="container"><h1>Monitoring (Coming Soon)</h1></div>
              </PrivateRoute>
            }
          />
          <Route
            path="/audit-logs"
            element={
              <PrivateRoute>
                <div className="container"><h1>Audit Logs (Coming Soon)</h1></div>
              </PrivateRoute>
            }
          />
          <Route
            path="/plugins"
            element={
              <PrivateRoute>
                <div className="container"><h1>Plugins (Coming Soon)</h1></div>
              </PrivateRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <PrivateRoute>
                <div className="container"><h1>Admin (Coming Soon)</h1></div>
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
