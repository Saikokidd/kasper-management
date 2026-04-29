<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
      <router-link to="/" class="text-gray-400 hover:text-gray-600">← Назад</router-link>
      <h1 class="text-xl font-bold text-gray-900">Объявления</h1>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">

      <!-- Вкладки платформ -->
      <div class="flex gap-2 mb-6">
        <button v-for="p in platforms" :key="p.value"
          @click="selectPlatform(p.value)"
          :class="platform === p.value ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          {{ p.icon }} {{ p.label }}
        </button>
      </div>

      <!-- Кнопка добавить -->
      <div class="flex justify-end mb-6">
        <button v-if="!auth.isPult" @click="openForm()"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          + Добавить
        </button>
      </div>

      <!-- Форма -->
      <div v-if="showForm" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <h2 class="font-semibold text-gray-800 mb-4">{{ editingId ? 'Редактировать' : 'Новое объявление' }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-if="!editingId">
            <label class="block text-sm font-medium text-gray-700 mb-1">Платформа</label>
            <select v-model="form.platform"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option v-for="p in platforms" :key="p.value" :value="p.value">{{ p.icon }} {{ p.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Время публикации</label>
            <input v-model="form.published_at" type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Отклики</label>
            <input v-model.number="form.responses" type="number" min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Статус</label>
            <select v-model="form.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="active">✅ Размещено</option>
              <option value="blocked">🚫 Заблокировано</option>
            </select>
          </div>
          <div v-if="form.status === 'blocked'" class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Причина блокировки</label>
            <input v-model="form.block_reason" type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Составляющая объявления</label>
            <textarea v-model="form.content" rows="3" placeholder="Текст объявления, ссылка, описание..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Комментарий HR</label>
            <textarea v-model="form.comment" rows="2"
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

      <!-- Список -->
      <div v-else-if="filteredPosts.length" class="space-y-4">
        <div v-for="post in filteredPosts" :key="post.id"
          class="bg-white border rounded-xl p-5 hover:shadow-sm transition-shadow"
          :class="post.status === 'blocked' ? 'border-red-200' : 'border-gray-200'">
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2 flex-wrap">
                <span class="text-lg">{{ platformIcon(post.platform) }}</span>
                <span class="font-semibold text-gray-900">{{ platformLabel(post.platform) }}</span>
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :class="post.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                  {{ post.status === 'active' ? '✅ Размещено' : '🚫 Заблокировано' }}
                </span>
                <span class="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                  📨 {{ post.responses }} откликов
                </span>
              </div>
              <div class="text-sm text-gray-500 space-y-1">
                <p v-if="post.published_at">🕐 {{ formatDate(post.published_at) }}</p>
                <p v-if="post.content" class="text-gray-700">📄 {{ post.content }}</p>
                <p v-if="post.comment" class="italic text-gray-400">💬 {{ post.comment }}</p>
                <p v-if="post.block_reason" class="text-red-500">⛔ {{ post.block_reason }}</p>
                <p class="text-xs text-gray-300">Добавил: {{ post.created_by.full_name }}</p>
              </div>
            </div>
            <div v-if="!auth.isPult" class="flex gap-2 ml-4 shrink-0">
              <button @click="openForm(post)"
                class="text-xs text-blue-500 hover:text-blue-700 px-2 py-1 rounded transition-colors">
                Ред.
              </button>
              <button @click="removePost(post.id)"
                class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Пусто -->
      <div v-else class="text-center py-16 text-gray-400">
        <p class="text-4xl mb-3">📋</p>
        <p>Объявлений пока нет</p>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useJobPostsStore } from '../stores/jobPosts'
import { useAuthStore } from '../stores/auth'

const store = useJobPostsStore()
const auth = useAuthStore()

const platforms = [
  { value: 'olx',    icon: '🟠', label: 'OLX' },
  { value: 'workua', icon: '🔵', label: 'Work.UA' },
]

const platform = ref('olx')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)

const form = ref({
  platform: 'olx',
  content: '',
  published_at: '',
  responses: 0,
  comment: '',
  status: 'active',
  block_reason: ''
})

const filteredPosts = computed(() =>
  store.posts.filter(p => p.platform === platform.value)
)

function selectPlatform(val) {
  platform.value = val
  store.fetch(val)
}

function platformIcon(val) {
  return platforms.find(p => p.value === val)?.icon || '📋'
}

function platformLabel(val) {
  return platforms.find(p => p.value === val)?.label || val
}

function openForm(post = null) {
  editingId.value = post?.id || null
  form.value = {
    platform: post?.platform || platform.value,
    content: post?.content || '',
    published_at: post?.published_at ? post.published_at.slice(0, 16) : '',
    responses: post?.responses ?? 0,
    comment: post?.comment || '',
    status: post?.status || 'active',
    block_reason: post?.block_reason || ''
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
  try {
    const payload = {
      ...form.value,
      published_at: form.value.published_at || null,
      block_reason: form.value.status === 'blocked' ? form.value.block_reason || null : null
    }
    if (editingId.value) {
      await store.update(editingId.value, payload)
    } else {
      await store.create(payload)
    }
    resetForm()
    store.fetch(platform.value)
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Ошибка сохранения'
  }
}

async function removePost(id) {
  if (confirm('Удалить объявление?')) {
    await store.remove(id)
  }
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => store.fetch(platform.value))
</script>
