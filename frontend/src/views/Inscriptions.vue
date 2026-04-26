<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
      <router-link to="/" class="text-gray-400 hover:text-gray-600">← Назад</router-link>
      <h1 class="text-xl font-bold text-gray-900">Прописи</h1>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">

      <!-- Поиск и кнопка -->
      <div class="flex gap-3 mb-6">
        <input
          v-model="search"
          @input="onSearch"
          type="text"
          placeholder="Поиск по ФИО, нику, телефону..."
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        />
        <button
          v-if="!auth.isManager"
          @click="showForm = true"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
        >
          + Добавить
        </button>
      </div>

      <!-- Форма -->
      <div v-if="showForm" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <h2 class="font-semibold text-gray-800 mb-4">{{ editingId ? 'Редактировать' : 'Новая пропись' }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">ФИО *</label>
            <input v-model="form.full_name" type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Никнейм</label>
            <input v-model="form.username" type="text" placeholder="@username"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
            <input v-model="form.phone" type="text" placeholder="+380..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Источник</label>
            <select v-model="form.source"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="self">Сам пришёл</option>
              <option value="referral">Реферал</option>
            </select>
          </div>
          <div v-if="form.source === 'referral'" class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">От кого (ID пользователя)</label>
            <input v-model.number="form.referred_by_id" type="number" placeholder="ID сотрудника"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Комментарий</label>
            <textarea v-model="form.comment" rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div v-if="formError" class="text-red-500 text-sm mt-2">{{ formError }}</div>
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
      <div v-else-if="store.inscriptions.length" class="space-y-3">
        <div v-for="item in store.inscriptions" :key="item.id"
          class="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-sm transition-shadow">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2">
                <h3 class="font-semibold text-gray-900">{{ item.full_name }}</h3>
                <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="item.source === 'referral' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'">
                  {{ item.source === 'referral' ? '👥 Реферал' : '🙋 Сам' }}
                </span>
              </div>
              <div class="text-sm text-gray-500 mt-1 space-y-0.5">
                <p v-if="item.username">💬 {{ item.username }}</p>
                <p v-if="item.phone">📞 {{ item.phone }}</p>
                <p v-if="item.referred_by">👤 От: {{ item.referred_by.full_name }}</p>
                <p v-if="item.comment" class="text-gray-400 italic">{{ item.comment }}</p>
                <p class="text-xs text-gray-300">{{ formatDate(item.created_at) }}</p>
              </div>
            </div>
            <div v-if="!auth.isManager" class="flex gap-2 ml-4">
              <button @click="startEdit(item)"
                class="text-xs text-blue-500 hover:text-blue-700 px-2 py-1 rounded transition-colors">
                Ред.
              </button>
              <button @click="confirmDelete(item.id)"
                class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Пусто -->
      <div v-else class="text-center py-16 text-gray-400">
        <p class="text-4xl mb-3">✍️</p>
        <p>{{ search ? 'Ничего не найдено' : 'Прописей пока нет' }}</p>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useInscriptionsStore } from '../stores/inscriptions'
import { useAuthStore } from '../stores/auth'

const store = useInscriptionsStore()
const auth = useAuthStore()

const search = ref('')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)

const form = ref({
  full_name: '',
  username: '',
  phone: '',
  source: 'self',
  referred_by_id: null,
  comment: '',
})

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => store.fetch(search.value), 400)
}

onMounted(() => store.fetch())

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function resetForm() {
  form.value = { full_name: '', username: '', phone: '', source: 'self', referred_by_id: null, comment: '' }
  showForm.value = false
  formError.value = ''
  editingId.value = null
}

function startEdit(item) {
  editingId.value = item.id
  form.value = {
    full_name: item.full_name,
    username: item.username || '',
    phone: item.phone || '',
    source: item.source,
    referred_by_id: item.referred_by?.id || null,
    comment: item.comment || '',
  }
  showForm.value = true
}

async function submitForm() {
  formError.value = ''
  if (!form.value.full_name.trim()) {
    formError.value = 'ФИО обязательно'
    return
  }
  try {
    const payload = {
      ...form.value,
      referred_by_id: form.value.source === 'referral' ? form.value.referred_by_id : null,
    }
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

async function confirmDelete(id) {
  if (confirm('Удалить запись?')) {
    await store.remove(id)
  }
}
</script>
