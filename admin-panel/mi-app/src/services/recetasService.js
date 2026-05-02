// src/services/recetasService.js
const API_URL = 'http://localhost:5000';

export const recetasService = {
  // Obtener todas las recetas
  async getRecetas() {
    try {
      const response = await fetch(`${API_URL}/recetas`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar recetas');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.getRecetas:', error);
      throw error;
    }
  },

  // Obtener recetas por producto
  async getRecetasPorProducto(productoId) {
    try {
      const response = await fetch(`${API_URL}/recetas/producto/${productoId}`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar recetas del producto');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.getRecetasPorProducto:', error);
      throw error;
    }
  },

  // Obtener costo de producción
  async getCostoProduccion(productoId) {
    try {
      const response = await fetch(`${API_URL}/recetas/costo-produccion/${productoId}`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al calcular costo de producción');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.getCostoProduccion:', error);
      throw error;
    }
  },

  // src/services/recetasService.js - MODIFICA la función createReceta:

async createReceta(recetaData) {
  try {
    console.log('🔍 Enviando datos al backend:', recetaData);
    
    const response = await fetch(`${API_URL}/recetas`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(recetaData)
    });
    
    console.log('🔍 Respuesta del servidor - Status:', response.status);
    
    if (!response.ok) {
      let errorMessage = `Error ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
        console.error('🔍 Error del servidor:', errorData);
      } catch (e) {
        console.error('🔍 No se pudo parsear error del servidor');
      }
      throw new Error(errorMessage);
    }
    
    const result = await response.json();
    console.log('🔍 Receta creada exitosamente:', result);
    return result;
    
  } catch (error) {
    console.error('❌ Error en recetasService.createReceta:', error);
    
    // Mensajes más específicos según el tipo de error
    if (error.message.includes('Failed to fetch')) {
      throw new Error('No se pudo conectar con el servidor. Verifica que el backend esté corriendo.');
    }
    
    throw error;
  }
},

  // Crear múltiples recetas
  async createRecetasMultiples(productoId, ingredientes) {
    try {
      const response = await fetch(`${API_URL}/recetas/multiple`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          id_producto: productoId,
          ingredientes: ingredientes
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al crear recetas');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.createRecetasMultiples:', error);
      throw error;
    }
  },

  // Actualizar receta
  async updateReceta(recetaId, recetaData) {
    try {
      const response = await fetch(`${API_URL}/recetas/${recetaId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(recetaData)
      });
      
      if (!response.ok) {
        throw new Error('Error al actualizar receta');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.updateReceta:', error);
      throw error;
    }
  },

  // Eliminar receta
  async deleteReceta(recetaId) {
    try {
      const response = await fetch(`${API_URL}/recetas/${recetaId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al eliminar receta');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.deleteReceta:', error);
      throw error;
    }
  },

  // Eliminar todas las recetas de un producto
  async deleteRecetasProducto(productoId) {
    try {
      const response = await fetch(`${API_URL}/recetas/producto/${productoId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al eliminar recetas del producto');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en recetasService.deleteRecetasProducto:', error);
      throw error;
    }
  }
};