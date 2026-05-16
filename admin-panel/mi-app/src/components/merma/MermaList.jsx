import React, { useState, useEffect } from 'react';
import { mermaService } from '../../services/mermaService';
import { productosService } from '../../services/productosService';
import { ingredientesService } from '../../services/ingredientesService';

const MermaList = () => {
  const [wasteRecords, setWasteRecords] = useState([]);
  const [products, setProducts] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState({ message: '', type: '' });
  
  const [wasteType, setWasteType] = useState('producto'); // 'producto' or 'ingrediente'
  const [newRecord, setNewRecord] = useState({
    item_id: '',
    cantidad: '',
    fecha: new Date().toISOString().split('T')[0],
    motivo: 'Expiration'
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [mermaData, productosData, ingredientesData] = await Promise.all([
        mermaService.getWasteRecords(),
        productosService.getProducts(),
        ingredientesService.getIngredients()
      ]);
      setWasteRecords(mermaData);
      setProducts(productosData);
      setIngredients(ingredientesData);
    } catch (err) {
      setError('Could not load data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewRecord(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setNotification({ message: '', type: '' });

    if (!newRecord.item_id || !newRecord.cantidad || !newRecord.fecha) {
      setError('Please select an item and fill in all fields.');
      return;
    }

    const dataToSend = {
      id_producto: wasteType === 'producto' ? newRecord.item_id : null,
      id_ingrediente: wasteType === 'ingrediente' ? newRecord.item_id : null,
      cantidad: newRecord.cantidad,
      fecha: newRecord.fecha,
      motivo: newRecord.motivo
    };

    try {
      await mermaService.createWasteRecord(dataToSend);
      setNotification({ message: 'Waste record created successfully.', type: 'success' });
      setNewRecord({ item_id: '', cantidad: '', fecha: new Date().toISOString().split('T')[0], motivo: 'Expiration' });
      fetchData();
    } catch (err) {
      setError(`Error creating waste record: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this waste record?')) {
      try {
        await mermaService.deleteWasteRecord(id);
        fetchData();
      } catch (err) {
        setError('Error deleting record.');
      }
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(value || 0);
  };

  return (
    <div className="container-fluid p-4">
      <h2 className="mb-4">📉 Waste Management (Losses)</h2>

      {notification.message && <div className={`alert alert-${notification.type}`}>{notification.message}</div>}

      <div className="row">
        <div className="col-lg-4 mb-4">
          <div className="card shadow-sm">
            <div className="card-header"><h5>Register New Loss</h5></div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">Type of Waste</label>
                  <select className="form-select" value={wasteType} onChange={(e) => { setWasteType(e.target.value); setNewRecord(p => ({...p, item_id: ''}))}}>
                    <option value="producto">Finished Product</option>
                    <option value="ingrediente">Ingredient / Supply</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="item_id" className="form-label">Item</label>
                  <select id="item_id" name="item_id" className="form-select" value={newRecord.item_id} onChange={handleInputChange} required>
                    <option value="">-- Select --</option>
                    {wasteType === 'producto' 
                      ? products.map(p => <option key={p.id_producto} value={p.id_producto}>{p.nombre}</option>)
                      : ingredients.map(i => <option key={i.id_ingrediente} value={i.id_ingrediente}>{i.nombre}</option>)
                    }
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="cantidad" className="form-label">Quantity Lost</label>
                  <input type="number" id="cantidad" name="cantidad" className="form-control" value={newRecord.cantidad} onChange={handleInputChange} required step="0.01" />
                </div>

                <div className="mb-3">
                  <label htmlFor="fecha" className="form-label">Date of Loss</label>
                  <input type="date" id="fecha" name="fecha" className="form-control" value={newRecord.fecha} onChange={handleInputChange} required />
                </div>

                <div className="mb-3">
                  <label htmlFor="motivo" className="form-label">Reason</label>
                  <select id="motivo" name="motivo" className="form-select" value={newRecord.motivo} onChange={handleInputChange}>
                    <option value="Expiration">Expiration</option>
                    <option value="Production Error">Production Error</option>
                    <option value="Unsold Product">Unsold Product</option>
                    <option value="Damage">Damage / Breakage</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <button type="submit" className="btn btn-danger w-100">Register Loss</button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header"><h5>Waste History</h5></div>
            <div className="card-body p-0">
              {loading && <p className="p-3">Loading...</p>}
              {error && <p className="p-3 text-danger">{error}</p>}
              {!loading && !error && (
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Reason</th>
                        <th className="text-end">Cost of Loss</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {wasteRecords.map(r => (
                        <tr key={r.id_merma}>
                          <td>{r.fecha}</td>
                          <td>{r.descripcion} (x{r.cantidad})</td>
                          <td><span className="badge bg-warning text-dark">{r.motivo}</span></td>
                          <td className="text-end fw-bold text-danger">{formatCurrency(r.costo_perdida)}</td>
                          <td className="text-center">
                            <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(r.id_merma)}>🗑️</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MermaList;
