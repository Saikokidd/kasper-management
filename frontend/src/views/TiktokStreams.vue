<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
      <router-link to="/" class="text-gray-400 hover:text-gray-600">← Назад</router-link>
      <h1 class="text-xl font-bold text-gray-900">TikTok — Эфиры</h1>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">

      <!-- Кнопка добавить -->
      <div class="flex justify-end mb-6">
        <button v-if="!auth.isPult" @click="openForm()"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          + Добавить эфир
        </button>
      </div>

      <!-- Форма -->
      <div v-if="showForm" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <h2 class="font-semibold text-gray-800 mb-4">{{ editingId ? 'Редактировать эфир' : 'Новый эфир' }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Дата эфира *</label>
            <input v-model="form.stream_date" type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">👁 Просмотров</label>
            <input v-model.number="form.views" type="number" min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">➕ Подписалось</label>
            <input v-model.number="form.subscriptions" type="number" min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">💬 Написало за работу</label>
            <input v-model.number="form.inquiries" type="number" min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div v-if="formError" class="text-red-500 text-sm mt-3">{{ formError }}</div>
        <div class="flex gap-3 mt-4">
          <button @click="submitForm"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            Сохранить
          </button>
          <button @click="resetForm"
            class="text-gray-500 hover:text-gray-700 px-4 py-2 rounded-lg text-sm transition-colors">
            Отмена
          </button>
        </div>
      </div>

      <!-- Загрузка -->
      <div v-if="store.loading" class="text-center py-12 text-gray-400">Загрузка...</div>

      <!-- Статистика сводная -->
      <div v-if="!store.loading && store.streams.length" class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <p class="text-2xl font-bold text-gray-900">{{ totalViews.toLocaleString('ru-RU') }}</p>
          <p class="text-sm text-gray-500 mt-1">👁 Просмотров</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <p class="text-2xl font-bold text-gray-900">{{ totalSubscriptions.toLocaleString('ru-RU') }}</p>
          <p class="text-sm text-gray-500 mt-1">➕ Подписалось</p>
        </div>
        <div class="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <p class="text-2xl font-bold text-gray-900">{{ totalInquiries.toLocaleString('ru-RU') }}</p>
          <p class="text-sm text-gray-500 mt-1">💬 За работу</p>
        </div>
      </div>

      <!-- Список -->
      <div v-if="!store.loading && store.streams.length" class="space-y-3">
        <div v-for="stream in store.streams" :key="stream.id"
          class="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-sm transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-3">
                <span class="text-lg">🎵</span>
                <span class="font-semibold text-gray-900">{{ formatDate(stream.stream_date) }}</span>
              </div>
              <div class="grid grid-cols-3 gap-4">
                <div class="text-center bg-gray-50 rounded-lg p-3">
                  <p class="text-xl font-bold text-gray-800">{{ stream.views.toLocaleString('ru-RU') }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">👁 Просмотров</p>
                </div>
                <div class="text-center bg-gray-50 rounded-lg p-3">
                  <p class="text-xl font-bold text-gray-800">{{ stream.subscriptions.toLocaleString('ru-RU') }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">➕ Подписалось</p>
                </div>
                <div class="text-center bg-gray-50 rounded-lg p-3">
                  <p class="text-xl font-bold text-gray-800">{{ stream.inquiries.toLocaleString('ru-RU') }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">💬 За работу</p>
                </div>
              </div>
              <p class="text-xs text-gray-300 mt-3">Добавил: {{ stream.created_by.full_name }}</p>
            </div>
            <div v-if="!auth.isPult" class="flex gap-2 ml-4 shrink-0">
              <button @click="openForm(stream)"
                class="text-xs text-blue-500 hover:text-blue-700 px-2 py-1 rounded transition-colors">
                Ред.
              </button>
              <button @click="removeStream(stream.id)"
                class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Пусто -->
      <div v-else-if="!store.loading" class="text-center py-16 text-gray-400">
        <p class="text-4xl mb-3">🎵</p>
        <p>Эфиров пока нет</p>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTiktokStreamsStore } from '../stores/tiktokStreams'
import { useAuthStore } from '../stores/auth'

const store = useTiktokStreamsStore()
const auth = useAuthStore()

const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)

const form = ref({
  stream_date: '',
  views: 0,
  subscriptions: 0,
  inquiries: 0,
})

const totalViews = computed(() => store.streams.reduce((s, r) => s + r.views, 0))
const totalSubscriptions = computed(() => store.streams.reduce((s, r) => s + r.subscriptions, 0))
const totalInquiries = computed(() => store.streams.reduce((s, r) => s + r.inquiries, 0))

function openForm(stream = null) {
  editingId.value = stream?.id || null
  form.value = {
    stream_date: stream?.stream_date ? stream.stream_date.slice(0, 16) : '',
    views: stream?.views ?? 0,
    subscriptions: stream?.subscriptions ?? 0,
    inquiries: stream?.inquiries ?? 0,
  }
  formError.value = ''
  showForm.value = true
}

function resetForm() {
  showForm.value = false
  editingId.value = null
  formError.value = ''
}

async function submitForm() {
  formError.value = ''
  if (!form.value.stream_date) {
    formError.value = 'Укажите дату эфира'
    return
  }
  try {
    const payload = { ...form.value }
    if (editingId.value) {
      await store.update(editingId.value, payload)
    } else {
      await store.create(payload)
    }
    resetForm()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Ошибка сохранения'
  }
}

async function removeStream(id) {
  if (confirm('Удалить запись?')) {
    await store.remove(id)
  }
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => store.fetch())
</script>
