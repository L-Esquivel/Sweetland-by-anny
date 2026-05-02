import React, { useState, useEffect } from 'react';
import './IngredientesList.css';
import { ingredientesService } from '../../services/ingredientesService';

const IngredientesList = () => {
  const [ingredientes, setIngredientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mostrarModal, setMostrarModal] = useState(false);
  const [ingredienteEditando, setIngredienteEditando] = useState(null);
  const [formData, setFormData] = useState({
    nombre: '',
    unidad: '',
    cantidad: '',
    costo_unitario: ''
  });

  // Unidades disponibles
  const unidades = ['kg', 'g', 'lb', 'oz', 'lt', 'ml', 'unidad', 'paquete'];

  useEffect(() => {
    cargarIngredientes();
  }, []);

  const cargarIngredientes = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await ingredientesService.getIngredientes();
      setIngredientes(data);
    } catch (error) {
      console.error('Error cargando ingredientes:', error);
      setError('No se pudieron cargar los ingredientes');
    } finally {
      setLoading(false);
    }
  };

  const abrirModalCrear = () => {
    setIngredienteEditando(null);
    setFormData({
      nombre: '',
      unidad: '',
      cantidad: '',
      costo_unitario: ''
    });
    setMostrarModal(true);
  };

  const abrirModalEditar = (ingrediente) => {
    setIngredienteEditando(ingrediente);
    setFormData({
      nombre: ingrediente.nombre,
      unidad: ingrediente.unidad,
      cantidad: ingrediente.cantidad || '',
      costo_unitario: ingrediente.costo_unitario || ''
    });
    setMostrarModal(true);
  };

  const cerrarModal = () => {
    setMostrarModal(false);
    setIngredienteEditando(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError('');

      const datosEnviar = {
        ...formData,
        cantidad: formData.cantidad ? parseFloat(formData.cantidad) : null,
        costo_unitario: formData.costo_unitario ? parseFloat(formData.costo_unitario) : null
      };

      if (ingredienteEditando) {
        await ingredientesService.updateIngrediente(ingredienteEditando.id_ingrediente, datosEnviar);
      } else {
        await ingredientesService.createIngrediente(datosEnviar);
      }

      cerrarModal();
      cargarIngredientes();
    } catch (error) {
      console.error('Error guardando ingrediente:', error);
      setError('No se pudo guardar el ingrediente');
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este ingrediente?')) {
      try {
        await ingredientesService.deleteIngrediente(id);
        cargarIngredientes();
      } catch (error) {
        console.error('Error eliminando ingrediente:', error);
        setError('No se pudo eliminar el ingrediente');
      }
    }
  };

  const formatearMoneda = (valor) => {
    if (!valor) return '$ 0';
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP'
    }).format(valor);
  };

  const getUnidadBadgeClass = (unidad) => {
    switch (unidad) {
      case 'kg':
      case 'lb':
        return 'bg-primary';
      case 'g':
      case 'oz':
        return 'bg-success';
      case 'lt':
      case 'ml':
        return 'bg-info';
      case 'unidad':
        return 'bg-warning text-dark';
      case 'paquete':
        return 'bg-secondary';
      default:
        return 'bg-light text-dark';
    }
  };

  if (loading) {
    return <div className="text-center p-4">Cargando ingredientes...</div>;
  }

  return (
    <div className="ingredientes-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">🧂 Gestión de Ingredientes</h2>
        <button className="btn btn-primary" onClick={abrirModalCrear}>
          ➕ Nuevo Ingrediente
        </button>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <div className="card">
        <div className="card-body p-0">
          <div className="table-responsive">
            <table className="table table-striped table-hover mb-0">
              <thead className="table-dark">
                <tr>
                  <th>Nombre</th>
                  <th>Unidad</th>
                  <th>Cantidad en Stock</th>
                  <th>Costo Unitario</th>
                  <th className="text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {ingredientes.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center text-muted py-4">
                      No hay ingredientes registrados
                    </td>
                  </tr>
                ) : (
                  ingredientes.map(ingrediente => (
                    <tr key={ingrediente.id_ingrediente}>
                      <td className="fw-semibold">{ingrediente.nombre}</td>
                      <td>
                        <span className={`badge ${getUnidadBadgeClass(ingrediente.unidad)}`}>
                          {ingrediente.unidad}
                        </span>
                      </td>
                      <td>
                        {ingrediente.cantidad !== null ? (
                          <span className="fw-bold">
                            {ingrediente.cantidad} {ingrediente.unidad}
                          </span>
                        ) : (
                          <span className="text-muted">N/A</span>
                        )}
                      </td>
                      <td className="fw-bold text-success">
                        {formatearMoneda(ingrediente.costo_unitario)}
                      </td>
                      <td className="text-center">
                        <div className="btn-group" role="group">
                          <button 
                            className="btn btn-warning btn-sm me-1"
                            onClick={() => abrirModalEditar(ingrediente)}
                            title="Editar ingrediente"
                          >
                            ✏️ Editar
                          </button>
                          <button 
                            className="btn btn-danger btn-sm"
                            onClick={() => handleEliminar(ingrediente.id_ingrediente)}
                            title="Eliminar ingrediente"
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
        </div>
      </div>

      {/* Modal para crear/editar */}
      {mostrarModal && (
        <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header bg-primary text-white">
                <h5 className="modal-title">
                  {ingredienteEditando ? '✏️ Editar Ingrediente' : '➕ Nuevo Ingrediente'}
                </h5>
                <button 
                  type="button" 
                  className="btn-close btn-close-white" 
                  onClick={cerrarModal}
                ></button>
              </div>
              
              <form onSubmit={handleSubmit}>
                <div className="modal-body">
                  <div className="mb-3">
                    <label className="form-label">Nombre del Ingrediente *</label>
                    <input
                      type="text"
                      name="nombre"
                      className="form-control"
                      value={formData.nombre}
                      onChange={handleInputChange}
                      required
                      placeholder="Ej: Harina, Azúcar, Huevos..."
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Unidad de Medida *</label>
                    <select
                      name="unidad"
                      className="form-select"
                      value={formData.unidad}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="">Seleccionar unidad</option>
                      {unidades.map(unidad => (
                        <option key={unidad} value={unidad}>
                          {unidad}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="row">
                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Cantidad en Stock</label>
                        <input
                          type="number"
                          name="cantidad"
                          className="form-control"
                          value={formData.cantidad}
                          onChange={handleInputChange}
                          step="0.01"
                          min="0"
                          placeholder="0.00"
                        />
                      </div>
                    </div>

                    <div className="col-md-6">
                      <div className="mb-3">
                        <label className="form-label">Costo Unitario (COP)</label>
                        <input
                          type="number"
                          name="costo_unitario"
                          className="form-control"
                          value={formData.costo_unitario}
                          onChange={handleInputChange}
                          step="0.01"
                          min="0"
                          placeholder="0.00"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="modal-footer">
                  <button 
                    type="button"
                    className="btn btn-secondary"
                    onClick={cerrarModal}
                  >
                    Cancelar
                  </button>
                  <button 
                    type="submit"
                    className="btn btn-primary"
                  >
                    {ingredienteEditando ? '📝 Actualizar' : '✅ Crear'} Ingrediente
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

export default IngredientesList;