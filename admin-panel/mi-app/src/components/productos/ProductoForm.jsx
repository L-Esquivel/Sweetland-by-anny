import React, { useState, useEffect, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';

const ProductoForm = ({ producto, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    categoria: 'tortas',
    descripcion: '',
    precio: '',
    imagen: ''
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (producto) {
      setFormData({
        nombre: producto.nombre || '',
        categoria: producto.categoria || 'tortas',
        descripcion: producto.descripcion || '',
        precio: producto.precio || '',
        imagen: producto.imagen || ''
      });
      if (producto.imagen) {
        setImagePreview(`${API_BASE}/static/images/${producto.imagen}`);
      }
    }
  }, [producto]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setImageFile(file);
    setUploadError('');

    const reader = new FileReader();
    reader.onloadend = () => setImagePreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploadError('');

    let imagenFinal = formData.imagen;

    // Si hay un archivo nuevo, subirlo primero
    if (imageFile) {
      setUploading(true);
      try {
        const fd = new FormData();
        fd.append('imagen', imageFile);

        const res = await fetch(`${API_BASE}/productos/upload-image`, {
          method: 'POST',
          credentials: 'include',
          body: fd
        });

        const data = await res.json();

        if (!res.ok) {
          setUploadError(data.error || 'Error al subir la imagen');
          setUploading(false);
          return;
        }

        imagenFinal = data.filename;
      } catch (err) {
        setUploadError('Error de conexión al subir la imagen');
        setUploading(false);
        return;
      } finally {
        setUploading(false);
      }
    }

    const datosEnviar = {
      ...formData,
      precio: parseFloat(formData.precio),
      imagen: imagenFinal
    };

    onSubmit(datosEnviar);
  };

  const categorias = [
    { value: 'tortas', label: 'Tortas' },
    { value: 'postres', label: 'Postres' },
    { value: 'detalles', label: 'Detalles' }
  ];

  return (
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header bg-primary text-white">
            <h5 className="modal-title">
              {producto ? '✏️ Editar Producto' : '➕ Nuevo Producto'}
            </h5>
            <button type="button" className="btn-close btn-close-white" onClick={onClose}></button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              <div className="row">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Nombre *</label>
                    <input
                      type="text"
                      name="nombre"
                      className="form-control"
                      value={formData.nombre}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Categoría *</label>
                    <select
                      name="categoria"
                      className="form-select"
                      value={formData.categoria}
                      onChange={handleChange}
                      required
                    >
                      {categorias.map(cat => (
                        <option key={cat.value} value={cat.value}>{cat.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label">Descripción</label>
                <textarea
                  name="descripcion"
                  className="form-control"
                  value={formData.descripcion}
                  onChange={handleChange}
                  rows="3"
                  placeholder="Describe el producto..."
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Precio (COP) *</label>
                <input
                  type="number"
                  name="precio"
                  className="form-control"
                  value={formData.precio}
                  onChange={handleChange}
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              {/* ---- IMAGEN ---- */}
              <div className="mb-3">
                <label className="form-label">Imagen del producto</label>

                {/* Preview */}
                {imagePreview && (
                  <div className="mb-2 text-center">
                    <img
                      src={imagePreview}
                      alt="Preview"
                      style={{
                        maxHeight: '180px',
                        maxWidth: '100%',
                        borderRadius: '12px',
                        objectFit: 'cover',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                      }}
                    />
                  </div>
                )}

                {/* Input de archivo */}
                <input
                  type="file"
                  ref={fileInputRef}
                  className="form-control"
                  accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                  onChange={handleFileChange}
                />
                <div className="form-text">
                  Formatos aceptados: PNG, JPG, JPEG, GIF, WEBP.
                  {formData.imagen && !imageFile && (
                    <span className="ms-1 text-muted">Imagen actual: <strong>{formData.imagen}</strong></span>
                  )}
                </div>

                {uploadError && (
                  <div className="alert alert-danger mt-2 py-2">{uploadError}</div>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancelar
              </button>
              <button type="submit" className="btn btn-primary" disabled={uploading}>
                {uploading ? (
                  <><span className="spinner-border spinner-border-sm me-2"></span>Subiendo...</>
                ) : (
                  <>{producto ? '📝 Actualizar' : '✅ Crear'} Producto</>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductoForm;