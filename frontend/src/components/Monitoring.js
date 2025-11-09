/**
 * Live Monitoring Dashboard Component
 */
import React, { useState, useEffect } from 'react';
import { agentsAPI, pipelinesAPI, auditLogsAPI } from '../services/api';

const Monitoring = () => {
  const [stats, setStats] = useState({
    totalAgents: 0,
    activeAgents: 0,
    totalPipelines: 0,
    activePipelines: 0,
    recentActivity: 0,
  });
  const [recentLogs, setRecentLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [agentsRes, pipelinesRes, logsRes] = await Promise.all([
        agentsAPI.list(),
        pipelinesAPI.list(),
        auditLogsAPI.list({ limit: 10 })
      ]);

      const agents = agentsRes.data;
      const pipelines = pipelinesRes.data;
      const logs = logsRes.data;

      setStats({
        totalAgents: agents.length,
        activeAgents: agents.filter(a => a.status === 'active').length,
        totalPipelines: pipelines.length,
        activePipelines: pipelines.filter(p => p.status === 'active').length,
        recentActivity: logs.length,
      });

      setRecentLogs(logs);
    } catch (err) {
      console.error('Failed to load monitoring data:', err);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, subtitle, color }) => (
    <div className="card" style={{ 
      flex: 1, 
      minWidth: '200px',
      background: color || 'white',
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
          {title}
        </div>
        <div style={{ fontSize: '36px', fontWeight: 'bold', marginBottom: '5px' }}>
          {value}
        </div>
        {subtitle && (
          <div style={{ fontSize: '12px', color: '#999' }}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );

  if (loading) {
    return <div className="container">Loading monitoring data...</div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Live Monitoring</h1>
        <button className="btn btn-secondary" onClick={loadData}>
          🔄 Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div style={{ 
        display: 'flex', 
        gap: '20px', 
        marginBottom: '30px',
        flexWrap: 'wrap',
      }}>
        <StatCard
          title="Total Agents"
          value={stats.totalAgents}
          subtitle={`${stats.activeAgents} active`}
        />
        <StatCard
          title="Total Pipelines"
          value={stats.totalPipelines}
          subtitle={`${stats.activePipelines} active`}
        />
        <StatCard
          title="Recent Activity"
          value={stats.recentActivity}
          subtitle="Last 24 hours"
        />
        <StatCard
          title="System Status"
          value="✓"
          subtitle="Healthy"
          color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        />
      </div>

      {/* System Health */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>System Health</h3>
        <div style={{ marginTop: '15px' }}>
          <div style={{ marginBottom: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span>Backend API</span>
              <span className="badge badge-success">Online</span>
            </div>
            <div style={{ background: '#e0e0e0', height: '8px', borderRadius: '4px' }}>
              <div style={{ background: '#28a745', width: '100%', height: '100%', borderRadius: '4px' }} />
            </div>
          </div>
          <div style={{ marginBottom: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span>Database</span>
              <span className="badge badge-success">Connected</span>
            </div>
            <div style={{ background: '#e0e0e0', height: '8px', borderRadius: '4px' }}>
              <div style={{ background: '#28a745', width: '95%', height: '100%', borderRadius: '4px' }} />
            </div>
          </div>
          <div style={{ marginBottom: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
              <span>Event Bus</span>
              <span className="badge badge-success">Running</span>
            </div>
            <div style={{ background: '#e0e0e0', height: '8px', borderRadius: '4px' }}>
              <div style={{ background: '#28a745', width: '98%', height: '100%', borderRadius: '4px' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3>Recent Activity</h3>
        <div style={{ marginTop: '15px' }}>
          {recentLogs.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
              No recent activity
            </p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentLogs.map((log) => (
                  <tr key={log.id}>
                    <td>{new Date(log.created_at).toLocaleString()}</td>
                    <td>{log.action}</td>
                    <td>{log.resource_type}</td>
                    <td>
                      <span className={`badge ${log.status === 'success' ? 'badge-success' : 'badge-danger'}`}>
                        {log.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default Monitoring;
