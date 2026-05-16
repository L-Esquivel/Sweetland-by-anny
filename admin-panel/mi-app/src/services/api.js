// src/services/api.js
// 🚀 Backend URL for production
const API_BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';

// Basic function to make requests to the backend
const fetchAPI = async (endpoint, options = {}) => {
  // Ensure a trailing slash if it doesn't have one (prevents redirects to HTTP)
  if (endpoint && !endpoint.endsWith('/')) {
    endpoint = endpoint + '/';
  }

  const config = {
    credentials: 'include', // important for session cookies
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
      throw new Error(data.error || 'Request Error');
    }
    
    return data;
  } catch (error) {
    throw new Error(error.message || 'Connection Error');
  }
};

// Authentication endpoints, used by AuthContext
export const authAPI = {
  login: (email, password) => 
    fetchAPI('/auth/login', {
      method: 'POST',
      body: { email, password }
    }),
  
  // This is for the public customer registration
  register: (userData) =>
    fetchAPI('/auth/public/register', {
      method: 'POST',
      body: userData
    }),

  logout: () => 
    fetchAPI('/auth/logout', {
      method: 'POST'
    }),

  // Gets the current user from the server session
  me: () => fetchAPI('/auth/me')
};

export default fetchAPI;