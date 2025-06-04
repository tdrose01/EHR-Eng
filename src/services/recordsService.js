// Records Service
// Handles API requests for medical records

import axios from 'axios';

const API_URL = '/api/records';

// Get all records with optional filters
const getRecords = async (params = {}) => {
  try {
    const response = await axios.get(API_URL, { params });
    return response.data;
  } catch (error) {
    console.error('Error getting records:', error);
    throw error;
  }
};

// Get a single record by ID
const getRecord = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error getting record with ID ${id}:`, error);
    throw error;
  }
};

// Create a new record
const createRecord = async (recordData) => {
  try {
    const response = await axios.post(API_URL, recordData);
    return response.data;
  } catch (error) {
    console.error('Error creating record:', error);
    throw error;
  }
};

// Update an existing record
const updateRecord = async (id, recordData) => {
  try {
    const response = await axios.put(`${API_URL}/${id}`, recordData);
    return response.data;
  } catch (error) {
    console.error(`Error updating record with ID ${id}:`, error);
    throw error;
  }
};

// Delete a record
const deleteRecord = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting record with ID ${id}:`, error);
    throw error;
  }
};

export default {
  getRecords,
  getRecord,
  createRecord,
  updateRecord,
  deleteRecord
}; 