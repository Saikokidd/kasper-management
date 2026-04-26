import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Interviews from '../views/Interviews.vue'
import Inscriptions from '../views/Inscriptions.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/interviews', component: Interviews, meta: { requiresAuth: true } },
  { path: '/inscriptions', component: Inscriptions, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'
  if (to.path === '/login' && auth.isAuthenticated) return '/'
})

export default router
