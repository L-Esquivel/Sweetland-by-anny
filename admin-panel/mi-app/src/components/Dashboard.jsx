import React, { useState, useEffect } from 'react';
import { pedidosService } from '../services/pedidosService';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Estado para los filtros de fecha, inicializado a los últimos 30 días
  const [fechas, setFechas] = useState(() => {
    const fin = new Date();
    const inicio = new Date();
    inicio.setDate(fin.getDate() - 29);
    return {
      inicio: inicio.toISOString().split('T')[0],
      fin: fin.toISOString().split('T')[0],
    };
  });

  const cargarStats = async (fechaInicio, fechaFin) => {
    try {
      setLoading(true);
      setError(null);
      const data = await pedidosService.getStats(fechaInicio, fechaFin);
      setStats(data);
    } catch (err) {
      setError('No se pudieron cargar las estadísticas. Intenta de nuevo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Carga inicial de datos al montar el componente
  useEffect(() => {
    cargarStats(fechas.inicio, fechas.fin);
  }, []);

  const handleFiltrar = () => {
    cargarStats(fechas.inicio, fechas.fin);
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
  };

  if (loading) {
    return <div className="text-center p-5"><h3>Cargando Dashboard...</h3></div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <div className="container-fluid p-4">
      <h2 className="mb-4">📊 Dashboard de Rendimiento</h2>

      {/* SECCIÓN DE FILTROS */}
      <div className="card shadow-sm mb-4">
        <div className="card-body d-flex align-items-center gap-3 flex-wrap">
          <div>
            <label htmlFor="fecha_inicio" className="form-label fw-bold">Desde:</label>
            <input 
              type="date" 
              id="fecha_inicio" 
              className="form-control" 
              value={fechas.inicio}
              onChange={(e) => setFechas({ ...fechas, inicio: e.target.value })}
            />
          </div>
          <div>
            <label htmlFor="fecha_fin" className="form-label fw-bold">Hasta:</label>
            <input 
              type="date" 
              id="fecha_fin" 
              className="form-control" 
              value={fechas.fin}
              onChange={(e) => setFechas({ ...fechas, fin: e.target.value })}
            />
          </div>
          <div className="align-self-end">
            <button className="btn btn-primary" onClick={handleFiltrar}>
              Filtrar
            </button>
          </div>
        </div>
        {stats?.filtros_aplicados && (
          <div className="card-footer text-muted small">
            Mostrando datos del <strong>{stats.filtros_aplicados.fecha_inicio}</strong> al <strong>{stats.filtros_aplicados.fecha_fin}</strong>
          </div>
        )}
      </div>

      {/* TARJETAS DE RESUMEN */}
      <div className="row">
        <div className="col-lg-4 col-md-6 mb-4">
          <div className="card text-white bg-success h-100">
            <div className="card-body">
              <h5 className="card-title">Ventas en Rango</h5>
              <p className="card-text fs-2 fw-bold">{formatearMoneda(stats?.resumen?.total_ventas_rango)}</p>
            </div>
          </div>
        </div>
        <div className="col-lg-4 col-md-6 mb-4">
          <div className="card text-white bg-info h-100">
            <div className="card-body">
              <h5 className="card-title">Pedidos en Rango</h5>
              <p className="card-text fs-2 fw-bold">{stats?.resumen?.num_pedidos_rango}</p>
            </div>
          </div>
        </div>
        <div className="col-lg-4 col-md-12 mb-4">
          <div className="card text-dark bg-light h-100">
            <div className="card-body">
              <h5 className="card-title">Ventas Totales Históricas</h5>
              <p className="card-text fs-2 fw-bold">{formatearMoneda(stats?.resumen?.total_historico)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* GRÁFICA DE VENTAS */}
      <div className="card shadow-sm mb-4">
        <div className="card-header">Ventas Diarias en el Periodo</div>
        <div className="card-body">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats?.grafica} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="fecha" />
              <YAxis tickFormatter={formatearMoneda} width={100} />
              <Tooltip formatter={(value) => formatearMoneda(value)} />
              <Legend />
              <Bar dataKey="venta" fill="#82ca9d" name="Ventas" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;