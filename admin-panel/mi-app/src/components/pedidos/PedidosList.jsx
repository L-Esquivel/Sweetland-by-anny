import React, { useState, useEffect } from 'react';
import './PedidosList.css';
import { pedidosService } from '../../services/pedidosService';
import { productosService } from '../../services/productosService';
import PedidoForm from './PedidoForm';
import EditarPedidoModal from './EditarPedidoModal';

const PedidosList = () => {
  const [pedidos, setPedidos] = useState([]);
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pedidoSeleccionado, setPedidoSeleccionado] = useState(null);
  const [detallesPedido, setDetallesPedido] = useState([]);
  const [error, setError] = useState('');
  const [mostrarModalEstado, setMostrarModalEstado] = useState(false);
  const [pedidoParaCambiar, setPedidoParaCambiar] = useState(null);
  const [nuevoEstado, setNuevoEstado] = useState('');
  const [mostrarModalNuevoPedido, setMostrarModalNuevoPedido] = useState(false);
  const [mostrarModalEditarPedido, setMostrarModalEditarPedido] = useState(false);
  const [pedidoParaEditar, setPedidoParaEditar] = useState(null);

  useEffect(() => {
    cargarDatosIniciales();
  }, []);

  const cargarDatosIniciales = async () => {
    try {
      setLoading(true);
      setError('');
      const [pedidosData, productosData] = await Promise.all([
        pedidosService.getPedidos(),
        productosService.getProductos()
      ]);
      setPedidos(pedidosData);
      setProductos(productosData);
    } catch (error) {
      console.error('Error cargando datos:', error);
      setError('No se pudieron cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const cargarDetallesPedido = async (pedidoId) => {
    try {
      setError('');
      const data = await pedidosService.getDetallesPedido(pedidoId);
      setDetallesPedido(data);
      setPedidoSeleccionado(pedidoId);
    } catch (error) {
      console.error('Error cargando detalles:', error);
      setError('No se pudieron cargar los detalles del pedido');
    }
  };

  const abrirModalCambioEstado = (pedido) => {
    setPedidoParaCambiar(pedido);
    setNuevoEstado(pedido.estado);
    setMostrarModalEstado(true);
  };

  const cerrarModalEstado = () => {
    setMostrarModalEstado(false);
    setPedidoParaCambiar(null);
    setNuevoEstado('');
  };

  const abrirModalNuevoPedido = () => {
    setMostrarModalNuevoPedido(true);
  };

  const cerrarModalNuevoPedido = () => {
    setMostrarModalNuevoPedido(false);
  };

  const abrirModalEditarPedido = (pedido) => {
    setPedidoParaEditar(pedido);
    setMostrarModalEditarPedido(true);
  };

  const cerrarModalEditarPedido = () => {
    setMostrarModalEditarPedido(false);
    setPedidoParaEditar(null);
  };

  const actualizarEstadoPedido = async () => {
    if (!pedidoParaCambiar || !nuevoEstado) return;

    try {
      setError('');
      await pedidosService.updateEstadoPedido(pedidoParaCambiar.id, nuevoEstado);
      
      setPedidos(pedidos.map(pedido => 
        pedido.id === pedidoParaCambiar.id 
          ? { ...pedido, estado: nuevoEstado }
          : pedido
      ));
      
      cerrarModalEstado();
    } catch (error) {
      console.error('Error actualizando estado:', error);
      setError('No se pudo actualizar el estado del pedido');
    }
  };

  const handleCrearPedido = async (pedidoData) => {
  try {
    setError('');
    // ❌ ELIMINAR ESTA LÍNEA - el pedido ya se creó en el formulario
    // await pedidosService.createPedido(pedidoData);
    
    // ✅ Solo recargar la lista para mostrar el nuevo pedido
    await cargarDatosIniciales();
    cerrarModalNuevoPedido();
  } catch (error) {
    console.error('Error creando pedido:', error);
    setError('No se pudo crear el pedido');
    throw error;
  }
};

useEffect(() => {
  const handlePedidoCreado = () => {
    console.log('🔄 Recargando lista por pedido creado...');
    cargarDatosIniciales();
  };

  const handlePedidoActualizado = () => {
    console.log('🔄 Recargando lista por pedido actualizado...');
    cargarDatosIniciales();
  };

  window.addEventListener('pedidoCreado', handlePedidoCreado);
  window.addEventListener('pedidoActualizado', handlePedidoActualizado);

  return () => {
    window.removeEventListener('pedidoCreado', handlePedidoCreado);
    window.removeEventListener('pedidoActualizado', handlePedidoActualizado);
  };
}, []);

  const handleEditarPedido = async (pedidoId, pedidoData) => {
    try {
      setError('');
      await pedidosService.updatePedido(pedidoId, pedidoData);
      await cargarDatosIniciales();
      cerrarModalEditarPedido();
    } catch (error) {
      console.error('Error editando pedido:', error);
      setError('No se pudo editar el pedido');
      throw error;
    }
  };

  const cerrarDetalles = () => {
    setPedidoSeleccionado(null);
    setDetallesPedido([]);
  };

  const formatearFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP'
    }).format(valor);
  };

  const generarRecibo = async (pedido) => {
    try {
      const detalles = await pedidosService.getDetallesPedido(pedido.id);
      
      const ventanaRecibo = window.open('', '_blank');
      
      const contenidoRecibo = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Recibo - Pedido #${pedido.id}</title>
          <style>
            body { 
              font-family: 'Courier New', monospace; 
              margin: 0; 
              padding: 20px; 
              background: white;
            }
            .recibo {
              max-width: 400px;
              margin: 0 auto;
              border: 2px solid #333;
              padding: 20px;
              background: white;
            }
            .header { 
              text-align: center; 
              border-bottom: 2px dashed #333;
              padding-bottom: 15px;
              margin-bottom: 15px;
            }
            .header h1 { 
              margin: 0; 
              font-size: 24px; 
              color: #333;
            }
            .header .subtitle {
              font-size: 14px;
              color: #666;
            }
            .info-section {
              margin-bottom: 15px;
            }
            .info-section h3 {
              margin: 0 0 8px 0;
              font-size: 16px;
              color: #333;
              border-bottom: 1px solid #ddd;
              padding-bottom: 4px;
            }
            .info-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 4px;
              font-size: 14px;
            }
            .productos-table {
              width: 100%;
              border-collapse: collapse;
              margin: 10px 0;
              font-size: 12px;
            }
            .productos-table th {
              background: #f8f9fa;
              border-bottom: 2px solid #333;
              padding: 6px 4px;
              text-align: left;
            }
            .productos-table td {
              padding: 6px 4px;
              border-bottom: 1px solid #ddd;
            }
            .productos-table .total-row {
              font-weight: bold;
              border-top: 2px dashed #333;
            }
            .total-section {
              border-top: 2px dashed #333;
              padding-top: 10px;
              margin-top: 15px;
              font-weight: bold;
            }
            .footer {
              text-align: center;
              margin-top: 20px;
              font-size: 12px;
              color: #666;
              border-top: 1px solid #ddd;
              padding-top: 10px;
            }
            @media print {
              body { margin: 0; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          <div class="recibo">
            <div class="header">
              <h1>Sweetland By Anny</h1>
              <div class="subtitle">Delicias hechas con amor</div>
              <div class="subtitle">Pedido #${pedido.id}</div>
            </div>
            
            <div class="info-section">
              <h3>📋 Información del Pedido</h3>
              <div class="info-row">
                <span>Fecha:</span>
                <span>${new Date(pedido.fecha_pedido).toLocaleDateString('es-ES')}</span>
              </div>
              <div class="info-row">
                <span>Estado:</span>
                <span>${pedido.estado}</span>
              </div>
            </div>
            
            <div class="info-section">
              <h3>👤 Información del Cliente</h3>
              <div class="info-row">
                <span>Nombre:</span>
                <span>${pedido.cliente_nombre}</span>
              </div>
              <div class="info-row">
                <span>Teléfono:</span>
                <span>${pedido.cliente_telefono}</span>
              </div>
              <div class="info-row">
                <span>Dirección:</span>
                <span>${pedido.direccion}</span>
              </div>
            </div>
            
            <div class="info-section">
              <h3>🛒 Productos del Pedido</h3>
              <table class="productos-table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cant</th>
                    <th>Precio</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  ${detalles.map(detalle => `
                    <tr>
                      <td>${detalle.producto_nombre}</td>
                      <td>${detalle.cantidad}</td>
                      <td>${new Intl.NumberFormat('es-CO', {
                        style: 'currency',
                        currency: 'COP'
                      }).format(detalle.precio_unitario)}</td>
                      <td>${new Intl.NumberFormat('es-CO', {
                        style: 'currency',
                        currency: 'COP'
                      }).format(detalle.subtotal)}</td>
                    </tr>
                  `).join('')}
                  <tr class="total-row">
                    <td colspan="3" style="text-align: right;"><strong>TOTAL:</strong></td>
                    <td><strong>${new Intl.NumberFormat('es-CO', {
                      style: 'currency',
                      currency: 'COP'
                    }).format(detalles.reduce((sum, detalle) => sum + detalle.subtotal, 0))}</strong></td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="footer">
              <div>¡Gracias por su compra!</div>
              <div>Sweetland By Anny - ${new Date().getFullYear()}</div>
              <button class="no-print" onclick="window.print()" style="margin-top: 10px; padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                🖨️ Imprimir Recibo
              </button>
            </div>
          </div>
        </body>
        </html>
      `;
      
      ventanaRecibo.document.write(contenidoRecibo);
      ventanaRecibo.document.close();
    } catch (error) {
      console.error('Error generando recibo:', error);
      alert('Error al generar el recibo. Intente nuevamente.');
    }
  };

  const estados = [
    { value: 'pendiente', label: '⏳ Pendiente', color: '#f39c12' },
    { value: 'confirmado', label: '✅ Confirmado', color: '#3498db' },
    { value: 'en_preparacion', label: '👨‍🍳 En Preparación', color: '#9b59b6' },
    { value: 'completado', label: '🎉 Completado', color: '#27ae60' },
    { value: 'cancelado', label: '❌ Cancelado', color: '#e74c3c' }
  ];

  const getEstadoBadgeClass = (estado) => {
    switch (estado) {
      case 'pendiente':
        return 'bg-warning text-dark';
      case 'confirmado':
        return 'bg-info';
      case 'en_preparacion':
        return 'bg-primary';
      case 'completado':
        return 'bg-success';
      case 'cancelado':
        return 'bg-danger';
      default:
        return 'bg-secondary';
    }
  };

  if (loading) {
    return <div className="text-center p-4">Cargando pedidos...</div>;
  }

  return (
    <div className="pedidos-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">📦 Gestión de Pedidos</h2>
        <button 
          className="btn btn-success"
          onClick={abrirModalNuevoPedido}
        >
          ➕ Nuevo Pedido
        </button>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <div className="row">
        {/* Lista de Pedidos */}
        <div className={`${pedidoSeleccionado ? 'col-md-8' : 'col-12'}`}>
          <div className="card">
            <div className="card-header bg-light">
              <h5 className="mb-0">Lista de Pedidos</h5>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-striped table-hover mb-0">
                  <thead className="table-dark">
                    <tr>
                      <th>ID</th>
                      <th>Cliente</th>
                      <th>Fecha</th>
                      <th>Estado</th>
                      <th>Total</th>
                      <th className="text-center">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pedidos.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="text-center text-muted py-4">
                          No hay pedidos registrados
                        </td>
                      </tr>
                    ) : (
                      pedidos.map(pedido => (
                        <tr key={pedido.id} className={pedidoSeleccionado === pedido.id ? 'table-active' : ''}>
                          <td className="fw-bold">#{pedido.id}</td>
                          <td>
                            <div className="fw-semibold">{pedido.cliente_nombre}</div>
                            <small className="text-muted">{pedido.cliente_telefono}</small>
                          </td>
                          <td>
                            <small>{formatearFecha(pedido.fecha_pedido)}</small>
                          </td>
                          <td>
                            <button 
                              className={`btn btn-sm ${getEstadoBadgeClass(pedido.estado)}`}
                              onClick={() => abrirModalCambioEstado(pedido)}
                              title="Click para cambiar estado"
                            >
                              {estados.find(e => e.value === pedido.estado)?.label || pedido.estado}
                            </button>
                          </td>
                          <td className="fw-bold text-success">{formatearMoneda(pedido.total)}</td>
                          <td className="text-center">
                            <div className="btn-group" role="group">
                              <button 
                                className="btn btn-info btn-sm me-1"
                                onClick={() => cargarDetallesPedido(pedido.id)}
                                title="Ver detalles"
                              >
                                👁️ Detalles
                              </button>
                              <button 
                                className="btn btn-outline-primary btn-sm"
                                onClick={() => generarRecibo(pedido)}
                                title="Generar recibo"
                              >
                                🧾 Recibo
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Panel de Detalles */}
        {pedidoSeleccionado && (
          <div className="col-md-4">
            <div className="card">
              <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Detalles del Pedido #{pedidoSeleccionado}</h5>
                <button 
                  className="btn btn-sm btn-light" 
                  onClick={cerrarDetalles}
                >
                  ✕
                </button>
              </div>
              <div className="card-body">
                {detallesPedido.length > 0 ? (
                  <div>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <h6 className="mb-0">Productos del Pedido</h6>
                      <button 
                        className="btn btn-warning btn-sm"
                        onClick={() => {
                          const pedido = pedidos.find(p => p.id === pedidoSeleccionado);
                          if (pedido) abrirModalEditarPedido(pedido);
                        }}
                      >
                        ✏️ Editar Pedido
                      </button>
                    </div>
                    <div className="table-responsive">
                      <table className="table table-sm">
                        <thead>
                          <tr>
                            <th>Producto</th>
                            <th>Cant</th>
                            <th>Precio</th>
                            <th>Subtotal</th>
                          </tr>
                        </thead>
                        <tbody>
                          {detallesPedido.map(detalle => (
                            <tr key={detalle.id}>
                              <td>
                                <div className="fw-semibold">{detalle.producto_nombre}</div>
                                <small className="text-muted">{detalle.categoria}</small>
                              </td>
                              <td className="fw-bold">{detalle.cantidad}</td>
                              <td>{formatearMoneda(detalle.precio_unitario)}</td>
                              <td className="fw-bold text-success">{formatearMoneda(detalle.subtotal)}</td>
                            </tr>
                          ))}
                        </tbody>
                        <tfoot>
                          <tr>
                            <td colSpan="3" className="fw-bold">Total:</td>
                            <td className="fw-bold text-success">
                              {formatearMoneda(
                                detallesPedido.reduce((sum, detalle) => sum + detalle.subtotal, 0)
                              )}
                            </td>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted">
                    No se encontraron detalles para este pedido
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal para cambiar estado */}
      {mostrarModalEstado && pedidoParaCambiar && (
        <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header bg-warning text-dark">
                <h5 className="modal-title">🔄 Cambiar Estado del Pedido</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={cerrarModalEstado}
                ></button>
              </div>
              <div className="modal-body">
                <p>
                  Pedido <strong>#{pedidoParaCambiar.id}</strong> - {pedidoParaCambiar.cliente_nombre}
                </p>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Nuevo Estado:</label>
                  <select 
                    className="form-select"
                    value={nuevoEstado} 
                    onChange={(e) => setNuevoEstado(e.target.value)}
                  >
                    {estados.map(estado => (
                      <option key={estado.value} value={estado.value}>
                        {estado.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  className="btn btn-secondary"
                  onClick={cerrarModalEstado}
                >
                  Cancelar
                </button>
                <button 
                  className="btn btn-warning"
                  onClick={actualizarEstadoPedido}
                >
                  ✅ Actualizar Estado
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal para nuevo pedido */}
      {mostrarModalNuevoPedido && (
      <PedidoForm
      productos={productos}
      onSubmit={handleCrearPedido}
      onClose={() => {
      cerrarModalNuevoPedido();
      cargarDatosIniciales(); // ← SOLO AGREGAR ESTA LÍNEA
      }}
      titulo="➕ Crear Nuevo Pedido"
      />
      )}

      {mostrarModalEditarPedido && pedidoParaEditar && (
  <EditarPedidoModal
    pedido={pedidoParaEditar}
    productos={productos}
    onSubmit={handleEditarPedido}
    onClose={() => {
      cerrarModalEditarPedido();
      cargarDatosIniciales(); // ← Actualizar lista general
      
      // ✅ SI ESTÁS VIENDO LOS DETALLES DE ESE PEDIDO, RECARGARLOS TAMBIÉN
      if (pedidoSeleccionado === pedidoParaEditar.id) {
        console.log('🔄 Recargando detalles del pedido editado...');
        cargarDetallesPedido(pedidoParaEditar.id);
      }
    }}
  />
)}
    </div>
  );
};

export default PedidosList;