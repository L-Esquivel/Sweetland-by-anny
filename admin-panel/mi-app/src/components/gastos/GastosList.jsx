import React, { useState, useEffect } from 'react';
import { gastosService } from '../../services/gastosService';

const GastosList = () => {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newExpense, setNewExpense] = useState({
    descripcion: '', // These keys must match the backend API
    monto: '',       //
    fecha: new Date().toISOString().split('T')[0],
    categoria: 'Operational'
  });

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      const data = await gastosService.getExpenses();
      setExpenses(data);
    } catch (err) {
      setError('Could not load expenses.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewExpense(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newExpense.descripcion || !newExpense.monto || !newExpense.fecha) {
      alert('Please fill in all fields.');
      return;
    }
    try {
      await gastosService.createExpense(newExpense);
      // Clear form
      setNewExpense({
        descripcion: '',
        monto: '',
        fecha: new Date().toISOString().split('T')[0],
        categoria: 'Operational'
      });
      // Reload list
      fetchExpenses();
    } catch (err) {
      alert('Error creating expense.');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this expense?')) {
      try {
        await gastosService.deleteExpense(id);
        fetchExpenses();
      } catch (err) {
        alert('Error deleting expense.');
      }
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value || 0);
  };

  return (
    <div className="container-fluid p-4">
      <h2 className="mb-4">💸 Fixed and Operational Expenses Management</h2>

      <div className="row">
        {/* Form Column */}
        <div className="col-lg-4 mb-4">
          <div className="card shadow-sm">
            <div className="card-header">
              <h5>Register New Expense</h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="descripcion" className="form-label">Description</label>
                  <input type="text" id="descripcion" name="descripcion" className="form-control" value={newExpense.descripcion} onChange={handleInputChange} required />
                </div>
                <div className="mb-3">
                  <label htmlFor="monto" className="form-label">Amount</label>
                  <input type="number" id="monto" name="monto" className="form-control" value={newExpense.monto} onChange={handleInputChange} required placeholder="e.g., 50" />
                </div>
                <div className="mb-3">
                  <label htmlFor="fecha" className="form-label">Expense Date</label>
                  <input type="date" id="fecha" name="fecha" className="form-control" value={newExpense.fecha} onChange={handleInputChange} required />
                </div>
                <div className="mb-3">
                  <label htmlFor="categoria" className="form-label">Category</label>
                  <select id="categoria" name="categoria" className="form-select" value={newExpense.categoria} onChange={handleInputChange}>
                    <option value="Operational">Operational</option>
                    <option value="Rent">Rent</option>
                    <option value="Utilities">Utilities</option>
                    <option value="Salaries">Salaries</option>
                    <option value="Marketing">Marketing</option>
                    <option value="Miscellaneous">Miscellaneous</option>
                  </select>
                </div>
                <button type="submit" className="btn btn-primary w-100">Add Expense</button>
              </form>
            </div>
          </div>
        </div>

        {/* Table Column */}
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header">
              <h5>Expense History</h5>
            </div>
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
                        <th>Category</th>
                        <th className="text-end">Amount</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {expenses.map(expense => (
                        <tr key={expense.id_gasto}>
                          <td>{expense.fecha}</td>
                          <td>{expense.descripcion}</td>
                          <td><span className="badge bg-secondary">{expense.categoria}</span></td>
                          <td className="text-end fw-bold">{formatCurrency(expense.monto)}</td>
                          <td className="text-center">
                            <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(expense.id_gasto)}>🗑️</button>
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

export default GastosList;