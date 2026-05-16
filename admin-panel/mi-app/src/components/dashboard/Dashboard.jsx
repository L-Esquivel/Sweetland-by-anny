import React from 'react';
import SuperAdminDashboard from './SuperAdminDashboard';
import TenantDashboard from './TenantDashboard';

function Dashboard({ user }) {
  // If the user is a superadmin, show the platform dashboard.
  if (user?.rol === 'superadmin') {
    return <SuperAdminDashboard />;
  }
  
  // For any other role (e.g., 'admin'), show the tenant dashboard.
  return <TenantDashboard user={user} />;
}

export default Dashboard;