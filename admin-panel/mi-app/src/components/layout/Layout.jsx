// src/components/layout/Layout.jsx
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import '../../styles/Layout.css';

const Layout = () => {
  const { user, logout } = useAuth();
  const [activeSection, setActiveSection] = useState('inicio');

  const sections = {
    inicio: { title: 'Inicio', component: <Inicio /> },
    usuarios: { title: 'Usuarios', component: <Usuarios /> },
    productos: { title: 'Productos', component: <Productos /> },
    pedidos: { title: 'Pedidos', component: <Pedidos /> },
    ingredientes: { title: 'Ingredientes', component: <Ingredientes /> },
    recetas: { title: 'Recetas', component: <Recetas /> }
  };

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>Sweetland Panel</h2>
        
        <nav>
          <ul className="nav-list">
            {Object.keys(sections).map(key => (
              <li key={key} className="nav-item">
                <button
                  onClick={() => setActiveSection(key)}
                  className={`nav-button ${activeSection === key ? 'active' : ''}`}
                >
                  {sections[key].title}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        <div className="user-section">
          <p>👋 Hola, {user.nombre}</p>
          <button 
            onClick={handleLogout}
            className="logout-button"
          >
            Cerrar Sesión
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <header style={{ marginBottom: '2rem' }}>
          <h1 style={{ color: '#2c3e50', margin: 0 }}>
            {sections[activeSection].title}
          </h1>
          <p style={{ color: '#7f8c8d', margin: 0 }}>
            Panel de administración - Sweetland By Anny
          </p>
        </header>

        <main className="content-card">
          {sections[activeSection].component}
        </main>
      </div>
    </div>
  );
};

// Componentes para cada sección
const Inicio = () => (
  <div>
    <h2>Bienvenido al Sistema</h2>
    <p>Selecciona una sección del menú para comenzar a gestionar.</p>
    
    <div className="dashboard-grid">
      <div className="grid-card card-usuarios">
        <h3>Usuarios</h3>
        <p>Gestiona clientes y empleados</p>
      </div>
      <div className="grid-card card-productos">
        <h3>Productos</h3>
        <p>Administra tortas y postres</p>
      </div>
      <div className="grid-card card-pedidos">
        <h3>Pedidos</h3>
        <p>Controla los pedidos</p>
      </div>
      <div className="grid-card card-ingredientes">
        <h3>Ingredientes</h3>
        <p>Gestiona inventario</p>
      </div>
    </div>
  </div>
);

const Usuarios = () => (
  <div>
    <h2>Gestión de Usuarios</h2>
    <p>Esta sección estará disponible pronto.</p>
  </div>
);

const Productos = () => (
  <div>
    <h2>Gestión de Productos</h2>
    <p>Esta sección estará disponible pronto.</p>
  </div>
);

const Pedidos = () => (
  <div>
    <h2>Gestión de Pedidos</h2>
    <p>Esta sección estará disponible pronto.</p>
  </div>
);

const Ingredientes = () => (
  <div>
    <h2>Gestión de Ingredientes</h2>
    <p>Esta sección estará disponible pronto.</p>
  </div>
);

const Recetas = () => (
  <div>
    <h2>Gestión de Recetas</h2>
    <p>Esta sección estará disponible pronto.</p>
  </div>
);

export default Layout;