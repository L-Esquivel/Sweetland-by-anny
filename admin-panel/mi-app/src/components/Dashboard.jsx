import React, { useState, useEffect } from 'react';
import { pedidosService } from '../services/pedidosService';

const Dashboard = ({ user }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cargarStats = async () => {
      try {
        const data = await pedidosService.getStats();
        setStats(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    cargarStats();
  }, []);

  const formatearDinero = (valor) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
  };

  if (loading) return <div className="text-center p-5"><h5>Analizando finanzas...</h5></div>;

  return (
    <div className="dashboard-container">
      <h2 className="mb-4">📊 Resumen de Negocio</h2>
      
      {/* TARJETAS DE KPIs */}
      <div className="row g-4 mb-5">
        <div className="col-md-4">
          <div className="card border-0 shadow-sm bg-primary text-white h-100">
            <div className="card-body">
              <h6 className="text-uppercase opacity-75">Ventas de Hoy</h6>
              <h2 className="fw-bold">{formatearDinero(stats?.resumen?.hoy)}</h2>
              <small>Pedidos procesados hoy</small>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card border-0 shadow-sm bg-success text-white h-100">
            <div className="card-body">
              <h6 className="text-uppercase opacity-75">Ventas del Mes</h6>
              <h2 className="fw-bold">{formatearDinero(stats?.resumen?.mes)}</h2>
              <small>Total acumulado este mes</small>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card border-0 shadow-sm bg-dark text-white h-100">
            <div className="card-body">
              <h6 className="text-uppercase opacity-75">Total Histórico</h6>
              <h2 className="fw-bold">{formatearDinero(stats?.resumen?.total_historico)}</h2>
              <small>{stats?.resumen?.num_pedidos} pedidos en total</small>
            </div>
          </div>
        </div>
      </div>

      {/* LISTA DE ÚLTIMAS VENTAS (Opcional por ahora) */}
      <div className="card shadow-sm border-0">
        <div className="card-header bg-white fw-bold">📈 Tendencia de Ventas (Últimos días)</div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th className="text-end">Venta Total</th>
                </tr>
              </thead>
              <tbody>
                {stats?.grafica?.map((dia, i) => (
                  <tr key={i}>
                    <td>{dia.fecha}</td>
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