import React, { useState, useEffect } from 'react';
import { pedidosService } from '../../services/pedidosService';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './Dashboard.css';

function TenantDashboard({ user }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [startDate, setStartDate] = useState(new Date(new Date().setDate(new Date().getDate() - 29)));
  const [endDate, setEndDate] = useState(new Date());

  const fetchStats = async () => {
    try {
      setLoading(true);
      const formattedStartDate = startDate.toISOString().split('T')[0];
      const formattedEndDate = endDate.toISOString().split('T')[0];
      const data = await pedidosService.getStats(formattedStartDate, formattedEndDate);
      setStats(data);
    } catch (err) {
      setError('Error al cargar las estadísticas.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleDateFilter = () => {
    fetchStats();
  };

  if (loading) return <div className="loading">Cargando dashboard...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!stats) return <div className="error-message">No se pudieron cargar los datos.</div>;

  const { resumen, grafica, pedidos_por_estado } = stats;
  const netProfit = (resumen.total_ventas_rango || 0) - (resumen.total_gastos_rango || 0) - (resumen.total_merma_rango || 0);

  const pieData = Object.entries(pedidos_por_estado || {}).map(([name, value]) => ({ name, value }));
  const COLORS = { pendiente: '#ffc107', completado: '#28a745', cancelado: '#dc3545', en_proceso: '#17a2b8' };

  return (
    <div className="dashboard-container">
      <h1>Dashboard de {user.nombre}</h1>
      <div className="date-filter-container mb-4 d-flex gap-2 align-items-center">
        <DatePicker selected={startDate} onChange={date => setStartDate(date)} selectsStart startDate={startDate} endDate={endDate} className="form-control" />
        <DatePicker selected={endDate} onChange={date => setEndDate(date)} selectsEnd startDate={startDate} endDate={endDate} minDate={startDate} className="form-control" />
        <button onClick={handleDateFilter} className="btn btn-primary">Filtrar</button>
      </div>

      <div className="row">
        <div className="col-md-3">
          <div className="stat-card">
            <h3>Ventas Totales</h3>
            <p className="stat-number">${(resumen.total_ventas_rango || 0).toLocaleString('es-CO')}</p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h3>Ganancia Neta Real</h3>
            <p className="stat-number" style={{ color: netProfit >= 0 ? '#28a745' : '#dc3545' }}>
              ${netProfit.toLocaleString('es-CO')}
            </p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h3>Gastos y Merma</h3>
            <p className="stat-number">${((resumen.total_gastos_rango || 0) + (resumen.total_merma_rango || 0)).toLocaleString('es-CO')}</p>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stat-card">
            <h3>N° de Pedidos</h3>
            <p className="stat-number">{resumen.num_pedidos_rango || 0}</p>
          </div>
        </div>
      </div>

      {/* Aquí irían las gráficas, si las quieres añadir */}

    </div>
  );
}

export default TenantDashboard;