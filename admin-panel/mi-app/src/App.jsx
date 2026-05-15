import React, { useState, useEffect } from 'react';
import './App.css';
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

// 🚀 URL del backend en producción (Render)
const API_BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';

function App() {
  const [activeSection, setActiveSection] = useState('inicio');
  
  // 1. Inicializamos el estado intentando leer del localStorage para evitar el salto al Login al recargar
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('sweetland_admin_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [isLoggedIn, setIsLoggedIn] = useState(!!user);

  const [loading, setLoading] = useState(true);
  const [showSupportModal, setShowSupportModal] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, { credentials: 'include' });
      if (response.ok) {
        const userData = await response.json();
        const usuario = userData.usuario || userData;
        
        if (usuario.rol === 'cliente') {
          await handleLogout();
          return;
        }
        
        // 2. Sincronizamos el estado de React con la respuesta real del servidor
        setUser(usuario);
        setIsLoggedIn(true);
        localStorage.setItem('sweetland_admin_user', JSON.stringify(usuario));
      } else {
        // Si el servidor dice que no estamos autorizados, limpiamos todo
        limpiarSesionLocal();
      }
    } catch (error) {
      console.log('Error en checkAuth:', error);
      // En caso de error de red, mantenemos lo que hay en localStorage (opcional)
    } finally {
      setLoading(false);
    }
  };

  const limpiarSesionLocal = () => {
    setUser(null);
    setIsLoggedIn(false);
    localStorage.removeItem('sweetland_admin_user');
  };

  const handleLogin = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const data = await response.json();
        const usuario = data.usuario;
        
        if (usuario.rol === 'cliente') {
          await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' });
          return { success: false, error: '❌ Acceso denegado al panel administrativo.' };
        }
        
        // Guardamos en local para persistencia al recargar
        localStorage.setItem('sweetland_admin_user', JSON.stringify(usuario));
        setUser(usuario);
        setIsLoggedIn(true);
        return { success: true, user: usuario };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error };
      }
    } catch (error) {
      return { success: false, error: 'Error de conexión' };
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' });
    } finally {
      limpiarSesionLocal();
    }
  };

  const renderSection = () => {
    if (activeSection === 'usuarios' && user?.rol !== 'admin') {
      setActiveSection('inicio');
      return null;
    }

    switch (activeSection) {
      case 'usuarios': return <UsuariosList />;
      case 'productos': return <ProductosList />;
      case 'pedidos': return <PedidosList />;
      case 'insumos': return <InsumosPage />;
      case 'recetas': return <RecetasList />;
      case 'gastos': return <GastosList />;
      case 'merma': return <MermaList />;
      case 'tenants': return <TenantsList />; // 2. Añadimos el nuevo caso
      case 'inicio': return <Dashboard user={user} />;
      default: return <Dashboard user={user} />;
    }
  };

  if (loading && !user) return <div className="loading">Verificando sesión...</div>;

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      {/* Header ahora usa clases de App.css */}
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
                <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>🚪 Salir</button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Sidebar ahora usa clases de App.css */}
      <div className="app-body">
        <nav className="sidebar">
          <ul className="nav nav-pills flex-column p-3">
            <li className="nav-item">
              <button className={`nav-link w-100 text-start ${activeSection === 'inicio' ? 'active' : ''}`} onClick={() => setActiveSection('inicio')}>📊 Inicio / Dashboard</button>
            </li>

            {/* 3. Botón visible solo para Super Admin */}
            {user?.rol === 'superadmin' && (
              <li className="nav-item">
                <button className={`nav-link w-100 text-start ${activeSection === 'tenants' ? 'active' : ''}`} onClick={() => setActiveSection('tenants')}>🏢 Tenants</button>
              </li>
            )}
            
            {/* 4. Botones visibles solo para Admin de Tenant */}
            {user?.rol === 'admin' && (
              <>
                {/* Renderizado dinámico del menú basado en la configuración de módulos del tenant */}
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
                  <button className="nav-link w-100 text-start" onClick={() => setShowSupportModal(true)}>❓ Soporte</button>
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