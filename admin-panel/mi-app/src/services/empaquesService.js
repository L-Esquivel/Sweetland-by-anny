// src/services/empaquesService.js
import API_URL from './api.js';

export const empaquesService = {

  // Catálogo completo de empaques
  getEmpaques: () => fetchAPI('/empaques/'),

  // Empaques asignados a un producto
  getEmpaquesProducto: (productoId) => fetchAPI(`/empaques/producto/${productoId}`),

  // Asignar empaque a un producto
  addEmpaque: (productoId, data) => fetchAPI(`/empaques/producto/${productoId}`, {
    method: 'POST',
    body: data
  }),

  // Eliminar empaque de un producto
  deleteEmpaque: (id) => fetchAPI(`/empaques/producto/item/${id}`, {
    method: 'DELETE'
  })
};