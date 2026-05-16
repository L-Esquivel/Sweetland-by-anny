import React, { useState, useEffect } from 'react';
import { pedidosService } from '../../services/pedidosService';

const EditarPedidoModal = ({ pedido, productos, onSubmit, onClose }) => {
  const [details, setDetails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetchOrderDetails();
  }, [pedido.id]);

  const fetchOrderDetails = async () => {
    try {
      const data = await pedidosService.getDetallesPedido(pedido.id);
      setDetails(data);
    } catch (error) {
      console.error('Error loading details:', error);
      setError('Error loading order details');
    } finally {
      setLoading(false);
    }
  };

  const addProduct = () => {
    if (!selectedProduct || quantity < 1) {
      setError('Select a valid product and quantity');
      return;
    }

    const product = productos.find(p => p.id_producto === parseInt(selectedProduct));
    if (!product) {
      setError('Product not found');
      return;
    }

    const subtotal = product.precio * quantity;
    const newDetail = {
      producto_id: product.id_producto,
      producto_nombre: product.nombre,
      cantidad: quantity,
      precio_unitario: product.precio,
      subtotal: subtotal,
      isNew: true
    };

    setDetails(prev => [...prev, newDetail]);
    setSelectedProduct('');
    setQuantity(1);
    setError('');
  };

  const removeProduct = async (detail, index) => {
    try {
      // If the detail already exists in the DB (has an ID), delete it from the backend
      if (detail.id && !detail.isNew) {
        await pedidosService.deleteDetallePedido(detail.id);
        console.log('✅ Product removed from DB:', detail.id);
      }
      
      // Remove from local list
      setDetails(prev => prev.filter((_, i) => i !== index));
      console.log('✅ Product removed from list');
      
    } catch (error) {
      console.error('❌ Error removing product:', error);
      setError('Error removing product from order');
    }
  };

  const calculateTotal = () => {
    return details.reduce((total, detail) => total + detail.subtotal, 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setError('');
    
    try {
      // 1. Update the main order
      const orderData = {
        cliente_nombre: pedido.cliente_nombre,
        cliente_telefono: pedido.cliente_telefono,
        telefono: pedido.cliente_telefono,
        direccion: pedido.direccion,
        total: calcularTotal(),
        estado: pedido.estado
      };

      console.log('📤 Updating order with data:', orderData);
      await pedidosService.updatePedido(pedido.id, orderData);
      console.log('✅ Order updated successfully');

      // 2. Create new details using the alternative endpoint
      const newDetails = details.filter(detail => detail.isNew);
      console.log(`📝 Creating ${newDetails.length} new details with alternative endpoint`);

      for (const detail of newDetails) {
        try {
          await pedidosService.createDetallePedido(pedido.id, {
            producto_id: detail.producto_id,
            cantidad: detail.cantidad,
            precio_unitario: detail.precio_unitario,
            subtotal: detail.subtotal
          });
          console.log(`✅ Detail created for product ${detail.producto_nombre}`);
        } catch (detalleError) {
          console.error(`❌ Error creating detail:`, detalleError);
          throw new Error(`Error adding product ${detail.producto_nombre}: ${detalleError.message}`);
        }
      }

      console.log('✅ Process completed with alternative endpoint');
      
      // ✅ Dispatch event to update the list
      window.dispatchEvent(new CustomEvent('orderUpdated', {
        detail: { pedidoId: pedido.id }
      }));
      
      onClose();
      
    } catch (error) {
      console.error('❌ General error:', error);
      setError('Error updating order: ' + error.message);
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-body text-center">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-2">Loading order details...</p>
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
            <h5 className="modal-title">✏️ Edit Order #{pedido.id}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body" style={{overflowY: 'auto', maxHeight: 'calc(95vh - 120px)'}}>
              {error && <div className="alert alert-danger">{error}</div>}

              <div className="row mb-3">
                <div className="col-md-6">
                  <label className="form-label">Customer</label>
                  <input
                    type="text"
                    className="form-control"
                    value={pedido.cliente_nombre}
                    disabled
                  />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Phone</label>
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
                  <label className="form-label">Address</label>
                  <input
                    type="text"
                    className="form-control"
                    value={pedido.direccion}
                    disabled
                  />
                </div>
                <div className="col-md-4">
                  <label className="form-label">Current Status</label>
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
                  <h6 className="mb-0">🛒 Order Products</h6>
                </div>
                <div className="card-body">
                  <div className="row g-2 mb-3">
                    <div className="col-md-6">
                      <select
                        className="form-select"
                        value={selectedProduct}
                        onChange={(e) => setSelectedProduct(e.target.value)}
                      >
                        <option value="">Select a product...</option>
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
                        value={quantity}
                        onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                      />
                    </div>
                    <div className="col-md-3">
                      <button
                        type="button"
                        className="btn btn-primary w-100"
                        onClick={addProduct}
                      >
                        ➕ Add
                      </button>
                    </div>
                  </div>

                  {details.length > 0 ? (
                    <div className="table-responsive">
                      <table className="table table-sm">
                        <thead className="table-dark">
                          <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Unit Price</th>
                            <th>Subtotal</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {details.map((detail, index) => (
                            <tr key={index}>
                              <td>
                                {detail.producto_nombre}
                                {detail.isNew && <span className="badge bg-success ms-1">New</span>}
                              </td>
                              <td>{detail.cantidad}</td>
                              <td>${detail.precio_unitario.toLocaleString()}</td>
                              <td>${detail.subtotal.toLocaleString()}</td>
                              <td>
                                <button
                                  type="button"
                                  className="btn btn-danger btn-sm"
                                  onClick={() => removeProduct(detail, index)}
                                  title="Remove product"
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
                            <td className="fw-bold text-success">${calculateTotal().toLocaleString()}</td>
                            <td></td>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center text-muted">
                      There are no products in this order
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-warning" disabled={isSaving}>
                {isSaving ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Saving...
                  </>
                ) : (
                  '💾 Save Changes'
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