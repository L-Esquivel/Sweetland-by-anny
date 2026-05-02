const API_URL = 'http://localhost:5000';

export const pedidosService = {
  // Obtener todos los pedidos
  async getPedidos() {
    try {
      const response = await fetch(`${API_URL}/pedidos`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar pedidos');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.getPedidos:', error);
      throw error;
    }
  },

  // Obtener detalles de un pedido específico
  async getDetallesPedido(pedidoId) {
    try {
      const response = await fetch(`${API_URL}/pedidos/${pedidoId}/detalles`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar detalles del pedido');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.getDetallesPedido:', error);
      throw error;
    }
  },

  // Obtener usuarios
  async getUsuarios() {
    try {
      const response = await fetch(`${API_URL}/pedidos/usuarios`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al cargar usuarios');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.getUsuarios:', error);
      throw error;
    }
  },

  // Crear nuevo usuario
  async createUsuario(usuarioData) {
    try {
      console.log('🔍 [CREATE USUARIO] Datos enviados:', usuarioData);

      const response = await fetch(`${API_URL}/pedidos/usuarios`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(usuarioData)
      });
      
      console.log('🔍 [CREATE USUARIO] Respuesta:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });
      
      if (!response.ok) {
        let errorDetail = '';
        try {
          const errorData = await response.json();
          errorDetail = errorData.error || 'Sin detalles';
          console.error('🔍 [CREATE USUARIO] Error del servidor:', errorData);
        } catch (e) {
          errorDetail = await response.text();
          console.error('🔍 [CREATE USUARIO] Error sin JSON:', errorDetail);
        }
        throw new Error(`Error al crear usuario: ${response.status} - ${errorDetail}`);
      }
      
      const result = await response.json();
      console.log('🔍 [CREATE USUARIO] Éxito:', result);
      return result;
      
    } catch (error) {
      console.error('❌ [CREATE USUARIO] Error completo:', error);
      throw error;
    }
  },

  // Crear nuevo pedido
  async createPedido(pedidoData) {
    try {
      console.log('🔍 [CREATE PEDIDO] Datos enviados:', pedidoData);

      const response = await fetch(`${API_URL}/pedidos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(pedidoData)
      });
      
      console.log('🔍 [CREATE PEDIDO] Respuesta:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });
      
      if (!response.ok) {
        let errorDetail = '';
        try {
          const errorData = await response.json();
          errorDetail = errorData.error || 'Sin detalles';
          console.error('🔍 [CREATE PEDIDO] Error del servidor:', errorData);
        } catch (e) {
          errorDetail = await response.text();
          console.error('🔍 [CREATE PEDIDO] Error sin JSON:', errorDetail);
        }
        throw new Error(`Error al crear pedido: ${response.status} - ${errorDetail}`);
      }
      
      const result = await response.json();
      console.log('🔍 [CREATE PEDIDO] Éxito:', result);
      return result;
      
    } catch (error) {
      console.error('❌ [CREATE PEDIDO] Error completo:', error);
      throw error;
    }
  },

  // Actualizar pedido
  async updatePedido(pedidoId, pedidoData) {
    try {
      console.log('🔍 [UPDATE PEDIDO] Datos enviados:', {
        pedidoId,
        pedidoData
      });

      const response = await fetch(`${API_URL}/pedidos/${pedidoId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(pedidoData)
      });
      
      console.log('🔍 [UPDATE PEDIDO] Respuesta:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });
      
      if (!response.ok) {
        let errorDetail = '';
        try {
          const errorData = await response.json();
          errorDetail = errorData.error || 'Sin detalles';
          console.error('🔍 [UPDATE PEDIDO] Error del servidor:', errorData);
        } catch (e) {
          errorDetail = await response.text();
          console.error('🔍 [UPDATE PEDIDO] Error sin JSON:', errorDetail);
        }
        throw new Error(`Error al actualizar pedido: ${response.status} - ${errorDetail}`);
      }
      
      const result = await response.json();
      console.log('🔍 [UPDATE PEDIDO] Éxito:', result);
      return result;
      
    } catch (error) {
      console.error('❌ [UPDATE PEDIDO] Error completo:', error);
      throw error;
    }
  },

  // Eliminar pedido
  async deletePedido(pedidoId) {
    try {
      const response = await fetch(`${API_URL}/pedidos/${pedidoId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al eliminar pedido');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.deletePedido:', error);
      throw error;
    }
  },

  // Actualizar estado del pedido
  async updateEstadoPedido(pedidoId, nuevoEstado) {
    try {
      console.log('🔍 [UPDATE ESTADO] Datos:', { pedidoId, nuevoEstado });
      
      const response = await fetch(`${API_URL}/pedidos/${pedidoId}/estado`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ estado: nuevoEstado })
      });
      
      console.log('🔍 [UPDATE ESTADO] Respuesta:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });
      
      if (!response.ok) {
        let errorMessage = `Error ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          console.error('🔍 [UPDATE ESTADO] Error del servidor:', errorData);
          errorMessage = errorData.error || errorMessage;
        } catch (e) {
          console.error('🔍 [UPDATE ESTADO] No se pudo parsear error');
        }
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      console.log('🔍 [UPDATE ESTADO] Éxito:', result);
      return result;
      
    } catch (error) {
      console.error('❌ [UPDATE ESTADO] Error completo:', error);
      throw error;
    }
  },

  // Crear nuevo detalle de pedido
  async createDetallePedido(detalleData) {
    try {
      console.log('🔍 [CREATE DETALLE] Datos enviados:', detalleData);

      const response = await fetch(`${API_URL}/detalle_pedidos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(detalleData)
      });
      
      console.log('🔍 [CREATE DETALLE] Respuesta:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });
      
      if (!response.ok) {
        let errorDetail = '';
        try {
          const errorData = await response.json();
          errorDetail = errorData.error || 'Sin detalles';
          console.error('🔍 [CREATE DETALLE] Error del servidor:', errorData);
        } catch (e) {
          errorDetail = await response.text();
          console.error('🔍 [CREATE DETALLE] Error sin JSON:', errorDetail);
        }
        throw new Error(`Error al crear detalle: ${response.status} - ${errorDetail}`);
      }
      
      const result = await response.json();
      console.log('🔍 [CREATE DETALLE] Éxito:', result);
      return result;
      
    } catch (error) {
      console.error('❌ [CREATE DETALLE] Error completo:', error);
      throw error;
    }
  },

  // Actualizar detalle de pedido
  async updateDetallePedido(detalleId, detalleData) {
    try {
      const response = await fetch(`${API_URL}/detalle_pedidos/${detalleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(detalleData)
      });
      
      if (!response.ok) {
        throw new Error('Error al actualizar detalle del pedido');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.updateDetallePedido:', error);
      throw error;
    }
  },

  // Eliminar detalle de pedido
  async deleteDetallePedido(detalleId) {
    try {
      const response = await fetch(`${API_URL}/detalle_pedidos/${detalleId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Error al eliminar detalle del pedido');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error en pedidosService.deleteDetallePedido:', error);
      throw error;
    }
  },

    // Crear detalle de pedido - ENDPOINT ALTERNATIVO
  async createDetallePedidoAlternativo(pedidoId, detalleData) {
    try {
      console.log('🔍 [CREATE DETALLE ALT] Datos:', { pedidoId, detalleData });

      const response = await fetch(`${API_URL}/pedidos/${pedidoId}/agregar_detalle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(detalleData)
      });
      
      console.log('🔍 [CREATE DETALLE ALT] Respuesta:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });
      
      if (!response.ok) {
        let errorDetail = '';
        try {
          const errorData = await response.json();
          errorDetail = errorData.error || 'Sin detalles';
          console.error('🔍 [CREATE DETALLE ALT] Error del servidor:', errorData);
        } catch (e) {
          errorDetail = await response.text();
          console.error('🔍 [CREATE DETALLE ALT] Error sin JSON:', errorDetail);
        }
        throw new Error(`Error al crear detalle: ${response.status} - ${errorDetail}`);
      }
      
      const result = await response.json();
      console.log('🔍 [CREATE DETALLE ALT] Éxito:', result);
      return result;
      
    } catch (error) {
      console.error('❌ [CREATE DETALLE ALT] Error completo:', error);
      throw error;
    }
  }
};

