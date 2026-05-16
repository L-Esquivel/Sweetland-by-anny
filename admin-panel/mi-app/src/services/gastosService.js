// 🚀 Backend URL
const BASE = import.meta.env.VITE_API_URL || 'https://precivox-backend.onrender.com';
const GASTOS_URL = `${BASE.replace(/\/$/, '')}/gastos`;

export const gastosService = {
  /**
   * Gets the list of expenses, optionally filtered by month and year.
   * @param {number} month - The month to filter by (1-12).
   * @param {number} year - The year to filter by.
   * @returns {Promise<Array>} The list of expenses.
   */
  async getExpenses(month, year) {
    try {
      let url = GASTOS_URL;
      if (month && year) {
        const params = new URLSearchParams({ month, year });
        url += `?${params.toString()}`;
      }
      const response = await fetch(url, { credentials: 'include' });
      if (!response.ok) throw new Error('Error loading expenses');
      return await response.json();
    } catch (error) {
      console.error('Error in gastosService.getExpenses:', error);
      throw error;
    }
  },

  /**
   * Creates a new expense record.
   * @param {object} expenseData - The expense data to create.
   * @returns {Promise<object>} The server's response.
   */
  async createExpense(expenseData) {
    try {
      const response = await fetch(GASTOS_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(expenseData)
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error creating expense');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in gastosService.createExpense:', error);
      throw error;
    }
  },

  async deleteExpense(id) {
    try {
      const response = await fetch(`${GASTOS_URL}/${id}`, { method: 'DELETE', credentials: 'include' });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error deleting expense');
      }
      return await response.json();
    } catch (error) {
      console.error('Error in gastosService.deleteExpense:', error);
      throw error;
    }
  }
};