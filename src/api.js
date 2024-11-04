// src/api.js

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

export const analyzeCarrier = async (carrierId) => {
  try {
    const response = await /api//api/(`${API_BASE_URL}/carriers/${carrierId}/analysis`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching carrier analysis:', error);
    throw error;
  }
};