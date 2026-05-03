const BASE = import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app';
const API_URL = `${BASE}/pedidos`;
const USUARIOS_URL = `${BASE}/usuarios`;

export const pedidosService = {

  // ==================== PEDIDOS ====================

  async getPedidos() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar pedidos');
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.getPedidos:', error);
      throw error;
    }
  },

  async getDetallesPedido(pedidoId) {
    try {
      const response = await fetch(`${API_URL}/${pedidoId}/detalles`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar detalles del pedido');
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.getDetallesPedido:', error);
      throw error;
    }
  },

  async createPedido(pedidoData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(pedidoData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.createPedido:', error);
      throw error;
    }
  },

  async updatePedido(pedidoId, pedidoData) {
    try {
      const response = await fetch(`${API_URL}/${pedidoId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(pedidoData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.updatePedido:', error);
      throw error;
    }
  },

  async updateEstadoPedido(pedidoId, nuevoEstado) {
    try {
      const response = await fetch(`${API_URL}/${pedidoId}/estado`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ estado: nuevoEstado })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.updateEstadoPedido:', error);
      throw error;
    }
  },

  async deletePedido(pedidoId) {
    try {
      const response = await fetch(`${API_URL}/${pedidoId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error al eliminar pedido');
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.deletePedido:', error);
      throw error;
    }
  },

  async createDetallePedidoAlternativo(pedidoId, detalleData) {
    try {
      const response = await fetch(`${API_URL}/${pedidoId}/agregar_detalle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(detalleData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.createDetallePedidoAlternativo:', error);
      throw error;
    }
  },

  // ==================== USUARIOS (para formulario de pedidos) ====================

  async getUsuarios() {
    try {
      const response = await fetch(`${USUARIOS_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error al cargar usuarios');
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.getUsuarios:', error);
      throw error;
    }
  },

  async createUsuario(usuarioData) {
    try {
      const response = await fetch(`${API_URL}/usuarios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(usuarioData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.createUsuario:', error);
      throw error;
    }
  }
};