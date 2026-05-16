// 🚀 Backend URL
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const API_URL = `${BASE.replace(/\/$/, '')}/usuarios`;

export const usuariosService = {
  // Get all users
  async getUsers() {
    try {
      const response = await fetch(`${API_URL}/`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading users');
      return await response.json();
    } catch (error) {
      console.error('Error in usuariosService.getUsers:', error);
      throw error;
    }
  },

  // Get user by ID
  async getUser(id) {
    try {
      const response = await fetch(`${API_URL}/${id}`, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading user details');
      return await response.json();
    } catch (error) {
      console.error('Error in usuariosService.getUser:', error);
      throw error;
    }
  },

  // Create user
  async createUser(userData) {
    try {
      const response = await fetch(`${API_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(userData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error creating user');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in usuariosService.createUser:', error);
      throw error;
    }
  },

  // Update user
  async updateUser(id, userData) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(userData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error updating user');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in usuariosService.updateUser:', error);
      throw error;
    }
  },

  // Delete user
  async deleteUser(id) {
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error deleting user');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in usuariosService.deleteUser:', error);
      throw error;
    }
  }
};