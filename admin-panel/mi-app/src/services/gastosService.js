const BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';
const GASTOS_URL = `${BASE.replace(/\/$/, '')}/gastos`;

export const gastosService = {
  /**
   * Obtiene la lista de gastos, opcionalmente filtrada por mes y año.
   * @param {number} mes - El mes para filtrar (1-12).
   * @param {number} ano - El año para filtrar.
   * @returns {Promise<Array>} La lista de gastos.
   */
  async getGastos(mes, ano) {
    try {
      let url = GASTOS_URL;
      if (mes && ano) {
        const params = new URLSearchParams({ mes, ano });
        url += `?${params.toString()}`;
      }
      const response = await fetch(url, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar gastos');
      return await response.json();
    } catch (error) {
      console.error('Error en gastosService.getGastos:', error);
      throw error;
    }
  },

  /**
   * Crea un nuevo registro de gasto.
   * @param {object} gastoData - Los datos del gasto a crear.
   * @returns {Promise<object>} La respuesta del servidor.
   */
  async createGasto(gastoData) {
    try {
      const response = await fetch(GASTOS_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(gastoData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al crear el gasto');
      }
      return await response.json();
    } catch (error) {
      console.error('Error en gastosService.createGasto:', error);
      throw error;
    }
  },

  async deleteGasto(id) {
    const response = await fetch(`${GASTOS_URL}/${id}`, { method: 'DELETE', credentials: 'include' });
    if (!response.ok) throw new Error('Error al eliminar el gasto');
    return await response.json();
  }
};