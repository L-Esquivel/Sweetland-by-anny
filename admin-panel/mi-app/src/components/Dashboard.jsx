import React, { useState, useEffect, useRef } from 'react';
import { pedidosService } from '../services/pedidosService';

// Importación modular de Chart.js
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarController, // <--- FALTABA ESTE (El "cerebro" de las barras)
  BarElement, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';

// Registramos incluyendo el BarController
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarController, // <--- REGISTRAR AQUÍ TAMBIÉN
  BarElement, 
  Title, 
  Tooltip, 
  Legend
);

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  const coloresEstados = {
    'completado': '#28a745',
    'confirmado': '#17a2b8',
    'en_preparacion': '#007bff',
    'pendiente': '#ffc107',
    'cancelado': '#dc3545'
  };

  // EFECTO 1: Carga de datos reales desde el Backend
  useEffect(() => {
    const cargarDatosReales = async () => {
      try {
        setLoading(true);
        const statsData = await pedidosService.getStats();
        setStats(statsData);
      } catch (err) {
        console.error('Error en Dashboard:', err);
        setError('No se pudieron cargar las estadísticas reales.');
      } finally {
        setLoading(false);
      }
    };
    cargarDatosReales();
  }, []);

  // EFECTO 2: Renderizado del Gráfico de Ventas
  useEffect(() => {
    // SEGURO: Si no hay datos, no hay canvas o la lista de gráfica está vacía, no hacer nada
    if (!stats?.grafica || stats.grafica.length === 0 || !chartRef.current) return;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    
    // Invertimos el array para mostrar cronológicamente de izquierda a derecha
    const datosGrafica = [...stats.grafica].reverse();
    const labels = datosGrafica.map(d => formatearFechaCorta(d.fecha));
    const data = datosGrafica.map(d => d.venta);

    chartInstance.current = new ChartJS(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Ventas Diarias',
          data: data,
          backgroundColor: 'rgba(102, 126, 234, 0.8)',
          borderColor: 'rgba(102, 126, 234, 1)',
          borderWidth: 2,
          borderRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { callback: (value) => '$' + value.toLocaleString() } }
        }
      }
    });

    return () => {
      if (chartInstance.current) chartInstance.current.destroy();
    };
  }, [stats]);

  // Funciones de Formateo
  const formatearDinero = (v) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(v || 0);
  
  const formatearFecha = (f) => f ? new Intl.DateTimeFormat('es-CO', { dateStyle: 'long' }).format(new Date(f)) : '---';

  const formatearFechaCorta = (f) => {
    if (!f) return '';
    const date = new Date(f);
    return date.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
  };

  if (loading) return (
    <div className="text-center p-5">
      <div className="spinner-border text-primary" role="status"></div>
      <h5 className="mt-3">Consultando base de datos en tiempo real...</h5>
    </div>
  );

  if (error) return <div className="alert alert-danger m-4">{error}</div>;

  return (
    <div className="dashboard-container p-4">
      <h2 className="mb-4">📊 Dashboard de Gestión Real</h2>

      {/* TARJETAS DE DATOS REALES */}
      <div className="row g-4 mb-5">
        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-primary text-white p-3">
            <h6 className="opacity-75">VENTAS HOY</h6>
            <h3 className="fw-bold">{formatearDinero(stats.resumen.hoy)}</h3>
            <small>Basado en pedidos de hoy</small>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-success text-white p-3">
            <h6 className="opacity-75">VENTAS MES</h6>
            <h3 className="fw-bold">{formatearDinero(stats.resumen.mes)}</h3>
            <small>Acumulado mes actual</small>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-dark text-white p-3">
            <h6 className="opacity-75">PEDIDOS TOTALES</h6>
            <h3 className="fw-bold">{stats.resumen.num_pedidos}</h3>
            <small>Excluyendo cancelados</small>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-warning text-dark p-3">
            <h6 className="opacity-75">PRODUCTO MÁS VENDIDO</h6>
            <h5 className="fw-bold text-truncate">{stats.producto_top?.nombre || 'Sin ventas aún'}</h5>
            <small>{stats.producto_top ? `Vendidos: ${stats.producto_top.total_vendido}` : 'Esperando datos'}</small>
          </div>
        </div>
      </div>

      <div className="row g-4 mb-5">
        {/* GRÁFICO REAL */}
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 p-4 h-100">
            <h6 className="fw-bold mb-4 text-muted">📈 FLUJO DE CAJA (ÚLTIMOS 7 DÍAS)</h6>
            <div style={{ height: '300px' }}>
              {stats.grafica.length > 0 ? (
                <canvas ref={chartRef}></canvas>
              ) : (
                <div className="h-100 d-flex align-items-center justify-content-center text-muted italic">
                  No hay ventas registradas en la última semana
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ESTADOS REALES */}
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 p-4 h-100">
            <h6 className="fw-bold mb-4 text-muted">📋 ESTADO DE OPERACIONES</h6>
            {stats.pedidos_por_estado && Object.keys(stats.pedidos_por_estado).length > 0 ? (
              Object.entries(stats.pedidos_por_estado).map(([estado, cant], i) => {
                const total = stats.resumen.num_pedidos || 1;
                const porc = ((cant / total) * 100).toFixed(0);
                return (
                  <div key={i} className="mb-3">
                    <div className="d-flex justify-content-between small fw-bold">
                      <span className="text-uppercase">{estado.replace('_', ' ')}</span>
                      <span>{cant}</span>
                    </div>
                    <div className="progress" style={{ height: '10px' }}>
                      <div className="progress-bar" style={{ width: `${porc}%`, backgroundColor: coloresEstados[estado] || '#6c757d' }}></div>
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-center text-muted my-auto">Sin historial de estados</p>
            )}
          </div>
        </div>
      </div>

      {/* TABLA DE VENTAS DIARIAS */}
      <div className="card shadow-sm border-0 overflow-hidden">
        <div className="card-header bg-white py-3">
          <h6 className="mb-0 fw-bold">📅 Detalle Cronológico de Ingresos</h6>
        </div>
        <div className="table-responsive">
          <table className="table table-hover mb-0">
            <thead className="table-light">
              <tr>
                <th>Fecha</th>
                <th className="text-end">Venta Bruta</th>
              </tr>
            </thead>
            <tbody>
              {stats.grafica.map((dia, i) => (
                <tr key={i}>
                  <td>{formatearFecha(dia.fecha)}</td>
                  <td className="text-end fw-bold text-success">{formatearDinero(dia.venta)}</td>
                </tr>
              ))}
              {stats.grafica.length === 0 && (
                <tr><td colSpan="2" className="text-center p-4 text-muted">No se encontraron registros de ventas</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;