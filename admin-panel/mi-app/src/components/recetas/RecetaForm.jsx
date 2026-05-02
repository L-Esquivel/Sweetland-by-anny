// src/components/recetas/RecetaForm.jsx
import React, { useState, useEffect } from 'react';

const RecetaForm = ({ receta, producto, ingredientes, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    id_ingrediente: '',
    cantidad_necesaria: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (receta) {
      setFormData({
        id_ingrediente: receta.id_ingrediente,
        cantidad_necesaria: receta.cantidad_necesaria
      });
    }
  }, [receta]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validaciones
      if (!formData.id_ingrediente || !formData.cantidad_necesaria) {
        throw new Error('Todos los campos son obligatorios');
      }

      if (parseFloat(formData.cantidad_necesaria) <= 0) {
        throw new Error('La cantidad debe ser mayor a 0');
      }

      await onSubmit(formData);
    } catch (error) {
      console.error('Error en RecetaForm:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getIngredienteSeleccionado = () => {
    return ingredientes.find(ing => ing.id_ingrediente === parseInt(formData.id_ingrediente));
  };

  const ingredienteSeleccionado = getIngredienteSeleccionado();

  return (
    <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header bg-primary text-white">
            <h5 className="modal-title">
              {receta ? '✏️ Editar Ingrediente en Receta' : '➕ Agregar Ingrediente a Receta'}
            </h5>
            <button 
              type="button" 
              className="btn-close btn-close-white" 
              onClick={onClose}
              disabled={loading}
            ></button>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              {/* Información del Producto */}
              {producto && (
                <div className="alert alert-info">
                  <strong>Producto:</strong> {producto.nombre}
                  <br />
                  <strong>Categoría:</strong> {producto.categoria}
                </div>
              )}

              {/* Selector de Ingrediente */}
              <div className="mb-3">
                <label className="form-label">Ingrediente *</label>
                <select
                  name="id_ingrediente"
                  className="form-select"
                  value={formData.id_ingrediente}
                  onChange={handleChange}
                  required
                  disabled={loading}
                >
                  <option value="">-- Selecciona un ingrediente --</option>
                  {ingredientes.map(ingrediente => (
                    <option key={ingrediente.id_ingrediente} value={ingrediente.id_ingrediente}>
                      {ingrediente.nombre} - {ingrediente.unidad} 
                      {ingrediente.costo_unitario && (
                        ` (${new Intl.NumberFormat('es-CO', {
                          style: 'currency',
                          currency: 'COP'
                        }).format(ingrediente.costo_unitario)})`
                      )}
                    </option>
                  ))}
                </select>
              </div>

              {/* Información del Ingrediente Seleccionado */}
              {ingredienteSeleccionado && (
                <div className="card mb-3">
                  <div className="card-body py-2">
                    <div className="row">
                      <div className="col-md-6">
                        <small>
                          <strong>Stock disponible:</strong> {ingredienteSeleccionado.cantidad} {ingredienteSeleccionado.unidad}
                        </small>
                      </div>
                      <div className="col-md-6">
                        <small>
                          <strong>Costo unitario:</strong> {new Intl.NumberFormat('es-CO', {
                            style: 'currency',
                            currency: 'COP'
                          }).format(ingredienteSeleccionado.costo_unitario)}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Cantidad Necesaria */}
              <div className="mb-3">
                <label className="form-label">
                  Cantidad Necesaria * 
                  {ingredienteSeleccionado && (
                    <span className="text-muted"> ({ingredienteSeleccionado.unidad})</span>
                  )}
                </label>
                <input
                  type="number"
                  name="cantidad_necesaria"
                  className="form-control"
                  value={formData.cantidad_necesaria}
                  onChange={handleChange}
                  step="0.01"
                  min="0.01"
                  required
                  disabled={loading}
                  placeholder="Ej: 0.5, 2, 10.25"
                />
                <div className="form-text">
                  Ingresa la cantidad necesaria para producir una unidad del producto
                </div>
              </div>

              {/* Información de Costo */}
              {ingredienteSeleccionado && formData.cantidad_necesaria && (
                <div className="alert alert-warning">
                  <strong>Costo estimado por producto:</strong>{' '}
                  {new Intl.NumberFormat('es-CO', {
                    style: 'currency',
                    currency: 'COP'
                  }).format(ingredienteSeleccionado.costo_unitario * parseFloat(formData.cantidad_necesaria))}
                </div>
              )}

              {/* Mensaje de Error */}
              {error && (
                <div className="alert alert-danger">
                  {error}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={onClose}
                disabled={loading}
              >
                Cancelar
              </button>
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Guardando...
                  </>
                ) : (
                  receta ? '📝 Actualizar' : '✅ Agregar a Receta'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RecetaForm;