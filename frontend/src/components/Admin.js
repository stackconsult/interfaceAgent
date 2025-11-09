/**
 * Admin Panel Component
 */
import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';

const Admin = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    try {
      if (activeTab === 'users') {
        const response = await adminAPI.listUsers();
        setUsers(response.data);
      } else if (activeTab === 'roles') {
        const response = await adminAPI.listRoles();
        setRoles(response.data);
      }
      setError('');
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const TabButton = ({ name, label }) => (
    <button
      className={`btn ${activeTab === name ? 'btn-primary' : 'btn-secondary'}`}
      onClick={() => setActiveTab(name)}
      style={{ marginRight: '10px' }}
    >
      {label}
    </button>
  );

  return (
    <div className="container">
      <h1>Admin Panel</h1>

      {error && (
        <div className="alert alert-error">{error}</div>
      )}

      {/* Tabs */}
      <div style={{ marginBottom: '20px' }}>
        <TabButton name="users" label="Users" />
        <TabButton name="roles" label="Roles" />
        <TabButton name="permissions" label="Permissions" />
      </div>

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3>User Management</h3>
            <button className="btn btn-primary">Add User</button>
          </div>
          
          {loading ? (
            <p>Loading users...</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Full Name</th>
                  <th>Status</th>
                  <th>Superuser</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{ textAlign: 'center', padding: '20px' }}>
                      No users found
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td><strong>{user.username}</strong></td>
                      <td>{user.email}</td>
                      <td>{user.full_name || '-'}</td>
                      <td>
                        <span className={`badge ${user.is_active ? 'badge-success' : 'badge-warning'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>{user.is_superuser ? '✓' : '-'}</td>
                      <td>
                        <button className="btn btn-secondary" style={{ marginRight: '5px' }}>
                          Edit
                        </button>
                        <button className="btn btn-secondary">
                          Roles
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Roles Tab */}
      {activeTab === 'roles' && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3>Role Management</h3>
            <button className="btn btn-primary">Add Role</button>
          </div>

          {loading ? (
            <p>Loading roles...</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {roles.length === 0 ? (
                  <tr>
                    <td colSpan="4" style={{ textAlign: 'center', padding: '20px' }}>
                      No roles found
                    </td>
                  </tr>
                ) : (
                  roles.map((role) => (
                    <tr key={role.id}>
                      <td>{role.id}</td>
                      <td><strong>{role.name}</strong></td>
                      <td>{role.description || '-'}</td>
                      <td>
                        <button className="btn btn-secondary" style={{ marginRight: '5px' }}>
                          Edit
                        </button>
                        <button className="btn btn-secondary">
                          Permissions
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Permissions Tab */}
      {activeTab === 'permissions' && (
        <div className="card">
          <h3>Permission Management</h3>
          <p style={{ marginTop: '15px', color: '#666' }}>
            Select a role to manage permissions
          </p>
        </div>
      )}
    </div>
  );
};

export default Admin;
