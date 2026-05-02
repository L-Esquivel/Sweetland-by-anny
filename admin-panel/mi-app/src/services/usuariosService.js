const API_URL = 'http://localhost:5000/usuarios';

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
  console.log('Enviando al backend:', usuarioData); // ← AGREGAR
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(usuarioData)
  });
  
  console.log('Respuesta del servidor - Status:', response.status); // ← AGREGAR
  console.log('Respuesta del servidor - OK:', response.ok); // ← AGREGAR
  
  if (!response.ok) {
    const errorText = await response.text();
    console.error('Error del servidor:', errorText); // ← AGREGAR
    throw new Error(`Error ${response.status}: ${errorText}`);
  }
  
  const result = await response.json();
  console.log('Respuesta exitosa:', result); // ← AGREGAR
  return result;
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