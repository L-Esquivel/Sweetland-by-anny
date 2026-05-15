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
        setError('Error al cargar las estadísticas de la plataforma.');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <div className="loading">Cargando estadísticas de la plataforma...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="dashboard-container">
      <h1>Dashboard de la Plataforma</h1>
      <p>Visión general del estado de Precivox.</p>

      <div className="row mt-4">
        <div className="col-md-4">
          <div className="stat-card">
            <h3>Total de Tenants</h3>
            <p className="stat-number">{stats.total_tenants}</p>
            <small>Organizaciones activas en la plataforma.</small>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card">
            <h3>Nuevos Tenants (30 días)</h3>
            <p className="stat-number">{stats.new_tenants_30_days}</p>
            <small>Crecimiento reciente de la plataforma.</small>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card">
            <h3>Total de Usuarios</h3>
            <p className="stat-number">{stats.total_users}</p>
            <small>Usuarios registrados en todas las organizaciones.</small>
          </div>
        </div>
      </div>

      {/* Aquí se podrían añadir más componentes, como una lista de logs recientes o una gráfica de crecimiento */}
    </div>
  );
}

export default SuperAdminDashboard;