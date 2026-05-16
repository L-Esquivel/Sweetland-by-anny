// c:\Proyectos de programacion\SWEETLAND FULL PROYECT\admin-panel\mi-app\src\components\tenants\TenantsList.jsx
import React, { useState, useEffect } from 'react';
import { tenantsService } from '../../services/tenantsService';
import { modulesService } from '../../services/modulesService';
import PaymentManagerModal from './PaymentManagerModal';
import './TenantsList.css';

function TenantsList() {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [availableModules, setAvailableModules] = useState([]);
  const [form, setForm] = useState({
    tenant_name: '',
    admin_name: '',
    admin_email: '',
    admin_password: ''
  });
  const [customLabels, setCustomLabels] = useState({});
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedTenant, setSelectedTenant] = useState(null);

  const fetchTenants = async () => {
    try {
      // No need to set loading to true here if called from another function that already handles it
      const data = await tenantsService.getAllTenants();
      setTenants(data);
      setError('');
    } catch (err) {
      setError(err.message || 'Error loading tenants');
    }
  };

  useEffect(() => {
    const fetchInitialData = async () => {
      setLoading(true);
      try {
        const [tenantsData, modulesRawData] = await Promise.all([
          tenantsService.getAllTenants(),
          modulesService.getAllModules()
        ]);

        // The API returns an array of objects, which is the correct format.
        // The previous mapping was incorrect and has been removed.
        const modulesData = modulesRawData;

        setTenants(tenantsData);
        setAvailableModules(modulesData);
        
        // This ensures that each input is a "controlled component" from the start,
        // fixing the issue of not being able to edit the text.
        const initialLabels = modulesData.reduce((acc, module) => {
          acc[module.module_key] = '';
          return acc;
        }, {});
        setCustomLabels(initialLabels);

      } catch (err) {
        setError(err.message || 'Error loading initial data.');
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleLabelChange = (e) => {
    const { name, value } = e.target;
    setCustomLabels(prev => ({ ...prev, [name]: value }));
  };

  const openPaymentModal = (tenant) => {
    setSelectedTenant(tenant);
    setShowPaymentModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setNotification({ message: '', type: '' });
    setLoading(true);
    try {
      const payload = { ...form, custom_labels: customLabels };
      await tenantsService.createTenant(payload);
      setNotification({ message: 'Tenant created successfully', type: 'success' });
      setForm({ tenant_name: '', admin_name: '', admin_email: '', admin_password: '' });
      
      // Reset labels to their initial (empty) state for the next form.
      const initialLabels = availableModules.reduce((acc, module) => {
        acc[module.module_key] = '';
        return acc;
      }, {});
      setCustomLabels(initialLabels);
      
      await fetchTenants(); // Reload the list
    } catch (err) {
      setNotification({ message: err.message, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (window.confirm(`Are you sure you want to delete the tenant "${name}"? This action is irreversible and will delete all its data.`)) {
      setNotification({ message: '', type: '' });
      setLoading(true);
      try {
        await tenantsService.deleteTenant(id);
        setNotification({ message: 'Tenant deleted successfully', type: 'success' });
        await fetchTenants(); // Reload the list
      } catch (err) {
        setNotification({ message: err.message, type: 'error' });
      } finally {
        setLoading(false);
      }
    }
  };

  const Notification = ({ message, type }) => {
    if (!message) return null;
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    return <div className={`alert ${alertClass}`}>{message}</div>;
  };

  return (
    <>
      <div className="tenants-container">
        <h2>Tenant Management</h2>
      
      <Notification message={notification.message} type={notification.type} />
      {error && <div className="alert alert-danger">{error}</div>}

      <div className="card mb-4">
        <div className="card-header">
          <h5>Create New Tenant and Administrator</h5>
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="row g-3" aria-busy={loading}>
            <div className="col-md-6">
              <input type="text" name="tenant_name" value={form.tenant_name} onChange={handleInputChange} className="form-control" placeholder="Organization Name" required />
            </div>
            <div className="col-md-6">
              <input type="text" name="admin_name" value={form.admin_name} onChange={handleInputChange} className="form-control" placeholder="Admin Name" required />
            </div>
            <div className="col-md-6">
              <input type="email" name="admin_email" value={form.admin_email} onChange={handleInputChange} className="form-control" placeholder="Admin Email" required />
            </div>
            <div className="col-md-6">
              <input type="password" name="admin_password" value={form.admin_password} onChange={handleInputChange} className="form-control" placeholder="Admin Password" required />
            </div>
            <div className="col-12 mt-4">
              <h6>Customize Module Labels:</h6>
              <div className="row">
                {availableModules.map(module => (
                  <div key={module.module_key} className="col-md-6 mb-3">
                    <label htmlFor={`label-for-${module.module_key}`} className="form-label fw-bold">
                      {module.label || module.module_key}
                    </label>
                    <div className="input-group">
                      <input
                        type="text"
                        className="form-control"
                        name={module.module_key}
                        id={`label-for-${module.module_key}`}
                        value={customLabels[module.module_key] || ''}
                        onChange={handleLabelChange}
                        placeholder={`Customize: ${module.label || module.module_key}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="col-12">
              <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Creating...' : 'Create Tenant'}</button>
            </div>
          </form>
        </div>
      </div>
      
      <div className="table-responsive">
        <table className="table table-striped table-hover">
          <thead className="thead-dark">
            <tr>
              <th>ID</th>
              <th>Organization Name</th>
              <th>Creation Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && tenants.length === 0 && <tr><td colSpan="4" className="text-center">Loading...</td></tr>}
            {tenants.map(tenant => (
              <tr key={tenant.id_tenant}>
                <td>{tenant.id_tenant}</td>
                <td>{tenant.nombre}</td>
                <td>{new Date(tenant.fecha_creacion).toLocaleDateString()}</td>
                <td className="d-flex gap-2">
                  <button 
                    className="btn btn-info btn-sm"
                    onClick={() => openPaymentModal(tenant)}
                    title="Manage Payments"
                  >
                    💰 Payments
                  </button>
                  <button 
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(tenant.id_tenant, tenant.nombre)}
                    disabled={loading}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      </div>
      {showPaymentModal && selectedTenant && (
        <PaymentManagerModal
          tenant={selectedTenant}
          onClose={() => setShowPaymentModal(false)}
        />
      )}
    </>
  );
}

export default TenantsList;
