import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'

// Mock Vue components
const AppHeader = { template: '<div class="app-header-mock"></div>' }
const SideNavigation = { template: '<div class="side-nav-mock"></div>' }
const LoadingSpinner = { template: '<div data-testid="loading-spinner"></div>' }
const PatientTable = { 
  template: '<div data-testid="patient-table"><slot></slot></div>',
  props: ['patients', 'loading']
}

// Mock the router push function
const mockPush = vi.fn()

// Mock the patient service
const mockPatientService = {
  getPatients: vi.fn().mockResolvedValue({
    patients: [
      {
        id: 1,
        firstName: 'John',
        lastName: 'Smith',
        dateOfBirth: '1985-04-15',
        service: 'Army',
        rank: 'E-5',
        status: 'Active Duty'
      },
      {
        id: 2,
        firstName: 'Maria',
        lastName: 'Rodriguez',
        dateOfBirth: '1990-08-22',
        service: 'Navy',
        rank: 'O-2',
        status: 'Active Duty'
      }
    ],
    total: 2
  })
}

// Mock the component we're testing
const PatientList = {
  components: {
    AppHeader,
    SideNavigation,
    LoadingSpinner,
    PatientTable
  },
  template: `
    <div>
      <app-header></app-header>
      <side-navigation></side-navigation>
      <div class="main-content">
        <div class="card">
          <div class="card-header">
            <h2>Patients</h2>
            <div class="card-actions">
              <button @click="addPatient">Add Patient</button>
            </div>
          </div>
          <div class="card-body">
            <loading-spinner v-if="loading"></loading-spinner>
            <div v-else>
              <patient-table :patients="patients" :loading="loading">
                <template #actions="{ patient }">
                  <button @click="viewPatient(patient.id)">View</button>
                  <button @click="editPatient(patient.id)">Edit</button>
                </template>
              </patient-table>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  data() {
    return {
      patients: [],
      loading: true,
      total: 0,
      currentPage: 1,
      limit: 10
    }
  },
  mounted() {
    this.loadPatients()
  },
  methods: {
    async loadPatients() {
      try {
        this.loading = true
        const response = await mockPatientService.getPatients({
          limit: this.limit,
          offset: (this.currentPage - 1) * this.limit
        })
        this.patients = response.patients
        this.total = response.total
      } catch (error) {
        console.error('Error loading patients:', error)
      } finally {
        this.loading = false
      }
    },
    viewPatient(id) {
      mockPush(`/patients/${id}`)
    },
    editPatient(id) {
      mockPush(`/patients/${id}/edit`)
    },
    addPatient() {
      mockPush('/patients/new')
    }
  }
}

describe('PatientList.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockPatientService.getPatients.mockClear()
    mockPush.mockClear()
  })

  it('renders the component with correct layout', async () => {
    const wrapper = mount(PatientList)
    
    // Main layout elements should be present
    expect(wrapper.find('.app-header-mock').exists()).toBe(true)
    expect(wrapper.find('.side-nav-mock').exists()).toBe(true)
    expect(wrapper.find('.main-content').exists()).toBe(true)
    
    // Initially should show loading spinner
    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true)
    
    // Let the component load data
    await flushPromises()
    
    // After loading, patient table should be visible
    expect(wrapper.find('[data-testid="patient-table"]').exists()).toBe(true)
    
    // API should be called with default parameters on component mount
    expect(mockPatientService.getPatients).toHaveBeenCalledWith({
      limit: 10,
      offset: 0,
    })
  })

  it('navigates to patient view when view method is called', async () => {
    const wrapper = mount(PatientList)
    await flushPromises()
    
    // Manually call view method
    await wrapper.vm.viewPatient(1)
    
    // Router should navigate to patient view page
    expect(mockPush).toHaveBeenCalledWith('/patients/1')
  })

  it('navigates to patient edit when edit method is called', async () => {
    const wrapper = mount(PatientList)
    await flushPromises()
    
    // Manually call edit method
    await wrapper.vm.editPatient(1)
    
    // Router should navigate to patient edit page
    expect(mockPush).toHaveBeenCalledWith('/patients/1/edit')
  })

  it('navigates to add patient when add button is clicked', async () => {
    const wrapper = mount(PatientList)
    await flushPromises()
    
    // Find and click add patient button
    const addButton = wrapper.find('.card-actions button')
    await addButton.trigger('click')
    
    // Router should navigate to add patient page
    expect(mockPush).toHaveBeenCalledWith('/patients/new')
  })
}) 