import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { paymentsService } from '../../services/paymentsService';

const PaymentManagerModal = ({ tenant, onClose }) => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    amount: '',
    payment_date: new Date().toISOString().split('T')[0],
    notes: '',
  });

  useEffect(() => {
    fetchPayments();
  }, [tenant]);

  const fetchPayments = async () => {
    if (!tenant) return;
    setLoading(true);
    try {
      const data = await paymentsService.getPaymentsForTenant(tenant.id_tenant);
      setPayments(data);
    } catch (err) {
      setError('No se pudieron cargar los pagos.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await paymentsService.addPayment({
        ...formData,
        tenant_id: tenant.id_tenant,
        amount: parseFloat(formData.amount),
      });
      setFormData({
        amount: '',
        payment_date: new Date().toISOString().split('T')[0],
        notes: '',
      });
      fetchPayments(); // Refresh list
    } catch (err) {
      setError(err.message || 'Error al registrar el pago.');
    }
  };

  const handleDelete = async (paymentId) => {
    if (window.confirm('¿Eliminar este pago?')) {
      try {
        await paymentsService.deletePayment(paymentId);
        fetchPayments(); // Refresh list
      } catch (err) {
        setError(err.message || 'Error al eliminar el pago.');
      }
    }
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
  };

  return createPortal(
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-xl">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Gestión de Pagos - {tenant.nombre}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            {error && <div className="alert alert-danger">{error}</div>}
            
            <div className="card mb-4">
              <div className="card-body">
                <h6 className="card-title">Registrar Nuevo Pago</h6>
                <form onSubmit={handleSubmit} className="row g-3 align-items-end">
                  <div className="col-md-4"><label htmlFor="amount" className="form-label">Monto (COP)</label><input type="number" id="amount" name="amount" className="form-control" value={formData.amount} onChange={handleInputChange} required step="0.01" /></div>
                  <div className="col-md-3"><label htmlFor="payment_date" className="form-label">Fecha</label><input type="date" id="payment_date" name="payment_date" className="form-control" value={formData.payment_date} onChange={handleInputChange} required /></div>
                  <div className="col-md-3"><label htmlFor="notes" className="form-label">Notas</label><input type="text" id="notes" name="notes" className="form-control" value={formData.notes} onChange={handleInputChange} /></div>
                  <div className="col-md-2"><button type="submit" className="btn btn-primary w-100">Registrar</button></div>
                </form>
              </div>
            </div>

            <h6>Historial de Pagos</h6>
            {loading ? <p>Cargando historial...</p> : (
              <div className="table-responsive"><table className="table table-striped"><thead><tr><th>Fecha</th><th>Monto</th><th>Notas</th><th>Acciones</th></tr></thead>
                  <tbody>
                    {payments.length === 0 ? (<tr><td colSpan="4" className="text-center">No hay pagos registrados.</td></tr>) : (payments.map(p => (<tr key={p.id_payment}><td>{p.payment_date}</td><td className="fw-bold">{formatearMoneda(p.amount)}</td><td>{p.notes}</td><td><button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.id_payment)}>Eliminar</button></td></tr>)))}
                  </tbody>
              </table></div>
            )}
          </div>
          <div className="modal-footer"><button type="button" className="btn btn-secondary" onClick={onClose}>Cerrar</button></div>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default PaymentManagerModal;