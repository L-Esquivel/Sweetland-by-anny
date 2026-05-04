import React, { useState, useEffect } from 'react';
import { empaquesService } from '../../services/empaquesService';
import '../ingredientes/IngredientesList.css'; // Reutilizamos tu CSS de ingredientes

const EmpaquesList = () => {
  const [empaques, setEmpaques] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mostrarModal, setMostrarModal] = useState(false);
  const [editando, setEditando] = useState(null);
  
  // Estado inicial del formulario
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
      console.error('Error guardando empaque:', err);
      setError(err.message || 'Error al guardar el empaque');
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este empaque del catálogo?')) {
      try {
        await empaquesService.deleteEmpaqueCatalogo(id);
        cargarEmpaques();
      } catch (err) {
        alert(err.message); // Aquí mostrará el error si está en uso en una receta
      }
    }
  };

  if (loading) return <div className="loading">Cargando catálogo de empaques...</div>;

  return (
    <div className="ingredientes-container">
      <div className="ingredientes-header">
        <h2>🛍️ Catálogo General de Empaques</h2>
        <button className="btn-nuevo-ingrediente" onClick={abrirModalCrear}>
          ➕ Nuevo Empaque
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="ingredientes-content">
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
                  <td colSpan="4" className="no-data">No hay empaques registrados en el catálogo</td>
                </tr>
              ) : (
                empaques.map(e => (
                  <tr key={e.id_empaque}>
                    <td className="nombre">{e.nombre}</td>
                    <td>{e.descripcion || <span className="text-muted">Sin descripción</span>}</td>
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

      {/* Modal para Crear/Editar Empaque */}
      {mostrarModal && (
        <div className="modal-overlay">
          <div className="modal shadow-lg">
            <div className="modal-header">
              <h3>{editando ? '✏️ Editar Empaque' : '➕ Nuevo Empaque'}</h3>
              <button className="btn-cerrar" onClick={() => setMostrarModal(false)}>×</button>
            </div>
            
            <form className="modal-content" onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre del Empaque *</label>
                <input
                  type="text"
                  name="nombre"
                  placeholder="Ej: Caja para Torta 25x25, Base de cartón..."
                  value={formData.nombre}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Descripción</label>
                <input
                  type="text"
                  name="descripcion"
                  placeholder="Ej: Material resistente, color blanco..."
                  value={formData.descripcion}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Precio Unitario (Costo Base) *</label>
                <input
                  type="number"
                  name="precio"
                  step="0.01"
                  placeholder="0.00"
                  value={formData.precio}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancelar" onClick={() => setMostrarModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-confirmar">
                  {editando ? 'Actualizar' : 'Guardar'} Empaque
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmpaquesList;