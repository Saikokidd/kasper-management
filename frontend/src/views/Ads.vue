<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
      <router-link to="/" class="text-gray-400 hover:text-gray-600">← Назад</router-link>
      <h1 class="text-xl font-bold text-gray-900">Реклама</h1>
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
        <h2 class="font-semibold text-gray-800 mb-4">{{ editingId ? 'Редактировать' : 'Новая запись' }}</h2>
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
      <div v-else-if="filteredAds.length" class="space-y-4">
        <div v-for="ad in filteredAds" :key="ad.id"
          class="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-sm transition-shadow">
          <div class="flex items-start justify-between mb-4">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="text-lg">{{ platformIcon(ad.platform) }}</span>
                <span class="font-semibold text-gray-900">{{ platformLabel(ad.platform) }}</span>
              </div>
              <p v-if="ad.published_at" class="text-sm text-gray-500">
                🕐 {{ formatDate(ad.published_at) }}
              </p>
              <p v-else class="text-sm text-gray-400 italic">Время не указано</p>
              <p class="text-xs text-gray-300 mt-1">Добавил: {{ ad.created_by.full_name }}</p>
            </div>
            <div v-if="!auth.isPult" class="flex gap-2">
              <button @click="openForm(ad)"
                class="text-xs text-blue-500 hover:text-blue-700 px-2 py-1 rounded transition-colors">
                Ред.
              </button>
              <button @click="removeAd(ad.id)"
                class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
                Удалить
              </button>
            </div>
          </div>

          <!-- Медиафайлы -->
          <div class="border-t border-gray-100 pt-4">
            <p class="text-xs font-medium text-gray-500 mb-2">Скрины</p>
            <MediaUpload entity-type="ad" :entity-id="ad.id" />
          </div>
        </div>
      </div>

      <!-- Пусто -->
      <div v-else class="text-center py-16 text-gray-400">
        <p class="text-4xl mb-3">📢</p>
        <p>Записей пока нет</p>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAdsStore } from '../stores/ads'
import { useAuthStore } from '../stores/auth'
import MediaUpload from '../components/MediaUpload.vue'

const store = useAdsStore()
const auth = useAuthStore()

const platforms = [
  { value: 'telegram',  icon: '✈️',  label: 'Telegram' },
  { value: 'facebook',  icon: '👥',  label: 'Facebook' },
  { value: 'instagram', icon: '📸',  label: 'Instagram' },
  { value: 'tiktok',   icon: '🎵',  label: 'TikTok' },
]

const platform = ref('telegram')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)
const form = ref({ platform: 'telegram', published_at: '' })

const filteredAds = computed(() =>
  store.ads.filter(a => a.platform === platform.value)
)

function selectPlatform(val) {
  platform.value = val
  store.fetch(val)
}

function platformIcon(val) {
  return platforms.find(p => p.value === val)?.icon || '📢'
}

function platformLabel(val) {
  return platforms.find(p => p.value === val)?.label || val
}

function openForm(ad = null) {
  editingId.value = ad?.id || null
  form.value = {
    platform: ad?.platform || platform.value,
    published_at: ad?.published_at ? ad.published_at.slice(0, 16) : ''
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
      published_at: form.value.published_at || null
    }
    if (editingId.value) {
      await store.update(editingId.value, { published_at: payload.published_at })
    } else {
      await store.create(payload)
    }
    resetForm()
    store.fetch(platform.value)
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Ошибка сохранения'
  }
}

async function removeAd(id) {
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

onMounted(() => store.fetch(platform.value))
</script>
