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
            <select v-model="form.source" class="form-select">
              <option value="self">Сам пришёл</option>
              <option value="referral">Реферал</option>
            </select>
          </div>
          <div v-if="form.source === 'referral'" class="form-group col-2">
            <label class="form-label">От кого (ID пользователя)</label>
            <input v-model.number="form.referred_by_id" type="number" class="form-input" placeholder="ID сотрудника" />
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
          <div class="insc-main">
            <div class="insc-avatar">{{ initials(item.full_name) }}</div>
            <div class="insc-info">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                <span class="insc-name">{{ item.full_name }}</span>
                <span class="badge" :class="item.source === 'referral' ? 'badge-purple' : 'badge-green'">
                  {{ item.source === 'referral' ? '👥 Реферал' : '🙋 Сам' }}
                </span>
              </div>
              <div class="interview-meta">
                <span v-if="item.username" class="meta-chip">💬 {{ item.username }}</span>
                <span v-if="item.phone" class="meta-chip">📞 {{ item.phone }}</span>
                <span v-if="item.referred_by" class="meta-chip">👤 От: {{ item.referred_by.full_name }}</span>
              </div>
              <p v-if="item.comment" class="interview-comment">{{ item.comment }}</p>
              <p class="insc-date">{{ formatDate(item.created_at) }}</p>
            </div>
          </div>
          <div v-if="!auth.isPult" class="card-actions">
            <button class="btn btn-ghost btn-sm" @click="openForm(item)">Изменить</button>
            <button class="btn btn-danger btn-sm" @click="confirmDelete(item.id)">Удалить</button>
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
const form = ref({ full_name: '', username: '', phone: '', source: 'self', referred_by_id: null, comment: '' })

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => store.fetch(search.value), 400)
}

function initials(name) { return name.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase() }
function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })
}

function openForm(item = null) {
  editingId.value = item?.id || null
  form.value = {
    full_name: item?.full_name || '',
    username: item?.username || '',
    phone: item?.phone || '',
    source: item?.source || 'self',
    referred_by_id: item?.referred_by?.id || null,
    comment: item?.comment || '',
  }
  formError.value = ''
  showForm.value = true
}

function resetForm() {
  showForm.value = false; editingId.value = null; formError.value = ''
  form.value = { full_name: '', username: '', phone: '', source: 'self', referred_by_id: null, comment: '' }
}

async function submitForm() {
  formError.value = ''
  if (!form.value.full_name.trim()) { formError.value = 'ФИО обязательно'; return }
  try {
    const payload = { ...form.value, referred_by_id: form.value.source === 'referral' ? form.value.referred_by_id : null }
    if (editingId.value) await store.update(editingId.value, payload)
    else await store.create(payload)
    resetForm()
  } catch (e) { formError.value = e.response?.data?.detail || 'Ошибка сохранения' }
}

async function confirmDelete(id) {
  if (confirm('Удалить запись?')) await store.remove(id)
}

onMounted(() => store.fetch())
</script>

<style scoped>
.insc-card { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; transition: border-color 0.2s; }
.insc-card:hover { border-color: rgba(110,231,183,0.2); }
.insc-main { display: flex; align-items: flex-start; gap: 12px; flex: 1; min-width: 0; }
.insc-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--accent-dim); color: var(--accent);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.insc-info { flex: 1; min-width: 0; }
.insc-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.insc-date { font-size: 11px; color: var(--text-muted); margin-top: 6px; }
.interview-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px; }
.meta-chip { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: var(--text-secondary); background: var(--bg-elevated); border-radius: 999px; padding: 2px 8px; }
.interview-comment { font-size: 12px; color: var(--text-muted); font-style: italic; margin-top: 4px; }
.card-actions { display: flex; gap: 6px; flex-shrink: 0; }
</style>