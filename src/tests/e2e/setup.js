// End-to-End Test Setup
// This file configures the environment for end-to-end tests

import { beforeAll, afterAll, afterEach, vi } from 'vitest';
import axios from 'axios';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

// In-memory test database - simulates database state
let testDb = {
  patients: [
    {
      id: 1,
      firstName: 'John',
      lastName: 'Smith',
      dateOfBirth: '1985-04-15',
      gender: 'Male',
      service: 'Army',
      rank: 'E-5',
      status: 'Active Duty',
      contactInfo: {
        email: 'john.smith@example.com',
        phone: '555-123-4567',
        address: '123 Military Ave, Base City, ST 12345'
      },
      emergencyContact: {
        name: 'Jane Smith',
        relationship: 'Spouse',
        phone: '555-987-6543'
      },
      medicalInfo: {
        bloodType: 'O+',
        allergies: ['Penicillin'],
        conditions: ['Hypertension'],
        medications: ['Lisinopril']
      }
    },
    {
      id: 2,
      firstName: 'Maria',
      lastName: 'Rodriguez',
      dateOfBirth: '1990-08-22',
      gender: 'Female',
      service: 'Navy',
      rank: 'O-2',
      status: 'Active Duty',
      contactInfo: {
        email: 'maria.rodriguez@example.com',
        phone: '555-234-5678',
        address: '456 Naval Blvd, Port City, ST 67890'
      },
      emergencyContact: {
        name: 'Carlos Rodriguez',
        relationship: 'Brother',
        phone: '555-876-5432'
      },
      medicalInfo: {
        bloodType: 'A-',
        allergies: [],
        conditions: [],
        medications: []
      }
    }
  ],
  appointments: [
    {
      id: 101,
      patientId: 1,
      date: '2025-04-20T09:30:00',
      type: 'Follow-up',
      provider: 'Dr. Wilson',
      status: 'Scheduled',
      notes: 'Blood pressure check'
    },
    {
      id: 102,
      patientId: 2,
      date: '2025-04-21T13:15:00',
      type: 'Annual Physical',
      provider: 'Dr. Johnson',
      status: 'Scheduled',
      notes: 'Routine annual physical examination'
    }
  ],
  records: [
    {
      id: 201,
      patientId: 1,
      date: '2025-03-15',
      type: 'Physical Examination',
      provider: 'Dr. Wilson',
      status: 'Completed',
      notes: 'Patient appears healthy. Blood pressure slightly elevated at 130/85.'
    },
    {
      id: 202,
      patientId: 1,
      date: '2025-02-10',
      type: 'Laboratory Test',
      provider: 'Dr. Johnson',
      status: 'Completed',
      notes: 'Blood work shows normal cholesterol levels.'
    }
  ]
};

