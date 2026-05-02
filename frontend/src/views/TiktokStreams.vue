<template>
  <AppLayout>
    <div class="page-wrap">
      <div class="page-title-row">
        <h1 class="page-heading">TikTok <span>Эфиры</span></h1>
        <button v-if="!auth.isPult" class="btn btn-primary" @click="openForm()">+ Добавить эфир</button>
      </div>

      <!-- Сводная статистика -->
      <div v-if="store.streams.length" class="stats-row">
        <div class="stat-card">
          <div class="stat-value">{{ totalViews.toLocaleString('ru-RU') }}</div>
          <div class="stat-label">👁 Просмотров</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalSubscriptions.toLocaleString('ru-RU') }}</div>
          <div class="stat-label">➕ Подписалось</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalInquiries.toLocaleString('ru-RU') }}</div>
          <div class="stat-label">💬 За работу</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ store.streams.length }}</div>
          <div class="stat-label">🎵 Эфиров</div>
        </div>
      </div>

      <!-- Форма -->
      <div v-if="showForm" class="card-form">
        <h2>{{ editingId ? 'Редактировать эфир' : 'Новый эфир' }}</h2>
        <div class="form-grid">
          <div class="form-group col-2">
            <label class="form-label">Дата эфира *</label>
            <input v-model="form.stream_date" type="datetime-local" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">👁 Просмотров</label>
            <input v-model.number="form.views" type="number" min="0" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">➕ Подписалось</label>
            <input v-model.number="form.subscriptions" type="number" min="0" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">💬 Написало за работу</label>
            <input v-model.number="form.inquiries" type="number" min="0" class="form-input" />
          </div>
        </div>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitForm">Сохранить</button>
          <button class="btn btn-ghost" @click="resetForm">Отмена</button>
        </div>
      </div>

      <div v-if="store.loading" class="loading-state">Загрузка...</div>
      <div v-else-if="store.streams.length" style="display:flex;flex-direction:column;gap:10px">
        <div v-for="stream in store.streams" :key="stream.id" class="card stream-card">
          <div class="stream-top">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                <span style="font-size:20px">🎵</span>
                <span style="font-size:14px;font-weight:600;color:var(--text-primary)">{{ formatDate(stream.stream_date) }}</span>
              </div>
              <p style="font-size:11px;color:var(--text-muted)">{{ stream.created_by.full_name }}</p>
            </div>
            <div v-if="!auth.isPult" class="card-actions">
              <button class="btn btn-ghost btn-sm" @click="openForm(stream)">Изменить</button>
              <button class="btn btn-danger btn-sm" @click="removeStream(stream.id)">Удалить</button>
            </div>
          </div>
          <div class="stream-metrics">
            <div class="metric">
              <div class="metric-value">{{ stream.views.toLocaleString('ru-RU') }}</div>
              <div class="metric-label">👁 Просмотров</div>
            </div>
            <div class="metric">
              <div class="metric-value">{{ stream.subscriptions.toLocaleString('ru-RU') }}</div>
              <div class="metric-label">➕ Подписалось</div>
            </div>
            <div class="metric">
              <div class="metric-value">{{ stream.inquiries.toLocaleString('ru-RU') }}</div>
              <div class="metric-label">💬 За работу</div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state"><div class="empty-icon">🎵</div><p>Эфиров пока нет</p></div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useTiktokStreamsStore } from '../stores/tiktokStreams'
import { useAuthStore } from '../stores/auth'

const store = useTiktokStreamsStore()
const auth = useAuthStore()

const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)
const form = ref({ stream_date:'', views:0, subscriptions:0, inquiries:0 })

const totalViews = computed(() => store.streams.reduce((s,r) => s + r.views, 0))
const totalSubscriptions = computed(() => store.streams.reduce((s,r) => s + r.subscriptions, 0))
const totalInquiries = computed(() => store.streams.reduce((s,r) => s + r.inquiries, 0))

function openForm(stream = null) {
  editingId.value = stream?.id || null
  form.value = { stream_date: stream?.stream_date ? stream.stream_date.slice(0,16) : '', views: stream?.views ?? 0, subscriptions: stream?.subscriptions ?? 0, inquiries: stream?.inquiries ?? 0 }
  formError.value = ''; showForm.value = true
}
function resetForm() { showForm.value = false; editingId.value = null; formError.value = '' }

async function submitForm() {
  formError.value = ''
  if (!form.value.stream_date) { formError.value = 'Укажите дату'; return }
  try {
    if (editingId.value) await store.update(editingId.value, { ...form.value })
    else await store.create({ ...form.value })
    resetForm()
  } catch (e) { formError.value = e.response?.data?.detail || 'Ошибка' }
}

async function removeStream(id) { if (confirm('Удалить?')) await store.remove(id) }

function formatDate(dt) { return new Date(dt).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) }

onMounted(() => store.fetch())
</script>

<style scoped>
.stats-row { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:24px; }
@media (max-width:600px) { .stats-row { grid-template-columns:repeat(2,1fr); } }
.stat-card { background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius); padding:16px; text-align:center; }
.stat-value { font-size:24px; font-weight:700; color:var(--accent); margin-bottom:4px; }
.stat-label { font-size:12px; color:var(--text-muted); }

.stream-card { transition: border-color 0.2s; }
.stream-card:hover { border-color: rgba(110,231,183,0.2); }
.stream-top { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px; }
.stream-metrics { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; border-top:1px solid var(--border); padding-top:14px; }
.metric { text-align:center; background:var(--bg-elevated); border-radius:var(--radius-sm); padding:12px 8px; }
.metric-value { font-size:20px; font-weight:700; color:var(--text-primary); margin-bottom:3px; }
.metric-label { font-size:11px; color:var(--text-muted); }
.card-actions { display:flex; gap:6px; }
</style>