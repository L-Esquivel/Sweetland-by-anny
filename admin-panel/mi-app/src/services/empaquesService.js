import api from './api';

export const empaquesService = {

  // Catálogo completo de empaques
  getEmpaques: async () => {
    const response = await api.get('/empaques/');
    return response.data;
  },

  // Empaques asignados a un producto
  getEmpaquesProducto: async (productoId) => {
    const response = await api.get(`/empaques/producto/${productoId}`);
    return response.data;
  },

  // Asignar empaque a un producto
  addEmpaque: async (productoId, data) => {
    const response = await api.post(`/empaques/producto/${productoId}`, data);
    return response.data;
  },

  // Eliminar empaque de un producto
  deleteEmpaque: async (id) => {
    const response = await api.delete(`/empaques/producto/item/${id}`);
    return response.data;
  }
};