import React, { useState, useEffect } from 'react';
import { pedidosService } from '../../services/pedidosService';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './TenantDashboard.css';

const TenantDashboard = ({ user }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Default to last 30 days
  const today = new Date();
  const thirtyDaysAgo = new Date(new Date().setDate(today.getDate() - 30));
  
  // State for date inputs (controlled)
  const [dateRange, setDateRange] = useState({
    startDate: thirtyDaysAgo.toISOString().split('T')[0],
    endDate: today.toISOString().split('T')[0],
  });

  // State for applied filters that trigger the fetch
  const [appliedFilters, setAppliedFilters] = useState(dateRange);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await pedidosService.getStats(appliedFilters.startDate, appliedFilters.endDate);
        setStats(data);
      } catch (err) {
        setError('Could not load statistics. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [appliedFilters]); // Re-runs only when filters are applied

  const handleDateChange = (e) => {
    setDateRange(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleApplyFilters = () => {
    // Simple validation to prevent invalid ranges
    if (new Date(dateRange.startDate) > new Date(dateRange.endDate)) {
      setError('Start date cannot be after the end date.');
      return;
    }
    setError('');
    setAppliedFilters(dateRange);
  };

  const formatCurrency = (value) => {
    // Using a more generic currency format, can be adjusted
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value || 0);
  };

  if (loading) {
    return <div className="text-center p-5"><h3>Loading Dashboard...</h3></div>;
  }

  if (error) {
    return <div className="alert alert-danger m-4">{error}</div>;
  }

  return (
    <div className="container-fluid p-4">
      <h2 className="mb-4">{user?.tenant_name || 'Your Business'} Dashboard</h2>

      {/* Date Range Picker */}
      <div className="card mb-4">
        <div className="card-body d-flex justify-content-center align-items-center flex-wrap gap-3">
          <div className="me-3">
            <label htmlFor="startDate" className="form-label">From</label>
            <input type="date" id="startDate" name="startDate" className="form-control" value={dateRange.startDate} onChange={handleDateChange} />
          </div>
          <div>
            <label htmlFor="endDate" className="form-label">To</label>
            <input type="date" id="endDate" name="endDate" className="form-control" value={dateRange.endDate} onChange={handleDateChange} />
          </div>
          <div className="align-self-end">
            <button className="btn btn-primary" onClick={handleApplyFilters}>Apply</button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {stats?.summary && (
        <div className="row g-4 mb-4">
          <div className="col-md-6 col-lg-3">
            <div className="card text-white bg-success h-100">
              <div className="card-body">
                <h5 className="card-title">Total Sales</h5>
                <p className="card-text fs-4 fw-bold">{formatCurrency(stats.summary.total_sales_range)}</p>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-3">
            <div className="card text-white bg-primary h-100">
              <div className="card-body">
                <h5 className="card-title">Total Orders</h5>
                <p className="card-text fs-4 fw-bold">{stats.summary.num_orders_range}</p>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-3">
            <div className="card text-white bg-warning h-100">
              <div className="card-body">
                <h5 className="card-title">Total Expenses</h5>
                <p className="card-text fs-4 fw-bold">{formatCurrency(stats.summary.total_expenses_range)}</p>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-3">
            <div className="card text-white bg-danger h-100">
              <div className="card-body">
                <h5 className="card-title">Total Waste</h5>
                <p className="card-text fs-4 fw-bold">{formatCurrency(stats.summary.total_waste_range)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sales Chart */}
      <div className="card">
        <div className="card-header">
          <h5>Sales by Day</h5>
        </div>
        <div className="card-body">
          {stats?.sales_chart_data && stats.sales_chart_data.length > 0 ? (
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart data={stats.sales_chart_data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="fecha" />
                  <YAxis tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`} />
                  <Tooltip formatter={(value) => [formatCurrency(value), 'Sale']} />
                  <Legend />
                  <Line type="monotone" dataKey="venta" name="Sales" stroke="#28a745" strokeWidth={2} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-center text-muted p-5">No sales data to display for this period.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TenantDashboard;