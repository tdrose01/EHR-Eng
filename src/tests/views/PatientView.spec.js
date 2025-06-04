import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PatientView from '@/views/PatientView.vue'

// Mock route params
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({
    params: { id: '123' }
  })
}))

// Create a mock function for router.push
const mockPush = vi.fn()

// Directly mock the service instead of relying on import resolution
const mockPatient = {
  id: 123,
  firstName: 'John',
  lastName: 'Smith',
  dateOfBirth: '1985-04-15',
  gender: 'Male',
  service: 'Army',
  rank: 'E-5',
  status: 'Active Duty',
  deployments: [
    { location: 'Afghanistan', startDate: '2010-03-01', endDate: '2011-03-01' }
  ],
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
  },
  recentRecords: [
    {
      id: 1,
      date: '2023-05-15',
      type: 'Physical Examination',
      provider: 'Dr. Wilson'
    },
    {
      id: 2,
      date: '2023-04-10',
      type: 'Laboratory Test',
      provider: 'Dr. Johnson'
    }
  ],
  upcomingAppointments: [
    {
      id: 101,
      date: '2023-06-20T09:30:00',
      type: 'Follow-up',
      provider: 'Dr. Wilson'
    }
  ]
}

vi.mock('@/services/patientService', () => ({
  default: {
    getPatient: vi.fn().mockResolvedValue(mockPatient)
  }
}), { virtual: true })

// Get the mocked service
const patientService = vi.mocked(await import('@/services/patientService')).default;

// Mock components
vi.mock('@/components/AppHeader.vue', () => ({
  default: {
    name: 'AppHeader',
    template: '<div class="app-header-mock"></div>'
  }
}))

vi.mock('@/components/SideNavigation.vue', () => ({
  default: {
    name: 'SideNavigation',
    template: '<div class="side-nav-mock"></div>'
  }
}))

vi.mock('@/components/LoadingSpinner.vue', () => ({
  default: {
    name: 'LoadingSpinner',
    template: '<div data-testid="loading-spinner"></div>'
  }
}))

describe('PatientView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the component with correct layout', async () => {
    const wrapper = mount(PatientView)
    
    // Loading spinner should be shown initially
    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true)
    
    // Wait for patient data to load
    await new Promise(resolve => setTimeout(resolve, 0))
    await wrapper.vm.$nextTick()
    
    // Should call getPatient with the correct ID
    expect(patientService.getPatient).toHaveBeenCalledWith('123')
  })

  it('navigates to edit patient when edit button is clicked', async () => {
    const wrapper = mount(PatientView)
    
    // Wait for patient data to load
    await new Promise(resolve => setTimeout(resolve, 0))
    await wrapper.vm.$nextTick()
    
    // Find and click edit patient button
    const editButton = wrapper.find('.patient-header-actions button:first-child')
    await editButton.trigger('click')
    
    // Router should navigate to edit page
    expect(mockPush).toHaveBeenCalledWith('/patients/123/edit')
  })

  it('navigates back to patients list when back button is clicked', async () => {
    const wrapper = mount(PatientView)
    
    // Wait for patient data to load
    await new Promise(resolve => setTimeout(resolve, 0))
    await wrapper.vm.$nextTick()
    
    // Find and click back button
    const backButton = wrapper.find('.patient-header-actions button:last-child')
    await backButton.trigger('click')
    
    // Router should navigate back to patients list
    expect(mockPush).toHaveBeenCalledWith('/patients')
  })
}) 