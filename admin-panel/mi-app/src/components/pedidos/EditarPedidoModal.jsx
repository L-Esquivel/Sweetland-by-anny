import React, { useState, useEffect } from 'react';
import { pedidosService } from '../../services/pedidosService';

const EditarPedidoModal = ({ pedido, productos, onSubmit, onClose }) => {
  const [detalles, setDetalles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [productoSeleccionado, setProductoSeleccionado] = useState('');
  const [cantidad, setCantidad] = useState(1);
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    cargarDetallesPedido();
  }, [pedido.id]);

  const cargarDetallesPedido = async () => {
    try {
      const data = await pedidosService.getDetallesPedido(pedido.id);
      setDetalles(data);
    } catch (error) {
      console.error('Error cargando detalles:', error);
      setError('Error al cargar los detalles del pedido');
    } finally {
      setLoading(false);
    }
  };

  const agregarProducto = () => {
    if (!productoSeleccionado || cantidad < 1) {
      setError('Selecciona un producto y cantidad válida');
      return;
    }

    const producto = productos.find(p => p.id_producto === parseInt(productoSeleccionado));
    if (!producto) {
      setError('Producto no encontrado');
      return;
    }

    const subtotal = producto.precio * cantidad;
    const nuevoDetalle = {
      producto_id: producto.id_producto,
      producto_nombre: producto.nombre,
      cantidad: cantidad,
      precio_unitario: producto.precio,
      subtotal: subtotal,
      esNuevo: true
    };

    setDetalles(prev => [...prev, nuevoDetalle]);
    setProductoSeleccionado('');
    setCantidad(1);
    setError('');
  };

  const eliminarProducto = async (detalle, index) => {
    try {
      // Si el detalle ya existe en la BD (tiene ID), eliminarlo del backend
      if (detalle.id && !detalle.esNuevo) {
        await pedidosService.deleteDetallePedido(detalle.id);
        console.log('✅ Producto eliminado de la BD:', detalle.id);
      }
      
      // Eliminar de la lista local
      setDetalles(prev => prev.filter((_, i) => i !== index));
      console.log('✅ Producto eliminado de la lista');
      
    } catch (error) {
      console.error('❌ Error eliminando producto:', error);
      setError('Error al eliminar el producto del pedido');
    }
  };

  const calcularTotal = () => {
    return detalles.reduce((total, detalle) => total + detalle.subtotal, 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGuardando(true);
    setError('');
    
    try {
      // 1. Actualizar el pedido principal
      const pedidoData = {
        cliente_nombre: pedido.cliente_nombre,
        cliente_telefono: pedido.cliente_telefono,
        telefono: pedido.cliente_telefono,
        direccion: pedido.direccion,
        total: calcularTotal(),
        estado: pedido.estado
      };

      console.log('📤 Actualizando pedido con datos:', pedidoData);
      await pedidosService.updatePedido(pedido.id, pedidoData);
      console.log('✅ Pedido actualizado exitosamente');

      // 2. Crear nuevos detalles usando el endpoint alternativo
      const nuevosDetalles = detalles.filter(detalle => detalle.esNuevo);
      console.log(`📝 Creando ${nuevosDetalles.length} nuevos detalles con endpoint alternativo`);

      for (const detalle of nuevosDetalles) {
        try {
          await pedidosService.createDetallePedidoAlternativo(pedido.id, {
            producto_id: detalle.producto_id,
            cantidad: detalle.cantidad,
            precio_unitario: detalle.precio_unitario,
            subtotal: detalle.subtotal
          });
          console.log(`✅ Detalle creado para producto ${detalle.producto_nombre}`);
        } catch (detalleError) {
          console.error(`❌ Error creando detalle:`, detalleError);
          throw new Error(`Error al agregar producto ${detalle.producto_nombre}: ${detalleError.message}`);
        }
      }

      console.log('✅ Proceso completado con endpoint alternativo');
      
      // ✅ Emitir evento para actualizar la lista
      window.dispatchEvent(new CustomEvent('pedidoActualizado', {
        detail: { pedidoId: pedido.id }
      }));
      
      onClose();
      
    } catch (error) {
      console.error('❌ Error general:', error);
      setError('Error al actualizar el pedido: ' + error.message);
    } finally {
      setGuardando(false);
    }
  };

  if (loading) {
    return (
      <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-body text-center">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Cargando...</span>
              </div>
              <p className="mt-2">Cargando detalles del pedido...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
      <div className="modal-dialog modal-xl" style={{maxWidth: '95%', height: '95vh'}}>
        <div className="modal-content h-100">
          <div className="modal-header bg-warning text-dark">
            <h5 className="modal-title">✏️ Editar Pedido #{pedido.id}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body" style={{overflowY: 'auto', maxHeight: 'calc(95vh - 120px)'}}>
              {error && <div className="alert alert-danger">{error}</div>}

              <div className="row mb-3">
                <div className="col-md-6">
                  <label className="form-label">Cliente</label>
                  <input
                    type="text"
                    className="form-control"
                    value={pedido.cliente_nombre}
                    disabled
                  />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Teléfono</label>
                  <input
                    type="text"
                    className="form-control"
                    value={pedido.cliente_telefono}
                    disabled
                  />
                </div>
              </div>

              <div className="row mb-3">
                <div className="col-md-8">
                  <label className="form-label">Dirección</label>
                  <input
                    type="text"
                    className="form-control"
                    value={pedido.direccion}
                    disabled
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Estado Actual</label>
                  <input
                    type="text"
                    className="form-control"
                    value={pedido.estado}
                    disabled
                  />
                </div>
              </div>

              <div className="card mb-3">
                <div className="card-header bg-light">
                  <h6 className="mb-0">🛒 Productos del Pedido</h6>
                </div>
                <div className="card-body">
                  <div className="row g-2 mb-3">
                    <div className="col-md-6">
                      <select
                        className="form-select"
                        value={productoSeleccionado}
                        onChange={(e) => setProductoSeleccionado(e.target.value)}
                      >
                        <option value="">Seleccionar producto...</option>
                        {productos.map(producto => (
                          <option key={producto.id_producto} value={producto.id_producto}>
                            {producto.nombre} - ${producto.precio.toLocaleString()}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="col-md-3">
                      <input
                        type="number"
                        className="form-control"
                        min="1"
                        value={cantidad}
                        onChange={(e) => setCantidad(parseInt(e.target.value) || 1)}
                      />
                    </div>
                    <div className="col-md-3">
                      <button
                        type="button"
                        className="btn btn-primary w-100"
                        onClick={agregarProducto}
                      >
                        ➕ Agregar
                      </button>
                    </div>
                  </div>

                  {detalles.length > 0 ? (
                    <div className="table-responsive">
                      <table className="table table-sm">
                        <thead className="table-dark">
                          <tr>
                            <th>Producto</th>
                            <th>Cantidad</th>
                            <th>Precio Unitario</th>
                            <th>Subtotal</th>
                            <th>Acciones</th>
                          </tr>
                        </thead>
                        <tbody>
                          {detalles.map((detalle, index) => (
                            <tr key={index}>
                              <td>
                                {detalle.producto_nombre}
                                {detalle.esNuevo && <span className="badge bg-success ms-1">Nuevo</span>}
                              </td>
                              <td>{detalle.cantidad}</td>
                              <td>${detalle.precio_unitario.toLocaleString()}</td>
                              <td>${detalle.subtotal.toLocaleString()}</td>
                              <td>
                                <button
                                  type="button"
                                  className="btn btn-danger btn-sm"
                                  onClick={() => eliminarProducto(detalle, index)}
                                  title="Eliminar producto"
                                >
                                  🗑️
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                        <tfoot>
                          <tr>
                            <td colSpan="3" className="text-end fw-bold">Total:</td>
                            <td className="fw-bold text-success">${calcularTotal().toLocaleString()}</td>
                            <td></td>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center text-muted">
                      No hay productos en este pedido
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancelar
              </button>
              <button type="submit" className="btn btn-warning" disabled={guardando}>
                {guardando ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Guardando...
                  </>
                ) : (
                  '💾 Guardar Cambios'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditarPedidoModal;