import React, { useState, useEffect } from 'react';

const ProductoForm = ({ producto, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    categoria: 'tortas',
    descripcion: '',
    precio: '',
    imagen: ''
  });

  useEffect(() => {
    if (producto) {
      setFormData({
        nombre: producto.nombre || '',
        categoria: producto.categoria || 'tortas',
        descripcion: producto.descripcion || '',
        precio: producto.precio || '',
        imagen: producto.imagen || ''
      });
    }
  }, [producto]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const datosEnviar = {
      ...formData,
      precio: parseFloat(formData.precio)
    };
    
    onSubmit(datosEnviar);
  };

  const categorias = [
    { value: 'tortas', label: 'Tortas' },
    { value: 'postres', label: 'Postres' },
    { value: 'detalles', label: 'Detalles' }
  ];

  return (
    <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header bg-primary text-white">
            <h5 className="modal-title">
              {producto ? '✏️ Editar Producto' : '➕ Nuevo Producto'}
            </h5>
            <button 
              type="button" 
              className="btn-close btn-close-white" 
              onClick={onClose}
            ></button>
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
                        <option key={cat.value} value={cat.value}>
                          {cat.label}
                        </option>
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

              <div className="row">
                <div className="col-md-6">
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
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Imagen</label>
                    <input
                      type="text"
                      name="imagen"
                      className="form-control"
                      value={formData.imagen}
                      onChange={handleChange}
                      placeholder="nombre_imagen.jpg"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={onClose}
              >
                Cancelar
              </button>
              <button 
                type="submit" 
                className="btn btn-primary"
              >
                {producto ? '📝 Actualizar' : '✅ Crear'} Producto
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductoForm;