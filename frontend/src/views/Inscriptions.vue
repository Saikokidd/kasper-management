<template>
  <AppLayout>
    <div class="page-wrap">

      <div class="page-title-row">
        <h1 class="page-heading">Прописи</h1>
        <div style="display:flex;gap:8px">
          <input v-model="search" @input="onSearch" class="form-input" style="width:220px" placeholder="Поиск..." />
          <button v-if="!auth.isPult" class="btn btn-primary" @click="openForm()">+ Добавить</button>
        </div>
      </div>

      <!-- Форма -->
      <div v-if="showForm" class="card-form">
        <h2>{{ editingId ? 'Редактировать' : 'Новая пропись' }}</h2>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">ФИО *</label>
            <input v-model="form.full_name" class="form-input" placeholder="Иванов Иван" />
          </div>
          <div class="form-group">
            <label class="form-label">Никнейм</label>
            <input v-model="form.username" class="form-input" placeholder="@username" />
          </div>
          <div class="form-group">
            <label class="form-label">Телефон</label>
            <input v-model="form.phone" class="form-input" placeholder="+380..." />
          </div>
          <div class="form-group">
            <label class="form-label">Источник</label>
            <input v-model="form.source_text" class="form-input" placeholder="Откуда пришёл..." />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Соцсеть</label>
            <div class="social-select">
              <button
                v-for="s in socials"
                :key="s.value"
                type="button"
                class="social-btn"
                :class="{ active: form.social_network === s.value }"
                @click="toggleSocial(s.value)"
              >
                <span>{{ s.icon }}</span>
                {{ s.label }}
              </button>
            </div>
          </div>
          <div class="form-group col-2">
            <label class="form-label">Комментарий</label>
            <textarea v-model="form.comment" class="form-textarea" placeholder="Заметки..." />
          </div>
        </div>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitForm">Сохранить</button>
          <button class="btn btn-ghost" @click="resetForm">Отмена</button>
        </div>
      </div>

      <div v-if="store.loading" class="loading-state">Загрузка...</div>

      <div v-else-if="store.inscriptions.length" style="display:flex;flex-direction:column;gap:10px">
        <div v-for="item in store.inscriptions" :key="item.id" class="card insc-card">
          <div class="insc-header" @click="toggleExpand(item.id)">
            <div class="insc-header-left">
              <div class="expand-arrow" :class="{ expanded: expandedIds.has(item.id) }">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </div>
              <div class="insc-avatar">{{ initials(item.full_name) }}</div>
              <div class="insc-main-info">
                <div class="insc-name-row">
                  <span class="insc-name">{{ item.full_name }}</span>
                  <span v-if="item.social_network" class="social-badge" :class="'social-' + item.social_network">
                    {{ socialIcon(item.social_network) }} {{ socialLabel(item.social_network) }}
                  </span>
                  <span v-if="item.source_text" class="source-badge">{{ item.source_text }}</span>
                </div>
                <div class="insc-meta-row">
                  <span v-if="item.username" class="meta-chip">💬 {{ item.username }}</span>
                  <span v-if="item.phone" class="meta-chip">📞 {{ item.phone }}</span>
                </div>
              </div>
            </div>
            <span class="insc-date-short">{{ formatDateShort(item.created_at) }}</span>
          </div>

          <div v-if="expandedIds.has(item.id)" class="insc-details">
            <div class="details-grid">
              <div v-if="item.username" class="detail-item">
                <span class="detail-label">Никнейм</span>
                <span class="detail-value">{{ item.username }}</span>
              </div>
              <div v-if="item.phone" class="detail-item">
                <span class="detail-label">Телефон</span>
                <span class="detail-value">{{ item.phone }}</span>
              </div>
              <div v-if="item.source_text" class="detail-item">
                <span class="detail-label">Источник</span>
                <span class="detail-value">{{ item.source_text }}</span>
              </div>
              <div v-if="item.referred_by" class="detail-item">
                <span class="detail-label">От кого</span>
                <span class="detail-value">{{ item.referred_by.full_name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Добавил</span>
                <span class="detail-value">{{ item.created_by.full_name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Дата</span>
                <span class="detail-value">{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
            <div v-if="item.comment" class="detail-comment">
              <span class="detail-label">Комментарий</span>
              <p class="detail-value">{{ item.comment }}</p>
            </div>
            <div v-if="!auth.isPult" class="card-actions">
              <button class="btn btn-ghost btn-sm" @click.stop="openForm(item)">Изменить</button>
              <button class="btn btn-danger btn-sm" @click.stop="confirmDelete(item.id)">Удалить</button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">✍️</div>
        <p>{{ search ? 'Ничего не найдено' : 'Прописей пока нет' }}</p>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useInscriptionsStore } from '../stores/inscriptions'
import { useAuthStore } from '../stores/auth'

const store = useInscriptionsStore()
const auth = useAuthStore()

const search = ref('')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)
const expandedIds = ref(new Set())

const socials = [
  { value: 'tiktok',    icon: '🎵', label: 'TikTok' },
  { value: 'telegram',  icon: '✈️', label: 'Telegram' },
  { value: 'instagram', icon: '📸', label: 'Instagram' },
  { value: 'facebook',  icon: '👥', label: 'Facebook' },
]

const defaultForm = () => ({
  full_name: '',
  username: '',
  phone: '',
  social_network: '',
  source_text: '',
  referred_by_id: null,
  comment: '',
})

const form = ref(defaultForm())

function toggleSocial(val) {
  form.value.social_network = form.value.social_network === val ? '' : val
}

function socialIcon(val) {
  return socials.find(s => s.value === val)?.icon || ''
}

function socialLabel(val) {
  return socials.find(s => s.value === val)?.label || val
}

function toggleExpand(id) {
  const newSet = new Set(expandedIds.value)
  if (newSet.has(id)) newSet.delete(id)
  else newSet.add(id)
  expandedIds.value = newSet
}

function initials(name) {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDateShort(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function openForm(item = null) {
  editingId.value = item?.id || null
  form.value = {
    full_name: item?.full_name || '',
    username: item?.username || '',
    phone: item?.phone || '',
    social_network: item?.social_network || '',
    source_text: item?.source_text || '',
    referred_by_id: item?.referred_by?.id || null,
    comment: item?.comment || '',
  }
  formError.value = ''
  showForm.value = true
}

function resetForm() {
  showForm.value = false
  editingId.value = null
  formError.value = ''
  form.value = defaultForm()
}

async function submitForm() {
  formError.value = ''
  if (!form.value.full_name.trim()) { formError.value = 'ФИО обязательно'; return }
  try {
    const payload = {
      ...form.value,
      social_network: form.value.social_network || null,
      source_text: form.value.source_text || null,
    }
    if (editingId.value) await store.update(editingId.value, payload)
    else await store.create(payload)
    resetForm()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Ошибка сохранения'
  }
}

async function confirmDelete(id) {
  if (confirm('Удалить запись?')) await store.remove(id)
}

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => store.fetch(search.value), 400)
}

onMounted(() => store.fetch())
</script>

<style scoped>
.insc-card {
  padding: 0;
  overflow: hidden;
  transition: border-color 0.2s;
}
.insc-card:hover { border-color: rgba(110,231,183,0.2); }

.insc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
  gap: 12px;
}
.insc-header:hover { background: var(--bg-hover); }

.insc-header-left {
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

.insc-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--accent-dim); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
}

.insc-main-info {
  flex: 1;
  min-width: 0;
}

.insc-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.insc-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.social-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.social-tiktok    { background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.15); }
.social-telegram  { background: rgba(41,182,246,0.15); color: #29b6f6; }
.social-instagram { background: rgba(225,48,108,0.15); color: #e1306c; }
.social-facebook  { background: rgba(66,103,178,0.15); color: #4267B2; }

.source-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  background: var(--bg-elevated);
  color: var(--text-muted);
  border: 1px solid var(--border);
}

.insc-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: var(--text-secondary);
  background: var(--bg-elevated);
  border-radius: 999px;
  padding: 2px 8px;
}

.insc-date-short {
  font-size: 11px;
  color: var(--text-muted);
  flex-shrink: 0;
  white-space: nowrap;
}

.insc-details {
  border-top: 1px solid var(--border);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--bg-elevated);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
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

.card-actions { display: flex; gap: 6px; flex-wrap: wrap; padding-top: 4px; }

/* Соцсети в форме */
.social-select {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.social-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
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

.social-btn:hover {
  border-color: var(--accent);
  color: var(--text-primary);
}

.social-btn.active {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}
</style>
