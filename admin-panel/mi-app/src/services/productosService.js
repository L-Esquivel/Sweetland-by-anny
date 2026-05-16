// 🚀 Backend URL
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/productos`;

export const productosService = {
  // Get all products
  async getProducts() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading products');
      return await response.json();
    } catch (error) {
      console.error('Error in productosService.getProducts:', error);
      throw error;
    }
  },

  // Get product by ID
  async getProduct(id) {
    try {
      const response = await fetch(`${API_URL}/${id}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading product details');
      return await response.json();
    } catch (error) {
      console.error('Error in productosService.getProduct:', error);
      throw error;
    }
  },

  // Create product
  async createProduct(productData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(productData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error creating product');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in productosService.createProduct:', error);
      throw error;
    }
  },

  // Update product
  async updateProduct(id, productData) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(productData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error updating product');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in productosService.updateProduct:', error);
      throw error;
    }
  },

  // Delete product
  async deleteProduct(id) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error deleting product');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in productosService.deleteProduct:', error);
      throw error;
    }
  }
};