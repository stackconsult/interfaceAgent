/**
 * Audit Logs Viewer Component
 */
import React, { useState, useEffect } from 'react';
import { auditLogsAPI } from '../services/api';

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    action: '',
    resource_type: '',
    status: '',
  });
  const [actions, setActions] = useState([]);
  const [resourceTypes, setResourceTypes] = useState([]);

  useEffect(() => {
    loadFilters();
    loadLogs();
  }, []);

  const loadFilters = async () => {
    try {
      const [actionsRes, typesRes] = await Promise.all([
        auditLogsAPI.listActions(),
        auditLogsAPI.listResourceTypes(),
      ]);
      setActions(actionsRes.data.actions || []);
      setResourceTypes(typesRes.data.resource_types || []);
    } catch (err) {
      console.error('Failed to load filter options:', err);
    }
  };

  const loadLogs = async () => {
    try {
      const params = {};
      if (filters.action) params.action = filters.action;
      if (filters.resource_type) params.resource_type = filters.resource_type;
      if (filters.status) params.status = filters.status;

      const response = await auditLogsAPI.list(params);
      setLogs(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
  };

  const handleApplyFilters = () => {
    setLoading(true);
    loadLogs();
  };

  const handleClearFilters = () => {
    setFilters({ action: '', resource_type: '', status: '' });
    setLoading(true);
    setTimeout(() => loadLogs(), 100);
  };

  const getStatusBadge = (status) => {
    return (
      <span className={`badge ${status === 'success' ? 'badge-success' : 'badge-danger'}`}>
        {status}
      </span>
    );
  };

  if (loading) {
    return <div className="container">Loading audit logs...</div>;
  }

  return (
    <div className="container">
      <h1>Audit Logs</h1>

      {error && (
        <div className="alert alert-error">{error}</div>
      )}

      {/* Filters */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Filters</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
          <div className="form-group">
            <label>Action</label>
            <select
              className="form-control"
              value={filters.action}
              onChange={(e) => handleFilterChange('action', e.target.value)}
            >
              <option value="">All Actions</option>
              {actions.map((action) => (
                <option key={action} value={action}>{action}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Resource Type</label>
            <select
              className="form-control"
              value={filters.resource_type}
              onChange={(e) => handleFilterChange('resource_type', e.target.value)}
            >
              <option value="">All Resources</option>
              {resourceTypes.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Status</label>
            <select
              className="form-control"
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failure">Failure</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <button className="btn btn-primary" onClick={handleApplyFilters}>
            Apply Filters
          </button>
          <button className="btn btn-secondary" onClick={handleClearFilters}>
            Clear Filters
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Action</th>
              <th>Resource</th>
              <th>Status</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '40px' }}>
                  No audit logs found
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>{log.user_id ? `User #${log.user_id}` : 'System'}</td>
                  <td><span className="badge badge-info">{log.action}</span></td>
                  <td>
                    {log.resource_type}
                    {log.resource_id && <span style={{ color: '#666', fontSize: '12px' }}> #{log.resource_id}</span>}
                  </td>
                  <td>{getStatusBadge(log.status)}</td>
                  <td>
                    {log.details && Object.keys(log.details).length > 0 ? (
                      <details>
                        <summary style={{ cursor: 'pointer', color: '#007bff' }}>View</summary>
                        <pre style={{ 
                          fontSize: '11px', 
                          background: '#f5f5f5', 
                          padding: '10px', 
                          borderRadius: '4px',
                          marginTop: '5px',
                          maxWidth: '300px',
                          overflow: 'auto',
                        }}>
                          {JSON.stringify(log.details, null, 2)}
                        </pre>
                      </details>
                    ) : (
                      <span style={{ color: '#999' }}>-</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditLogs;
