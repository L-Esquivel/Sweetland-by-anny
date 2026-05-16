// 🚀 Backend URL
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
// Clean up potential duplicate slashes
const API_URL = `${BASE.replace(/\/$/, '')}/empaques`;

export const empaquesService = {
  
  // ==================== 1. GENERAL CATALOG MANAGEMENT ====================
  // (Used in the "Packaging" tab within Supplies)

  async getPackagingCatalog() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading packaging catalog');
      return await response.json();
    } catch (error) {
      console.error('Error in getPackagingCatalog:', error);
      throw error;
    }
  },

  async createPackagingItem(packagingData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(packagingData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error creating packaging item');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in createPackagingItem:', error);
      throw error;
    }
  },

  async updatePackagingItem(id, packagingData) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(packagingData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error updating packaging item');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in updatePackagingItem:', error);
      throw error;
    }
  },

  async deletePackagingFromCatalog(id) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) {
        const errorData = await response.json();
        // This will capture the "In use" error from the backend
        throw new Error(errorData.error || 'Error deleting packaging item');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in deletePackagingFromCatalog:', error);
      throw error;
    }
  },


  // ==================== 2. ASSIGNMENT TO PRODUCTS (RECIPES) ====================
  // (Used within the Recipes section)

  async getPackagingForProduct(productId) {
    try {
      const response = await fetch(`${API_URL}/producto/${productId}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading packaging for product');
      return await response.json();
    } catch (error) {
      console.error('Error in getPackagingForProduct:', error);
      throw error;
    }
  },

  async addPackagingToProduct(productId, data) {
    try {
      const response = await fetch(`${API_URL}/producto/${productId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Error assigning packaging to product');
      return await response.json();
    } catch (error) {
      console.error('Error in addPackagingToProduct:', error);
      throw error;
    }
  },

  async deletePackagingFromProduct(id) {
    try {
      const response = await fetch(`${API_URL}/producto/item/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error removing packaging from product');
      return await response.json();
    } catch (error) {
      console.error('Error in deletePackagingFromProduct:', error);
      throw error;
    }
  }
};