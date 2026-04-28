<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
      <router-link to="/" class="text-gray-400 hover:text-gray-600">← Назад</router-link>
      <h1 class="text-xl font-bold text-gray-900">Задачи</h1>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-8">

      <div class="flex gap-2 mb-6">
        <button v-for="t in periods" :key="t.value" @click="setPeriod(t.value)"
          :class="period === t.value && tab !== 'templates' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          {{ t.label }}
        </button>
        <button v-if="auth.isManager || auth.isAdmin" @click="tab = 'templates'"
          :class="tab === 'templates' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors ml-auto">
          🗂 Шаблоны
        </button>
      </div>

      <template v-if="tab !== 'templates'">
        <div class="flex gap-3 mb-6">
          <select v-model="statusFilter" @change="loadTasks"
            class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Все статусы</option>
            <option value="pending">Ожидает</option>
            <option value="done">Выполнено</option>
          </select>
          <div class="flex-1"></div>
          <button v-if="auth.isManager || auth.isAdmin" @click="showTaskForm = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            + Создать задачу
          </button>
        </div>

        <div v-if="showTaskForm" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
          <h2 class="font-semibold text-gray-800 mb-4">Новая задача</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Название *</label>
              <input v-model="taskForm.title" type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
              <textarea v-model="taskForm.description" rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Период</label>
              <select v-model="taskForm.type"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="daily">На день</option>
                <option value="weekly">На неделю</option>
                <option value="monthly">На месяц</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Дедлайн</label>
              <input v-model="taskForm.due_date" type="datetime-local"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Назначить *</label>
              <select v-model.number="taskForm.assigned_to_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option :value="null">— Выберите сотрудника —</option>
                <option v-for="u in store.users" :key="u.id" :value="u.id">{{ u.full_name }} ({{ u.role }})</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Шаблон (опц.)</label>
              <select v-model="taskForm.template_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option :value="null">—</option>
                <option v-for="t in store.templates" :key="t.id" :value="t.id">{{ t.name }}</option>
              </select>
            </div>
          </div>
          <div v-if="taskError" class="text-red-500 text-sm mt-2">{{ taskError }}</div>
          <div class="flex gap-3 mt-4">
            <button @click="submitTask"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Создать
            </button>
            <button @click="resetTaskForm"
              class="text-gray-500 hover:text-gray-700 px-4 py-2 rounded-lg text-sm transition-colors">
              Отмена
            </button>
          </div>
        </div>

        <div v-if="store.loading" class="text-center py-12 text-gray-400">Загрузка...</div>

        <div v-else-if="store.tasks.length" class="space-y-3">
          <div v-for="task in store.tasks" :key="task.id"
            class="bg-white border rounded-xl p-5 transition-shadow hover:shadow-sm"
            :class="task.status === 'done' ? 'border-green-200 bg-green-50' : 'border-gray-200'">
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <h3 class="font-semibold text-gray-900"
                    :class="task.status === 'done' ? 'line-through text-gray-400' : ''">
                    {{ task.title }}
                  </h3>
                  <span class="text-xs px-2 py-0.5 rounded-full"
                    :class="{
                      'bg-blue-100 text-blue-700': task.type === 'daily',
                      'bg-purple-100 text-purple-700': task.type === 'weekly',
                      'bg-orange-100 text-orange-700': task.type === 'monthly',
                    }">{{ typeLabels[task.type] }}</span>
                  <span v-if="task.status === 'done'"
                    class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">✓ Выполнено</span>
                </div>
                <p v-if="task.description" class="text-sm text-gray-500 mt-1">{{ task.description }}</p>
                <div class="text-xs text-gray-400 mt-1 space-y-0.5">
                  <p>👤 {{ task.assigned_to.full_name }}</p>
                  <p v-if="task.due_date">⏰ {{ formatDate(task.due_date) }}</p>
                  <p v-if="task.completion_comment" class="text-green-600 italic">💬 {{ task.completion_comment }}</p>
                </div>
                <div class="mt-3 pt-3 border-t border-gray-100">
                  <MediaUpload entity-type="task" :entity-id="task.id" />
                </div>
              </div>
              <div class="flex flex-col gap-2 items-end shrink-0">
                <template v-if="auth.isHR && task.status === 'pending' && task.assigned_to.id === auth.user.id">
                  <button @click="openComplete(task)"
                    class="text-xs bg-green-500 hover:bg-green-600 text-white px-3 py-1.5 rounded-lg transition-colors">
                    Выполнить
                  </button>
                </template>
                <template v-if="auth.isManager || auth.isAdmin">
                  <button v-if="task.status === 'done'" @click="store.reopenTask(task.id)"
                    class="text-xs text-gray-400 hover:text-gray-600 px-2 py-1 rounded transition-colors">
                    Открыть снова
                  </button>
                  <button @click="store.deleteTask(task.id)"
                    class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
                    Удалить
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-16 text-gray-400">
          <p class="text-4xl mb-3">✅</p>
          <p>Задач нет</p>
        </div>

        <div v-if="completeModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
          <div class="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">
            <h3 class="font-semibold text-gray-800 mb-3">Отметить как выполнено</h3>
            <p class="text-sm text-gray-500 mb-4">{{ completeModal.title }}</p>
            <textarea v-model="completeComment" rows="3" placeholder="Комментарий (необязательно)"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <div class="flex gap-3 mt-4">
              <button @click="submitComplete"
                class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                Выполнено
              </button>
              <button @click="completeModal = null"
                class="text-gray-500 hover:text-gray-700 px-4 py-2 rounded-lg text-sm transition-colors">
                Отмена
              </button>
            </div>
          </div>
        </div>
      </template>

      <template v-if="tab === 'templates'">
        <div class="flex justify-between items-center mb-6">
          <button @click="tab = 'tasks'" class="text-gray-400 hover:text-gray-600 text-sm">← К задачам</button>
          <button @click="showTemplateForm = true"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            + Новый шаблон
          </button>
        </div>

        <div v-if="showTemplateForm" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
          <h2 class="font-semibold text-gray-800 mb-4">Новый шаблон задачи</h2>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Название *</label>
              <input v-model="templateForm.name" type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
              <textarea v-model="templateForm.description" rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>
          <div class="flex gap-3 mt-4">
            <button @click="submitTemplate"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Сохранить
            </button>
            <button @click="showTemplateForm = false"
              class="text-gray-500 hover:text-gray-700 px-4 py-2 rounded-lg text-sm transition-colors">
              Отмена
            </button>
          </div>
        </div>

        <div v-if="store.templates.length" class="space-y-3">
          <div v-for="t in store.templates" :key="t.id"
            class="bg-white border border-gray-200 rounded-xl p-5 flex items-start justify-between">
            <div>
              <h3 class="font-semibold text-gray-900">{{ t.name }}</h3>
              <p v-if="t.description" class="text-sm text-gray-400 mt-1">{{ t.description }}</p>
            </div>
            <button @click="store.deleteTemplate(t.id)"
              class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
              Удалить
            </button>
          </div>
        </div>

        <div v-else class="text-center py-16 text-gray-400">
          <p class="text-4xl mb-3">🗂</p>
          <p>Шаблонов пока нет</p>
        </div>
      </template>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTasksStore } from '../stores/tasks'
