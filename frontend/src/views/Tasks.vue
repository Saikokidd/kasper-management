<template>
  <AppLayout>
    <div class="page-wrap">

      <div class="page-title-row">
        <h1 class="page-heading">Задачи</h1>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <div class="tabs" style="margin:0">
            <button class="tab" :class="{ active: tab === 'active' }" @click="switchTab('active')">Активные</button>
            <button class="tab" :class="{ active: tab === 'history' }" @click="switchTab('history')">Прошедшие</button>
          </div>
          <button v-if="auth.isPult || auth.isAdmin" class="btn btn-primary" @click="showTaskForm = !showTaskForm">
            {{ showTaskForm ? 'Отмена' : '+ Задача' }}
          </button>
        </div>
      </div>

      <!-- Фильтры активных -->
      <div v-if="tab === 'active'" style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">
        <div class="tabs" style="margin:0">
          <button v-for="p in periods" :key="p.value" class="tab" :class="{ active: period === p.value }" @click="setPeriod(p.value)">{{ p.label }}</button>
        </div>
        <select v-model="statusFilter" @change="loadTasks" class="form-select" style="width:160px">
          <option value="">Все статусы</option>
          <option value="pending">Ожидает</option>
          <option value="done">Выполнено</option>
        </select>
      </div>

      <!-- Фильтры прошедших -->
      <div v-if="tab === 'history'" style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;align-items:center">
        <div class="form-group" style="flex-direction:row;align-items:center;gap:8px;margin:0">
          <label class="form-label" style="margin:0;white-space:nowrap">С:</label>
          <input v-model="dateFrom" type="date" class="form-input" style="width:160px" @change="loadHistory" />
        </div>
        <div class="form-group" style="flex-direction:row;align-items:center;gap:8px;margin:0">
          <label class="form-label" style="margin:0;white-space:nowrap">По:</label>
          <input v-model="dateTo" type="date" class="form-input" style="width:160px" @change="loadHistory" />
        </div>
        <div class="tabs" style="margin:0">
          <button v-for="p in periods" :key="p.value" class="tab" :class="{ active: historyPeriod === p.value }" @click="setHistoryPeriod(p.value)">{{ p.label }}</button>
        </div>
      </div>

      <!-- Форма создания -->
      <div v-if="showTaskForm" class="card-form">
        <h2>Новая задача</h2>
        <div class="form-grid">
          <div class="form-group col-2">
            <label class="form-label">Название *</label>
            <input v-model="taskForm.title" class="form-input" placeholder="Название задачи" />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Описание</label>
            <textarea v-model="taskForm.description" class="form-textarea" placeholder="Подробности..." />
          </div>
          <div class="form-group">
            <label class="form-label">Период</label>
            <select v-model="taskForm.type" class="form-select">
              <option value="daily">На день</option>
              <option value="weekly">На неделю</option>
              <option value="monthly">На месяц</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Дедлайн</label>
            <input v-model="taskForm.due_date" type="datetime-local" class="form-input" />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Назначить исполнителей *</label>
            <div class="assignees-select">
              <div
                v-for="u in hrUsers"
                :key="u.id"
                class="assignee-chip"
                :class="{ selected: taskForm.assigned_to_ids.includes(u.id) }"
                @click="toggleAssignee(u.id)"
              >
                <div class="assignee-avatar">{{ initials(u.full_name) }}</div>
                <span>{{ u.full_name }}</span>
                <span v-if="taskForm.assigned_to_ids.includes(u.id)" class="chip-check">✓</span>
              </div>
            </div>
          </div>
        </div>
        <p v-if="taskError" class="form-error">{{ taskError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitTask">Создать</button>
          <button class="btn btn-ghost" @click="resetTaskForm">Отмена</button>
        </div>
      </div>

      <!-- СПИСОК -->
      <div v-if="store.loading" class="loading-state">Загрузка...</div>
      <div v-else-if="displayTasks.length" style="display:flex;flex-direction:column;gap:10px">
        <div v-for="task in displayTasks" :key="task.id" class="card task-card" :class="{ 'task-done': task.status === 'done' }">
          <div class="task-main">
            <div class="task-status-dot" :class="task.status === 'done' ? 'dot-done' : 'dot-pending'"></div>
            <div class="task-body">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px">
                <span class="task-title">{{ task.title }}</span>
                <span class="badge" :class="{ 'badge-blue': task.type==='daily', 'badge-purple': task.type==='weekly', 'badge-yellow': task.type==='monthly' }">
                  {{ typeLabels[task.type] }}
                </span>
                <span v-if="task.status === 'done'" class="badge badge-green">✓ Выполнено</span>
                <span v-else-if="isOverdue(task)" class="badge badge-red">Просрочено</span>
              </div>

              <p v-if="task.description" class="task-desc">{{ task.description }}</p>

              <div class="task-assignees">
                <div v-for="u in task.assignees" :key="u.id" class="task-assignee-chip">
                  <div class="assignee-avatar small">{{ initials(u.full_name) }}</div>
                  <span>{{ u.full_name }}</span>
                </div>
              </div>

              <div class="interview-meta" style="margin-top:6px">
                <span v-if="task.due_date" class="meta-chip" :class="isOverdue(task) ? 'chip-danger' : ''">
                  ⏰ {{ formatDate(task.due_date) }}
                </span>
                <span class="meta-chip">от {{ task.created_by.full_name }}</span>
              </div>

              <div v-if="task.status === 'done'" class="task-result">
                <div v-if="task.completion_comment" class="task-completion">
                  💬 {{ task.completion_comment }}
                </div>
                <div v-if="task.completion_media" class="task-media-preview">
                  <img :src="mediaUrl(task.completion_media)" alt="скриншот" @click="lightbox = mediaUrl(task.completion_media)" />
                </div>
              </div>
            </div>
          </div>

          <div class="task-actions">
            <template v-if="auth.isHR && task.status === 'pending' && isAssignedToMe(task)">
              <button class="btn btn-primary btn-sm" @click="openComplete(task)">Выполнить</button>
            </template>
            <template v-if="auth.isPult || auth.isAdmin">
              <button v-if="task.status === 'done'" class="btn btn-ghost btn-sm" @click="store.reopenTask(task.id)">Открыть</button>
              <button class="btn btn-danger btn-sm" @click="store.deleteTask(task.id)">Удалить</button>
            </template>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="empty-icon">✅</div>
        <p>{{ tab === 'history' ? 'За выбранный период задач нет' : 'Задач нет' }}</p>
      </div>

      <!-- Модал выполнения -->
      <div v-if="completeModal" class="modal-overlay" @click.self="completeModal = null">
        <div class="modal">
          <h3 class="modal-title">Отметить как выполнено</h3>
          <p style="font-size:13px;color:var(--text-secondary);margin-bottom:14px">{{ completeModal.title }}</p>
          <div class="form-group" style="margin-bottom:12px">
            <label class="form-label">Комментарий</label>
            <textarea v-model="completeComment" class="form-textarea" placeholder="Что сделано..." />
          </div>
          <div class="form-group" style="margin-bottom:16px">
            <label class="form-label">Скриншот / фото (необязательно)</label>
            <div class="photo-upload-area">
              <div v-if="completePhotoPreview" class="photo-preview">
                <img :src="completePhotoPreview" alt="preview" />
                <button class="photo-remove" @click="removeCompletePhoto" type="button">✕</button>
              </div>
              <label v-else class="photo-upload-btn">
                <input type="file" accept="image/*" @change="onCompletePhotoSelect" style="display:none" />
                <span>📷 Прикрепить скриншот</span>
              </label>
            </div>
          </div>
          <div style="display:flex;gap:8px">
            <button class="btn btn-primary" @click="submitComplete" :disabled="completing">
              {{ completing ? 'Сохранение...' : 'Выполнено' }}
            </button>
            <button class="btn btn-ghost" @click="completeModal = null">Отмена</button>
          </div>
        </div>
      </div>

      <!-- Лайтбокс -->
      <div v-if="lightbox" class="lightbox" @click="lightbox = null">
        <img :src="lightbox" alt="скриншот" />
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useTasksStore } from '../stores/tasks'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const store = useTasksStore()
const auth = useAuthStore()
const API = import.meta.env.VITE_API_URL

const tab = ref('active')
const period = ref('')
const statusFilter = ref('')
const historyPeriod = ref('')
const historyTasks = ref([])

// Даты по умолчанию — текущий месяц
const now = new Date()
const dateFrom = ref(new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10))
const dateTo = ref(new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().slice(0, 10))

const typeLabels = { daily: 'День', weekly: 'Неделя', monthly: 'Месяц' }
const periods = [
  { label: 'Все', value: '' },
  { label: 'День', value: 'daily' },
  { label: 'Неделя', value: 'weekly' },
  { label: 'Месяц', value: 'monthly' }
]

const hrUsers = computed(() => store.users.filter(u => u.role === 'hr'))

// Задачи для отображения
const displayTasks = computed(() => tab.value === 'history' ? historyTasks.value : store.tasks)

function switchTab(t) {
  tab.value = t
  showTaskForm.value = false
  if (t === 'history') loadHistory()
  else loadTasks()
}

function setPeriod(val) { period.value = val; loadTasks() }
function setHistoryPeriod(val) { historyPeriod.value = val; loadHistory() }

function loadTasks() {
  const filters = {}
  if (period.value) filters.type = period.value
  if (statusFilter.value) filters.status = statusFilter.value
  store.fetchTasks(filters)
}

async function loadHistory() {
  store.loading = true
  try {
    const filters = { status: 'done' }
    if (historyPeriod.value) filters.type = historyPeriod.value
    if (dateFrom.value) filters.date_from = dateFrom.value
    if (dateTo.value) filters.date_to = dateTo.value
    const res = await axios.get(`${API}/api/tasks`, { params: filters })
    historyTasks.value = res.data
  } finally {
    store.loading = false
  }
}

// Форма создания
const showTaskForm = ref(false)
const taskError = ref('')
const taskForm = ref({ title: '', description: '', type: 'daily', assigned_to_ids: [], due_date: '' })

function toggleAssignee(id) {
  const idx = taskForm.value.assigned_to_ids.indexOf(id)
  if (idx === -1) taskForm.value.assigned_to_ids.push(id)
  else taskForm.value.assigned_to_ids.splice(idx, 1)
}

function resetTaskForm() {
  taskForm.value = { title: '', description: '', type: 'daily', assigned_to_ids: [], due_date: '' }
  showTaskForm.value = false
  taskError.value = ''
}

async function submitTask() {
  taskError.value = ''
  if (!taskForm.value.title.trim()) { taskError.value = 'Название обязательно'; return }
  if (!taskForm.value.assigned_to_ids.length) { taskError.value = 'Выберите хотя бы одного исполнителя'; return }
  try {
    await store.createTask({
      title: taskForm.value.title,
      description: taskForm.value.description || null,
      type: taskForm.value.type,
      assigned_to_ids: taskForm.value.assigned_to_ids,
      due_date: taskForm.value.due_date || null,
    })
    resetTaskForm()
    loadTasks()
  } catch (e) {
    taskError.value = e.response?.data?.detail || 'Ошибка'
  }
}

// Выполнение
const completeModal = ref(null)
const completeComment = ref('')
const completePhotoFile = ref(null)
const completePhotoPreview = ref(null)
const completing = ref(false)
const lightbox = ref(null)

function openComplete(task) {
  completeModal.value = task
  completeComment.value = ''
  completePhotoFile.value = null
  completePhotoPreview.value = null
}

function onCompletePhotoSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  completePhotoFile.value = file
  completePhotoPreview.value = URL.createObjectURL(file)
}

function removeCompletePhoto() {
  completePhotoFile.value = null
  completePhotoPreview.value = null
}

async function submitComplete() {
  completing.value = true
  try {
    if (completePhotoFile.value) {
      if (completeComment.value) {
        await axios.post(`${API}/api/tasks/${completeModal.value.id}/complete`, {
          completion_comment: completeComment.value
        })
      }
      const formData = new FormData()
      formData.append('file', completePhotoFile.value)
      const res = await axios.post(
        `${API}/api/tasks/${completeModal.value.id}/complete-media`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      store._replaceTask(res.data)
    } else {
      await store.completeTask(completeModal.value.id, completeComment.value)
    }
    completeModal.value = null
  } catch (e) {
    console.error(e)
  } finally {
    completing.value = false
  }
}

function isAssignedToMe(task) {
  return task.assignees.some(u => u.id === auth.user?.id)
}

function isOverdue(task) {
  if (!task.due_date || task.status === 'done') return false
  return new Date(task.due_date) < new Date()
}

function mediaUrl(path) { return `${API}/media/${path}` }
function initials(name) { return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() }
function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  await store.fetchUsers()
  await store.fetchTasks()
})
</script>

