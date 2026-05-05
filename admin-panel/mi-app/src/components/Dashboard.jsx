import React, { useState, useEffect, useRef } from 'react';
import { pedidosService } from '../services/pedidosService';
import Chart from 'chart.js/auto';

const Dashboard = ({ user }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  // Configuración de colores por estado
  const coloresEstados = {
    'completado': '#28a745',
    'confirmado': '#17a2b8',
    'en_preparacion': '#007bff',
    'pendiente': '#ffc107',
    'cancelado': '#dc3545'
  };

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const statsData = await pedidosService.getStats();
        setStats(statsData);
      } catch (error) {
        console.error('Error cargando dashboard:', error);
      } finally {
        setLoading(false);
      }
    };
    cargarDatos();
  }, []);

  // Efecto para renderizar el gráfico de tendencia
  useEffect(() => {
    if (!stats?.grafica || !chartRef.current) return;

    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    
    // Invertimos el array para que la fecha más antigua salga a la izquierda
    const datosGrafica = [...stats.grafica].reverse();
    const labels = datosGrafica.map(d => formatearFechaCorta(d.fecha));
    const data = datosGrafica.map(d => d.venta);

    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Ventas (COP)',
          data: data,
          backgroundColor: 'rgba(102, 126, 234, 0.8)',
          borderColor: 'rgba(102, 126, 234, 1)',
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => formatearDinero(context.raw)
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => formatearDineroCompacto(value)
            }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [stats]);

  const formatearDinero = (valor) => {
    return new Intl.NumberFormat('es-CO', { 
      style: 'currency', 
      currency: 'COP', 
      maximumFractionDigits: 0 
    }).format(valor || 0);
  };

  const formatearDineroCompacto = (valor) => {
    if (valor >= 1000000) return `$${(valor / 1000000).toFixed(1)}M`;
    if (valor >= 1000) return `$${(valor / 1000).toFixed(0)}K`;
    return `$${valor}`;
  };

  const formatearFecha = (fechaStr) => {
    if (!fechaStr) return 'Fecha no disponible';
    const fecha = new Date(fechaStr);
    return new Intl.DateTimeFormat('es-CO', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(fecha);
  };

  const formatearFechaCorta = (fechaStr) => {
    if (!fechaStr) return '';
    const fecha = new Date(fechaStr);
    return new Intl.DateTimeFormat('es-CO', {
      weekday: 'short',
      day: 'numeric',
      month: 'short'
    }).format(fecha);
  };

  if (loading) return (
    <div className="text-center p-5">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Cargando...</span>
      </div>
      <h5 className="mt-3">Analizando finanzas reales...</h5>
    </div>
  );

  return (
    <div className="dashboard-container p-4">
      <h2 className="mb-4">📊 Resumen de Negocio</h2>

      {/* TARJETAS DE KPIs */}
      <div className="row g-4 mb-5">
        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-primary text-white h-100">
            <div className="card-body">
              <h6 className="text-uppercase opacity-75">Ventas de Hoy</h6>
              <h2 className="fw-bold">{formatearDinero(stats?.resumen?.hoy)}</h2>
              <small>Pedidos procesados hoy</small>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-success text-white h-100">
            <div className="card-body">
              <h6 className="text-uppercase opacity-75">Ventas del Mes</h6>
              <h2 className="fw-bold">{formatearDinero(stats?.resumen?.mes)}</h2>
              <small>Total acumulado este mes</small>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-dark text-white h-100">
            <div className="card-body">
              <h6 className="text-uppercase opacity-75">Total Histórico</h6>
              <h2 className="fw-bold">{formatearDinero(stats?.resumen?.total_historico)}</h2>
              <small>{stats?.resumen?.num_pedidos} pedidos (no cancelados)</small>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-warning text-dark h-100">
            <div className="card-body">
              <h6 className="text-uppercase opacity-75">Producto Top</h6>
              <h5 className="fw-bold text-truncate">{stats?.producto_top?.nombre || 'Sin ventas'}</h5>
              <small>{stats?.producto_top ? `${formatearDinero(stats.producto_top.precio)} unidad` : 'Esperando ventas'}</small>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4 mb-5">
        {/* GRÁFICO DE TENDENCIA */}
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
              <span>📈 Tendencia de Ventas (Últimos 7 días)</span>
              <small className="text-muted">{stats?.grafica?.length} días registrados</small>
            </div>
            <div className="card-body">
              <div style={{ height: '300px' }}>
                <canvas ref={chartRef}></canvas>
              </div>
            </div>
          </div>
        </div>

        {/* PEDIDOS POR ESTADO REALES */}
        <div className="col-lg-4">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold">📋 Pedidos por Estado</div>
            <div className="card-body">
              {stats?.pedidos_por_estado && Object.entries(stats.pedidos_por_estado).map(([estado, cantidad], i) => {
                const totalPedidos = Object.values(stats.pedidos_por_estado).reduce((a, b) => a + b, 0);
                const porcentaje = ((cantidad / totalPedidos) * 100).toFixed(0);
                const color = coloresEstados[estado.toLowerCase()] || '#secondary';

                return (
                  <div key={i} className="mb-3">
                    <div className="d-flex justify-content-between align-items-center mb-1">
                      <span className="text-capitalize d-flex align-items-center">
                        <span 
                          className="rounded-circle me-2" 
                          style={{ width: '12px', height: '12px', backgroundColor: color }}
                        ></span>
                        {estado.replace('_', ' ')}
                      </span>
                      <span className="fw-bold">{cantidad}</span>
                    </div>
                    <div className="progress" style={{ height: '8px' }}>
                      <div 
                        className="progress-bar" 
                        style={{ width: `${porcentaje}%`, backgroundColor: color }}
                        aria-valuenow={porcentaje} 
                      ></div>
                    </div>
                    <small className="text-muted">{porcentaje}% del total</small>
                  </div>
                );
              })}
              {(!stats?.pedidos_por_estado || Object.keys(stats.pedidos_por_estado).length === 0) && (
                <p className="text-center text-muted">No hay pedidos registrados.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* TABLA DE ÚLTIMAS VENTAS */}
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white fw-bold">📅 Detalle de Ventas Recientes</div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-hover">
              <thead className="table-light">
                <tr>
                  <th>Fecha</th>
                  <th>Día</th>
                  <th className="text-end">Venta Total</th>
                </tr>
              </thead>
              <tbody>
                {stats?.grafica?.map((dia, i) => (
                  <tr key={i}>
                    <td className="fw-semibold">{formatearFecha(dia.fecha)}</td>
                    <td>
                      <span className="badge bg-light text-dark">
                        {formatearFechaCorta(dia.fecha)}
                      </span>
                    </td>
                    <td className="text-end fw-bold text-success">{formatearDinero(dia.venta)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;