import React, { useState, useEffect } from 'react';
import { empaquesService } from '../../services/empaquesService';
import '../ingredientes/IngredientesList.css'; // Reutilizamos tu CSS base

const EmpaquesList = () => {
  const [empaques, setEmpaques] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mostrarModal, setMostrarModal] = useState(false);
  const [editando, setEditando] = useState(null);
  
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    precio: ''
  });

  useEffect(() => {
    cargarEmpaques();
  }, []);

  const cargarEmpaques = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await empaquesService.getEmpaques();
      setEmpaques(data);
    } catch (err) {
      console.error('Error:', err);
      setError('No se pudo cargar el catálogo de empaques');
    } finally {
      setLoading(false);
    }
  };

  const abrirModalCrear = () => {
    setEditando(null);
    setFormData({ nombre: '', descripcion: '', precio: '' });
    setMostrarModal(true);
  };

  const abrirModalEditar = (empaque) => {
    setEditando(empaque);
    setFormData({
      nombre: empaque.nombre,
      descripcion: empaque.descripcion || '',
      precio: empaque.precio
    });
    setMostrarModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError('');
      const datosEnviar = {
        ...formData,
        precio: parseFloat(formData.precio) || 0
      };

      if (editando) {
        await empaquesService.updateEmpaque(editando.id_empaque, datosEnviar);
      } else {
        await empaquesService.createEmpaque(datosEnviar);
      }

      setMostrarModal(false);
      cargarEmpaques();
    } catch (err) {
      console.error('Error guardando:', err);
      setError(err.message || 'Error al guardar');
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm('¿Eliminar este empaque del catálogo general?')) {
      try {
        await empaquesService.deleteEmpaqueCatalogo(id);
        cargarEmpaques();
      } catch (err) {
        alert(err.message);
      }
    }
  };

  if (loading) return <div className="text-center p-5"><h5>Cargando empaques...</h5></div>;

  return (
    <div className="ingredientes-container">
      <div className="ingredientes-header d-flex justify-content-between align-items-center mb-4">
        <h2>🛍️ Catálogo de Empaques</h2>
        <button className="btn-nuevo-ingrediente" onClick={abrirModalCrear}>
          ➕ Nuevo Empaque
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="ingredientes-content shadow-sm rounded">
        <div className="table-container">
          <table className="ingredientes-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Descripción</th>
                <th>Precio Base</th>
                <th className="text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {empaques.length === 0 ? (
                <tr>
                  <td colSpan="4" className="text-center py-5 text-muted">No hay empaques en el catálogo</td>
                </tr>
              ) : (
                empaques.map(e => (
                  <tr key={e.id_empaque}>
                    <td className="nombre">{e.nombre}</td>
                    <td>{e.descripcion || <span className="text-muted italic">Sin descripción</span>}</td>
                    <td className="costo">
                      {new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(e.precio)}
                    </td>
                    <td className="acciones">
                      <button className="btn-editar" onClick={() => abrirModalEditar(e)}>✏️ Editar</button>
                      <button className="btn-eliminar" onClick={() => handleEliminar(e.id_empaque)}>🗑️ Borrar</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal para Crear/Editar */}
      {mostrarModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 1050 }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content shadow-lg border-0" style={{ borderRadius: '15px' }}>
              
              <div className="modal-header text-white" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                <h5 className="modal-title fw-bold">
                  {editando ? '✏️ Editar Empaque' : '➕ Nuevo Empaque'}
                </h5>
                <button type="button" className="btn-close btn-close-white" onClick={() => setMostrarModal(false)}></button>
              </div>
              
              <form onSubmit={handleSubmit}>
                <div className="modal-body p-4">
                  <div className="mb-3">
                    <label className="form-label fw-bold">Nombre del Empaque *</label>
                    <input
                      type="text"
                      name="nombre"
                      className="form-control"
                      placeholder="Ej: Caja para Torta 25x25"
                      value={formData.nombre}
                      onChange={handleInputChange}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label fw-bold">Descripción</label>
                    <input
                      type="text"
                      name="descripcion"
                      className="form-control"
                      placeholder="Ej: Material resistente"
                      value={formData.descripcion}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label fw-bold">Precio Unitario *</label>
                    <div className="input-group">
                      <span className="input-group-text">$</span>
                      <input
                        type="number"
                        name="precio"
                        step="0.01"
                        className="form-control"
                        placeholder="0.00"
                        value={formData.precio}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="modal-footer bg-light p-3">
                  <button type="button" className="btn btn-secondary px-4" onClick={() => setMostrarModal(false)}>
                    Cancelar
                  </button>
                  <button type="submit" className="btn btn-primary px-4 fw-bold" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none' }}>
                    {editando ? 'Actualizar' : 'Guardar'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmpaquesList;