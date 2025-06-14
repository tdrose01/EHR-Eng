<template>
  <div class="min-h-screen bg-gray-900 text-gray-100">
    <header class="bg-gray-800 flex justify-between items-center px-6 py-4 border-b border-gray-700">
      <div class="flex items-center gap-2">
        <h1 class="text-xl font-bold text-blue-400">AF EHR System</h1>
      </div>
      <div class="relative flex items-center gap-4">
        <span class="font-medium cursor-pointer" @click="toggleDropdown">{{ username || 'User' }}</span>
        <div v-if="dropdownOpen" class="absolute right-0 top-full mt-2 bg-gray-800 border border-gray-700 rounded shadow-lg z-10 min-w-[150px] flex flex-col">
          <button @click="toggleChangePassword" class="px-4 py-2 text-left hover:bg-blue-100/10">Change Password</button>
          <button @click="logout" class="px-4 py-2 text-left hover:bg-blue-100/10">Logout</button>
        </div>
      </div>
    </header>
    <div v-if="showChangePassword" class="max-w-xs mx-auto mt-6 bg-gray-800 p-6 rounded shadow flex flex-col gap-3 border border-gray-700">
      <label for="oldPassword">Enter your current password to confirm changes</label>
      <input v-model="oldPassword" type="password" id="oldPassword" placeholder="Current password" class="px-3 py-2 rounded bg-gray-900 border border-gray-700 text-gray-100" />
      <label for="newPassword">Enter your new password</label>
      <input v-model="newPassword" type="password" id="newPassword" placeholder="New password" class="px-3 py-2 rounded bg-gray-900 border border-gray-700 text-gray-100" />
      <button @click="changePassword" class="btn bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded">Update Password</button>
      <div v-if="changePasswordStatus" :class="['mt-2 text-center', changePasswordStatusType === 'success' ? 'text-green-400' : 'text-red-400']">{{ changePasswordStatus }}</div>
    </div>
    <div class="container mx-auto px-4 py-8">
      <div class="flex gap-6">
        <AppSidebar />
        <main class="flex-1">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div class="stat-card bg-gray-800 border border-gray-700 rounded-lg p-6 text-center cursor-pointer hover:bg-blue-100/10" @click="navigateTo('patients_list.html?filter=all')">
              <div class="stat-value text-3xl font-bold text-blue-400">{{ stats.totalPatients ?? '--' }}</div>
              <div class="stat-label text-gray-400 mt-2">Total Patients</div>
            </div>
            <div class="stat-card bg-gray-800 border border-gray-700 rounded-lg p-6 text-center cursor-pointer hover:bg-blue-100/10" @click="navigateTo('patients_list.html?filter=active')">
              <div class="stat-value text-3xl font-bold text-blue-400">{{ stats.activePatients ?? '--' }}</div>
              <div class="stat-label text-gray-400 mt-2">Active Patients</div>
            </div>
            <div class="stat-card bg-gray-800 border border-gray-700 rounded-lg p-6 text-center cursor-pointer hover:bg-blue-100/10" @click="navigateTo('appointments.html?filter=today')">
              <div class="stat-value text-3xl font-bold text-blue-400">{{ stats.appointmentsToday ?? '--' }}</div>
              <div class="stat-label text-gray-400 mt-2">Today's Appointments</div>
            </div>
            <div class="stat-card bg-gray-800 border border-gray-700 rounded-lg p-6 text-center cursor-pointer hover:bg-blue-100/10" @click="navigateTo('records.html?filter=pending')">
              <div class="stat-value text-3xl font-bold text-blue-400">{{ stats.pendingRecords ?? '--' }}</div>
              <div class="stat-label text-gray-400 mt-2">Pending Records</div>
            </div>
          </div>
          <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-blue-400">Recent Patients</h3>
              <div class="flex gap-2">
                <button class="btn bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded" @click="navigateTo('add_patient.html')">Add Patient</button>
                <button class="btn bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded" @click="fetchPatients">Refresh</button>
              </div>
            </div>
            <div class="flex mb-4">
              <input v-model="search" @keyup.enter="fetchPatients" type="text" placeholder="Search patients..." class="flex-1 px-4 py-2 rounded-l bg-gray-900 border border-gray-700 text-gray-100" />
              <button @click="fetchPatients" class="px-4 py-2 rounded-r bg-blue-500 hover:bg-blue-600 text-white font-semibold">Search</button>
            </div>
            <div v-if="loadingPatients" class="flex flex-col items-center justify-center py-8">
              <div class="loader mb-2"></div>
              <p>Loading patient data...</p>
            </div>
            <table v-else class="w-full text-left border-collapse">
              <thead>
                <tr>
                  <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Patient ID</th>
                  <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Name</th>
                  <th class="py-2 px-3 border-b border-gray-700 text-blue-400">DOB</th>
                  <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Service</th>
                  <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Rank</th>
                  <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Blood Type</th>
                  <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Contact</th>
                  <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="patient in patients" :key="patient.patient_id" class="hover:bg-blue-100/5">
                  <td class="py-2 px-3">{{ patient.patient_id }}</td>
                  <td class="py-2 px-3">{{ patient.last_name }}, {{ patient.first_name }}</td>
                  <td class="py-2 px-3">{{ formatDate(patient.date_of_birth) }}</td>
                  <td class="py-2 px-3">{{ patient.service || 'N/A' }}</td>
                  <td class="py-2 px-3">{{ patient.rank || 'N/A' }}</td>
                  <td class="py-2 px-3">{{ patient.blood_type || 'Unknown' }}</td>
                  <td class="py-2 px-3">{{ patient.contact_number || 'N/A' }}</td>
                  <td class="py-2 px-3">
                    <div class="flex gap-2">
                      <button class="text-blue-400 hover:underline" @click="viewPatient(patient.patient_id)">View</button>
                      <button class="text-yellow-400 hover:underline" @click="editPatient(patient.patient_id)">Edit</button>
                    </div>
                  </td>
                </tr>
                <tr v-if="patients.length === 0">
                  <td colspan="8" class="text-center py-4 text-gray-400">No patients found</td>
                </tr>
              </tbody>
            </table>
            <!-- Pagination can be added here if needed -->
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppSidebar from '../components/AppSidebar.vue'

