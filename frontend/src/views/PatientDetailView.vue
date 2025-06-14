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
          <div class="flex items-center justify-between mb-6">
            <button class="btn bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded" @click="navigateTo('patients_list.html?filter=all')">← Back to Patients</button>
            <button class="btn bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded" @click="editPatient(patient.patient_id)">Edit Patient</button>
          </div>
          <h2 class="text-2xl font-bold text-blue-400 mb-4">Patient Detail</h2>
          <div class="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Patient ID:</span> {{ patient.patient_id }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Full Name:</span> {{ patient.last_name }}, {{ patient.first_name }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Date of Birth:</span> {{ formatDate(patient.date_of_birth) }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Gender:</span> {{ patient.gender }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Phone Number:</span> {{ patient.contact_number }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Email:</span> {{ patient.email }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Address:</span> {{ patient.address }}</div>
              </div>
              <div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Service:</span> {{ patient.service }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Rank:</span> {{ patient.rank }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Blood Type:</span> {{ patient.blood_type }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Insurance:</span> {{ patient.insurance_provider }}</div>
                <div class="mb-2"><span class="font-semibold text-blue-400">Insurance Number:</span> {{ patient.insurance_number }}</div>
              </div>
            </div>
          </div>
          <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div class="flex gap-4 border-b border-gray-700 mb-4">
              <button :class="['px-4 py-2 font-semibold', activeTab === 'overview' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400']" @click="activeTab = 'overview'">Overview</button>
              <button :class="['px-4 py-2 font-semibold', activeTab === 'records' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400']" @click="activeTab = 'records'">Medical Records</button>
            </div>
            <div v-if="activeTab === 'overview'">
              <h3 class="text-lg font-semibold text-blue-400 mb-2">Patient Overview</h3>
              <p class="text-gray-300">{{ patient.notes || 'No additional notes.' }}</p>
            </div>
            <div v-else-if="activeTab === 'records'">
              <h3 class="text-lg font-semibold text-blue-400 mb-2">Medical Records</h3>
              <ul>
                <li v-for="record in records" :key="record.record_id" class="mb-2">
                  <span class="font-semibold text-blue-400">{{ record.date }}:</span> {{ record.description }}
                </li>
                <li v-if="records.length === 0" class="text-gray-400">No medical records found.</li>
              </ul>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '../components/AppSidebar.vue'

const route = useRoute()
const patient = ref({})
const records = ref([])
const activeTab = ref('overview')

const username = ref(localStorage.getItem('ehrUsername') || 'User')
const dropdownOpen = ref(false)
const showChangePassword = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const changePasswordStatus = ref('')
const changePasswordStatusType = ref('')

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

function fetchPatient() {
  const id = route.query.id
  fetch(`http://localhost:8002/api/patients/${id}`)
    .then(res => res.json())
    .then(data => {
      patient.value = data.patient || {}
    })
    .catch(() => {
      patient.value = {}
    })
}

function fetchRecords() {
  const id = route.query.id
  fetch(`http://localhost:8002/api/patients/${id}/records`)
    .then(res => res.json())
    .then(data => {
      records.value = data.records || []
    })
    .catch(() => {
      records.value = []
    })
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
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
  fetchPatient()
  fetchRecords()
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
</style>
