<template>
  <div class="max-w-xl mx-auto mt-10">
    <h1 class="text-2xl font-semibold mb-4">Patient Detail</h1>
    <div class="bg-white rounded shadow p-4">
      <p><strong>ID:</strong> {{ patient.id }}</p>
      <p><strong>Name:</strong> {{ patient.name }}</p>
      <p><strong>DOB:</strong> {{ patient.dob }}</p>
      <p><strong>Phone:</strong> {{ patient.phone }}</p>
      <p><strong>Email:</strong> {{ patient.email }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      patient: {
        id: 1,
        name: 'John Doe',
        dob: '1980-01-01',
        phone: '555-5555',
        email: 'john@example.com'
      }
    };
  }
};
</script>
