<template>
  <div class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="bg-white p-6 rounded shadow-md w-80" id="app">
      <h1 class="text-xl font-semibold mb-4 text-center">Login</h1>
      <input v-model="username" type="text" placeholder="Username" class="mb-2 p-2 border w-full rounded" />
      <input v-model="password" type="password" placeholder="Password" class="mb-2 p-2 border w-full rounded" />
      <p v-if="statusMessage" :class="messageClass" class="text-center mb-2">{{ statusMessage }}</p>
      <button @click="login" :disabled="loading" class="w-full bg-blue-500 hover:bg-blue-600 text-white p-2 rounded">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const username = ref('')
const password = ref('')
const loading = ref(false)
const statusMessage = ref('')
const messageType = ref('')

const messageClass = computed(() => {
  return messageType.value === 'error' ? 'text-red-600' : 'text-green-600'
})

async function login() {
  loading.value = true
  statusMessage.value = ''
  messageType.value = ''
  try {
    const response = await fetch('http://localhost:8001/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: username.value, password: password.value })
    })
    const data = await response.json()
    if (!response.ok || !data.success) {
      throw new Error(data.message || 'Invalid username or password')
    }
    localStorage.setItem('ehrToken', data.token)
    localStorage.setItem('ehrUsername', username.value)
    statusMessage.value = 'Login successful!'
    messageType.value = 'success'
    setTimeout(() => {
      window.location.href = 'dashboard.html'
    }, 1000)
  } catch (err) {
    statusMessage.value = err.message
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
</style>
