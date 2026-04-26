<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
      <router-link to="/" class="text-gray-400 hover:text-gray-600">← Назад</router-link>
      <h1 class="text-xl font-bold text-gray-900">Собеседования</h1>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">

      <!-- Вкладки -->
      <div class="flex gap-2 mb-6">
        <button @click="tab = 'list'"
          :class="tab === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          📋 Список
        </button>
        <button @click="tab = 'calendar'"
          :class="tab === 'calendar' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          📅 Календарь
        </button>
      </div>

      <!-- СПИСОК -->
      <template v-if="tab === 'list'">
        <div class="flex justify-between items-center mb-6">
          <p class="text-gray-500 text-sm">{{ store.interviews.length }} записей</p>
          <button
            v-if="!auth.isManager"
            @click="showForm = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            + Добавить
          </button>
        </div>

        <div v-if="showForm" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
          <h2 class="font-semibold text-gray-800 mb-4">{{ editingId ? 'Редактировать' : 'Новое собеседование' }}</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">ФИО *</label>
              <input v-model="form.full_name" type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Дата и время</label>
              <input v-model="form.scheduled_at" type="datetime-local"
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

        <div v-if="store.loading" class="text-center py-12 text-gray-400">Загрузка...</div>

        <div v-else-if="store.interviews.length" class="space-y-3">
          <div v-for="item in store.interviews" :key="item.id"
            class="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-sm transition-shadow">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="font-semibold text-gray-900">{{ item.full_name }}</h3>
                <div class="text-sm text-gray-500 mt-1 space-y-0.5">
                  <p v-if="item.scheduled_at">📅 {{ formatDate(item.scheduled_at) }}</p>
                  <p v-if="item.username">💬 {{ item.username }}</p>
                  <p v-if="item.phone">📞 {{ item.phone }}</p>
                  <p v-if="item.comment" class="text-gray-400 italic">{{ item.comment }}</p>
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

        <div v-else class="text-center py-16 text-gray-400">
          <p class="text-4xl mb-3">📅</p>
          <p>Собеседований пока нет</p>
        </div>
      </template>

      <!-- КАЛЕНДАРЬ -->
      <template v-if="tab === 'calendar'">
        <div class="bg-white border border-gray-200 rounded-xl p-6">

          <!-- Навигация по месяцу -->
          <div class="flex items-center justify-between mb-6">
            <button @click="prevMonth" class="text-gray-400 hover:text-gray-600 px-2 py-1 rounded transition-colors">
              ← Пред.
            </button>
            <h2 class="font-semibold text-gray-800 capitalize">{{ monthTitle }}</h2>
            <button @click="nextMonth" class="text-gray-400 hover:text-gray-600 px-2 py-1 rounded transition-colors">
              След. →
            </button>
          </div>

          <!-- Дни недели -->
          <div class="grid grid-cols-7 mb-2">
            <div v-for="d in ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']" :key="d"
              class="text-center text-xs font-medium text-gray-400 py-1">
              {{ d }}
            </div>
          </div>

          <!-- Ячейки -->
          <div class="grid grid-cols-7 gap-1">
            <div v-for="(cell, i) in calendarCells" :key="i"
              class="min-h-16 rounded-lg p-1"
              :class="cell.day ? 'bg-gray-50 hover:bg-gray-100' : ''">
              <template v-if="cell.day">
                <p class="text-xs font-medium mb-1"
                  :class="cell.isToday ? 'text-blue-600 font-bold' : 'text-gray-500'">
                  {{ cell.day }}
                </p>
                <div v-for="item in cell.interviews" :key="item.id"
                  class="text-xs bg-blue-100 text-blue-700 rounded px-1 py-0.5 mb-0.5 truncate cursor-pointer"
                  :title="item.full_name + ' ' + formatTime(item.scheduled_at)">
                  {{ formatTime(item.scheduled_at) }} {{ item.full_name }}
                </div>
              </template>
            </div>
          </div>

        </div>
      </template>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useInterviewsStore } from '../stores/interviews'
import { useAuthStore } from '../stores/auth'

const store = useInterviewsStore()
const auth = useAuthStore()

const tab = ref('list')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)

const form = ref({
  full_name: '',
  username: '',
  phone: '',
  scheduled_at: '',
  comment: '',
})

// Календарь
const today = new Date()
const calYear = ref(today.getFullYear())
const calMonth = ref(today.getMonth()) // 0-11

const monthTitle = computed(() => {
  return new Date(calYear.value, calMonth.value, 1)
    .toLocaleString('ru-RU', { month: 'long', year: 'numeric' })
})

function prevMonth() {
  if (calMonth.value === 0) { calMonth.value = 11; calYear.value-- }
  else calMonth.value--
}
function nextMonth() {
  if (calMonth.value === 11) { calMonth.value = 0; calYear.value++ }
  else calMonth.value++
}

const calendarCells = computed(() => {
  const firstDay = new Date(calYear.value, calMonth.value, 1)
  const lastDay = new Date(calYear.value, calMonth.value + 1, 0)

  // Пн=0 ... Вс=6
  let startOffset = firstDay.getDay() - 1
  if (startOffset < 0) startOffset = 6

  const cells = []

  // Пустые ячейки до первого дня
  for (let i = 0; i < startOffset; i++) {
    cells.push({ day: null, interviews: [] })
  }

  // Дни месяца
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${calYear.value}-${String(calMonth.value + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const isToday =
      d === today.getDate() &&
      calMonth.value === today.getMonth() &&
      calYear.value === today.getFullYear()

    const dayInterviews = store.interviews.filter(item => {
      if (!item.scheduled_at) return false
      return item.scheduled_at.slice(0, 10) === dateStr
    })

    cells.push({ day: d, isToday, interviews: dayInterviews })
  }

  return cells
})

onMounted(() => store.fetch())

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function formatTime(dt) {
  return new Date(dt).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function resetForm() {
  form.value = { full_name: '', username: '', phone: '', scheduled_at: '', comment: '' }
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
    scheduled_at: item.scheduled_at ? item.scheduled_at.slice(0, 16) : '',
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
    const payload = { ...form.value, scheduled_at: form.value.scheduled_at || null }
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
