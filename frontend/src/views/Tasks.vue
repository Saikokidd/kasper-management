<template>
  <AppLayout>
    <div class="page-wrap">

      <div class="page-title-row">
        <h1 class="page-heading">Задачи</h1>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <div class="tabs" style="margin:0">
            <button v-for="p in periods" :key="p.value" class="tab" :class="{ active: period === p.value && tab !== 'templates' }" @click="setPeriod(p.value)">{{ p.label }}</button>
          </div>
          <button v-if="auth.isPult || auth.isAdmin" class="tab" :class="{ active: tab === 'templates' }" @click="tab = 'templates'" style="border:1px solid var(--border);border-radius:6px;padding:6px 12px">Шаблоны</button>
          <button v-if="auth.isPult || auth.isAdmin" class="btn btn-primary" @click="showTaskForm = true">+ Задача</button>
        </div>
      </div>

      <!-- Фильтр статус -->
      <div v-if="tab !== 'templates'" style="display:flex;gap:8px;margin-bottom:20px">
        <select v-model="statusFilter" @change="loadTasks" class="form-select" style="width:160px">
          <option value="">Все статусы</option>
          <option value="pending">Ожидает</option>
          <option value="done">Выполнено</option>
        </select>
      </div>

      <!-- Форма задачи -->
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
          <div class="form-group">
            <label class="form-label">Назначить *</label>
            <select v-model.number="taskForm.assigned_to_id" class="form-select">
              <option :value="null">— Выберите сотрудника —</option>
              <option v-for="u in store.users" :key="u.id" :value="u.id">{{ u.full_name }} ({{ u.role }})</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Шаблон (опц.)</label>
            <select v-model="taskForm.template_id" class="form-select">
              <option :value="null">—</option>
              <option v-for="t in store.templates" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
        </div>
        <p v-if="taskError" class="form-error">{{ taskError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitTask">Создать</button>
          <button class="btn btn-ghost" @click="resetTaskForm">Отмена</button>
        </div>
      </div>

      <!-- СПИСОК ЗАДАЧ -->
      <template v-if="tab !== 'templates'">
        <div v-if="store.loading" class="loading-state">Загрузка...</div>
        <div v-else-if="store.tasks.length" style="display:flex;flex-direction:column;gap:10px">
          <div v-for="task in store.tasks" :key="task.id" class="card task-card" :class="{ 'task-done': task.status === 'done' }">
            <div class="task-main">
              <div class="task-status-dot" :class="task.status === 'done' ? 'dot-done' : 'dot-pending'"></div>
              <div class="task-body">
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px">
                  <span class="task-title" :class="{ 'task-title--done': task.status === 'done' }">{{ task.title }}</span>
                  <span class="badge" :class="{ 'badge-blue': task.type==='daily', 'badge-purple': task.type==='weekly', 'badge-yellow': task.type==='monthly' }">{{ typeLabels[task.type] }}</span>
                  <span v-if="task.status === 'done'" class="badge badge-green">✓ Выполнено</span>
                </div>
                <p v-if="task.description" class="task-desc">{{ task.description }}</p>
                <div class="interview-meta" style="margin-top:6px">
                  <span class="meta-chip">👤 {{ task.assigned_to.full_name }}</span>
                  <span v-if="task.due_date" class="meta-chip">⏰ {{ formatDate(task.due_date) }}</span>
                </div>
                <p v-if="task.completion_comment" class="task-completion">💬 {{ task.completion_comment }}</p>
              </div>
            </div>
            <div class="task-actions">
              <button v-if="auth.isHR && task.status === 'pending' && task.assigned_to.id === auth.user.id" class="btn btn-primary btn-sm" @click="openComplete(task)">Выполнить</button>
              <template v-if="auth.isPult || auth.isAdmin">
                <button v-if="task.status === 'done'" class="btn btn-ghost btn-sm" @click="store.reopenTask(task.id)">Открыть</button>
                <button class="btn btn-danger btn-sm" @click="store.deleteTask(task.id)">Удалить</button>
              </template>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">✅</div>
          <p>Задач нет</p>
        </div>
      </template>

      <!-- ШАБЛОНЫ -->
      <template v-if="tab === 'templates'">
        <div class="page-title-row" style="margin-bottom:16px">
          <span class="page-heading" style="font-size:16px">Шаблоны задач</span>
          <button class="btn btn-primary" @click="showTemplateForm = true">+ Шаблон</button>
        </div>
        <div v-if="showTemplateForm" class="card-form">
          <h2>Новый шаблон</h2>
          <div class="form-grid">
            <div class="form-group col-2">
              <label class="form-label">Название *</label>
              <input v-model="templateForm.name" class="form-input" />
            </div>
            <div class="form-group col-2">
              <label class="form-label">Описание</label>
              <textarea v-model="templateForm.description" class="form-textarea" />
            </div>
          </div>
          <div style="display:flex;gap:8px;margin-top:16px">
            <button class="btn btn-primary" @click="submitTemplate">Сохранить</button>
            <button class="btn btn-ghost" @click="showTemplateForm = false">Отмена</button>
          </div>
        </div>
        <div v-if="store.templates.length" style="display:flex;flex-direction:column;gap:10px">
          <div v-for="t in store.templates" :key="t.id" class="card" style="display:flex;align-items:center;justify-content:space-between">
            <div>
              <div style="font-size:14px;font-weight:600;color:var(--text-primary)">{{ t.name }}</div>
              <div v-if="t.description" style="font-size:12px;color:var(--text-muted);margin-top:3px">{{ t.description }}</div>
            </div>
            <button class="btn btn-danger btn-sm" @click="store.deleteTemplate(t.id)">Удалить</button>
          </div>
        </div>
        <div v-else class="empty-state"><div class="empty-icon">🗂</div><p>Шаблонов пока нет</p></div>
      </template>

      <!-- Модал выполнения -->
      <div v-if="completeModal" class="modal-overlay" @click.self="completeModal = null">
        <div class="modal">
          <h3 class="modal-title">Отметить как выполнено</h3>
          <p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px">{{ completeModal.title }}</p>
          <textarea v-model="completeComment" class="form-textarea" placeholder="Комментарий (необязательно)" />
          <div style="display:flex;gap:8px;margin-top:16px">
            <button class="btn btn-primary" @click="submitComplete">Выполнено</button>
            <button class="btn btn-ghost" @click="completeModal = null">Отмена</button>
          </div>
        </div>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useTasksStore } from '../stores/tasks'
import { useAuthStore } from '../stores/auth'

const store = useTasksStore()
const auth = useAuthStore()

const tab = ref('tasks')
const period = ref('')
const statusFilter = ref('')
const typeLabels = { daily: 'День', weekly: 'Неделя', monthly: 'Месяц' }
const periods = [{ label:'Все', value:'' }, { label:'День', value:'daily' }, { label:'Неделя', value:'weekly' }, { label:'Месяц', value:'monthly' }]

function setPeriod(val) { period.value = val; tab.value = 'tasks'; loadTasks() }
function loadTasks() {
  const filters = {}
  if (period.value) filters.type = period.value
  if (statusFilter.value) filters.status = statusFilter.value
  store.fetchTasks(filters)
}

const showTaskForm = ref(false)
const taskError = ref('')
const taskForm = ref({ title:'', description:'', type:'daily', assigned_to_id:null, due_date:'', template_id:null })

function resetTaskForm() { taskForm.value = { title:'', description:'', type:'daily', assigned_to_id:null, due_date:'', template_id:null }; showTaskForm.value = false; taskError.value = '' }

async function submitTask() {
  taskError.value = ''
  if (!taskForm.value.title.trim()) { taskError.value = 'Название обязательно'; return }
  if (!taskForm.value.assigned_to_id) { taskError.value = 'Укажите исполнителя'; return }
  try {
    await store.createTask({ ...taskForm.value, due_date: taskForm.value.due_date || null, template_id: taskForm.value.template_id || null })
    resetTaskForm()
  } catch (e) { taskError.value = e.response?.data?.detail || 'Ошибка' }
}

const completeModal = ref(null)
const completeComment = ref('')
function openComplete(task) { completeModal.value = task; completeComment.value = '' }
async function submitComplete() { await store.completeTask(completeModal.value.id, completeComment.value); completeModal.value = null }

const showTemplateForm = ref(false)
const templateForm = ref({ name:'', description:'' })
async function submitTemplate() {
  if (!templateForm.value.name.trim()) return
  await store.createTemplate(templateForm.value)
  templateForm.value = { name:'', description:'' }
  showTemplateForm.value = false
}

function formatDate(dt) { return new Date(dt).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) }

