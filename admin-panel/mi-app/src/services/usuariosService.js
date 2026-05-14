// 🚀 URL del backend en producción (Render)
const API_URL = (import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com') + '/usuarios/';

export const usuariosService = {
  // Obtener todos los usuarios
  getUsuarios: async () => {
    const response = await fetch(API_URL, {
      credentials: 'include' // Para las cookies de autenticación
    });
    return await response.json();
  },

  // Obtener usuario por ID
  getUsuario: async (id) => {
    const response = await fetch(`${API_URL}/${id}`, {
      credentials: 'include'
    });
    return await response.json();
  },

  // Crear usuario
  createUsuario: async (usuarioData) => {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(usuarioData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Error ${response.status}`);
    }
    
    return await response.json();
  },

  // Actualizar usuario
  updateUsuario: async (id, usuarioData) => {
    const response = await fetch(`${API_URL}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(usuarioData)
    });
    return await response.json();
  },

  // Eliminar usuario
  deleteUsuario: async (id) => {
    const response = await fetch(`${API_URL}/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    return await response.json();
  }
};