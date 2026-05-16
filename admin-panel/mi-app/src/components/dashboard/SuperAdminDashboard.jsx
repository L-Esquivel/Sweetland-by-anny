import React, { useState, useEffect } from 'react';
import { platformService } from '../../services/platformService';
import './Dashboard.css';

function SuperAdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await platformService.getPlatformStats();
        setStats(data);
      } catch (err) {
        setError('Error loading platform statistics.');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value || 0);
  };

  if (loading) return <div className="loading">Loading platform statistics...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!stats) return <div className="error-message">Could not load data.</div>;

  return (
    <div className="dashboard-container">
      <h1>Platform Dashboard</h1>
      <p>Overview of the Precivox platform status.</p>

      <div className="row mt-4">
        <div className="col-md-3">
          <div className="stat-card">
            <h3>Total Revenue</h3>
            <p className="stat-number">{formatCurrency(stats.total_revenue)}</p>
            <small>Total payments received from tenants.</small>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h3>Total Tenants</h3>
            <p className="stat-number">{stats.total_tenants}</p>
            <small>Active organizations on the platform.</small>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h3>New Tenants (30 days)</h3>
            <p className="stat-number">{stats.new_tenants_30_days}</p>
            <small>Recent platform growth.</small>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h3>Total Users</h3>
            <p className="stat-number">{stats.total_users}</p>
            <small>Registered users across all organizations.</small>
          </div>
        </div>
      </div>

      {/* More components could be added here, like a list of recent logs or a growth chart */}
    </div>
  );
}

export default SuperAdminDashboard;