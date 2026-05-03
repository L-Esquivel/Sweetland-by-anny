// src/services/api.js
const API_BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';

// Función básica para hacer peticiones al backend
const fetchAPI = async (endpoint, options = {}) => {
  // Asegurar slash al final si no tiene (evita redirects a HTTP)
  if (endpoint && !endpoint.endsWith('/')) {
    endpoint = endpoint + '/';
  }

  const config = {
    credentials: 'include', // importante para las cookies de sesión
    headers: {
      'Content-Type': 'application/json',
    },
    redirect: 'follow',     // sigue redirects automáticamente
    ...options,
  };

  if (options.body) {
    config.body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Error en la petición');
    }
    
    return data;
  } catch (error) {
    throw new Error(error.message || 'Error de conexión');
  }
};

// Solo endpoints de autenticación por ahora
export const authAPI = {
  login: (email, password) => 
    fetchAPI('/auth/login', {
      method: 'POST',
      body: { email, password }
    }),
  
  register: (userData) =>
    fetchAPI('/auth/registrarse', {
      method: 'POST',
      body: userData
    })
};

export default fetchAPI;