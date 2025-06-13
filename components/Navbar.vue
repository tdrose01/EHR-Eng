<template>
  <header class="flex justify-between items-center bg-gray-800 border-b border-gray-700 px-4 py-3 text-gray-100">
    <h1 class="text-xl font-semibold text-blue-400">AF EHR System</h1>
    <div class="relative">
      <span class="cursor-pointer" @click="toggleDropdown">{{ username }}</span>
      <div v-if="showDropdown" class="absolute right-0 mt-2 bg-gray-800 border border-gray-700 rounded shadow flex flex-col text-sm">
        <button class="px-4 py-2 text-left hover:bg-gray-700" @click="toggleChangePass">Change Password</button>
        <button class="px-4 py-2 text-left hover:bg-gray-700" @click="logout">Logout</button>
      </div>
    </div>
  </header>
  <div v-if="showChangePass" class="bg-gray-700 p-4 space-y-2 text-gray-100">
    <label class="block text-sm">Current Password
      <input v-model="oldPass" type="password" class="w-full mt-1 p-1 bg-gray-800 border border-gray-600 rounded" />
    </label>
    <label class="block text-sm">New Password
      <input v-model="newPass" type="password" class="w-full mt-1 p-1 bg-gray-800 border border-gray-600 rounded" />
    </label>
    <button class="bg-blue-500 text-white px-3 py-1 rounded" @click="updatePassword">Update Password</button>
    <div v-if="statusMessage" :class="statusClass" class="text-sm">{{ statusMessage }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const username = ref(localStorage.getItem('ehrUsername') || 'User')
const showDropdown = ref(false)
const showChangePass = ref(false)
const oldPass = ref('')
const newPass = ref('')
const statusMessage = ref('')
const statusClass = ref('')

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

function toggleChangePass() {
  showChangePass.value = !showChangePass.value
  showDropdown.value = false
}

async function updatePassword() {
  try {
    const res = await fetch('http://localhost:8001/api/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, old_password: oldPass.value, new_password: newPass.value })
    })
    const data = await res.json()
    if (data.success) {
      statusClass.value = 'text-green-500'
      statusMessage.value = 'Password updated successfully.'
      oldPass.value = ''
      newPass.value = ''
    } else {
      statusClass.value = 'text-red-500'
      statusMessage.value = data.message
    }
  } catch (err) {
    statusClass.value = 'text-red-500'
    statusMessage.value = 'Error updating password'
  }
}

function logout() {
  localStorage.removeItem('ehrToken')
  localStorage.removeItem('ehrUsername')
  window.location.href = 'login.html'
}
</script>

<style scoped>
</style>
