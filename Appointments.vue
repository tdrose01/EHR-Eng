<template>
  <div class="max-w-xl mx-auto mt-10">
    <h1 class="text-2xl font-semibold mb-4">Appointments</h1>
    <ul class="bg-white rounded shadow divide-y">
      <li v-for="a in appointments" :key="a.id" class="p-2">
        <span class="font-medium">{{ a.date }}</span> with {{ a.patient }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      appointments: [
        { id: 1, date: '2025-07-01', patient: 'John Doe' },
        { id: 2, date: '2025-07-02', patient: 'Jane Smith' }
      ]
    };
  }
};
</script>