onMounted(async () => { await store.fetchUsers(); await store.fetchTemplates(); await store.fetchTasks() })
</script>

<style scoped>
.task-card { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; transition:border-color 0.2s; }
.task-card:hover { border-color:rgba(110,231,183,0.2); }
.task-done { opacity:0.7; }
.task-main { display:flex; align-items:flex-start; gap:12px; flex:1; min-width:0; }
.task-status-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; margin-top:5px; }
.dot-pending { background:var(--warning); box-shadow:0 0 6px var(--warning); }
.dot-done { background:var(--accent); box-shadow:0 0 6px var(--accent); }
.task-body { flex:1; min-width:0; }
.task-title { font-size:14px; font-weight:600; color:var(--text-primary); }
.task-title--done { text-decoration:line-through; color:var(--text-muted); }
.task-desc { font-size:12px; color:var(--text-secondary); margin-top:4px; }
.task-completion { font-size:12px; color:var(--accent); margin-top:6px; font-style:italic; }
.task-actions { display:flex; gap:6px; flex-shrink:0; align-items:flex-start; }
.interview-meta { display:flex; flex-wrap:wrap; gap:6px; }
.meta-chip { display:inline-flex; align-items:center; gap:4px; font-size:12px; color:var(--text-secondary); background:var(--bg-elevated); border-radius:999px; padding:2px 8px; }

.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:200; display:flex; align-items:center; justify-content:center; padding:16px; backdrop-filter:blur(4px); }
.modal { background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius); padding:24px; width:100%; max-width:420px; }
.modal-title { font-size:16px; font-weight:700; color:var(--text-primary); margin-bottom:12px; }
</style>