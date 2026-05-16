import React, { useState, useEffect } from 'react';
import { recetasService } from '../../services/recetasService';
import { productosService } from '../../services/productosService';
import { ingredientesService } from '../../services/ingredientesService';
import { empaquesService } from '../../services/empaquesService';
import RecetaForm from './RecetaForm';
import './RecetasList.css';

const RecetasList = () => {
  const [products, setProducts] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [packagingCatalog, setPackagingCatalog] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [productRecipes, setProductRecipes] = useState([]);
  const [productPackaging, setProductPackaging] = useState([]);
  const [costs, setCosts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false); // For visual loading feedback

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [productosData, ingredientesData, empaquesData] = await Promise.all([
        productosService.getProducts(),
        ingredientesService.getIngredients(),
        empaquesService.getPackagingCatalog()
      ]);
      setProducts(productosData);
      setIngredients(ingredientesData);
      setPackagingCatalog(empaquesData);
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProductRecipes = async (productId) => {
    try {
      const product = products.find(p => p.id_producto === productId);
      setSelectedProduct(product);

      const data = await recetasService.getProductRecipeDetails(productId);
      setProductRecipes(data.recipes || []);
      setProductPackaging(data.packaging || []);
      setCosts(data.costs || null);
    } catch (error) {
      console.error('Error loading product recipes:', error);
    }
  };

  // OPTIMIZED: Single backend call to recalculate and save
  const updateProductField = async (field, value) => {
    if (!selectedProduct) return;

    // 1. Instant UI update to avoid lag
    const updatedProduct = { ...selectedProduct, [field]: value };
    setSelectedProduct(updatedProduct);
    setIsUpdating(true);

    try {
      const newPax = field === 'pax' ? value : updatedProduct.pax;
      const newProfit = field === 'utilidad_porcentaje' ? value : updatedProduct.utilidad_porcentaje;

      // 2. We only call recalculate. The backend already handles the UPDATE on the products table.
      const data = await recetasService.recalculateCosts(
        selectedProduct.id_producto,
        parseInt(newPax) || 1,
        parseFloat(newProfit) || 0
      );

      // 3. Sync the costs state with the server's response
      setCosts(data.costs || null);
    } catch (error) {
      console.error('Error recalculating:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDeleteRecipe = async (recipeId) => {
    if (window.confirm('Delete this ingredient?')) {
      try {
        await recetasService.deleteRecipeIngredient(recipeId);
        fetchProductRecipes(selectedProduct.id_producto);
      } catch (error) { console.error(error); }
    }
  };

  const handleDeletePackaging = async (id) => {
    if (window.confirm('Delete this packaging?')) {
      try {
        await empaquesService.deletePackagingFromProduct(id);
        fetchProductRecipes(selectedProduct.id_producto);
      } catch (error) { console.error(error); }
    }
  };

  const handleCreateRecipeItem = () => {
    if (!selectedProduct) return alert('Select a product first');
    setShowModal(true);
  };

  const handleRecipeFormSubmit = async (data, isPackaging = false) => {
    try {
      if (isPackaging) {
        await empaquesService.addPackagingToProduct(selectedProduct.id_producto, data);
      } else {
        await recetasService.addRecipeIngredient({ ...data, id_producto: selectedProduct.id_producto });
      }
      setShowModal(false);
      fetchProductRecipes(selectedProduct.id_producto);
    } catch (error) { console.error('Error saving:', error); }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(value || 0);
  };

  if (loading) return <div className="text-center p-5"><h3>Loading costing system...</h3></div>;

  return (
    <div className="recetas-container container-fluid p-4">
      <h2 className="mb-4 text-center">📋 Costing & Recipe Analysis</h2>

      <div className="card shadow-sm mb-4">
        <div className="card-body bg-light">
          <label className="form-label fw-bold">Select Product for Costing:</label>
          <select 
            className="form-select form-select-lg"
            value={selectedProduct?.id_producto || ''}
            onChange={(e) => {
              const selectedId = e.target.value;
              if (selectedId) {
                fetchProductRecipes(parseInt(selectedId));
              } else {
                // If the user deselects, clear the state
                setSelectedProduct(null);
                setCosts(null);
              }
            }}
          >
            <option value="">-- Select a product from the catalog --</option>
            {products.map(p => (
              <option key={p.id_producto} value={p.id_producto}>{p.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {selectedProduct && costs && (
        <div className="row">
          {/* Left Column: Adjustments */}
          <div className="col-lg-5">
            <div className="card shadow-sm border-0 mb-4">
              <div className="card-header bg-dark text-white">
                <h5 className="mb-0">⚙️ Sale Parameters</h5>
              </div>
              <div className="card-body">
                <h4 className="text-primary">{selectedProduct.nombre}</h4>
                <hr />
                
                <div className="mb-4">
                  <label className="form-label fw-bold">PAX (Units per recipe):</label>
                  <div className="input-group">
                    <span className="input-group-text">📦</span>
                    <input 
                      type="number" 
                      className="form-control form-control-lg" 
                      // 💡 FIX: Changed `|| 1` to `?? ''`.
                      // This allows the text field to be momentarily empty
                      // so the user can clear the value and type a new one,
                      // instead of immediately forcing it to '1'.
                      value={selectedProduct.pax ?? ''}
                      onChange={(e) => updateProductField('pax', e.target.value)}
                    />
                  </div>
                  <small className="text-muted">The final price will be divided by this number.</small>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-bold">Desired Profit (%):</label>
                  <div className="input-group">
                    <input 
                      type="number"
                      className="form-control form-control-lg"
                      value={selectedProduct.utilidad_porcentaje ?? ''}
                      onChange={(e) => updateProductField('utilidad_porcentaje', e.target.value)}
                    />
                    <span className="input-group-text">%</span>
                  </div>
                  <small className="text-muted">Percentage of profit over the total production cost.</small>
                </div>

                {isUpdating && <div className="text-primary"><span className="spinner-border spinner-border-sm me-2"></span>Recalculating...</div>}
              </div>
            </div>
          </div>

          {/* Right Column: Breakdown */}
          <div className="col-lg-7">
            <div className="card shadow-sm border-0">
              <div className="card-header bg-success text-white">
                <h5 className="mb-0">💰 Detailed Price Breakdown</h5>
              </div>
              <div className="card-body p-0">
                <table className="table table-hover mb-0">
                  <tbody>
                    <tr>
                      <td className="ps-4">Base Cost (Ingredients)</td>
                      <td className="text-end pe-4 fw-bold">{formatCurrency(costs.base_cost)}</td>
                    </tr>
                    <tr className="table-light">
                      <td className="ps-4 text-muted small">+ 35% Operational Expenses</td>
                      <td className="text-end pe-4">{formatCurrency(costs.operational_expenses)}</td>
                    </tr>
                    <tr className="table-light">
                      <td className="ps-4 text-muted small">+ 10% Market Depreciation</td>
                      <td className="text-end pe-4">{formatCurrency(costs.market_depreciation)}</td>
                    </tr>
                    <tr className="table-light border-bottom">
                      <td className="ps-4 text-muted small">+ 5% Equipment Depreciation</td>
                      <td className="text-end pe-4">{formatCurrency(costs.equipment_depreciation)}</td>
                    </tr>
                    <tr>
                      <td className="ps-4">+ Total Packaging Value</td>
                      <td className="text-end pe-4">{formatCurrency(costs.packaging_cost)}</td>
                    </tr>
                    <tr className="fw-bold bg-light">
                      <td className="ps-4 text-primary">TOTAL BEFORE PROFIT</td>
                      <td className="text-end pe-4 text-primary">{formatCurrency(costs.production_cost)}</td>
                    </tr>
                    <tr>
                      <td className="ps-4">{costs.profit_percentage}% Selected Profit</td>
                      <td className="text-end pe-4 text-success">+ {formatCurrency(costs.profit)}</td>
                    </tr>
                    <tr className="fw-bold">
                      <td className="ps-4">TOTAL WITH PROFIT</td>
                      <td className="text-end pe-4">{formatCurrency(costs.pre_tax_total)}</td>
                    </tr>
                    <tr>
                      <td className="ps-4">8% Consumption Tax (I.C.)</td>
                      <td className="text-end pe-4">{formatCurrency(costs.consumption_tax)}</td>
                    </tr>
                    <tr className="table-dark">
                      <td className="ps-4 fs-5 py-3 fw-bold">FINAL SUGGESTED PRICE (per unit)</td>
                      <td className="text-end pe-4 fs-5 py-3 fw-bold text-warning">{formatCurrency(costs.suggested_price)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="card-footer text-center bg-white border-0 py-3">
                <button className="btn btn-outline-primary btn-lg" onClick={handleCreateRecipeItem}>
                  ➕ Add Ingredient or Packaging
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Detailed Tables (Ingredients / Packaging) below for order */}
      {selectedProduct && (
        <div className="row mt-4">
            <div className="col-md-6">
                <div className="card shadow-sm">
                    <div className="card-header bg-secondary text-white">Ingredients</div>
                    <div className="table-responsive">
                        <table className="table table-sm mb-0">
                            <thead><tr><th>Item</th><th>Qty.</th><th>Subtotal</th><th></th></tr></thead>
                            <tbody>
                                {productRecipes.map((r) => (
                                    // FIX: Use the unique record ID as key and for the delete function.
                                    // The backend sends 'id', not 'id_receta'.
                                    <tr key={r.id}>
                                        <td>{r.ingrediente}</td>
                                        <td>{r.cantidad_necesaria} {r.unidad}</td>
                                        <td className="fw-bold">{formatCurrency(r.costo_ingrediente)}</td>
                                        <td><button className="btn btn-link btn-sm text-danger" onClick={() => handleDeleteRecipe(r.id)}>🗑️</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div className="col-md-6">
                <div className="card shadow-sm">
                    <div className="card-header bg-secondary text-white">Packaging</div>
                    <div className="table-responsive">
                        <table className="table table-sm mb-0">
                            <thead><tr><th>Item</th><th>Qty.</th><th>Subtotal</th><th></th></tr></thead>
                            <tbody>
                                {productPackaging.map((e, i) => (
                                    <tr key={i}>
                                        <td>{e.nombre}</td>
                                        <td>{e.cantidad}</td>
                                        <td className="fw-bold">{formatCurrency(e.subtotal)}</td>
                                        <td><button className="btn btn-link btn-sm text-danger" onClick={() => handleDeletePackaging(e.id)}>🗑️</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
      )}

      {showModal && (
        <RecetaForm
          product={selectedProduct}
          ingredients={ingredients}
          packagingCatalog={packagingCatalog}
          onSubmit={handleRecipeFormSubmit}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default RecetasList;