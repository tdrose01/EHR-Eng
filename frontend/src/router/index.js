import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import PatientsListView from '../views/PatientsListView.vue'
import PatientDetailView from '../views/PatientDetailView.vue'
import EditPatientView from '../views/EditPatientView.vue'
import AddPatientView from '../views/AddPatientView.vue'
import AppointmentsView from '../views/AppointmentsView.vue'
import RecordsView from '../views/RecordsView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/dashboard', component: DashboardView },
  { path: '/patients', component: PatientsListView },
  { path: '/patients/:id', component: PatientDetailView, props: true },
  { path: '/patients/:id/edit', component: EditPatientView, props: true },
  { path: '/add-patient', component: AddPatientView },
  { path: '/appointments', component: AppointmentsView },
  { path: '/records', component: RecordsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const publicPages = ['/login']
  const authRequired = !publicPages.includes(to.path)
  const token = localStorage.getItem('ehrToken')
  if (authRequired && !token) {
    return next('/login')
  }
  next()
})

export default router 