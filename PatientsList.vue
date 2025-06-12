<template>
  <div class="max-w-2xl mx-auto mt-10">
    <h1 class="text-2xl font-semibold mb-4">Patients</h1>
    <table class="min-w-full bg-white border">
      <thead>
        <tr class="bg-gray-200">
          <th class="px-2 py-1 text-left">ID</th>
          <th class="px-2 py-1 text-left">Name</th>
          <th class="px-2 py-1 text-left">DOB</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in patients" :key="p.id" class="border-t">
          <td class="px-2 py-1">{{ p.id }}</td>
          <td class="px-2 py-1">{{ p.name }}</td>
          <td class="px-2 py-1">{{ p.dob }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      patients: [
        { id: 1, name: 'John Doe', dob: '1980-01-01' },
        { id: 2, name: 'Jane Smith', dob: '1975-05-12' }
      ]
    };
  }
};
</script>
