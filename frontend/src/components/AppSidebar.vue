<template>
  <aside class="w-64 bg-gray-800 rounded-lg p-6 flex-shrink-0 h-full">
    <nav>
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="menu-item flex items-center gap-2 py-2 px-3 rounded mb-2"
        :class="isActive(item.path) ? 'bg-blue-100/10 text-blue-400 font-semibold' : 'hover:bg-blue-100/10 text-gray-100'"
      >
        <span>{{ item.icon }}</span> {{ item.label }}
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { label: 'Patients', path: '/patients', icon: '👥' },
  { label: 'Appointments', path: '/appointments', icon: '📅' },
  { label: 'Medical Records', path: '/records', icon: '📋' },
  { label: 'Medications', path: '#', icon: '💊' },
  { label: 'Settings', path: '#', icon: '⚙️' },
]

const route = useRoute()
function isActive(path) {
  return route.path.startsWith(path)
}
</script>

<style scoped>
.menu-item {
  transition: background 0.2s, color 0.2s;
  cursor: pointer;
}
</style> 