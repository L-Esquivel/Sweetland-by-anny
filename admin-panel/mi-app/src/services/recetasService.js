// src/services/recetasService.js
// 🚀 Backend URL
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/recipes`;

export const recetasService = {
  async getRecipes() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading recipes');
      return await response.json();
    } catch (error) {
      console.error('Error in recetasService.getRecipes:', error);
      throw error;
    }
  },

  async getProductRecipeDetails(productId) {
    try {
      const response = await fetch(`${API_URL}/producto/${productId}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading product recipe details');
      return await response.json();
    } catch (error) {
      console.error('Error in recetasService.getProductRecipeDetails:', error);
      throw error;
    }
  },

  // Recalculate costs with custom PAX and Profit
  async recalculateCosts(productId, pax, profitPercentage) {
    try {
      const response = await fetch(`${API_URL}/recalcular`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          id_producto: productId,
          pax: pax,
          utilidad_porcentaje: profitPercentage
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error recalculating costs');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in recetasService.recalculateCosts:', error);
      throw error;
    }
  },

  async addRecipeIngredient(recipeData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(recipeData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error in recetasService.addRecipeIngredient:', error);
      throw error;
    }
  },

  async addMultipleRecipeIngredients(productId, ingredients) {
    try {
      const response = await fetch(`${API_URL}/multiple`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ id_producto: productId, ingredientes })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error creating recipes');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in recetasService.addMultipleRecipeIngredients:', error);
      throw error;
    }
  },

  async updateRecipeIngredient(recipeId, recipeData) {
    try {
      const response = await fetch(`${API_URL}/${recetaId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(recipeData)
      });
      if (!response.ok) throw new Error('Error updating recipe');
      return await response.json();
    } catch (error) {
      console.error('Error in recetasService.updateRecipeIngredient:', error);
      throw error;
    }
  },

  async deleteRecipeIngredient(recipeId) {
    try {
      const response = await fetch(`${API_URL}/${recetaId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error deleting recipe');
      return await response.json();
    } catch (error) {
      console.error('Error in recetasService.deleteRecipeIngredient:', error);
      throw error;
    }
  },

  async deleteAllProductRecipes(productId) {
    try {
      const response = await fetch(`${API_URL}/producto/${productId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Error deleting product recipes');
      return await response.json();
    } catch (error) {
      console.error('Error in recetasService.deleteAllProductRecipes:', error);
      throw error;
    }
  }
};