import { useAuthStore } from '../stores/auth'
import MediaUpload from '../components/MediaUpload.vue'

const store = useTasksStore()
const auth = useAuthStore()

const tab = ref('tasks')
const period = ref('')
const statusFilter = ref('')
const typeLabels = { daily: 'День', weekly: 'Неделя', monthly: 'Месяц' }
const periods = [
  { label: 'Все', value: '' },
  { label: 'День', value: 'daily' },
  { label: 'Неделя', value: 'weekly' },
  { label: 'Месяц', value: 'monthly' },
]

function setPeriod(val) {
  period.value = val
  tab.value = 'tasks'
  loadTasks()
}

function loadTasks() {
  const filters = {}
  if (period.value) filters.type = period.value
  if (statusFilter.value) filters.status = statusFilter.value
  store.fetchTasks(filters)
}

const showTaskForm = ref(false)
const taskError = ref('')
const taskForm = ref({
  title: '', description: '', type: 'daily',
  assigned_to_id: null, due_date: '', template_id: null
})

function resetTaskForm() {
  taskForm.value = { title: '', description: '', type: 'daily', assigned_to_id: null, due_date: '', template_id: null }
  showTaskForm.value = false
  taskError.value = ''
}

async function submitTask() {
  taskError.value = ''
  if (!taskForm.value.title.trim()) { taskError.value = 'Название обязательно'; return }
  if (!taskForm.value.assigned_to_id) { taskError.value = 'Укажите кому назначить'; return }
  try {
    const payload = {
      ...taskForm.value,
      due_date: taskForm.value.due_date || null,
      template_id: taskForm.value.template_id || null,
    }
    await store.createTask(payload)
    resetTaskForm()
  } catch (e) {
    taskError.value = e.response?.data?.detail || 'Ошибка'
  }
}

const completeModal = ref(null)
const completeComment = ref('')

function openComplete(task) {
  completeModal.value = task
  completeComment.value = ''
}

async function submitComplete() {
  await store.completeTask(completeModal.value.id, completeComment.value)
  completeModal.value = null
}

const showTemplateForm = ref(false)
const templateForm = ref({ name: '', description: '' })

async function submitTemplate() {
  if (!templateForm.value.name.trim()) return
  await store.createTemplate(templateForm.value)
  templateForm.value = { name: '', description: '' }
  showTemplateForm.value = false
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(async () => {
  await store.fetchUsers()
  await store.fetchTemplates()
  await store.fetchTasks()
})
</script>
