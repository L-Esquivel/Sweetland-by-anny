import React, { useState, useEffect } from 'react';

const UsuarioForm = ({ usuario, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    password: '',
    telefono: '',
    direccion: '',
    rol: 'cliente'
  });

  useEffect(() => {
    if (usuario) {
      setFormData({
        nombre: usuario.nombre || '',
        email: usuario.email || '',
        password: '',
        telefono: usuario.telefono || '',
        direccion: usuario.direccion || '',
        rol: usuario.rol || 'cliente'
      });
    }
  }, [usuario]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header bg-primary text-white">
            <h5 className="modal-title">
              {usuario ? '✏️ Editar Usuario' : '➕ Nuevo Usuario'}
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
                    <label className="form-label">Email *</label>
                    <input
                      type="email"
                      name="email"
                      className="form-control"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label">
                  Password {!usuario && '*'}
                </label>
                <input
                  type="password"
                  name="password"
                  className="form-control"
                  value={formData.password}
                  onChange={handleChange}
                  required={!usuario}
                  placeholder={usuario ? "Dejar vacío para mantener la actual" : ""}
                />
                {usuario && (
                  <div className="form-text">
                    Dejar vacío para mantener la contraseña actual
                  </div>
                )}
              </div>

              <div className="row">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Teléfono</label>
                    <input
                      type="tel"
                      name="telefono"
                      className="form-control"
                      value={formData.telefono}
                      onChange={handleChange}
                    />
                  </div>
                </div>
                
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Rol</label>
                    <select
                      name="rol"
                      className="form-select"
                      value={formData.rol}
                      onChange={handleChange}
                    >
                      <option value="cliente">Cliente</option>
                      <option value="empleado">Empleado</option>
                      <option value="admin">Administrador</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label">Dirección</label>
                <input
                  type="text"
                  name="direccion"
                  className="form-control"
                  value={formData.direccion}
                  onChange={handleChange}
                />
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
                {usuario ? '📝 Actualizar' : '✅ Crear'} Usuario
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UsuarioForm;