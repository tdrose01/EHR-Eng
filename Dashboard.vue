<template>
  <div class="min-h-screen bg-gray-100 p-4">
    <header class="flex justify-between items-center bg-white shadow p-4 mb-4">
      <h1 class="text-xl font-semibold">AF EHR System</h1>
      <div>
        <span class="mr-4" v-text="username"></span>
        <button class="bg-blue-500 text-white px-3 py-1 rounded" @click="logout">Logout</button>
      </div>
    </header>
    <main>
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="bg-white p-4 rounded shadow" v-for="card in stats" :key="card.label">
          <div class="text-3xl font-bold text-blue-600" v-text="card.value"></div>
          <div class="text-sm" v-text="card.label"></div>
        </div>
      </div>
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-lg font-semibold mb-2">Recent Patients</h2>
        <ul>
          <li v-for="patient in patients" :key="patient.patient_id" class="flex justify-between py-1 border-b last:border-none">
            <span>{{ patient.last_name }}, {{ patient.first_name }}</span>
            <span class="text-sm" v-text="formatDate(patient.date_of_birth)"></span>
          </li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const username = ref(localStorage.getItem('ehrUsername') || '')
const stats = ref([
  { label: 'Total Patients', value: '--' },
  { label: "Today's Appointments", value: '--' }
])
const patients = ref([])

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function logout() {
  localStorage.removeItem('ehrToken')
  localStorage.removeItem('ehrUsername')
  window.location.href = 'login.html'
}

async function loadStats() {
  try {
    const res = await fetch('http://localhost:8002/api/dashboard-stats')
    const data = await res.json()
    if (data.success) {
      stats.value = [
        { label: 'Total Patients', value: data.stats.totalPatients },
        { label: "Today's Appointments", value: data.stats.appointmentsToday }
      ]
    }
  } catch (err) {
    stats.value = [
      { label: 'Total Patients', value: 100 },
      { label: "Today's Appointments", value: 12 }
    ]
  }
}

async function loadRecentPatients() {
  try {
    const res = await fetch('http://localhost:8002/api/patients?limit=5')
    const data = await res.json()
    if (data.success) {
      patients.value = data.patients
    }
  } catch (err) {
    patients.value = []
  }
}

onMounted(() => {
  loadStats()
  loadRecentPatients()
})
</script>

<style scoped>
</style>

