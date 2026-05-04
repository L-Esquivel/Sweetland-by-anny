import React, { useState, useEffect } from 'react';
import { productosService } from '../../services/productosService';
import ProductoForm from './ProductoForm';
import './ProductosList.css';

const ProductosList = () => {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProducto, setEditingProducto] = useState(null);

  useEffect(() => { loadProductos(); }, []);

  const loadProductos = async () => {
    try {
      const data = await productosService.getProductos();
      setProductos(data);
    } catch (error) {
      console.error('Error cargando productos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingProducto(null);
    setShowModal(true);
  };

  const handleEdit = (producto) => {
    setEditingProducto(producto);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar este producto?')) {
      try {
        await productosService.deleteProducto(id);
        await loadProductos();
      } catch (error) { console.error(error); }
    }
  };

  const handleSubmit = async (productoData) => {
    try {
      if (editingProducto) {
        await productosService.updateProducto(editingProducto.id_producto, productoData);
      } else {
        await productosService.createProducto(productoData);
      }
      setShowModal(false);
      await loadProductos();
    } catch (error) { console.error(error); }
  };

  const formatPrecio = (p) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(p);

  const renderStockBadge = (producto) => {
    if (!producto.controla_stock) {
      return <span className="badge bg-light text-muted border">N/A</span>;
    }
    
    let color = "bg-info";
    if (producto.stock <= 0) color = "bg-danger";
    else if (producto.stock < 5) color = "bg-warning text-dark";

    return (
      <span className={`badge ${color} px-3`}>
        {producto.stock} unidades
      </span>
    );
  };

  if (loading) return <div className="text-center p-5"><h4>Cargando catálogo...</h4></div>;

  return (
    <div className="productos-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">🎂 Gestión de Productos e Inventario</h2>
        <button className="btn btn-primary shadow-sm" onClick={handleCreate}>
          ➕ Nuevo Producto
        </button>
      </div>

      <div className="table-responsive shadow-sm rounded">
        <table className="table table-hover table-bordered mb-0 bg-white">
          <thead className="table-dark text-center">
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Precio</th>
              <th>Stock Actual</th> {/* NUEVA COLUMNA */}
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody className="align-middle">
            {productos.length === 0 ? (
              <tr><td colSpan="7" className="text-center py-4">No hay productos</td></tr>
            ) : (
              productos.map(producto => (
                <tr key={producto.id_producto}>
                  <td className="text-center fw-bold text-muted">{producto.id_producto}</td>
                  <td className="fw-semibold">{producto.nombre}</td>
                  <td className="text-center">
                    <span className="badge bg-secondary text-uppercase" style={{fontSize: '0.7rem'}}>
                        {producto.categoria}
                    </span>
                  </td>
                  <td className="fw-bold text-success text-end">{formatPrecio(producto.precio)}</td>
                  <td className="text-center">
                    {renderStockBadge(producto)}
                  </td>
                  <td className="text-center">
                    {producto.controla_stock ? 
                        <span className="text-primary small">📦 Inventario Activo</span> : 
                        <span className="text-muted small">✨ Personalizado</span>
                    }
                  </td>
                  <td className="text-center">
                    <div className="btn-group">
                      <button className="btn btn-outline-warning btn-sm" onClick={() => handleEdit(producto)}>✏️</button>
                      <button className="btn btn-outline-danger btn-sm" onClick={() => handleDelete(producto.id_producto)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <ProductoForm
          producto={editingProducto}
          onSubmit={handleSubmit}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default ProductosList;