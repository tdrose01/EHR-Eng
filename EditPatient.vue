<template>
  <div class="max-w-xl mx-auto bg-white p-4 rounded shadow mt-10">
    <h1 class="text-xl font-semibold mb-4">Edit Patient</h1>
    <form @submit.prevent="save">
      <div class="mb-2">
        <label class="block mb-1">First Name</label>
        <input v-model="form.firstName" type="text" class="border p-2 rounded w-full" required>
      </div>
      <div class="mb-2">
        <label class="block mb-1">Last Name</label>
        <input v-model="form.lastName" type="text" class="border p-2 rounded w-full" required>
      </div>
      <div class="mb-2">
        <label class="block mb-1">Date of Birth</label>
        <input v-model="form.dob" type="date" class="border p-2 rounded w-full" required>
      </div>
      <p v-if="saved" class="text-green-600 mb-2">Changes saved!</p>
      <button class="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded w-full">Save</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: { firstName: '', lastName: '', dob: '' },
      saved: false
    };
  },
  methods: {
    save() {
      this.saved = true;
    }
  }
};
</script>
