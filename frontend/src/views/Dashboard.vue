<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-900">Kasper Management</h1>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-600">{{ auth.user?.full_name }}</span>
        <span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">{{ roleLabel }}</span>
        <button @click="handleLogout" class="text-sm text-gray-500 hover:text-red-500 transition-colors">Выйти</button>
      </div>
    </nav>
    <main class="max-w-6xl mx-auto px-6 py-8">
      <h2 class="text-2xl font-semibold text-gray-800 mb-2">Добро пожаловать, {{ auth.user?.full_name }}</h2>
      <p class="text-gray-500">Выберите раздел для работы</p>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mt-8">
        <router-link v-for="section in sections" :key="section.name" :to="section.to || '#'"
          class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow block">
          <div class="text-3xl mb-3">{{ section.icon }}</div>
          <h3 class="font-semibold text-gray-800">{{ section.name }}</h3>
          <p class="text-sm text-gray-500 mt-1">{{ section.desc }}</p>
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const roleLabel = computed(() => ({
  admin: 'Администратор', manager: 'Руководитель', hr: 'HR'
}[auth.user?.role] || ''))

function handleLogout() {
  auth.logout()
  router.push('/login')
}

const sections = [
  { icon: '📅', name: 'Собеседования', desc: 'Календарь и список кандидатов', to: '/interviews' },
  { icon: '✍️', name: 'Прописи', desc: 'Ручной поиск в соцсетях', to: '/inscriptions' },
  { icon: '📋', name: 'Анкеты', desc: 'Личные дела сотрудников', to: '/candidates' },
  { icon: '✅', name: 'Задачи', desc: 'План на день, неделю, месяц', to: '/tasks' },
  { icon: '📢', name: 'Реклама', desc: 'Публикации в соцсетях', to: '#' },
  { icon: '📊', name: 'TikTok', desc: 'Статистика эфиров', to: '#' },
]
</script>
