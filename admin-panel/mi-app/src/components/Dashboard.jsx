import React, { useState, useEffect } from 'react';
import { pedidosService } from '../services/pedidosService';
import { productosService } from '../services/productosService';

// Chart.js se importa dinámicamente para evitar errores si no está instalado
import Chart from 'chart.js/auto';

const Dashboard = ({ user }) => {
  const [stats, setStats] = useState(null);
  const [productoTop, setProductoTop] = useState(null);
  const [pedidosPorEstado, setPedidosPorEstado] = useState([]);
  const [loading, setLoading] = useState(true);
  const chartRef = React.useRef(null);
  const chartInstance = React.useRef(null);

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        const [statsData, productosData] = await Promise.all([
          pedidosService.getStats(),
          productosService.getProductos()
        ]);

        setStats(statsData);

        // Calcular producto más vendido (simulado - en producción debería venir del backend)
        const productoMasVendido = calcularProductoTop(productosData);
        setProductoTop(productoMasVendido);

        // Calcular pedidos por estado (simulado - idealmente viene del backend)
        const estados = calcularPedidosPorEstado(statsData);
        setPedidosPorEstado(estados);

      } catch (error) {
        console.error('Error cargando dashboard:', error);
      } finally {
        setLoading(false);
      }
    };
    cargarDatos();
  }, []);

  // Efecto para renderizar el gráfico
  useEffect(() => {
    if (!Chart || !stats?.grafica || !chartRef.current) return;

    // Destruir gráfico anterior si existe
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    const labels = stats.grafica.map(d => formatearFechaCorta(d.fecha));
    const data = stats.grafica.map(d => d.venta);

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

  const calcularProductoTop = (productos) => {
    if (!productos || productos.length === 0) return null;
    // En producción, esto debería calcularse desde ventas reales
    // Por ahora, simulamos con el producto con más recetas (más complejo = más vendido)
    return productos.reduce((max, p) => (p.precio > max.precio ? p : max), productos[0]);
  };

  const calcularPedidosPorEstado = (stats) => {
    // Simulación - en producción debería venir del backend
    return [
      { estado: 'Completado', cantidad: 45, color: '#28a745', porcentaje: 68 },
      { estado: 'Pendiente', cantidad: 12, color: '#ffc107', porcentaje: 18 },
      { estado: 'En preparación', cantidad: 6, color: '#007bff', porcentaje: 9 },
      { estado: 'Cancelado', cantidad: 3, color: '#dc3545', porcentaje: 5 },
    ];
  };

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
      <h5 className="mt-3">Analizando finanzas...</h5>
    </div>
  );

  return (
    <div className="dashboard-container">
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
              <small>{stats?.resumen?.num_pedidos} pedidos en total</small>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card border-0 shadow-sm bg-warning text-dark h-100">
            <div className="card-body">
              <h6 className="text-uppercase opacity-75">Producto Top</h6>
              <h5 className="fw-bold">{productoTop?.nombre || 'N/A'}</h5>
              <small>{formatearDinero(productoTop?.precio)} por unidad</small>
            </div>
          </div>
        </div>
      </div>

      {/* GRÁFICO + PEDIDOS POR ESTADO */}
      <div className="row g-4 mb-5">
        <div className="col-md-8">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
              <span>📈 Tendencia de Ventas (Últimos 7 días)</span>
              <small className="text-muted">{stats?.grafica?.length} días</small>
            </div>
            <div className="card-body">
              {Chart ? (
                <div style={{ height: '300px' }}>
                  <canvas ref={chartRef}></canvas>
                </div>
              ) : (
                <div className="alert alert-warning">
                  <strong>Chart.js no instalado.</strong> Ejecuta: <code>npm install chart.js</code>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-header bg-white fw-bold">📋 Pedidos por Estado</div>
            <div className="card-body">
              {pedidosPorEstado.map((estado, i) => (
                <div key={i} className="mb-3">
                  <div className="d-flex justify-content-between align-items-center mb-1">
                    <span className="d-flex align-items-center">
                      <span 
                        className="rounded-circle me-2" 
                        style={{ 
                          width: '12px', 
                          height: '12px', 
                          backgroundColor: estado.color,
                          display: 'inline-block'
                        }}
                      ></span>
                      {estado.estado}
                    </span>
                    <span className="fw-bold">{estado.cantidad}</span>
                  </div>
                  <div className="progress" style={{ height: '8px' }}>
                    <div 
                      className="progress-bar" 
                      role="progressbar"
                      style={{ 
                        width: `${estado.porcentaje}%`, 
                        backgroundColor: estado.color 
                      }}
                      aria-valuenow={estado.porcentaje} 
                      aria-valuemin="0" 
                      aria-valuemax="100"
                    ></div>
                  </div>
                  <small className="text-muted">{estado.porcentaje}% del total</small>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* TABLA DE ÚLTIMAS VENTAS CON FECHAS LEGIBLES */}
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
                  <th className="text-end">Tendencia</th>
                </tr>
              </thead>
              <tbody>
                {stats?.grafica?.map((dia, i, arr) => {
                  const ventaAnterior = i < arr.length - 1 ? arr[i + 1].venta : dia.venta;
                  const diferencia = dia.venta - ventaAnterior;
                  const esPositivo = diferencia >= 0;

                  return (
                    <tr key={i}>
                      <td className="fw-semibold">{formatearFecha(dia.fecha)}</td>
                      <td>
                        <span className="badge bg-light text-dark">
                          {formatearFechaCorta(dia.fecha)}
                        </span>
                      </td>
                      <td className="text-end fw-bold text-success">{formatearDinero(dia.venta)}</td>
                      <td className="text-end">
                        {i < arr.length - 1 && (
                          <span className={`badge ${esPositivo ? 'bg-success' : 'bg-danger'}`}>
                            {esPositivo ? '↗' : '↘'} {formatearDinero(Math.abs(diferencia))}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;