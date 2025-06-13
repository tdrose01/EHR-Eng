<template>
  <aside class="w-60 bg-gray-800 rounded p-4 text-gray-100 space-y-2">
    <div
      v-for="item in items"
      :key="item.text"
      @click="navigate(item.link)"
      :class="['flex items-center px-3 py-2 rounded cursor-pointer hover:bg-gray-700', active === item.text ? 'bg-gray-700 border-l-4 border-blue-500' : '']"
    >
      <span class="mr-2">{{ item.icon }}</span>
      <span>{{ item.text }}</span>
    </div>
  </aside>
</template>

<script setup>
const props = defineProps({
  active: String
})

const items = [
  { text: 'Dashboard', icon: '📊', link: 'dashboard.html' },
  { text: 'Patients', icon: '👥', link: 'patients_list.html' },
  { text: 'Appointments', icon: '📅', link: 'appointments.html' },
  { text: 'Medical Records', icon: '📋', link: 'records.html' },
  { text: 'Medications', icon: '💊', link: '#' },
  { text: 'Settings', icon: '⚙️', link: '#' }
]

function navigate(url) {
  if (url) window.location.href = url
}
</script>

<style scoped>
</style>
