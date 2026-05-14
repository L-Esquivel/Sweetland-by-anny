// 🚀 URL del backend en producción (Render)
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const MERMA_URL = `${BASE.replace(/\/$/, '')}/merma`;

export const mermaService = {
  async getMermaRegistros() {
    try {
      const response = await fetch(MERMA_URL, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar registros de merma');
      return await response.json();
    } catch (error) {
      console.error('Error en mermaService.getMermaRegistros:', error);
      throw error;
    }
  },

  async createMermaRegistro(mermaData) {
    try {
      const response = await fetch(MERMA_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(mermaData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al crear el registro de merma');
      }
      return await response.json();
    } catch (error) {
      console.error('Error en mermaService.createMermaRegistro:', error);
      throw error;
    }
  },

  async deleteMermaRegistro(id) {
    const response = await fetch(`${MERMA_URL}/${id}`, { method: 'DELETE', credentials: 'include' });
    if (!response.ok) throw new Error('Error al eliminar el registro de merma');
    return await response.json();
  }
};