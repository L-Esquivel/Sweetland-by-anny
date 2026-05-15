import React, { useState, useEffect } from 'react';

const RecetaForm = ({ receta, producto, ingredientes = [], empaques = [], onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    id_ingrediente: '',
    cantidad_necesaria: '',
    id_empaque: '',
    cantidad_empaque: 1
  });

  const [isEmpaqueMode, setIsEmpaqueMode] = useState(false);

  useEffect(() => {
    if (receta) {
      setFormData({
        id_ingrediente: receta.id_ingrediente || '',
        cantidad_necesaria: receta.cantidad_necesaria || '',
      });
    }
  }, [receta]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData, isEmpaqueMode);
  };

  return (
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              {receta ? 'Editar' : 'Agregar'} {isEmpaqueMode ? 'Empaque' : 'Ingrediente'}
            </h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              <div className="btn-group mb-3 w-100">
                <button 
                  type="button"
                  className={`btn ${!isEmpaqueMode ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setIsEmpaqueMode(false)}
                >
                  Ingrediente
                </button>
                <button 
                  type="button"
                  className={`btn ${isEmpaqueMode ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setIsEmpaqueMode(true)}
                >
                  Empaque
                </button>
              </div>

              {isEmpaqueMode ? (
                <>
                  <div className="mb-3">
                    <label className="form-label">Empaque</label>
                    <select name="id_empaque" className="form-select" value={formData.id_empaque} onChange={handleChange} required>
                      <option value="">Seleccionar empaque</option>
                      {empaques && empaques.length > 0 ? (
                        empaques.map(e => (
                          <option key={e.id_empaque} value={e.id_empaque}>
                            {e.nombre} - ${e.precio}
                          </option>
                        ))
                      ) : (
                        <option value="">No hay empaques disponibles</option>
                      )}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Cantidad</label>
                    <input type="number" name="cantidad_empaque" className="form-control" value={formData.cantidad_empaque} onChange={handleChange} min="1" required />
                  </div>
                </>
              ) : (
                <>
                  <div className="mb-3">
                    <label className="form-label">Ingrediente</label>
                    <select name="id_ingrediente" className="form-select" value={formData.id_ingrediente} onChange={handleChange} required>
                      <option value="">Seleccionar ingrediente</option>
                      {ingredientes && ingredientes.length > 0 ? (
                        ingredientes.map(i => (
                          <option key={i.id_ingrediente} value={i.id_ingrediente}>
                            {/* FIX: El backend envía 'unidad_medida', no 'unidad'. */}
                            {i.nombre} ({i.unidad_medida})
                          </option>
                        ))
                      ) : (
                        <option value="">No hay ingredientes disponibles</option>
                      )}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Cantidad Necesaria</label>
                    <input type="number" name="cantidad_necesaria" className="form-control" value={formData.cantidad_necesaria} onChange={handleChange} step="0.01" required />
                  </div>
                </>
              )}
            </div>

            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancelar</button>
              <button type="submit" className="btn btn-primary">Guardar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RecetaForm;