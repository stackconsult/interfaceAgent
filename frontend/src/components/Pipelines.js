/**
 * Pipelines Management Component
 */
import React, { useState, useEffect } from 'react';
import { pipelinesAPI, agentsAPI } from '../services/api';

const Pipelines = () => {
  const [pipelines, setPipelines] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedPipeline, setSelectedPipeline] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [pipelinesRes, agentsRes] = await Promise.all([
        pipelinesAPI.list(),
        agentsAPI.list()
      ]);
      setPipelines(pipelinesRes.data);
      setAgents(agentsRes.data.filter(a => a.status === 'active'));
      setError('');
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this pipeline?')) {
      try {
        await pipelinesAPI.delete(id);
        loadData();
      } catch (err) {
        setError('Failed to delete pipeline');
      }
    }
  };

  const handleExecute = async (id) => {
    try {
      const inputData = { timestamp: new Date().toISOString() };
      await pipelinesAPI.execute(id, { input_data: inputData });
      alert('Pipeline execution started!');
      loadData();
    } catch (err) {
      setError('Failed to execute pipeline');
    }
  };

  const getStatusBadge = (status) => {
    const classes = {
      draft: 'badge-warning',
      active: 'badge-success',
      paused: 'badge-info',
      archived: 'badge-secondary',
    };
    return <span className={`badge ${classes[status]}`}>{status}</span>;
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Pipelines</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          Create Pipeline
        </button>
      </div>

      {error && (
        <div className="alert alert-error">{error}</div>
      )}

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Status</th>
              <th>Steps</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pipelines.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '40px' }}>
                  No pipelines found. Create your first pipeline to get started.
                </td>
              </tr>
            ) : (
              pipelines.map((pipeline) => (
                <tr key={pipeline.id}>
                  <td><strong>{pipeline.name}</strong></td>
                  <td>{pipeline.description || 'No description'}</td>
                  <td>{getStatusBadge(pipeline.status)}</td>
                  <td>{pipeline.steps?.length || 0} steps</td>
                  <td>
                    <button
                      className="btn btn-primary"
                      style={{ marginRight: '5px' }}
                      onClick={() => setSelectedPipeline(pipeline)}
                    >
                      View
                    </button>
                    {pipeline.status === 'active' && (
                      <button
                        className="btn btn-secondary"
                        style={{ marginRight: '5px' }}
                        onClick={() => handleExecute(pipeline.id)}
                      >
                        Execute
                      </button>
                    )}
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDelete(pipeline.id)}
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

      {/* Pipeline Details Modal */}
      {selectedPipeline && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div className="card" style={{ width: '600px', maxHeight: '80vh', overflow: 'auto' }}>
            <h2>{selectedPipeline.name}</h2>
            <p>{selectedPipeline.description}</p>
            
            <h3>Pipeline Steps</h3>
            {selectedPipeline.steps && selectedPipeline.steps.length > 0 ? (
              <div>
                {selectedPipeline.steps
                  .sort((a, b) => a.order - b.order)
                  .map((step, idx) => {
                    const agent = agents.find(a => a.id === step.agent_id);
                    return (
                      <div key={step.id} style={{
                        padding: '15px',
                        marginBottom: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                          <span style={{
                            background: '#007bff',
                            color: 'white',
                            width: '30px',
                            height: '30px',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            marginRight: '10px',
                            fontWeight: 'bold',
                          }}>
                            {step.order}
                          </span>
                          <div>
                            <strong>{agent?.name || `Agent #${step.agent_id}`}</strong>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                              {agent?.agent_type || 'Unknown type'}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            ) : (
              <p>No steps configured</p>
            )}

            <button
              className="btn btn-secondary"
              style={{ marginTop: '20px' }}
              onClick={() => setSelectedPipeline(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Create Pipeline Modal */}
      {showCreateModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div className="card" style={{ width: '500px' }}>
            <h2>Create Pipeline</h2>
            <form onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              try {
                await pipelinesAPI.create({
                  name: formData.get('name'),
                  description: formData.get('description'),
                  config: {},
                });
                setShowCreateModal(false);
                loadData();
              } catch (err) {
                setError('Failed to create pipeline');
              }
            }}>
              <div className="form-group">
                <label>Pipeline Name</label>
                <input
                  type="text"
                  name="name"
                  className="form-control"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  className="form-control"
                  rows="3"
                />
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary">
                  Create
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Pipelines;
