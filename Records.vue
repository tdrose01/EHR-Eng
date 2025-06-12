<template>
  <div class="max-w-xl mx-auto mt-10">
    <h1 class="text-2xl font-semibold mb-4">Medical Records</h1>
    <ul class="bg-white rounded shadow divide-y">
      <li v-for="r in records" :key="r.id" class="p-2">
        {{ r.date }} - {{ r.note }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      records: [
        { id: 1, date: '2025-01-01', note: 'Annual checkup' },
        { id: 2, date: '2025-03-15', note: 'Blood test' }
      ]
    };
  }
};
</script>
