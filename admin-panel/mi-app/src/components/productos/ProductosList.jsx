import React, { useState, useEffect } from 'react';
import { productosService } from '../../services/productosService';
import ProductoForm from './ProductoForm';
import './ProductosList.css';

const ProductosList = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  useEffect(() => { loadProducts(); }, []);

  const loadProducts = async () => {
    try {
      const data = await productosService.getProducts();
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingProduct(null);
    setShowModal(true);
  };

  const handleEdit = (producto) => {
    setEditingProduct(producto);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productosService.deleteProduct(id);
        await loadProducts();
      } catch (error) { console.error(error); }
    }
  };

  const handleSubmit = async (productoData) => {
    try {
      if (editingProduct) {
        await productosService.updateProduct(editingProduct.id_producto, productoData);
      } else {
        await productosService.createProduct(productoData);
      }
      setShowModal(false);
      await loadProducts();
    } catch (error) { console.error(error); }
  };

  const formatPrice = (p) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(p || 0);

  const renderStockBadge = (producto) => {
    if (!producto.controla_stock) {
      return <span className="badge bg-light text-muted border">N/A</span>;
    }
    
    let color = "bg-primary";
    if (producto.stock <= 0) color = "bg-danger";
    else if (producto.stock < 5) color = "bg-warning text-dark";

    return (
      <span className={`badge ${color} px-3`}>
        {producto.stock} units
      </span>
    );
  };

  if (loading) return <div className="text-center p-5"><h4>Loading catalog...</h4></div>;

  return (
    <div className="productos-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">🎂 Product & Inventory Management</h2>
        <button className="btn btn-primary shadow-sm" onClick={handleCreate}>
          ➕ New Product
        </button>
      </div>

      <div className="table-responsive shadow-sm rounded">
        <table className="table table-hover table-bordered mb-0 bg-white">
          <thead className="table-dark text-center">
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Category</th>
              <th>Price</th>
              <th>Current Stock</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody className="align-middle">
            {products.length === 0 ? (
              <tr><td colSpan="7" className="text-center py-4">No products yet</td></tr>
            ) : (
              products.map(producto => (
                <tr key={producto.id_producto}>
                  <td className="text-center fw-bold text-muted">{producto.id_producto}</td>
                  <td className="fw-semibold">{producto.nombre}</td>
                  <td className="text-center">
                    <span className="badge bg-secondary text-uppercase" style={{fontSize: '0.7rem'}}>
                        {producto.categoria}
                    </span>
                  </td>
                  <td className="fw-bold text-success text-end">{formatPrice(producto.precio)}</td>
                  <td className="text-center">
                    {renderStockBadge(producto)}
                  </td>
                  <td className="text-center">
                    {producto.controla_stock ? 
                        <span className="text-primary small">📦 Inventory Active</span> : 
                        <span className="text-muted small">✨ On-Demand</span>
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
          producto={editingProduct}
          onSubmit={handleSubmit}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default ProductosList;