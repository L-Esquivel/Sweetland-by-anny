import React, { useState, useEffect } from 'react';
import { empaquesService } from '../../services/empaquesService';
import '../ingredientes/IngredientesList.css'; // Reutilizamos el mismo CSS

const EmpaquesList = () => {
  const [empaques, setEmpaques] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mostrarModal, setMostrarModal] = useState(false);
  const [editando, setEditando] = useState(null);
  const [formData, setFormData] = useState({ nombre: '', descripcion: '', precio: '' });

  useEffect(() => { cargarEmpaques(); }, []);

  const cargarEmpaques = async () => {
    try {
      setLoading(true);
      const data = await empaquesService.getEmpaques();
      setEmpaques(data);
    } catch (err) {
      setError('No se pudo cargar el catálogo de empaques');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const dataFinal = { ...formData, precio: parseFloat(formData.precio) || 0 };
      if (editando) {
        await empaquesService.updateEmpaque(editando.id_empaque, dataFinal);
      } else {
        await empaquesService.createEmpaque(dataFinal);
      }
      setMostrarModal(false);
      cargarEmpaques();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm('¿Estás seguro? Se eliminará del catálogo general.')) {
      try {
        await empaquesService.deleteEmpaqueCatalogo(id);
        cargarEmpaques();
      } catch (err) {
        alert(err.message); // Muestra el error de "En uso" si el backend lo envía
      }
    }
  };

  if (loading) return <div className="loading">Cargando catálogo de empaques...</div>;

  return (
    <div className="ingredientes-container">
      <div className="ingredientes-header">
        <h2>🛍️ Catálogo de Empaques</h2>
        <button className="btn-nuevo-ingrediente" onClick={() => {
          setEditando(null);
          setFormData({ nombre: '', descripcion: '', precio: '' });
          setMostrarModal(true);
        }}>➕ Nuevo Empaque</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="ingredientes-content">
        <div className="table-container">
          <table className="ingredientes-table">
            <thead>
              <tr>
                <th>Nombre del Empaque</th>
                <th>Descripción</th>
                <th>Precio Base</th>
                <th className="text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {empaques.map(e => (
                <tr key={e.id_empaque}>
                  <td className="nombre">{e.nombre}</td>
                  <td>{e.descripcion || <span className="text-muted">Sin descripción</span>}</td>
                  <td className="costo">${parseFloat(e.precio).toLocaleString()}</td>
                  <td className="acciones">
                    <button className="btn-editar" onClick={() => {
                      setEditando(e);
                      setFormData({ nombre: e.nombre, descripcion: e.descripcion, precio: e.precio });
                      setMostrarModal(true);
                    }}>✏️</button>
                    <button className="btn-eliminar" onClick={() => handleEliminar(e.id_empaque)}>🗑️</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {mostrarModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{editando ? 'Editar Empaque' : 'Nuevo Empaque'}</h3>
              <button className="btn-cerrar" onClick={() => setMostrarModal(false)}>×</button>
            </div>
            <form className="modal-content" onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre *</label>
                <input type="text" value={formData.nombre} required onChange={e => setFormData({...formData, nombre: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Descripción</label>
                <input type="text" value={formData.descripcion} onChange={e => setFormData({...formData, descripcion: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Precio Unitario (COP) *</label>
                <input type="number" step="0.01" value={formData.precio} required onChange={e => setFormData({...formData, precio: e.target.value})} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-cancelar" onClick={() => setMostrarModal(false)}>Cancelar</button>
                <button type="submit" className="btn-confirmar">Guardar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmpaquesList;