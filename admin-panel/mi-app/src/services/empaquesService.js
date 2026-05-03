// src/services/empaquesService.js
const API_URL = (import.meta.env.VITE_API_URL || 'https://sweetland-by-anny-production.up.railway.app') + '/empaques';
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