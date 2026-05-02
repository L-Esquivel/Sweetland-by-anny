import React, { useState, useEffect } from 'react';
import './App.css';
import UsuariosList from './components/usuarios/UsuariosList';
import Login from './components/Login';
import Register from './components/Register';
import ProductosList from './components/productos/ProductosList';
import PedidosList from './components/pedidos/PedidosList';
import IngredientesList from "./components/ingredientes/IngredientesList";
import RecetasList from "./components/recetas/RecetasList";

function App() {
  const [activeSection, setActiveSection] = useState('inicio');
  const [currentView, setCurrentView] = useState('login');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  // DEBUG: Ver estado del usuario
  useEffect(() => {
    console.log('User state:', user);
    console.log('Current view:', currentView);
  }, [user, currentView]);

  const checkAuth = async () => {
    try {
      const response = await fetch('http://localhost:5000/auth/me', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const userData = await response.json();
        const usuario = userData.usuario || userData;
        
        // ✅ VERIFICAR SI ES ADMIN AL CARGAR LA APP
        if (usuario.rol !== 'admin') {
          console.log('❌ Cliente detectado en checkAuth, bloqueando acceso');
          await handleLogout();
          setCurrentView('login');
          return;
        }
        
        setUser(usuario);
        setCurrentView('app');
      } else {
        setCurrentView('login');
      }
    } catch (error) {
      console.log('Error en checkAuth:', error);
      setCurrentView('login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (email, password) => {
    try {
      const response = await fetch('http://localhost:5000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        const data = await response.json();
        const usuario = data.usuario;
        
        // ✅ VERIFICAR SI ES ADMIN DESPUÉS DEL LOGIN
        if (usuario.rol !== 'admin') {
          console.log('❌ Cliente detectado, bloqueando acceso al panel');
          // Cerrar sesión inmediatamente
          await fetch('http://localhost:5000/auth/logout', {
            method: 'POST',
            credentials: 'include'
          });
          return { 
            success: false, 
            error: '❌ Acceso denegado. Solo personal autorizado puede acceder al panel administrativo.' 
          };
        }
        
        // ✅ ES ADMIN - Permitir acceso
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
      await fetch('http://localhost:5000/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      setUser(null);
      setCurrentView('login');
    }
  };

  const renderSection = () => {
    switch (activeSection) {
      case 'usuarios':
        return <UsuariosList />;
      case 'productos':
        return <ProductosList />;
      case 'pedidos':
        return <PedidosList />;
      case 'ingredientes':
        return <IngredientesList />;
      case 'recetas':
        return <RecetasList />;
      case 'inicio':
      default:
        return (
          <div className="dashboard">
            <h2>Panel de Administración - Sweetland By Anny</h2>
            <div className="welcome-message">
              <p>Bienvenido{user ? `, ${user.nombre}` : ''} al sistema de administración de Sweetland by Anny</p>
              <p>Selecciona una sección del menú para comenzar</p>
            </div>
          </div>
        );
    }
  };

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  if (currentView === 'login' || currentView === 'register') {
    return (
      <div className="auth-container">
        {currentView === 'login' ? (
          <Login 
            onLogin={handleLogin}
            onShowRegister={() => setCurrentView('register')}
          />
        ) : (
          <Register 
            onShowLogin={() => setCurrentView('login')}
          />
        )}
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container-fluid">
          <span className="navbar-brand fs-3 fw-bold">🎂 Sweetland by Anny Panel Administrativo</span>
          
          <div className="navbar-nav ms-auto">
            {user ? (
              <div className="d-flex align-items-center gap-3">
                <span className="navbar-text text-white">
                  👋 Hola, {user.nombre} 
                  <small className="d-block text-warning">👑 Administrador</small>
                </span>
                <button 
                  className="btn btn-outline-light btn-sm"
                  onClick={handleLogout}
                >
                  🚪 Cerrar Sesión
                </button>
              </div>
            ) : (
              <button 
                className="btn btn-outline-light btn-sm"
                onClick={() => setCurrentView('login')}
              >
                🔑 Iniciar Sesión
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="app-body">
        <nav className="sidebar bg-light">
          <ul className="nav nav-pills flex-column p-3">
            <li className="nav-item">
              <button 
                className={`nav-link w-100 text-start ${activeSection === 'inicio' ? 'active' : ''}`}
                onClick={() => setActiveSection('inicio')}
              >
                📊 Inicio
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link w-100 text-start ${activeSection === 'usuarios' ? 'active' : ''}`}
                onClick={() => setActiveSection('usuarios')}
              >
                👥 Usuarios
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link w-100 text-start ${activeSection === 'productos' ? 'active' : ''}`}
                onClick={() => setActiveSection('productos')}
              >
                🎂 Productos
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link w-100 text-start ${activeSection === 'pedidos' ? 'active' : ''}`}
                onClick={() => setActiveSection('pedidos')}
              >
                📦 Pedidos
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link w-100 text-start ${activeSection === 'ingredientes' ? 'active' : ''}`}
                onClick={() => setActiveSection('ingredientes')}
              >
                🧂 Ingredientes
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link w-100 text-start ${activeSection === 'recetas' ? 'active' : ''}`}
                onClick={() => setActiveSection('recetas')}
              >
                📋 Recetas
              </button>
            </li>
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