// Create a request handler that simulates API endpoints
const handlers = [
  // Patient endpoints
  rest.get('/api/patients', (req, res, ctx) => {
    // Handle pagination and filtering
    const limit = parseInt(req.url.searchParams.get('limit') || '10');
    const offset = parseInt(req.url.searchParams.get('offset') || '0');
    const search = req.url.searchParams.get('search') || '';
    
    let filteredPatients = testDb.patients;
    if (search) {
      filteredPatients = filteredPatients.filter(patient => 
        `${patient.firstName} ${patient.lastName}`.toLowerCase().includes(search.toLowerCase()) ||
        patient.id.toString().includes(search)
      );
    }
    
    return res(
      ctx.status(200),
      ctx.json({
        patients: filteredPatients.slice(offset, offset + limit),
        total: filteredPatients.length
      })
    );
  }),
  
  rest.get('/api/patients/:id', (req, res, ctx) => {
    const { id } = req.params;
    const patient = testDb.patients.find(p => p.id.toString() === id);
    
    if (!patient) {
      return res(
        ctx.status(404),
        ctx.json({ message: 'Patient not found' })
      );
    }
    
    // Add related records and appointments
    const patientRecords = testDb.records.filter(r => r.patientId.toString() === id);
    const patientAppointments = testDb.appointments.filter(a => a.patientId.toString() === id);
    
    return res(
      ctx.status(200),
      ctx.json({
        ...patient,
        recentRecords: patientRecords.slice(0, 3),
        upcomingAppointments: patientAppointments
          .filter(a => new Date(a.date) > new Date())
          .sort((a, b) => new Date(a.date) - new Date(b.date))
          .slice(0, 3)
      })
    );
  }),
  
  rest.post('/api/patients', async (req, res, ctx) => {
    const patientData = await req.json();
    const newPatient = {
      id: testDb.patients.length > 0 ? Math.max(...testDb.patients.map(p => p.id)) + 1 : 1,
      ...patientData
    };
    
    testDb.patients.push(newPatient);
    
    return res(
      ctx.status(201),
      ctx.json(newPatient)
    );
  }),
  
  rest.put('/api/patients/:id', async (req, res, ctx) => {
    const { id } = req.params;
    const patientIndex = testDb.patients.findIndex(p => p.id.toString() === id);
    
    if (patientIndex === -1) {
      return res(
        ctx.status(404),
        ctx.json({ message: 'Patient not found' })
      );
    }
    
    const patientData = await req.json();
    testDb.patients[patientIndex] = {
      ...testDb.patients[patientIndex],
      ...patientData
    };
    
    return res(
      ctx.status(200),
      ctx.json(testDb.patients[patientIndex])
    );
  }),
  
  // Appointment endpoints
  rest.get('/api/appointments', (req, res, ctx) => {
    const limit = parseInt(req.url.searchParams.get('limit') || '10');
    const offset = parseInt(req.url.searchParams.get('offset') || '0');
    const search = req.url.searchParams.get('search') || '';
    const status = req.url.searchParams.get('status') || '';
    const fromDate = req.url.searchParams.get('fromDate') || '';
    const toDate = req.url.searchParams.get('toDate') || '';
    
    let filteredAppointments = testDb.appointments;
    
    // Filter by status
    if (status) {
      filteredAppointments = filteredAppointments.filter(a => a.status === status);
    }
    
    // Filter by date range
    if (fromDate && toDate) {
      filteredAppointments = filteredAppointments.filter(a => {
        const appointmentDate = new Date(a.date);
        return appointmentDate >= new Date(fromDate) && appointmentDate <= new Date(toDate);
      });
    }
    
    // Filter by search (patient name or ID)
    if (search) {
      filteredAppointments = filteredAppointments.filter(a => {
        const patient = testDb.patients.find(p => p.id === a.patientId);
        if (patient) {
          return `${patient.firstName} ${patient.lastName}`.toLowerCase().includes(search.toLowerCase()) ||
            patient.id.toString().includes(search);
        }
        return false;
      });
    }
    
    // Enhance appointment data with patient information
    const enhancedAppointments = filteredAppointments.map(appointment => {
      const patient = testDb.patients.find(p => p.id === appointment.patientId);
      return {
        ...appointment,
        patientName: patient ? `${patient.firstName} ${patient.lastName}` : 'Unknown Patient'
      };
    });
    
    return res(
      ctx.status(200),
      ctx.json({
        appointments: enhancedAppointments.slice(offset, offset + limit),
        total: enhancedAppointments.length
      })
    );
  }),
  
  // Records endpoints
  rest.get('/api/records', (req, res, ctx) => {
    const limit = parseInt(req.url.searchParams.get('limit') || '10');
    const offset = parseInt(req.url.searchParams.get('offset') || '0');
    const search = req.url.searchParams.get('search') || '';
    const type = req.url.searchParams.get('type') || '';
    const fromDate = req.url.searchParams.get('fromDate') || '';
    const toDate = req.url.searchParams.get('toDate') || '';
    
    let filteredRecords = testDb.records;
    
    // Filter by record type
    if (type) {
      filteredRecords = filteredRecords.filter(r => r.type === type);
    }
    
    // Filter by date range
    if (fromDate && toDate) {
      filteredRecords = filteredRecords.filter(r => {
        const recordDate = new Date(r.date);
        return recordDate >= new Date(fromDate) && recordDate <= new Date(toDate);
      });
    }
    
    // Filter by search (patient name, ID, or record type)
    if (search) {
      filteredRecords = filteredRecords.filter(r => {
        const patient = testDb.patients.find(p => p.id === r.patientId);
        if (patient) {
          return `${patient.firstName} ${patient.lastName}`.toLowerCase().includes(search.toLowerCase()) ||
            patient.id.toString().includes(search) ||
            r.type.toLowerCase().includes(search.toLowerCase());
        }
        return false;
      });
    }
    
    // Enhance record data with patient information
    const enhancedRecords = filteredRecords.map(record => {
      const patient = testDb.patients.find(p => p.id === record.patientId);
      return {
        ...record,
        patientName: patient ? `${patient.firstName} ${patient.lastName}` : 'Unknown Patient'
      };
    });
    
    return res(
      ctx.status(200),
      ctx.json({
        records: enhancedRecords.slice(offset, offset + limit),
        total: enhancedRecords.length
      })
    );
  })
];

// Create MSW server
const server = setupServer(...handlers);

// Setup before tests run
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
  
  // Intercept axios requests to use our mock server
  axios.defaults.baseURL = '';
});

// Clean up after each test
afterEach(() => {
  server.resetHandlers();
});

// Clean up after all tests
afterAll(() => {
  server.close();
});

// Export test database for direct manipulation in tests
export { testDb }; 