import React, { useState } from 'react';
import './App.css';
import { useAuth } from './context/AuthContext';
import UsuariosList from './components/usuarios/UsuariosList';
import Login from './components/Login';
import ProductosList from './components/productos/ProductosList';
import PedidosList from './components/pedidos/PedidosList';
import InsumosPage from "./components/Insumos/InsumosPage";
import RecetasList from "./components/recetas/RecetasList";
import Dashboard from './components/Dashboard';
import GastosList from './components/gastos/GastosList';
import MermaList from './components/merma/MermaList';
import TenantsList from './components/tenants/TenantsList';
import SupportModal from './components/support/SupportModal';

function App() {
  const [activeSection, setActiveSection] = useState('inicio');
  const { user, isAuthenticated, loading, logout } = useAuth();
  const [showSupportModal, setShowSupportModal] = useState(false);

  const renderSection = () => {
    switch (activeSection) {
      case 'usuarios': return <UsuariosList />;
      case 'productos': return <ProductosList />;
      case 'pedidos': return <PedidosList />;
      case 'insumos': return <InsumosPage />;
      case 'recetas': return <RecetasList />;
      case 'gastos': return <GastosList />;
      case 'merma': return <MermaList />;
      case 'tenants': return <TenantsList />;
      case 'inicio': return <Dashboard user={user} />;
      default: return <Dashboard user={user} />;
    }
  };

  if (loading) {
    return <div className="loading">Verifying session...</div>;
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <div className="app">
      <header className="app-header navbar navbar-expand-lg navbar-dark">
        <div className="container-fluid">
          <a className="navbar-brand d-flex align-items-center" href="#" onClick={() => setActiveSection('inicio')}>
            <img src="/logo-precivox.png" alt="Precivox Logo" className="header-logo" />
          </a>
          <div className="navbar-nav ms-auto">
            {user && (
              <div className="d-flex align-items-center gap-3">
                <span className="navbar-text text-white">
                  {user.nombre} <small className="d-block text-warning text-end">{user.rol?.toUpperCase()}</small>
                </span>
                <button className="btn btn-outline-light btn-sm" onClick={logout}>🚪 Logout</button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="app-body">
        <nav className="sidebar">
          <ul className="nav nav-pills flex-column p-3">
            <li className="nav-item">
              <button className={`nav-link w-100 text-start ${activeSection === 'inicio' ? 'active' : ''}`} onClick={() => setActiveSection('inicio')}>📊 Home / Dashboard</button>
            </li>

            {/* Button visible only for Super Admin */}
            {user?.rol === 'superadmin' && (
              <li className="nav-item">
                <button className={`nav-link w-100 text-start ${activeSection === 'tenants' ? 'active' : ''}`} onClick={() => setActiveSection('tenants')}>🏢 Tenants</button>
              </li>
            )}
            
            {/* Buttons visible only for Tenant Admin */}
            {user?.rol === 'admin' && (
              <>
                {/* Dynamic menu rendering based on tenant module settings */}
                {user.module_settings && user.module_settings.map(module => (
                  <li className="nav-item" key={module.module_key}>
                    <button 
                      className={`nav-link w-100 text-start ${activeSection === module.module_key ? 'active' : ''}`} 
                      onClick={() => setActiveSection(module.module_key)}
                    >
                      {module.icon} {module.label}
                    </button>
                  </li>
                ))}
                <hr className="text-white-50" />
                <li className="nav-item">
                  <button className="nav-link w-100 text-start" onClick={() => setShowSupportModal(true)}>❓ Support</button>
                </li>
              </>
            )}
          </ul>
        </nav>

        <main className="main-content p-4">
          {renderSection()}
        </main>

        <SupportModal show={showSupportModal} onClose={() => setShowSupportModal(false)} />
      </div>
    </div>
  );
}

export default App;