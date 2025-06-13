<template>
  <div class="bg-gray-800 border border-gray-700 rounded p-4 text-center cursor-pointer hover:bg-gray-700" @click="navigate">
    <div class="text-3xl font-bold text-blue-400">{{ value }}</div>
    <div class="text-sm text-gray-400">{{ label }}</div>
  </div>
</template>

<script setup>
const props = defineProps({
  label: String,
  value: [String, Number],
  link: String
})

function navigate() {
  if (props.link) window.location.href = props.link
}
</script>

<style scoped>
</style>
