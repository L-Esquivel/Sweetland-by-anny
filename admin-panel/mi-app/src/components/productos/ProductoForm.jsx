import React, { useState, useEffect, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';

const ProductoForm = ({ producto, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    categoria: 'tortas',
    descripcion: '',
    precio: '',
    imagen: '',
    stock: 0,
    controla_stock: false // NUEVO CAMPO
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  useEffect(() => {
    if (producto) {
      setFormData({
        nombre: producto.nombre || '',
        categoria: producto.categoria || 'tortas',
        descripcion: producto.descripcion || '',
        precio: producto.precio || '',
        imagen: producto.imagen || '',
        stock: producto.stock || 0,
        controla_stock: producto.controla_stock === 1 || producto.controla_stock === true
      });
      if (producto.imagen) {
        setImagePreview(`${API_BASE}/static/images/${producto.imagen}`);
      }
    }
  }, [producto]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({ 
        ...formData, 
        [name]: type === 'checkbox' ? checked : value 
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    let imagenFinal = formData.imagen;

    if (imageFile) {
      try {
        const fd = new FormData();
        fd.append('imagen', imageFile);
        const res = await fetch(`${API_BASE}/productos/upload-image`, {
          method: 'POST',
          credentials: 'include',
          body: fd
        });
        const data = await res.json();
        if (res.ok) imagenFinal = data.filename;
      } catch (err) { console.error(err); }
    }

    const datosEnviar = {
      ...formData,
      precio: parseFloat(formData.precio) || 0,
      stock: parseInt(formData.stock) || 0,
      imagen: imagenFinal
    };

    onSubmit(datosEnviar);
  };

  return (
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 1050 }}>
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content shadow-lg border-0" style={{borderRadius: '15px'}}>
          <div className="modal-header bg-primary text-white">
            <h5 className="modal-title fw-bold">
              {producto ? '✏️ Editar Producto' : '➕ Nuevo Producto'}
            </h5>
            <button type="button" className="btn-close btn-close-white" onClick={onClose}></button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body p-4">
              <div className="row g-3">
                <div className="col-md-8">
                  <label className="form-label fw-bold">Nombre del Producto *</label>
                  <input type="text" name="nombre" className="form-control" value={formData.nombre} onChange={handleChange} required />
                </div>
                <div className="col-md-4">
                  <label className="form-label fw-bold">Categoría *</label>
                  <select name="categoria" className="form-select" value={formData.categoria} onChange={handleChange}>
                    <option value="tortas">Tortas</option>
                    <option value="postres">Postres</option>
                    <option value="detalles">Detalles</option>
                  </select>
                </div>

                <div className="col-12">
                  <label className="form-label fw-bold">Descripción</label>
                  <textarea name="descripcion" className="form-control" rows="2" value={formData.descripcion} onChange={handleChange} />
                </div>

                <div className="col-md-6">
                  <label className="form-label fw-bold">Precio de Venta (COP) *</label>
                  <input type="number" name="precio" className="form-control" value={formData.precio} onChange={handleChange} required />
                </div>

                {/* --- SECCIÓN DE INVENTARIO --- */}
                <div className="col-md-6">
                  <div className="card bg-light border-0 p-2">
                    <div className="form-check form-switch mt-1">
                      <input className="form-check-input" type="checkbox" name="controla_stock" id="checkStock" checked={formData.controla_stock} onChange={handleChange} />
                      <label className="form-check-label fw-bold" htmlFor="checkStock">📦 Controlar Inventario</label>
                    </div>
                    {formData.controla_stock && (
                      <div className="mt-2">
                        <label className="form-label small mb-1">Unidades Disponibles:</label>
                        <input type="number" name="stock" className="form-control form-control-sm" value={formData.stock} onChange={handleChange} min="0" />
                      </div>
                    )}
                  </div>
                </div>

                <div className="col-12 text-center">
                  <label className="form-label fw-bold d-block">Imagen</label>
                  {imagePreview && <img src={imagePreview} alt="Preview" className="img-thumbnail mb-2" style={{maxHeight: '150px'}} />}
                  <input type="file" className="form-control" onChange={handleFileChange} accept="image/*" />
                </div>
              </div>
            </div>

            <div className="modal-footer bg-light border-0">
              <button type="button" className="btn btn-secondary px-4" onClick={onClose}>Cancelar</button>
              <button type="submit" className="btn btn-primary px-4 shadow-sm" disabled={uploading}>
                {uploading ? 'Guardando...' : (producto ? 'Guardar Cambios' : 'Crear Producto')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductoForm;