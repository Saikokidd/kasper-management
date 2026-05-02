<template>
  <AppLayout>
    <div class="page-wrap">

      <!-- Заголовок -->
      <div class="page-title-row">
        <h1 class="page-heading">Собеседования</h1>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <div class="tabs" style="margin:0">
            <button class="tab" :class="{ active: view === 'scheduled' }" @click="switchView('scheduled')">
              📋 Назначенные
              <span v-if="store.scheduled.length" class="tab-count">{{ store.scheduled.length }}</span>
            </button>
            <button class="tab" :class="{ active: view === 'completed' }" @click="switchView('completed')">
              ✅ Прошедшие
              <span v-if="store.completed.length" class="tab-count">{{ store.completed.length }}</span>
            </button>
            <button class="tab" :class="{ active: view === 'calendar' }" @click="switchView('calendar')">
              📅 Календарь
            </button>
          </div>
          <button v-if="!auth.isPult && view !== 'calendar'" class="btn btn-primary" @click="openForm()">
            + Добавить
          </button>
        </div>
      </div>

      <!-- ФОРМА -->
      <div v-if="showForm" class="card-form">
        <h2>{{ editingId ? 'Редактировать запись' : 'Новое собеседование' }}</h2>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">ФИО *</label>
            <input v-model="form.full_name" class="form-input" placeholder="Иванов Иван Иванович" />
          </div>
          <div class="form-group">
            <label class="form-label">Дата и время</label>
            <input v-model="form.scheduled_at" type="datetime-local" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Telegram</label>
            <input v-model="form.username" class="form-input" placeholder="@username" />
          </div>
          <div class="form-group">
            <label class="form-label">Телефон</label>
            <input v-model="form.phone" class="form-input" placeholder="+380..." />
          </div>
          <div class="form-group">
            <label class="form-label">Instagram</label>
            <input v-model="form.instagram" class="form-input" placeholder="@instagram" />
          </div>
          <div class="form-group">
            <label class="form-label">TikTok</label>
            <input v-model="form.tiktok" class="form-input" placeholder="@tiktok" />
          </div>
          <div v-if="!editingId" class="form-group col-2">
            <label class="form-label">Куда добавить *</label>
            <div class="status-select">
              <button
                type="button"
                class="status-btn"
                :class="{ active: form.status === 'scheduled' }"
                @click="form.status = 'scheduled'"
              >
                📋 Назначенные
              </button>
              <button
                type="button"
                class="status-btn"
                :class="{ active: form.status === 'completed' }"
                @click="form.status = 'completed'"
              >
                ✅ Прошедшие
              </button>
            </div>
          </div>
          <div class="form-group col-2">
            <label class="form-label">Комментарий</label>
            <textarea v-model="form.comment" class="form-textarea" placeholder="Заметки..." />
          </div>
          <div v-if="form.status === 'completed'" class="form-group col-2">
            <label class="form-label">Итог собеседования</label>
            <textarea v-model="form.result" class="form-textarea" placeholder="Результат, впечатления, решение..." />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Фото</label>
            <div class="photo-upload-area">
              <div v-if="form.photo_preview" class="photo-preview">
                <img :src="form.photo_preview" alt="preview" />
                <button class="photo-remove" @click="removePhoto" type="button">✕</button>
              </div>
              <label v-else class="photo-upload-btn">
                <input type="file" accept="image/*" @change="onPhotoSelect" style="display:none" />
                <span>📷 Прикрепить фото</span>
              </label>
            </div>
          </div>
        </div>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitForm" :disabled="saving">
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
          <button class="btn btn-ghost" @click="resetForm">Отмена</button>
        </div>
      </div>

      <!-- Модал перевода в прошедшие -->
      <div v-if="completeModal" class="modal-overlay" @click.self="completeModal = null">
        <div class="modal">
          <h3 class="modal-title">Перевести в прошедшие</h3>
          <p class="modal-subtitle">{{ completeModal.full_name }}</p>
          <div class="form-group" style="margin-top:14px">
            <label class="form-label">Итог собеседования</label>
            <textarea v-model="completeResult" class="form-textarea" placeholder="Результат, решение по кандидату..." />
          </div>
          <div style="display:flex;gap:8px;margin-top:16px">
            <button class="btn btn-primary" @click="submitComplete">Перевести</button>
            <button class="btn btn-ghost" @click="completeModal = null">Отмена</button>
          </div>
        </div>
      </div>

      <!-- НАЗНАЧЕННЫЕ -->
      <template v-if="view === 'scheduled'">
        <div v-if="store.loading" class="loading-state">Загрузка...</div>
        <div v-else-if="store.scheduled.length" style="display:flex;flex-direction:column;gap:10px">
          <div v-for="item in store.scheduled" :key="item.id" class="card interview-card">
            <div class="interview-header" @click="toggleExpand(item.id)">
              <div class="interview-header-left">
                <div class="expand-arrow" :class="{ expanded: expandedIds.has(item.id) }">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="9 18 15 12 9 6"/>
                  </svg>
                </div>
                <div class="interview-avatar">{{ initials(item.full_name) }}</div>
                <div>
                  <div class="interview-name">{{ item.full_name }}</div>
                  <div class="interview-meta-row">
                    <span v-if="item.scheduled_at" class="meta-chip chip-accent">
                      📅 {{ formatDate(item.scheduled_at) }}
                    </span>
                    <span v-else class="meta-chip chip-muted">Время не указано</span>
                    <span v-if="item.phone" class="meta-chip">📞 {{ item.phone }}</span>
                  </div>
                </div>
              </div>
              <div v-if="item.photo_path" class="interview-photo-thumb">
                <img :src="photoUrl(item.photo_path)" alt="фото" />
              </div>
            </div>

            <div v-if="expandedIds.has(item.id)" class="interview-details">
              <div class="details-grid">
                <div v-if="item.username" class="detail-item">
                  <span class="detail-label">Telegram</span>
                  <span class="detail-value">{{ item.username }}</span>
                </div>
                <div v-if="item.instagram" class="detail-item">
                  <span class="detail-label">Instagram</span>
                  <span class="detail-value">{{ item.instagram }}</span>
                </div>
                <div v-if="item.tiktok" class="detail-item">
                  <span class="detail-label">TikTok</span>
                  <span class="detail-value">{{ item.tiktok }}</span>
                </div>
                <div v-if="item.phone" class="detail-item">
                  <span class="detail-label">Телефон</span>
                  <span class="detail-value">{{ item.phone }}</span>
                </div>
              </div>
              <div v-if="item.comment" class="detail-comment">
                <span class="detail-label">Комментарий</span>
                <p class="detail-value">{{ item.comment }}</p>
              </div>
              <div v-if="item.photo_path" class="detail-photo">
                <img :src="photoUrl(item.photo_path)" alt="фото кандидата" />
              </div>
              <div v-if="!auth.isPult" class="card-actions">
                <button class="btn btn-primary btn-sm" @click.stop="openCompleteModal(item)">→ В прошедшие</button>
                <button class="btn btn-ghost btn-sm" @click.stop="openForm(item)">Изменить</button>
                <button class="btn btn-danger btn-sm" @click.stop="confirmDelete(item.id)">Удалить</button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">📋</div>
          <p>Назначенных собеседований нет</p>
        </div>
      </template>

      <!-- ПРОШЕДШИЕ -->
      <template v-if="view === 'completed'">
        <div v-if="store.loading" class="loading-state">Загрузка...</div>
        <div v-else-if="store.completed.length" style="display:flex;flex-direction:column;gap:10px">
          <div v-for="item in store.completed" :key="item.id" class="card interview-card">
            <div class="interview-header" @click="toggleExpand(item.id)">
              <div class="interview-header-left">
                <div class="expand-arrow" :class="{ expanded: expandedIds.has(item.id) }">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="9 18 15 12 9 6"/>
                  </svg>
                </div>
                <div class="interview-avatar completed-avatar">{{ initials(item.full_name) }}</div>
                <div>
                  <div style="display:flex;align-items:center;gap:8px">
                    <span class="interview-name">{{ item.full_name }}</span>
                    <span class="badge badge-green">✓ Прошёл</span>
                  </div>
                  <div class="interview-meta-row">
                    <span v-if="item.scheduled_at" class="meta-chip">📅 {{ formatDate(item.scheduled_at) }}</span>
                    <span v-if="item.phone" class="meta-chip">📞 {{ item.phone }}</span>
                  </div>
                </div>
              </div>
              <div v-if="item.photo_path" class="interview-photo-thumb">
                <img :src="photoUrl(item.photo_path)" alt="фото" />
              </div>
            </div>

            <div v-if="expandedIds.has(item.id)" class="interview-details">
              <div class="details-grid">
                <div v-if="item.username" class="detail-item">
                  <span class="detail-label">Telegram</span>
                  <span class="detail-value">{{ item.username }}</span>
                </div>
                <div v-if="item.instagram" class="detail-item">
                  <span class="detail-label">Instagram</span>
                  <span class="detail-value">{{ item.instagram }}</span>
                </div>
                <div v-if="item.tiktok" class="detail-item">
                  <span class="detail-label">TikTok</span>
                  <span class="detail-value">{{ item.tiktok }}</span>
                </div>
                <div v-if="item.phone" class="detail-item">
                  <span class="detail-label">Телефон</span>
                  <span class="detail-value">{{ item.phone }}</span>
                </div>
              </div>
              <div v-if="item.comment" class="detail-comment">
                <span class="detail-label">Комментарий</span>
                <p class="detail-value">{{ item.comment }}</p>
              </div>
              <div v-if="item.result" class="interview-result">
                <span class="result-label">Итог:</span> {{ item.result }}
              </div>
              <div v-if="item.photo_path" class="detail-photo">
                <img :src="photoUrl(item.photo_path)" alt="фото кандидата" />
              </div>
              <div v-if="!auth.isPult" class="card-actions">
                <button class="btn btn-ghost btn-sm" @click.stop="openForm(item)">Изменить</button>
                <button class="btn btn-danger btn-sm" @click.stop="confirmDelete(item.id)">Удалить</button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">✅</div>
          <p>Прошедших собеседований нет</p>
        </div>
      </template>

      <!-- КАЛЕНДАРЬ -->
      <template v-if="view === 'calendar'">
        <div class="card">
          <div class="cal-header">
            <button class="btn btn-ghost btn-sm" @click="prevMonth">← Пред.</button>
            <span class="cal-title">{{ monthTitle }}</span>
            <button class="btn btn-ghost btn-sm" @click="nextMonth">След. →</button>
          </div>
          <div class="cal-legend">
            <span class="legend-item legend-scheduled">● Назначено</span>
            <span class="legend-item legend-completed">● Прошло</span>
          </div>
          <div class="cal-weekdays">
            <div v-for="d in ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']" :key="d" class="cal-weekday">{{ d }}</div>
          </div>
          <div class="cal-grid">
            <div
              v-for="(cell, i) in calendarCells" :key="i"
              class="cal-cell"
              :class="{
                'cal-cell--empty': !cell.day,
                'cal-cell--today': cell.isToday,
                'cal-cell--has-events': cell.scheduled.length || cell.completed.length
              }"
            >
              <template v-if="cell.day">
                <span class="cal-day">{{ cell.day }}</span>
                <div v-for="item in cell.scheduled" :key="'s'+item.id" class="cal-event cal-event--scheduled" :title="item.full_name">
                  {{ formatTime(item.scheduled_at) }} {{ item.full_name }}
                </div>
                <div v-for="item in cell.completed" :key="'c'+item.id" class="cal-event cal-event--completed" :title="item.full_name">
                  ✓ {{ item.full_name }}
                </div>
              </template>
            </div>
          </div>
        </div>
      </template>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useInterviewsStore } from '../stores/interviews'
import { useAuthStore } from '../stores/auth'

const store = useInterviewsStore()
const auth = useAuthStore()

const API = 'http://10.0.0.2:8000'

const view = ref('scheduled')
const showForm = ref(false)
const formError = ref('')
const saving = ref(false)
const editingId = ref(null)
const photoFile = ref(null)
const expandedIds = ref(new Set())

const defaultForm = () => ({
  full_name: '', username: '', instagram: '', tiktok: '',
  phone: '', scheduled_at: '', comment: '', result: '',
  photo_preview: null,
  status: ''
})

const form = ref(defaultForm())
const completeModal = ref(null)
const completeResult = ref('')

const today = new Date()
const calYear = ref(today.getFullYear())
const calMonth = ref(today.getMonth())

const monthTitle = computed(() =>
  new Date(calYear.value, calMonth.value, 1)
    .toLocaleString('ru-RU', { month: 'long', year: 'numeric' })
)

function prevMonth() {
  calMonth.value === 0 ? (calMonth.value = 11, calYear.value--) : calMonth.value--
}
function nextMonth() {
  calMonth.value === 11 ? (calMonth.value = 0, calYear.value++) : calMonth.value++
}

const calendarCells = computed(() => {
  const firstDay = new Date(calYear.value, calMonth.value, 1)
  const lastDay = new Date(calYear.value, calMonth.value + 1, 0)
  let startOffset = firstDay.getDay() - 1
  if (startOffset < 0) startOffset = 6
  const cells = []
  for (let i = 0; i < startOffset; i++) cells.push({ day: null, scheduled: [], completed: [] })
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${calYear.value}-${String(calMonth.value + 1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const isToday = d === today.getDate() && calMonth.value === today.getMonth() && calYear.value === today.getFullYear()
    cells.push({
      day: d, isToday,
      scheduled: store.scheduled.filter(i => i.scheduled_at?.slice(0,10) === dateStr),
      completed: store.completed.filter(i => i.scheduled_at?.slice(0,10) === dateStr),
    })
  }
  return cells
})

function toggleExpand(id) {
  const newSet = new Set(expandedIds.value)
  if (newSet.has(id)) newSet.delete(id)
  else newSet.add(id)
  expandedIds.value = newSet
}

function switchView(v) {
  view.value = v
  resetForm()
  expandedIds.value = new Set()
}

function initials(name) { return name.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase() }

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })
}
function formatTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleTimeString('ru-RU', { hour:'2-digit', minute:'2-digit' })
}

function photoUrl(path) { return `${API}/media/${path}` }

function onPhotoSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  photoFile.value = file
  form.value.photo_preview = URL.createObjectURL(file)
}

function removePhoto() {
  photoFile.value = null
  form.value.photo_preview = null
}

function openForm(item = null) {
  editingId.value = item?.id || null
  photoFile.value = null
  form.value = {
    full_name: item?.full_name || '',
    username: item?.username || '',
    instagram: item?.instagram || '',
    tiktok: item?.tiktok || '',
    phone: item?.phone || '',
    scheduled_at: item?.scheduled_at ? item.scheduled_at.slice(0,16) : '',
    comment: item?.comment || '',
    result: item?.result || '',
    photo_preview: item?.photo_path ? photoUrl(item.photo_path) : null,
    status: item?.status || '',
  }
  formError.value = ''
  showForm.value = true
}

function resetForm() {
  showForm.value = false
  editingId.value = null
  formError.value = ''
  photoFile.value = null
  form.value = defaultForm()
}

async function submitForm() {
  formError.value = ''
  if (!form.value.full_name.trim()) { formError.value = 'ФИО обязательно'; return }
  if (!editingId.value && !form.value.status) { formError.value = 'Выберите куда добавить запись'; return }
  saving.value = true
  try {
    const payload = {
      full_name: form.value.full_name,
      username: form.value.username || null,
      instagram: form.value.instagram || null,
      tiktok: form.value.tiktok || null,
      phone: form.value.phone || null,
      scheduled_at: form.value.scheduled_at || null,
      comment: form.value.comment || null,
      result: form.value.result || null,
      status: form.value.status,
    }
    let result
    if (editingId.value) {
      result = await store.update(editingId.value, payload)
    } else {
      result = await store.create(payload)
    }
    if (photoFile.value && result?.id) {
      await store.uploadPhoto(result.id, photoFile.value)
    }
    resetForm()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

function openCompleteModal(item) {
  completeModal.value = item
  completeResult.value = ''
}

async function submitComplete() {
  await store.complete(completeModal.value.id, completeResult.value)
  completeModal.value = null
}

async function confirmDelete(id) {
  if (confirm('Удалить запись?')) await store.remove(id)
}

onMounted(() => store.fetchAll())
</script>

<style scoped>
.interview-card {
  padding: 0;
  overflow: hidden;
  transition: border-color 0.2s;
}
.interview-card:hover { border-color: rgba(110,231,183,0.2); }

.interview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
  gap: 12px;
}
.interview-header:hover { background: var(--bg-hover); }

.interview-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.expand-arrow {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  flex-shrink: 0;
  transition: transform 0.2s ease, color 0.2s;
}
.expand-arrow.expanded {
  transform: rotate(90deg);
  color: var(--accent);
}

.interview-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--accent-dim); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.completed-avatar { background: rgba(96,165,250,0.12); color: #60a5fa; }

.interview-name {
  font-size: 14px; font-weight: 600;
  color: var(--text-primary); margin-bottom: 4px;
}

.interview-meta-row { display: flex; flex-wrap: wrap; gap: 5px; }
.meta-chip { display: inline-flex; align-items: center; gap: 4px; font-size: 11.5px; color: var(--text-secondary); background: var(--bg-elevated); border-radius: 999px; padding: 2px 8px; }
.chip-accent { background: var(--accent-dim); color: var(--accent); }
.chip-muted { color: var(--text-muted); }

.interview-photo-thumb {
  width: 42px; height: 42px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
  flex-shrink: 0;
}
.interview-photo-thumb img { width: 100%; height: 100%; object-fit: cover; }

.interview-details {
  border-top: 1px solid var(--border);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--bg-elevated);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 13px;
  color: var(--text-primary);
}

.detail-comment { display: flex; flex-direction: column; gap: 4px; }

.detail-photo {
  width: 120px; height: 120px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
}
.detail-photo img { width: 100%; height: 100%; object-fit: cover; }

.interview-result {
  font-size: 13px; color: var(--text-secondary);
  background: var(--bg-surface);
  border-left: 3px solid var(--accent);
  padding: 10px 12px;
  border-radius: 0 var(--radius-xs) var(--radius-xs) 0;
}
.result-label { font-weight: 600; color: var(--accent); margin-right: 6px; }

.card-actions { display: flex; gap: 6px; flex-wrap: wrap; padding-top: 4px; }

.tab-count {
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--accent-dim); color: var(--accent);
  border-radius: 999px; font-size: 10px; font-weight: 700;
  padding: 0 5px; min-width: 16px; height: 16px; margin-left: 2px;
}
.tab.active .tab-count { background: rgba(255,255,255,0.2); color: inherit; }

.photo-upload-area { display: flex; align-items: center; gap: 10px; }
.photo-preview { position: relative; width: 80px; height: 80px; }
.photo-preview img { width: 100%; height: 100%; object-fit: cover; border-radius: var(--radius-sm); border: 1px solid var(--border); }
.photo-remove {
  position: absolute; top: -6px; right: -6px;
  width: 18px; height: 18px; background: var(--danger); color: #fff;
  border: none; border-radius: 50%; cursor: pointer;
  font-size: 10px; display: flex; align-items: center; justify-content: center;
}
.photo-upload-btn {
  cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px; background: var(--bg-elevated);
  border: 1px dashed var(--border); border-radius: var(--radius-sm);
  font-size: 13px; color: var(--text-secondary); transition: all 0.15s;
}
.photo-upload-btn:hover { border-color: var(--accent); color: var(--accent); }

.status-select {
  display: flex;
  gap: 8px;
}

.status-btn {
  flex: 1;
  padding: 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.18s ease;
  font-family: inherit;
}

.status-btn:hover {
  border-color: var(--accent);
  color: var(--text-primary);
}

.status-btn.active {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}

.cal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.cal-title { font-size: 15px; font-weight: 600; color: var(--text-primary); text-transform: capitalize; }
.cal-legend { display: flex; gap: 16px; margin-bottom: 14px; }
.legend-item { font-size: 12px; }
.legend-scheduled { color: var(--accent); }
.legend-completed { color: #60a5fa; }
.cal-weekdays { display: grid; grid-template-columns: repeat(7,1fr); margin-bottom: 4px; }
.cal-weekday { text-align: center; font-size: 11px; font-weight: 600; color: var(--text-muted); padding: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.cal-grid { display: grid; grid-template-columns: repeat(7,1fr); gap: 3px; }
.cal-cell { min-height: 80px; background: var(--bg-elevated); border-radius: 8px; padding: 6px; border: 1px solid transparent; transition: border-color 0.2s; }
.cal-cell:not(.cal-cell--empty):hover { border-color: var(--border); }
.cal-cell--empty { background: transparent; }
.cal-cell--today { border-color: var(--accent) !important; }
.cal-cell--has-events { background: var(--bg-hover); }
.cal-day { font-size: 12px; font-weight: 600; color: var(--text-secondary); display: block; margin-bottom: 4px; }
.cal-cell--today .cal-day { color: var(--accent); }
.cal-event { font-size: 10px; border-radius: 4px; padding: 2px 5px; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cal-event--scheduled { background: var(--accent-dim); color: var(--accent); }
.cal-event--completed { background: rgba(96,165,250,0.12); color: #60a5fa; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 16px; backdrop-filter: blur(4px); }
.modal { background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; width: 100%; max-width: 440px; }
.modal-title { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.modal-subtitle { font-size: 13px; color: var(--text-secondary); }
</style>
