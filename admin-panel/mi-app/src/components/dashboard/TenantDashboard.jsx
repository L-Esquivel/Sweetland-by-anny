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
  
  const [dateRange, setDateRange] = useState({
    startDate: thirtyDaysAgo.toISOString().split('T')[0],
    endDate: today.toISOString().split('T')[0],
  });

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await pedidosService.getStats(dateRange.startDate, dateRange.endDate);
        setStats(data);
      } catch (err) {
        setError('No se pudieron cargar las estadísticas. Intenta de nuevo.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [dateRange]);

  const handleDateChange = (e) => {
    setDateRange(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
  };

  if (loading) {
    return <div className="text-center p-5"><h3>Cargando Dashboard...</h3></div>;
  }

  if (error) {
    return <div className="alert alert-danger m-4">{error}</div>;
  }

  return (
    <div className="container-fluid p-4">
      <h2 className="mb-4">Dashboard de {user?.tenant_name || 'tu Negocio'}</h2>

      {/* Date Range Picker */}
      <div className="card mb-4">
        <div className="card-body d-flex justify-content-center align-items-center flex-wrap gap-3">
          <div className="me-3">
            <label htmlFor="startDate" className="form-label">Desde</label>
            <input type="date" id="startDate" name="startDate" className="form-control" value={dateRange.startDate} onChange={handleDateChange} />
          </div>
          <div>
            <label htmlFor="endDate" className="form-label">Hasta</label>
            <input type="date" id="endDate" name="endDate" className="form-control" value={dateRange.endDate} onChange={handleDateChange} />
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {stats?.resumen && (
        <div className="row g-4 mb-4">
          <div className="col-md-6 col-lg-3">
            <div className="card text-white bg-success h-100">
              <div className="card-body">
                <h5 className="card-title">Ventas Totales</h5>
                <p className="card-text fs-4 fw-bold">{formatearMoneda(stats.resumen.total_ventas_rango)}</p>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-3">
            <div className="card text-white bg-primary h-100">
              <div className="card-body">
                <h5 className="card-title">Nº de Pedidos</h5>
                <p className="card-text fs-4 fw-bold">{stats.resumen.num_pedidos_rango}</p>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-3">
            <div className="card text-white bg-warning h-100">
              <div className="card-body">
                <h5 className="card-title">Gastos Totales</h5>
                <p className="card-text fs-4 fw-bold">{formatearMoneda(stats.resumen.total_gastos_rango)}</p>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-3">
            <div className="card text-white bg-danger h-100">
              <div className="card-body">
                <h5 className="card-title">Merma Total</h5>
                <p className="card-text fs-4 fw-bold">{formatearMoneda(stats.resumen.total_merma_rango)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sales Chart */}
      <div className="card">
        <div className="card-header">
          <h5>Ventas por Día</h5>
        </div>
        <div className="card-body">
          {stats?.grafica && stats.grafica.length > 0 ? (
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart data={stats.grafica} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="fecha" />
                  <YAxis tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`} />
                  <Tooltip formatter={(value) => [formatearMoneda(value), 'Venta']} />
                  <Legend />
                  <Line type="monotone" dataKey="venta" name="Ventas" stroke="#28a745" strokeWidth={2} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-center text-muted p-5">No hay datos de ventas para mostrar en este período.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TenantDashboard;