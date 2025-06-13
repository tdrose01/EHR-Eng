<template>
  <div class="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
    <Navbar />
    <div class="flex flex-1 px-4 py-6 space-x-6">
      <Sidebar active="Dashboard" />
      <main class="flex-1 space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Patients" :value="stats.totalPatients" link="patients_list.html?filter=all" />
          <StatCard label="Active Patients" :value="stats.activePatients" link="patients_list.html?filter=active" />
          <StatCard label="Today's Appointments" :value="stats.appointmentsToday" link="appointments.html?filter=today" />
          <StatCard label="Pending Records" :value="stats.pendingRecords" link="records.html?filter=pending" />
        </div>
        <Chart />
        <div class="bg-gray-800 p-4 rounded">
          <h3 class="text-blue-400 font-semibold mb-2 flex justify-between items-center">
            Recent Patients
            <div>
              <button class="bg-blue-500 text-white px-3 py-1 rounded mr-2" @click="addPatient">Add Patient</button>
              <button class="bg-blue-500 text-white px-3 py-1 rounded" @click="loadPatientData">Refresh</button>
            </div>
          </h3>
          <div class="flex mb-4">
            <input v-model="searchTerm" type="text" placeholder="Search patients..." class="flex-grow bg-gray-700 border border-gray-600 p-2 rounded-l" />
            <button class="bg-blue-500 text-white px-4 rounded-r" @click="loadPatientData">Search</button>
          </div>
          <div v-if="loading" class="text-center my-4">Loading...</div>
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-gray-700 text-blue-400">
                <th class="p-2 text-left">Patient ID</th>
                <th class="p-2 text-left">Name</th>
                <th class="p-2 text-left">DOB</th>
                <th class="p-2 text-left">Service</th>
                <th class="p-2 text-left">Rank</th>
                <th class="p-2 text-left">Blood Type</th>
                <th class="p-2 text-left">Contact</th>
                <th class="p-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in patients" :key="p.patient_id" class="border-b border-gray-700 hover:bg-gray-700">
                <td class="p-2">{{ p.patient_id }}</td>
                <td class="p-2">{{ p.last_name }}, {{ p.first_name }}</td>
                <td class="p-2">{{ formatDate(p.date_of_birth) }}</td>
                <td class="p-2">{{ p.service || 'N/A' }}</td>
                <td class="p-2">{{ p.rank || 'N/A' }}</td>
                <td class="p-2">{{ p.blood_type || 'Unknown' }}</td>
                <td class="p-2">{{ p.contact_number || 'N/A' }}</td>
                <td class="p-2">
                  <div class="flex gap-2">
                    <button class="border px-2 py-1 rounded hover:bg-gray-600" @click="viewPatient(p.patient_id)">View</button>
                    <button class="border px-2 py-1 rounded hover:bg-gray-600 text-yellow-500" @click="editPatient(p.patient_id)">Edit</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!loading && patients.length === 0">
                <td class="p-2 text-center" colspan="8">No patients found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'
import StatCard from './components/StatCard.vue'
import Chart from './components/Chart.vue'

const stats = ref({
  totalPatients: '--',
  activePatients: '--',
  appointmentsToday: '--',
  pendingRecords: '--'
})

const patients = ref([])
const searchTerm = ref('')
const loading = ref(false)

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function addPatient() {
  window.location.href = 'add_patient.html'
}

async function loadDashboardStats() {
  try {
    const res = await fetch('http://localhost:8002/api/dashboard-stats')
    const data = await res.json()
    if (data.success) {
      stats.value = {
        totalPatients: data.stats.totalPatients,
        activePatients: data.stats.activePatients,
        appointmentsToday: data.stats.appointmentsToday,
        pendingRecords: data.stats.pendingRecords
      }
    }
  } catch (err) {
    stats.value = { totalPatients: 100, activePatients: 87, appointmentsToday: 12, pendingRecords: 5 }
  }
}

async function loadPatientData() {
  loading.value = true
  let apiUrl = 'http://localhost:8002/api/patients?limit=10&offset=0'
  if (searchTerm.value) {
    apiUrl += `&search=${encodeURIComponent(searchTerm.value)}`
  }
  try {
    const res = await fetch(apiUrl)
    const data = await res.json()
    if (data.success) {
      patients.value = data.patients
    } else {
      patients.value = []
    }
  } catch (err) {
    patients.value = generateSamplePatients()
  } finally {
    loading.value = false
  }
}

function generateSamplePatients() {
  return [
    { patient_id: 1, first_name: 'Stacey', last_name: 'Calderon', date_of_birth: '1985-07-12', service: 'Army', rank: 'E-5', blood_type: 'A+', contact_number: '555-123-4567' },
    { patient_id: 2, first_name: 'Ian', last_name: 'Williams', date_of_birth: '1992-03-24', service: 'Navy', rank: 'O-3', blood_type: 'O-', contact_number: '555-987-6543' },
    { patient_id: 3, first_name: 'Michael', last_name: 'Castaneda', date_of_birth: '1978-11-05', service: 'Air Force', rank: 'E-7', blood_type: 'B+', contact_number: '555-345-6789' },
    { patient_id: 4, first_name: 'Matthew', last_name: 'Howard', date_of_birth: '1990-09-30', service: 'Marines', rank: 'E-4', blood_type: 'AB+', contact_number: '555-234-5678' },
    { patient_id: 5, first_name: 'Sophia', last_name: 'Torres', date_of_birth: '1982-05-17', service: 'Coast Guard', rank: 'O-2', blood_type: 'A-', contact_number: '555-876-5432' }
  ]
}

function viewPatient(id) {
  fetch(`http://localhost:8002/api/patients/${id}`)
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const p = data.patient
        alert(`Patient Details:\nName: ${p.first_name} ${p.last_name}\nDOB: ${formatDate(p.date_of_birth)}\nGender: ${p.gender}\nService: ${p.service}\nRank: ${p.rank}\nContact: ${p.contact_number}`)
      } else {
        alert(`Error: ${data.message}`)
      }
    })
    .catch(err => {
      alert(`Error loading patient details: ${err.message}`)
    })
}

function editPatient(id) {
  window.location.href = `edit_patient.html?id=${id}`
}

onMounted(() => {
  loadDashboardStats()
  loadPatientData()
})
</script>

<style scoped>
</style>
