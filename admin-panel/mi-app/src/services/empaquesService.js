const BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';
const API_URL = `${BASE}/empaques`;

export const empaquesService = {
  async getEmpaques() {
    const response = await fetch(`${API_URL}/`, { credentials: 'include' });
    if (!response.ok) throw new Error('Error al cargar empaques');
    return await response.json();
  },

  async getEmpaquesProducto(productoId) {
    const response = await fetch(`${API_URL}/producto/${productoId}`, { credentials: 'include' });
    if (!response.ok) throw new Error('Error al cargar empaques del producto');
    return await response.json();
  },

  async addEmpaque(productoId, data) {
    const response = await fetch(`${API_URL}/producto/${productoId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Error al agregar empaque');
    return await response.json();
  },

  async deleteEmpaque(id) {
    const response = await fetch(`${API_URL}/producto/item/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    if (!response.ok) throw new Error('Error al eliminar empaque');
    return await response.json();
  }
};