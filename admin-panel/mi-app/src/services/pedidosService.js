// 🚀 Backend URL
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
// Ensure the base URL doesn't end with a slash to avoid duplicates
const API_URL = `${BASE.replace(/\/$/, '')}/pedidos`;
const DETAILS_API_URL = `${BASE.replace(/\/$/, '')}/detalle_pedidos`;

export const pedidosService = {

  // ==================== ORDERS ====================

  async getOrders() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading orders');
      return await response.json();
    } catch (error) {
      console.error('Error in pedidosService.getOrders:', error);
      throw error;
    }
  },

  async getOrderDetails(orderId) {
    try {
      // The backend now has a dedicated, more efficient endpoint for this
      const response = await fetch(`${DETAILS_API_URL}/pedido/${orderId}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading order details');
      return await response.json();
    } catch (error) {
      console.error('Error in pedidosService.getOrderDetails:', error);
      throw error;
    }
  },

  async createOrder(orderData) {
    try {
      const response = await fetch(`${API_URL}/`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(orderData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error in pedidosService.createOrder:', error);
      throw error;
    }
  },

  async updateOrder(orderId, orderData) {
    try {
      const response = await fetch(`${API_URL}/${orderId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(orderData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error in pedidosService.updateOrder:', error);
      throw error;
    }
  },

  async updateOrderStatus(orderId, newStatus) {
    try {
      const response = await fetch(`${API_URL}/${orderId}/estado`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ estado: newStatus })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error in pedidosService.updateOrderStatus:', error);
      throw error;
    }
  },

  async deleteOrder(orderId) {
    try {
      const response = await fetch(`${API_URL}/${orderId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error deleting order');
      return await response.json();
    } catch (error) {
      console.error('Error in pedidosService.deleteOrder:', error);
      throw error;
    }
  },

  // ==================== ORDER ITEMS (DETAILS) ====================

  async addOrderItem(itemData) {
    try {
      // This endpoint creates a single order item.
      const response = await fetch(`${DETAILS_API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(itemData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error in pedidosService.addOrderItem:', error);
      throw error;
    }
  },

  async deleteOrderItem(itemId) {
    try {
      const response = await fetch(`${DETAILS_API_URL}/${itemId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error deleting order item');
      return await response.json();
    } catch (error) {
      console.error('Error in pedidosService.deleteOrderItem:', error);
      throw error;
    }
  },

  // ==================== STATISTICS ====================

  async getStats(startDate, endDate) {
    try {
      let url = `${API_URL}/stats`;
      
      // If dates are provided, add them as query parameters
      if (startDate && endDate) {
        const params = new URLSearchParams({
          fecha_inicio: startDate, // Backend expects 'fecha_inicio'
          fecha_fin: endDate,       // and 'fecha_fin'
        });
        url += `?${params.toString()}`;
      }

      const response = await fetch(url, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading statistics');
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.getStats:', error);
      throw error;
    }
  }
};
