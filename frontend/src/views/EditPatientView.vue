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
          <h2 class="text-2xl font-bold text-blue-400 mb-4">Edit Patient</h2>
          <div class="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <form @submit.prevent="updatePatient">
              <!-- Form fields for patient info, insurance, etc. -->
              <!-- Use v-model for two-way binding and Tailwind for styling -->
              <!-- Example: -->
              <div class="mb-4">
                <label class="block mb-1 text-gray-400">First Name</label>
                <input v-model="patient.first_name" type="text" class="w-full px-4 py-2 rounded bg-gray-900 border border-gray-700 text-gray-100" required />
              </div>
              <!-- Add all other fields similarly -->
              <div class="flex gap-2 mt-6">
                <button type="submit" class="btn bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded">Save Changes</button>
                <button type="button" class="btn bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded" @click="navigateTo('patients_list.html?filter=all')">Cancel</button>
              </div>
              <div v-if="statusMessage" :class="['mt-4', statusType === 'success' ? 'text-green-400' : 'text-red-400']">{{ statusMessage }}</div>
            </form>
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
const statusMessage = ref('')
const statusType = ref('')

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

function updatePatient() {
  const id = route.query.id
  fetch(`http://localhost:8002/api/patients/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patient.value)
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
        statusMessage.value = 'Patient updated successfully!'
        statusType.value = 'success'
      } else {
        throw new Error(data.message || 'Update failed')
      }
    })
    .catch(error => {
      statusMessage.value = error.message || 'Error updating patient'
      statusType.value = 'error'
    })
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