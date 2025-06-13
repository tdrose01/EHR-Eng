<template>
  <div class="max-w-5xl mx-auto mt-10">
    <h1 class="text-2xl font-semibold mb-4">Patients</h1>
    <table class="min-w-full bg-white border">
      <thead class="bg-gray-200">
        <tr>
          <th class="px-2 py-1 text-left">ID</th>
          <th class="px-2 py-1 text-left">Name</th>
          <th class="px-2 py-1 text-left">DOB</th>
          <th class="px-2 py-1 text-left">Service</th>
          <th class="px-2 py-1 text-left">Rank</th>
          <th class="px-2 py-1 text-left">Blood Type</th>
          <th class="px-2 py-1 text-left">Contact</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in props.patients" :key="p.patient_id" class="border-t">
          <td class="px-2 py-1">{{ p.patient_id }}</td>
          <td class="px-2 py-1">{{ p.last_name }}, {{ p.first_name }}</td>
          <td class="px-2 py-1">{{ formatDate(p.date_of_birth) }}</td>
          <td class="px-2 py-1">{{ p.service }}</td>
          <td class="px-2 py-1">{{ p.rank }}</td>
          <td class="px-2 py-1">{{ p.blood_type }}</td>
          <td class="px-2 py-1">{{ p.contact_number }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
const props = defineProps({
  patients: {
    type: Array,
    default: () => [
      {
        patient_id: 1,
        first_name: 'Stacey',
        last_name: 'Calderon',
        date_of_birth: '1985-07-12',
        service: 'Army',
        rank: 'E-5',
        blood_type: 'A+',
        contact_number: '555-123-4567'
      },
      {
        patient_id: 2,
        first_name: 'Ian',
        last_name: 'Williams',
        date_of_birth: '1992-03-24',
        service: 'Navy',
        rank: 'O-3',
        blood_type: 'O-',
        contact_number: '555-987-6543'
      },
      {
        patient_id: 3,
        first_name: 'Michael',
        last_name: 'Castaneda',
        date_of_birth: '1978-11-05',
        service: 'Air Force',
        rank: 'E-7',
        blood_type: 'B+',
        contact_number: '555-345-6789'
      },
      {
        patient_id: 4,
        first_name: 'Matthew',
        last_name: 'Howard',
        date_of_birth: '1990-09-30',
        service: 'Marines',
        rank: 'E-4',
        blood_type: 'AB+',
        contact_number: '555-234-5678'
      },
      {
        patient_id: 5,
        first_name: 'Sophia',
        last_name: 'Torres',
        date_of_birth: '1982-05-17',
        service: 'Coast Guard',
        rank: 'O-2',
        blood_type: 'A-',
        contact_number: '555-876-5432'
      }
    ]
  }
})

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>
