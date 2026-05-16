import React, { useState, useEffect } from 'react';

const RecetaForm = ({ recipeItem, product, ingredients = [], packagingCatalog = [], onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    id_ingrediente: '',
    cantidad_necesaria: '',
    id_empaque: '',
    cantidad_empaque: 1
  });

  const [isPackagingMode, setIsPackagingMode] = useState(false);

  useEffect(() => {
    if (recipeItem) {
      setFormData({
        id_ingrediente: recipeItem.id_ingrediente || '',
        cantidad_necesaria: recipeItem.cantidad_necesaria || '',
      });
    }
  }, [recipeItem]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData, isPackagingMode);
  };

  return (
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              {recipeItem ? 'Edit' : 'Add'} {isPackagingMode ? 'Packaging' : 'Ingredient'}
            </h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              <div className="btn-group mb-3 w-100">
                <button 
                  type="button"
                  className={`btn ${!isPackagingMode ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setIsPackagingMode(false)}
                >
                  Ingredient
                </button>
                <button 
                  type="button"
                  className={`btn ${isPackagingMode ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setIsPackagingMode(true)}
                >
                  Packaging
                </button>
              </div>

              {isPackagingMode ? (
                <>
                  <div className="mb-3">
                    <label className="form-label">Packaging</label>
                    <select name="id_empaque" className="form-select" value={formData.id_empaque} onChange={handleChange} required>
                      <option value="">Select packaging</option>
                      {packagingCatalog && packagingCatalog.length > 0 ? (
                        packagingCatalog.map(e => (
                          <option key={e.id_empaque} value={e.id_empaque}>
                            {e.nombre} - ${e.precio}
                          </option>
                        ))
                      ) : (
                        <option value="">No packaging items available</option>
                      )}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Quantity</label>
                    <input type="number" name="cantidad_empaque" className="form-control" value={formData.cantidad_empaque} onChange={handleChange} min="1" required />
                  </div>
                </>
              ) : (
                <>
                  <div className="mb-3">
                    <label className="form-label">Ingredient</label>
                    <select name="id_ingrediente" className="form-select" value={formData.id_ingrediente} onChange={handleChange} required>
                      <option value="">Select ingredient</option>
                      {ingredients && ingredients.length > 0 ? (
                        ingredients.map(i => (
                          <option key={i.id_ingrediente} value={i.id_ingrediente}>
                            {/* FIX: El backend envía 'unidad_medida', no 'unidad'. */}
                            {i.nombre} ({i.unidad_medida})
                          </option>
                        ))
                      ) : (
                        <option value="">No ingredients available</option>
                      )}
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Quantity Needed</label>
                    <input type="number" name="cantidad_necesaria" className="form-control" value={formData.cantidad_necesaria} onChange={handleChange} step="0.01" required />
                  </div>
                </>
              )}
            </div>

            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RecetaForm;