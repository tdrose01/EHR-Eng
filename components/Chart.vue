<template>
  <div class="bg-gray-800 p-4 rounded">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const canvas = ref(null)

onMounted(async () => {
  try {
    const mod = await import('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.esm.js')
    const { Chart, registerables } = mod
    Chart.register(...registerables)
    new Chart(canvas.value, {
      type: 'bar',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{ label: 'Appointments', data: [5, 6, 4, 8, 3, 2, 1], backgroundColor: '#4d8bf0' }]
      },
      options: { plugins: { legend: { display: false } } }
    })
  } catch (e) {
    console.error('Chart failed to load', e)
  }
})
</script>

<style scoped>
</style>
