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
          <h2 class="text-2xl font-bold text-blue-400 mb-4">Appointments</h2>
          <div class="flex mb-4">
            <input v-model="search" @keyup.enter="fetchAppointments" type="text" placeholder="Search appointments..." class="flex-1 px-4 py-2 rounded-l bg-gray-900 border border-gray-700 text-gray-100" />
            <button @click="fetchAppointments" class="px-4 py-2 rounded-r bg-blue-500 hover:bg-blue-600 text-white font-semibold">Search</button>
          </div>
          <div class="flex gap-2 mb-4">
            <button v-for="tab in filterTabs" :key="tab.value" :class="['px-4 py-2 rounded', filter === tab.value ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-100']" @click="setFilter(tab.value)">{{ tab.label }}</button>
          </div>
          <div v-if="loadingAppointments" class="flex flex-col items-center justify-center py-8">
            <div class="loader mb-2"></div>
            <p>Loading appointment data...</p>
          </div>
          <table v-else class="w-full text-left border-collapse">
            <thead>
              <tr>
                <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Appointment ID</th>
                <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Patient</th>
                <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Date</th>
                <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Time</th>
                <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Status</th>
                <th class="py-2 px-3 border-b border-gray-700 text-blue-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in appointments" :key="appt.appointment_id" class="hover:bg-blue-100/5">
                <td class="py-2 px-3">{{ appt.appointment_id }}</td>
                <td class="py-2 px-3">{{ appt.patient_name }}</td>
                <td class="py-2 px-3">{{ formatDate(appt.date) }}</td>
                <td class="py-2 px-3">{{ appt.time }}</td>
                <td class="py-2 px-3">
                  <span :class="['badge', appt.status === 'Completed' ? 'badge-success' : appt.status === 'Cancelled' ? 'badge-danger' : 'badge-warning']">{{ appt.status }}</span>
                </td>
                <td class="py-2 px-3">
                  <div class="flex gap-2">
                    <button class="text-blue-400 hover:underline" @click="viewAppointment(appt.appointment_id)">View</button>
                    <button class="text-yellow-400 hover:underline" @click="editAppointment(appt.appointment_id)">Edit</button>
                  </div>
                </td>
              </tr>
              <tr v-if="appointments.length === 0">
                <td colspan="6" class="text-center py-4 text-gray-400">No appointments found</td>
              </tr>
            </tbody>
          </table>
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

const appointments = ref([])
const search = ref('')
const filter = ref('today')
const loadingAppointments = ref(false)

const filterTabs = [
  { label: 'Today', value: 'today' },
  { label: 'Upcoming', value: 'upcoming' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
]

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

function fetchAppointments() {
  loadingAppointments.value = true
  let url = `http://localhost:8003/api/appointments?filter=${filter.value}`
  if (search.value) {
    url += `&search=${encodeURIComponent(search.value)}`
  }
  fetch(url)
    .then(res => res.json())
    .then(data => {
      appointments.value = data.appointments || []
    })
    .catch(() => {
      appointments.value = []
    })
    .finally(() => {
      loadingAppointments.value = false
    })
}

function setFilter(val) {
  filter.value = val
  fetchAppointments()
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function viewAppointment(id) {
  // Implement view logic or navigation
}

function editAppointment(id) {
  // Implement edit logic or navigation
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
  fetchAppointments()
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
.badge {
  @apply px-2 py-1 rounded text-xs font-semibold;
}
.badge-success {
  @apply bg-green-700 text-green-200;
}
.badge-danger {
  @apply bg-red-700 text-red-200;
}
.badge-warning {
  @apply bg-yellow-700 text-yellow-200;
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