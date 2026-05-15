import React, { useState, useEffect } from 'react';
// FIX: Ruta ajustada a la ubicación actual del archivo.
import { tenantsService } from '../../services/tenantsService';
import { modulesService } from '../../services/modulesService';
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

  const fetchTenants = async () => {
    try {
      setLoading(true);
      const data = await tenantsService.getAllTenants();
      setTenants(data);
      setError('');
    } catch (err) {
      setError(err.message || 'Error al cargar los tenants');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      try {
        const [tenantsData, modulesData] = await Promise.all([
          tenantsService.getAllTenants(),
          modulesService.getAllModules()
        ]);
        setTenants(tenantsData);
        setAvailableModules(modulesData);
        // Pre-llenar las etiquetas personalizadas con los valores por defecto
        const initialLabels = {};
        modulesData.forEach(m => {
            initialLabels[m.module_key] = m.label;
        });
        setCustomLabels(initialLabels);
      } catch (err) {
        setError(err.message || 'Error al cargar datos iniciales.');
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleLabelChange = (e) => {
    const { name, value } = e.target;
    // El 'name' del input será la 'module_key', permitiendo actualizar el estado correctamente.
    setCustomLabels(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setNotification({ message: '', type: '' }); // Limpiar notificaciones previas
    setLoading(true);
    try {
      const payload = { ...form, custom_labels: customLabels };
      await tenantsService.createTenant(payload);
      setNotification({ message: 'Tenant creado con éxito', type: 'success' });
      setForm({ tenant_name: '', admin_name: '', admin_email: '', admin_password: '' });
      // Resetear etiquetas a los valores por defecto
      const initialLabels = {};
      availableModules.forEach(m => { initialLabels[m.module_key] = m.label; });
      setCustomLabels(initialLabels);
      fetchTenants(); // Recargar la lista
    } catch (err) {
      setNotification({ message: err.message, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar el tenant "${name}"? Esta acción es irreversible y borrará todos sus datos.`)) {
      setNotification({ message: '', type: '' });
      setLoading(true);
      try {
        await tenantsService.deleteTenant(id);
        setNotification({ message: 'Tenant eliminado con éxito', type: 'success' });
        fetchTenants(); // Recargar la lista
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
    <div className="tenants-container">
      <h2>Gestión de Tenants</h2>
      
      <Notification message={notification.message} type={notification.type} />
      {error && <div className="alert alert-danger">{error}</div>}

      <div className="card mb-4">
        <div className="card-header">
          <h5>Crear Nuevo Tenant y Administrador</h5>
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit} className="row g-3" aria-busy={loading}>
            <div className="col-md-6">
              <input type="text" name="tenant_name" value={form.tenant_name} onChange={handleInputChange} className="form-control" placeholder="Nombre de la Organización" required />
            </div>
            <div className="col-md-6">
              <input type="text" name="admin_name" value={form.admin_name} onChange={handleInputChange} className="form-control" placeholder="Nombre del Admin" required />
            </div>
            <div className="col-md-6">
              <input type="email" name="admin_email" value={form.admin_email} onChange={handleInputChange} className="form-control" placeholder="Email del Admin" required />
            </div>
            <div className="col-md-6">
              <input type="password" name="admin_password" value={form.admin_password} onChange={handleInputChange} className="form-control" placeholder="Contraseña del Admin" required />
            </div>
            <div className="col-12 mt-4">
              <h6>Personalizar Etiquetas de Módulos:</h6>
              <div className="row">
                {availableModules.map(module => (
                  <div key={module.module_key} className="col-md-6 mb-3">
                    {/* 💡 FIX 1: Etiqueta de referencia más visible y robusta. */}
                    <label htmlFor={`label-${module.module_key}`} className="form-label fw-bold">
                      {module.icon} {module.label || module.module_key}
                    </label>
                    <div className="input-group">
                      <input
                        type="text"
                        className="form-control"
                        name={module.module_key}
                        id={`label-${module.module_key}`}
                        // 💡 FIX 2: Aseguramos que el valor siempre sea un string para evitar el bug.
                        value={String(customLabels[module.module_key] || '')}
                        onChange={handleLabelChange}
                        placeholder={`Personalizar "${module.label || 'Módulo'}"...`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="col-12">
              <button type="submit" className="btn btn-primary" disabled={loading}>{loading ? 'Creando...' : 'Crear Tenant'}</button>
            </div>
          </form>
        </div>
      </div>
      
      <div className="table-responsive">
        <table className="table table-striped table-hover">
          <thead className="thead-dark">
            <tr>
              <th>ID</th>
              <th>Nombre de la Organización</th>
              <th>Fecha de Creación</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading && tenants.length === 0 && <tr><td colSpan="4" className="text-center">Cargando...</td></tr>}
            {tenants.map(tenant => (
              <tr key={tenant.id_tenant}>
                <td>{tenant.id_tenant}</td>
                <td>{tenant.nombre}</td>
                <td>{new Date(tenant.fecha_creacion).toLocaleDateString()}</td>
                <td>
                  <button 
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(tenant.id_tenant, tenant.nombre)}
                    disabled={loading}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TenantsList;