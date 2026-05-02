const API_URL = 'http://localhost:5000/productos';

export const productosService = {
  // Obtener todos los productos
  getProductos: async () => {
    const response = await fetch(API_URL, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        window.location.reload();
        throw new Error('No autenticado');
      }
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  },

  // Obtener producto por ID
  getProducto: async (id) => {
    const response = await fetch(`${API_URL}/${id}`, {
      credentials: 'include'
    });
    return await response.json();
  },

  // Crear producto
  createProducto: async (productoData) => {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(productoData)
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  },

  // Actualizar producto
  updateProducto: async (id, productoData) => {
    const response = await fetch(`${API_URL}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(productoData)
    });
    return await response.json();
  },

  // Eliminar producto
  deleteProducto: async (id) => {
    const response = await fetch(`${API_URL}/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    return await response.json();
  }
};