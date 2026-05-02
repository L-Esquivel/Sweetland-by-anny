// src/services/api.js
const API_BASE = 'http://localhost:5000';

// Función básica para hacer peticiones al backend
const fetchAPI = async (endpoint, options = {}) => {
  const config = {
    credentials: 'include', // importante para las cookies de sesión
    headers: {
      'Content-Type': 'application/json',
    },
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