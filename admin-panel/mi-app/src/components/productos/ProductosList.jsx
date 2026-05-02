import React, { useState, useEffect } from 'react';
import { productosService } from '../../services/productosService';
import ProductoForm from './ProductoForm';
import './ProductosList.css';

const ProductosList = () => {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProducto, setEditingProducto] = useState(null);

  useEffect(() => {
    loadProductos();
  }, []);

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
      } catch (error) {
        console.error('Error eliminando producto:', error);
      }
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
    } catch (error) {
      console.error('Error guardando producto:', error);
    }
  };

  const formatPrecio = (precio) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP'
    }).format(precio);
  };

  const getCategoriaBadgeClass = (categoria) => {
    switch (categoria) {
      case 'tortas':
        return 'bg-primary';
      case 'postres':
        return 'bg-success';
      case 'detalles':
        return 'bg-warning text-dark';
      default:
        return 'bg-secondary';
    }
  };

  if (loading) return <div className="text-center p-4">Cargando productos...</div>;

  return (
    <div className="productos-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">🎂 Gestión de Productos</h2>
        <button className="btn btn-primary" onClick={handleCreate}>
          ➕ Nuevo Producto
        </button>
      </div>

      <div className="table-responsive">
        <table className="table table-striped table-hover table-bordered">
          <thead className="table-dark">
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Categoría</th>
              <th>Descripción</th>
              <th>Precio</th>
              <th>Imagen</th>
              <th className="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {productos.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center text-muted py-4">
                  No hay productos registrados
                </td>
              </tr>
            ) : (
              productos.map(producto => (
                <tr key={producto.id_producto}>
                  <td className="fw-bold">{producto.id_producto}</td>
                  <td className="fw-semibold">{producto.nombre}</td>
                  <td>
                    <span className={`badge ${getCategoriaBadgeClass(producto.categoria)}`}>
                      {producto.categoria}
                    </span>
                  </td>
                  <td>
                    {producto.descripcion ? (
                      <span title={producto.descripcion}>
                        {producto.descripcion.length > 50 
                          ? `${producto.descripcion.substring(0, 50)}...`
                          : producto.descripcion}
                      </span>
                    ) : (
                      <span className="text-muted">N/A</span>
                    )}
                  </td>
                  <td className="fw-bold text-success">{formatPrecio(producto.precio)}</td>
                  <td className="text-center">
                    {producto.imagen ? (
                      <span className="badge bg-info">📷 Imagen</span>
                    ) : (
                      <span className="text-muted">N/A</span>
                    )}
                  </td>
                  <td className="text-center">
                    <div className="btn-group" role="group">
                      <button 
                        className="btn btn-warning btn-sm me-1"
                        onClick={() => handleEdit(producto)}
                        title="Editar producto"
                      >
                        ✏️ Editar
                      </button>
                      <button 
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(producto.id_producto)}
                        title="Eliminar producto"
                      >
                        🗑️ Eliminar
                      </button>
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