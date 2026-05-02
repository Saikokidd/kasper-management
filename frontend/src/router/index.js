import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Interviews from '../views/Interviews.vue'
import Inscriptions from '../views/Inscriptions.vue'
import Candidates from '../views/Candidates.vue'
import CandidateDetail from '../views/CandidateDetail.vue'
import Tasks from '../views/Tasks.vue'
import Ads from '../views/Ads.vue'
import JobPosts from '../views/JobPosts.vue'
import TiktokStreams from '../views/TiktokStreams.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/interviews', component: Interviews, meta: { requiresAuth: true } },
  { path: '/inscriptions', component: Inscriptions, meta: { requiresAuth: true } },
  { path: '/candidates', component: Candidates, meta: { requiresAuth: true } },
  { path: '/candidates/:id', component: CandidateDetail, meta: { requiresAuth: true } },
  { path: '/tasks', component: Tasks, meta: { requiresAuth: true } },
  { path: '/ads', component: Ads, meta: { requiresAuth: true } },
  { path: '/job-posts', component: JobPosts, meta: { requiresAuth: true } },
  { path: '/tiktok', component: TiktokStreams, meta: { requiresAuth: true } },
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