<style scoped>
.task-card { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; transition:border-color 0.2s; }
.task-card:hover { border-color:rgba(110,231,183,0.2); }
.task-done { opacity:0.75; }
.task-main { display:flex; align-items:flex-start; gap:12px; flex:1; min-width:0; }
.task-status-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; margin-top:5px; }
.dot-pending { background:var(--warning); box-shadow:0 0 6px var(--warning); }
.dot-done { background:var(--accent); box-shadow:0 0 6px var(--accent); }
.task-body { flex:1; min-width:0; }
.task-title { font-size:14px; font-weight:600; color:var(--text-primary); }
.task-desc { font-size:12px; color:var(--text-secondary); margin-top:4px; line-height:1.5; }
.task-actions { display:flex; gap:6px; flex-shrink:0; align-items:flex-start; flex-wrap:wrap; }

.task-assignees { display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }
.task-assignee-chip { display:inline-flex; align-items:center; gap:5px; background:var(--bg-elevated); border:1px solid var(--border); border-radius:999px; padding:3px 10px 3px 4px; font-size:12px; color:var(--text-secondary); }

.assignee-avatar { width:22px; height:22px; border-radius:50%; background:var(--accent-dim); color:var(--accent); display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:700; flex-shrink:0; }
.assignee-avatar.small { width:18px; height:18px; font-size:8px; }

.assignees-select { display:flex; flex-wrap:wrap; gap:8px; }
.assignee-chip { display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:var(--radius-sm); border:1px solid var(--border); background:var(--bg-elevated); cursor:pointer; transition:all 0.18s ease; font-size:13px; color:var(--text-secondary); }
.assignee-chip:hover { border-color:var(--accent); color:var(--text-primary); }
.assignee-chip.selected { background:var(--accent-dim); border-color:var(--accent); color:var(--accent); font-weight:600; }
.chip-check { font-size:11px; }

.interview-meta { display:flex; flex-wrap:wrap; gap:6px; }
.meta-chip { display:inline-flex; align-items:center; gap:4px; font-size:12px; color:var(--text-secondary); background:var(--bg-elevated); border-radius:999px; padding:2px 8px; }
.chip-danger { background:var(--danger-dim); color:var(--danger); }

.task-result { margin-top:10px; display:flex; flex-direction:column; gap:8px; }
.task-completion { font-size:12.5px; color:var(--text-secondary); background:var(--bg-surface); border-left:3px solid var(--accent); padding:8px 12px; border-radius:0 var(--radius-xs) var(--radius-xs) 0; font-style:italic; }
.task-media-preview { width:120px; height:80px; border-radius:var(--radius-sm); overflow:hidden; border:1px solid var(--border); cursor:zoom-in; }
.task-media-preview img { width:100%; height:100%; object-fit:cover; transition:opacity 0.15s; }
.task-media-preview img:hover { opacity:0.85; }

.photo-upload-area { display:flex; align-items:center; gap:10px; }
.photo-preview { position:relative; width:80px; height:80px; }
.photo-preview img { width:100%; height:100%; object-fit:cover; border-radius:var(--radius-sm); border:1px solid var(--border); }
.photo-remove { position:absolute; top:-6px; right:-6px; width:18px; height:18px; background:var(--danger); color:#fff; border:none; border-radius:50%; cursor:pointer; font-size:10px; display:flex; align-items:center; justify-content:center; }
.photo-upload-btn { cursor:pointer; display:inline-flex; align-items:center; gap:6px; padding:8px 14px; background:var(--bg-elevated); border:1px dashed var(--border); border-radius:var(--radius-sm); font-size:13px; color:var(--text-secondary); transition:all 0.15s; }
.photo-upload-btn:hover { border-color:var(--accent); color:var(--accent); }

.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:200; display:flex; align-items:center; justify-content:center; padding:16px; backdrop-filter:blur(4px); }
.modal { background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius); padding:24px; width:100%; max-width:440px; }
.modal-title { font-size:16px; font-weight:700; color:var(--text-primary); margin-bottom:4px; }

.lightbox { position:fixed; inset:0; background:rgba(0,0,0,0.9); z-index:300; display:flex; align-items:center; justify-content:center; cursor:zoom-out; padding:20px; }
.lightbox img { max-width:100%; max-height:100%; object-fit:contain; border-radius:var(--radius-sm); }
</style>
