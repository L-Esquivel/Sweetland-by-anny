import React from 'react';
import SuperAdminDashboard from './dashboard/SuperAdminDashboard';
import TenantDashboard from './dashboard/TenantDashboard';

function Dashboard({ user }) {
  // Si el usuario es superadmin, muestra el dashboard de la plataforma.
  if (user?.rol === 'superadmin') {
    return <SuperAdminDashboard />;
  }
  
  // Para cualquier otro rol (ej. 'admin'), muestra el dashboard del tenant.
  return <TenantDashboard user={user} />;
}

export default Dashboard;