import React, { useState, useEffect } from 'react';
import './App.css';
import UsuariosList from './components/usuarios/UsuariosList';
import Login from './components/Login';
import Register from './components/Register';
import ProductosList from './components/productos/ProductosList';
import PedidosList from './components/pedidos/PedidosList';
import InsumosPage from "./components/Insumos/InsumosPage";
import RecetasList from "./components/recetas/RecetasList";
import Dashboard from './components/Dashboard';
import GastosList from './components/gastos/GastosList';
import MermaList from './components/merma/MermaList';

const API_BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';

function App() {
  const [activeSection, setActiveSection] = useState('inicio');
  
  // 1. Inicializamos el estado intentando leer del localStorage para evitar el salto al Login al recargar
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('sweetland_admin_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [currentView, setCurrentView] = useState(() => {
    return localStorage.getItem('sweetland_admin_user') ? 'app' : 'login';
  });

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
        
        if (usuario.rol === 'cliente') {
          await handleLogout();
          return;
        }
        
        // 2. Sincronizamos el estado de React con la respuesta real del servidor
        setUser(usuario);
        setCurrentView('app');
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
    setCurrentView('login');
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
      case 'inicio': return <Dashboard user={user} />;
      default: return <Dashboard user={user} />;
    }
  };

  if (loading && !user) return <div className="loading">Verificando sesión...</div>;

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
      {/* Header con el nuevo color Azul Navy y estilos en línea */}
      <header className="app-header navbar navbar-expand-lg navbar-dark" style={{ backgroundColor: '#0A192F', padding: '0.5rem 2rem' }}>
        <div className="container-fluid">
          <a className="navbar-brand d-flex align-items-center" href="#" onClick={() => setActiveSection('inicio')}>
            <img src="/logo-precivox.png" alt="Precivox Logo" style={{ height: '50px', marginRight: '10px' }} />
            <span className="fs-4 fw-bold">Precivox</span>
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

      {/* Sidebar con el nuevo color Azul Navy y estilos en línea */}
      <div className="app-body">
        {/* Se elimina bg-light para que el estilo en línea tome precedencia */}
        <nav className="sidebar" style={{ backgroundColor: '#0A192F', color: '#ccd6f6' }}>
          <ul className="nav nav-pills flex-column p-3">
            <li className="nav-item">
              <button className={`nav-link w-100 text-start ${activeSection === 'inicio' ? 'active' : ''}`} onClick={() => setActiveSection('inicio')}>📊 Inicio / Dashboard</button>
            </li>

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

            {user?.rol === 'admin' && (
              <li className="nav-item">
                <button className={`nav-link w-100 text-start ${activeSection === 'recetas' ? 'active' : ''}`} onClick={() => setActiveSection('recetas')}>📋 Recetas y Costos</button>
              </li>
            )}

            {user?.rol === 'admin' && (
              <li className="nav-item">
                <button className={`nav-link w-100 text-start ${activeSection === 'gastos' ? 'active' : ''}`} onClick={() => setActiveSection('gastos')}>💸 Gastos</button>
              </li>
            )}

            {user?.rol === 'admin' && (
              <li className="nav-item">
                <button className={`nav-link w-100 text-start ${activeSection === 'merma' ? 'active' : ''}`} onClick={() => setActiveSection('merma')}>📉 Merma</button>
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