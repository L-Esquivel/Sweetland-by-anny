const BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';
// Limpiamos posibles slashes duplicados
const API_URL = `${BASE.replace(/\/$/, '')}/empaques`;

export const empaquesService = {
  
  // ==================== 1. GESTIÓN DEL CATÁLOGO GENERAL ====================
  // (Se usará en la nueva pestaña de "Empaques" dentro de Insumos)

  async getEmpaques() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar el catálogo de empaques');
      return await response.json();
    } catch (error) {
      console.error('Error en getEmpaques:', error);
      throw error;
    }
  },

  async createEmpaque(empaqueData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(empaqueData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al crear empaque');
      }
      return await response.json();
    } catch (error) {
      console.error('Error en createEmpaque:', error);
      throw error;
    }
  },

  async updateEmpaque(id, empaqueData) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(empaqueData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al actualizar empaque');
      }
      return await response.json();
    } catch (error) {
      console.error('Error en updateEmpaque:', error);
      throw error;
    }
  },

  async deleteEmpaqueCatalogo(id) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) {
        const errorData = await response.json();
        // Esto capturará el error "En uso" que pusimos en el backend
        throw new Error(errorData.error || 'Error al eliminar empaque');
      }
      return await response.json();
    } catch (error) {
      console.error('Error en deleteEmpaqueCatalogo:', error);
      throw error;
    }
  },


  // ==================== 2. ASIGNACIÓN A PRODUCTOS (RECETAS) ====================
  // (Se usa dentro de la sección de Recetas)

  async getEmpaquesProducto(productoId) {
    try {
      const response = await fetch(`${API_URL}/producto/${productoId}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar empaques del producto');
      return await response.json();
    } catch (error) {
      console.error('Error en getEmpaquesProducto:', error);
      throw error;
    }
  },

  async addEmpaqueProducto(productoId, data) {
    try {
      const response = await fetch(`${API_URL}/producto/${productoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Error al asignar empaque al producto');
      return await response.json();
    } catch (error) {
      console.error('Error en addEmpaqueProducto:', error);
      throw error;
    }
  },

  async deleteEmpaqueProducto(id) {
    try {
      const response = await fetch(`${API_URL}/producto/item/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error al eliminar empaque del producto');
      return await response.json();
    } catch (error) {
      console.error('Error en deleteEmpaqueProducto:', error);
      throw error;
    }
  }
};