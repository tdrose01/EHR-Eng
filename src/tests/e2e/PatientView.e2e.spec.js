import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import { createRouter, createWebHistory } from 'vue-router';
import PatientView from '@/views/PatientView.vue';
import { testDb } from './setup';

// Import required components to prevent errors
import AppHeader from '@/components/AppHeader.vue';
import SideNavigation from '@/components/SideNavigation.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';

// Set up router with the needed route
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { 
      path: '/patients/:id', 
      name: 'PatientView',
      component: PatientView 
    },
    { 
      path: '/patients/:id/edit', 
      name: 'PatientEdit',
      component: { template: '<div>Edit Patient</div>' } 
    },
    { 
      path: '/patients', 
      name: 'PatientList',
      component: { template: '<div>Patient List</div>' } 
    },
    { 
      path: '/patients/:id/records', 
      name: 'PatientRecords',
      component: { template: '<div>Patient Records</div>' } 
    },
    { 
      path: '/patients/:id/appointments', 
      name: 'PatientAppointments',
      component: { template: '<div>Patient Appointments</div>' } 
    }
  ]
});

// Create a wrapper factory function
const createWrapper = async (patientId) => {
  // Set the route to the patient view with the specified ID
  router.push(`/patients/${patientId}`);
  await router.isReady();
  
  const wrapper = mount(PatientView, {
    global: {
      plugins: [router],
      stubs: {
        AppHeader,
        SideNavigation,
        LoadingSpinner
      }
    }
  });
  
  // Wait for async operations to complete
  await flushPromises();
  
  return wrapper;
};

describe('PatientView E2E Tests', () => {
  beforeEach(async () => {
    // Reset the router
    router.push('/');
    await router.isReady();
  });

  it('loads and displays patient information correctly', async () => {
    const patientId = 1;
    const wrapper = await createWrapper(patientId);
    
    // Check that loading spinner is not visible after data loads
    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(false);
    
    // Check patient personal information
    const patient = testDb.patients.find(p => p.id === patientId);
    expect(wrapper.text()).toContain(patient.firstName);
    expect(wrapper.text()).toContain(patient.lastName);
    expect(wrapper.text()).toContain(patient.service);
    expect(wrapper.text()).toContain(patient.rank);
    
    // Check military information
    expect(wrapper.find('.military-info').exists()).toBe(true);
    
    // Check medical information
    expect(wrapper.find('.medical-info').exists()).toBe(true);
    expect(wrapper.text()).toContain(patient.medicalInfo.bloodType);
    
    // Check related records
    const patientRecords = testDb.records.filter(r => r.patientId === patientId);
    if (patientRecords.length > 0) {
      expect(wrapper.find('.recent-records').exists()).toBe(true);
    }
    
    // Check related appointments
    const patientAppointments = testDb.appointments.filter(a => a.patientId === patientId);
    if (patientAppointments.length > 0) {
      expect(wrapper.find('.upcoming-appointments').exists()).toBe(true);
    }
  });
  
  it('shows error message when patient not found', async () => {
    const nonExistentId = 9999;
    const wrapper = await createWrapper(nonExistentId);
    
    // Check if error message is displayed
    await flushPromises();
    expect(wrapper.find('.alert-error').exists()).toBe(true);
  });
  
  it('navigates to edit patient when edit button is clicked', async () => {
    const patientId = 1;
    const wrapper = await createWrapper(patientId);
    
    // Find and click edit patient button
    const spy = vi.spyOn(router, 'push');
    await wrapper.find('.edit-patient-btn').trigger('click');
    
    // Check if router was called with the correct path
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({
      name: 'PatientEdit',
      params: { id: patientId.toString() }
    }));
  });
  
  it('navigates back to patients list when back button is clicked', async () => {
    const patientId = 1;
    const wrapper = await createWrapper(patientId);
    
    // Find and click back button
    const spy = vi.spyOn(router, 'push');
    await wrapper.find('.back-btn').trigger('click');
    
    // Check if router was called with the correct path
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({
      name: 'PatientList'
    }));
  });
  
  it('navigates to patient records when view all records is clicked', async () => {
    const patientId = 1;
    const wrapper = await createWrapper(patientId);
    
    // Find and click view all records button
    const spy = vi.spyOn(router, 'push');
    await wrapper.find('.view-all-records-btn').trigger('click');
    
    // Check if router was called with the correct path
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({
      name: 'PatientRecords',
      params: { id: patientId.toString() }
    }));
  });
  
  it('navigates to patient appointments when view all appointments is clicked', async () => {
    const patientId = 1;
    const wrapper = await createWrapper(patientId);
    
    // Find and click view all appointments button
    const spy = vi.spyOn(router, 'push');
    await wrapper.find('.view-all-appointments-btn').trigger('click');
    
    // Check if router was called with the correct path
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({
      name: 'PatientAppointments',
      params: { id: patientId.toString() }
    }));
  });
}); 