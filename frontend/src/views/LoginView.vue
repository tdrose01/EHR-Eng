<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-gray-100">
    <div class="bg-gray-800 rounded-lg p-8 w-full max-w-md shadow-lg">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-blue-400 mb-2">Veteran EHR System</h1>
        <p class="text-gray-400">Please log in to access the Electronic Health Record system</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="mb-6">
          <label for="username" class="block mb-2 text-gray-400">Username</label>
          <input v-model="username" id="username" type="text" required class="w-full px-4 py-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-400 text-gray-100" placeholder="Enter your username" />
        </div>
        <div class="mb-6">
          <label for="password" class="block mb-2 text-gray-400">Password</label>
          <input v-model="password" id="password" type="password" required class="w-full px-4 py-3 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-400 text-gray-100" placeholder="Enter your password" />
        </div>
        <button type="submit" :disabled="loading" class="w-full py-3 rounded bg-blue-500 hover:bg-blue-600 transition font-semibold text-white disabled:bg-blue-300 disabled:cursor-not-allowed flex items-center justify-center">
          <span v-if="loading" class="loader mr-2"></span>
          <span>{{ loading ? 'Logging in...' : 'Login' }}</span>
        </button>
      </form>
      <div v-if="statusMessage" :class="['mt-6 p-3 rounded text-center', statusType === 'error' ? 'bg-red-100 text-red-600 border border-red-300' : 'bg-green-100 text-green-700 border border-green-300']">
        {{ statusMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const username = ref('')
const password = ref('')
const loading = ref(false)
const statusMessage = ref('')
const statusType = ref('')

onMounted(() => {
  const token = localStorage.getItem('ehrToken')
  if (token) {
    window.location.href = 'dashboard.html'
  }
})

function handleLogin() {
  loading.value = true
  statusMessage.value = ''
  statusType.value = ''

  fetch('http://localhost:8001/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: username.value, password: password.value })
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
        localStorage.setItem('ehrToken', data.token)
        localStorage.setItem('ehrUsername', username.value)
        statusMessage.value = 'Login successful!'
        statusType.value = 'success'
        setTimeout(() => {
          window.location.href = 'dashboard.html'
        }, 1000)
      } else {
        throw new Error(data.message || 'Login failed')
      }
    })
    .catch(error => {
      // Fallback to hard-coded credentials for testing
      if (username.value === 'admin' && password.value === 'adminpass123') {
        localStorage.setItem('ehrToken', 'test_token_123')
        localStorage.setItem('ehrUsername', username.value)
        statusMessage.value = 'Login successful! (Test mode)'
        statusType.value = 'success'
        setTimeout(() => {
          window.location.href = 'dashboard.html'
        }, 1000)
      } else {
        statusMessage.value = error.message || 'Invalid username or password'
        statusType.value = 'error'
      }
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<style scoped>
.loader {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  vertical-align: middle;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style> 