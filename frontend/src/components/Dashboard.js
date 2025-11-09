/**
 * Dashboard Component
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { logout } = useAuth();

  return (
    <div>
      <nav style={{
        background: 'white',
        padding: '15px 30px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '30px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <h2 style={{ margin: 0 }}>Interface Agent</h2>
        <button onClick={logout} className="btn btn-secondary">
          Logout
        </button>
      </nav>

      <div className="container">
        <h1>Dashboard</h1>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '20px',
          marginTop: '30px',
        }}>
          <Link to="/agents" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ 
              textAlign: 'center', 
              cursor: 'pointer',
              transition: 'transform 0.2s',
            }}>
              <h3>Agents</h3>
              <p style={{ color: '#666' }}>Manage modular agents</p>
            </div>
          </Link>

          <Link to="/pipelines" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ 
              textAlign: 'center', 
              cursor: 'pointer',
              transition: 'transform 0.2s',
            }}>
              <h3>Pipelines</h3>
              <p style={{ color: '#666' }}>Configure processing pipelines</p>
            </div>
          </Link>

          <Link to="/monitoring" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ 
              textAlign: 'center', 
              cursor: 'pointer',
              transition: 'transform 0.2s',
            }}>
              <h3>Monitoring</h3>
              <p style={{ color: '#666' }}>Live system monitoring</p>
            </div>
          </Link>

          <Link to="/audit-logs" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ 
              textAlign: 'center', 
              cursor: 'pointer',
              transition: 'transform 0.2s',
            }}>
              <h3>Audit Logs</h3>
              <p style={{ color: '#666' }}>View audit trail</p>
            </div>
          </Link>

          <Link to="/plugins" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ 
              textAlign: 'center', 
              cursor: 'pointer',
              transition: 'transform 0.2s',
            }}>
              <h3>Plugins</h3>
              <p style={{ color: '#666' }}>Manage plugin registry</p>
            </div>
          </Link>

          <Link to="/admin" style={{ textDecoration: 'none' }}>
            <div className="card" style={{ 
              textAlign: 'center', 
              cursor: 'pointer',
              transition: 'transform 0.2s',
            }}>
              <h3>Admin</h3>
              <p style={{ color: '#666' }}>System administration</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
