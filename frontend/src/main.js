import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import router from './router/index.js'
import App from './App.vue'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Глобальный interceptor — добавляет токен к каждому запросу
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

import { useAuthStore } from './stores/auth'
const auth = useAuthStore()
auth.initAuth()

app.mount('#app')