<template>
  <div class="max-w-sm mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden flex flex-col items-center p-6 space-y-4">
    <img :src="avatarUrl" alt="User avatar" class="w-24 h-24 rounded-full object-cover" />
    <div class="text-center">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ name }}</h2>
      <p class="text-sm text-gray-500 dark:text-gray-400">@{{ username }}</p>
    </div>
    <p class="text-center text-gray-700 dark:text-gray-300">
      {{ bio }}
    </p>
  </div>
</template>

<script setup>
const props = defineProps({
  avatarUrl: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  username: {
    type: String,
    required: true
  },
  bio: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
</style>
