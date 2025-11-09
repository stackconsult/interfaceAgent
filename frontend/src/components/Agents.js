/**
 * Agents Management Component
 */
import React, { useState, useEffect } from 'react';
import { agentsAPI } from '../services/api';

const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await agentsAPI.list();
      setAgents(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (id) => {
    try {
      await agentsAPI.activate(id);
      loadAgents();
    } catch (err) {
      setError('Failed to activate agent');
    }
  };

  const handleDeactivate = async (id) => {
    try {
      await agentsAPI.deactivate(id);
      loadAgents();
    } catch (err) {
      setError('Failed to deactivate agent');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      try {
        await agentsAPI.delete(id);
        loadAgents();
      } catch (err) {
        setError('Failed to delete agent');
      }
    }
  };

  const getStatusBadge = (status) => {
    const classes = {
      active: 'badge-success',
      inactive: 'badge-warning',
      error: 'badge-danger',
      maintenance: 'badge-info',
    };
    return <span className={`badge ${classes[status]}`}>{status}</span>;
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Agents</h1>
        <button className="btn btn-primary">Create Agent</button>
      </div>

      {error && (
        <div className="alert alert-error">{error}</div>
      )}

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Version</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {agents.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '40px' }}>
                  No agents found. Create your first agent to get started.
                </td>
              </tr>
            ) : (
              agents.map((agent) => (
                <tr key={agent.id}>
                  <td>{agent.name}</td>
                  <td>{agent.agent_type}</td>
                  <td>{getStatusBadge(agent.status)}</td>
                  <td>{agent.version}</td>
                  <td>
                    {agent.status === 'active' ? (
                      <button
                        className="btn btn-secondary"
                        style={{ marginRight: '5px' }}
                        onClick={() => handleDeactivate(agent.id)}
                      >
                        Deactivate
                      </button>
                    ) : (
                      <button
                        className="btn btn-primary"
                        style={{ marginRight: '5px' }}
                        onClick={() => handleActivate(agent.id)}
                      >
                        Activate
                      </button>
                    )}
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDelete(agent.id)}
                    >
                      Delete
                    </button>
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

export default Agents;
