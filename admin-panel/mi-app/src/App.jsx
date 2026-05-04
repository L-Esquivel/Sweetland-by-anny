import React, { useState, useEffect } from 'react';
import './App.css';
import UsuariosList from './components/usuarios/UsuariosList';
import Login from './components/Login';
import Register from './components/Register';
import ProductosList from './components/productos/ProductosList';
import PedidosList from './components/pedidos/PedidosList';
import InsumosPage from "./components/Insumos/InsumosPage";
import RecetasList from "./components/recetas/RecetasList";

const API_BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';

function App() {
  const [activeSection, setActiveSection] = useState('inicio');
  const [currentView, setCurrentView] = useState('login');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, { credentials: 'include' });
      if (response.ok) {
        const userData = await response.json();
        const usuario = userData.usuario || userData;
        
        // Bloqueamos SOLO a los clientes. Permitimos admin y empleado.
        if (usuario.rol === 'cliente') {
          await handleLogout();
          return;
        }
        
        setUser(usuario);
        setCurrentView('app');
      } else {
        setCurrentView('login');
      }
    } catch (error) {
      setCurrentView('login');
    } finally {
      setLoading(false);
    }
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
        
        setUser(usuario);
        setCurrentView('app');
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
      setUser(null);
      setCurrentView('login');
    }
  };

  const renderSection = () => {
    // Protección extra: Si un empleado intenta entrar a usuarios por consola
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
      case 'inicio':
      default:
        return (
          <div className="dashboard">
            <h2>Panel de Control - Sweetland By Anny</h2>
            <div className="welcome-message">
              <p>Bienvenido, <strong>{user?.nombre}</strong></p>
              <p>Rol: <span className="badge bg-info text-dark">{user?.rol?.toUpperCase()}</span></p>
            </div>
          </div>
        );
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;

  if (currentView === 'login' || currentView === 'register') {
    return (
      <div className="auth-container">
        {currentView === 'login' ? (
          <Login onLogin={handleLogin} onShowRegister={() => setCurrentView('register')} />
        ) : (
          <Register onShowLogin={() => setCurrentView('login')} />
        )}
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container-fluid">
          <span className="navbar-brand fs-3 fw-bold">🎂 Sweetland Admin</span>
          <div className="navbar-nav ms-auto">
            {user && (
              <div className="d-flex align-items-center gap-3">
                <span className="navbar-text text-white">
                  {user.nombre} <small className="d-block text-warning text-end">{user.rol}</small>
                </span>
                <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>🚪 Salir</button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="app-body">
        <nav className="sidebar bg-light">
          <ul className="nav nav-pills flex-column p-3">
            <li className="nav-item">
              <button className={`nav-link w-100 text-start ${activeSection === 'inicio' ? 'active' : ''}`} onClick={() => setActiveSection('inicio')}>📊 Inicio</button>
            </li>

            {/* SOLO ADMIN VE USUARIOS */}
            {user?.rol === 'admin' && (
              <li className="nav-item">
                <button className={`nav-link w-100 text-start ${activeSection === 'usuarios' ? 'active' : ''}`} onClick={() => setActiveSection('usuarios')}>👥 Usuarios</button>
              </li>
            )}

            <li className="nav-item">
              <button className={`nav-link w-100 text-start ${activeSection === 'productos' ? 'active' : ''}`} onClick={() => setActiveSection('productos')}>🎂 Productos</button>
            </li>
            <li className="nav-item">
              <button className={`nav-link w-100 text-start ${activeSection === 'pedidos' ? 'active' : ''}`} onClick={() => setActiveSection('pedidos')}>📦 Pedidos</button>
            </li>
            <li className="nav-item">
              <button className={`nav-link w-100 text-start ${activeSection === 'insumos' ? 'active' : ''}`} onClick={() => setActiveSection('insumos')}>📦 Insumos</button>
            </li>

            {/* SOLO ADMIN VE RECETAS (Finanzas/Margen) */}
            {user?.rol === 'admin' && (
              <li className="nav-item">
                <button className={`nav-link w-100 text-start ${activeSection === 'recetas' ? 'active' : ''}`} onClick={() => setActiveSection('recetas')}>📋 Recetas y Costos</button>
              </li>
            )}
          </ul>
        </nav>

        <main className="main-content p-4">
          {renderSection()}
        </main>
      </div>
    </div>
  );
}

export default App;