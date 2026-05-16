// 🚀 Backend URL
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const MERMA_URL = `${BASE.replace(/\/$/, '')}/merma`;

export const mermaService = {
  async getWasteRecords() {
    try {
      const response = await fetch(MERMA_URL, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading waste records');
      return await response.json();
    } catch (error) {
      console.error('Error in mermaService.getWasteRecords:', error);
      throw error;
    }
  },

  async createWasteRecord(wasteData) {
    try {
      const response = await fetch(MERMA_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(wasteData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error creating waste record');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in mermaService.createWasteRecord:', error);
      throw error;
    }
  },

  async deleteWasteRecord(id) {
    try {
      const response = await fetch(`${MERMA_URL}/${id}`, { method: 'DELETE', credentials: 'include' });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Error deleting waste record');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in mermaService.deleteWasteRecord:', error);
      throw error;
    }
  }
};