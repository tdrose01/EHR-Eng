// Patient Service
// Handles API requests for patients

import axios from 'axios';

const API_URL = '/api/patients';

// Get all patients with optional filters
const getPatients = async (params = {}) => {
  try {
    const response = await axios.get(API_URL, { params });
    return response.data;
  } catch (error) {
    console.error('Error getting patients:', error);
    throw error;
  }
};

// Get a single patient by ID
const getPatient = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error getting patient with ID ${id}:`, error);
    throw error;
  }
};

// Create a new patient
const createPatient = async (patientData) => {
  try {
    const response = await axios.post(API_URL, patientData);
    return response.data;
  } catch (error) {
    console.error('Error creating patient:', error);
    throw error;
  }
};

// Update an existing patient
const updatePatient = async (id, patientData) => {
  try {
    const response = await axios.put(`${API_URL}/${id}`, patientData);
    return response.data;
  } catch (error) {
    console.error(`Error updating patient with ID ${id}:`, error);
    throw error;
  }
};

export default {
  getPatients,
  getPatient,
  createPatient,
  updatePatient
}; 