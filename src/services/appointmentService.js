// Appointment Service
// Handles API requests for appointments

import axios from 'axios';

const API_URL = 'api/appointments';

// Get all appointments with optional filters
const getAppointments = async (params = {}) => {
  try {
    const response = await axios.get(API_URL, { params });
    return response.data;
  } catch (error) {
    console.error('Error getting appointments:', error);
    throw error;
  }
};

// Get a single appointment by ID
const getAppointment = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error getting appointment with ID ${id}:`, error);
    throw error;
  }
};

// Create a new appointment
const createAppointment = async (appointmentData) => {
  try {
    const response = await axios.post(API_URL, appointmentData);
    return response.data;
  } catch (error) {
    console.error('Error creating appointment:', error);
    throw error;
  }
};

// Update an existing appointment
const updateAppointment = async (id, appointmentData) => {
  try {
    const response = await axios.put(`${API_URL}/${id}`, appointmentData);
    return response.data;
  } catch (error) {
    console.error(`Error updating appointment with ID ${id}:`, error);
    throw error;
  }
};

// Cancel an appointment
const cancelAppointment = async (id) => {
  try {
    const response = await axios.put(`${API_URL}/${id}/cancel`);
    return response.data;
  } catch (error) {
    console.error(`Error cancelling appointment with ID ${id}:`, error);
    throw error;
  }
};

export default {
  getAppointments,
  getAppointment,
  createAppointment,
  updateAppointment,
  cancelAppointment
}; 