const username = ref(localStorage.getItem('ehrUsername') || 'User')
const dropdownOpen = ref(false)
const showChangePassword = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const changePasswordStatus = ref('')
const changePasswordStatusType = ref('')

const stats = ref({})
const patients = ref([])
const search = ref('')
const loadingPatients = ref(false)

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

function toggleChangePassword() {
  showChangePassword.value = !showChangePassword.value
  dropdownOpen.value = false
}

function logout() {
  localStorage.removeItem('ehrToken')
  localStorage.removeItem('ehrUsername')
  window.location.href = 'login.html'
}

function changePassword() {
  changePasswordStatus.value = ''
  changePasswordStatusType.value = ''
  if (!oldPassword.value || !newPassword.value) {
    changePasswordStatus.value = 'Please fill in all fields.'
    changePasswordStatusType.value = 'error'
    return
  }
  fetch('http://localhost:8001/api/change-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: username.value,
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
  })
    .then(async response => {
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Server error')
      }
      return response.json()
    })
    .then(data => {
      if (data.success) {
        changePasswordStatus.value = 'Password updated successfully!'
        changePasswordStatusType.value = 'success'
        oldPassword.value = ''
        newPassword.value = ''
        setTimeout(() => {
          showChangePassword.value = false
          changePasswordStatus.value = ''
        }, 1500)
      } else {
        throw new Error(data.message || 'Password update failed')
      }
    })
    .catch(error => {
      changePasswordStatus.value = error.message || 'Error updating password'
      changePasswordStatusType.value = 'error'
    })
}

function fetchStats() {
  fetch('http://localhost:8002/api/dashboard-stats')
    .then(res => res.json())
    .then(data => {
      stats.value = data.stats || {}
    })
    .catch(() => {
      stats.value = {}
    })
}

function fetchPatients() {
  loadingPatients.value = true
  let url = 'http://localhost:8002/api/patients?limit=10&offset=0'
  if (search.value) {
    url += `&search=${encodeURIComponent(search.value)}`
  }
  fetch(url)
    .then(res => res.json())
    .then(data => {
      patients.value = data.patients || []
    })
    .catch(() => {
      patients.value = []
    })
    .finally(() => {
      loadingPatients.value = false
    })
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function viewPatient(id) {
  window.location.href = `patient_detail.html?id=${id}`
}

function editPatient(id) {
  window.location.href = `edit_patient.html?id=${id}`
}

function navigateTo(url) {
  window.location.href = url
}

onMounted(() => {
  const token = localStorage.getItem('ehrToken')
  if (!token) {
    window.location.href = 'login.html'
    return
  }
  fetchStats()
  fetchPatients()
  document.addEventListener('click', (e) => {
    if (!(e.target.closest('.user-info'))) {
      dropdownOpen.value = false
    }
  })
})
</script>

<style scoped>
.btn {
  @apply bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded;
}
.loader {
  display: inline-block;
  width: 32px;
  height: 32px;
  border: 4px solid rgba(255,255,255,.2);
  border-radius: 50%;
  border-top-color: #4d8bf0;
  animation: spin 1s ease-in-out infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
