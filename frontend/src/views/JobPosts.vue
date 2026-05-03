<template>
  <AppLayout>
    <div class="page-wrap">
      <div class="page-title-row">
        <h1 class="page-heading">Объявления</h1>
        <button v-if="!auth.isPult" class="btn btn-primary" @click="openForm()">+ Добавить</button>
      </div>

      <div class="tabs">
        <button v-for="p in platforms" :key="p.value" class="tab" :class="{ active: platform === p.value }" @click="selectPlatform(p.value)">
          {{ p.icon }} {{ p.label }}
        </button>
      </div>

      <!-- Форма -->
      <div v-if="showForm" class="card-form">
        <h2>{{ editingId ? 'Редактировать' : 'Новое объявление' }}</h2>
        <div class="form-grid">
          <div v-if="!editingId" class="form-group">
            <label class="form-label">Платформа</label>
            <select v-model="form.platform" class="form-select">
              <option v-for="p in platforms" :key="p.value" :value="p.value">{{ p.icon }} {{ p.label }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Время публикации</label>
            <input v-model="form.published_at" type="datetime-local" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Отклики</label>
            <input v-model.number="form.responses" type="number" min="0" class="form-input" />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Текст объявления</label>
            <textarea v-model="form.content" class="form-textarea" placeholder="Текст, ссылка, описание..." />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Комментарий</label>
            <textarea v-model="form.comment" class="form-textarea" style="min-height:56px" />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Скриншоты</label>
            <div class="photo-previews">
              <div v-for="(photo, idx) in form.photos" :key="idx" class="photo-thumb">
                <img :src="photo.preview" />
                <button class="photo-remove" @click="form.photos.splice(idx,1)" type="button">✕</button>
              </div>
              <label class="photo-add-btn">
                <input type="file" accept="image/*" multiple @change="onPhotosSelect" style="display:none" />
                <span>+</span>
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

      <div v-if="store.loading" class="loading-state">Загрузка...</div>
      <div v-else-if="filteredPosts.length" style="display:flex;flex-direction:column;gap:10px">
        <div v-for="post in filteredPosts" :key="post.id" class="card post-card" :class="{ 'post-blocked': post.status === 'blocked' }">

          <!-- Шапка -->
          <div class="post-top">
            <div style="flex:1;min-width:0">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap">
                <span style="font-size:18px">{{ platformIcon(post.platform) }}</span>
                <span class="post-platform-name">{{ platformLabel(post.platform) }}</span>
                <button
                  v-if="!auth.isPult"
                  class="status-badge"
                  :class="post.status === 'active' ? 'status-active' : 'status-blocked'"
                  @click="openStatusModal(post)"
                  title="Нажмите чтобы изменить статус"
                >
                  {{ post.status === 'active' ? '✅ Размещено' : '🚫 Заблокировано' }}
                  <span class="status-edit-icon">✎</span>
                </button>
                <span v-else class="badge" :class="post.status === 'active' ? 'badge-green' : 'badge-red'">
                  {{ post.status === 'active' ? '✅ Размещено' : '🚫 Заблокировано' }}
                </span>
                <span class="badge badge-blue">📨 {{ post.responses }} откликов</span>
              </div>

              <div class="post-meta">
                <span v-if="post.published_at" class="meta-chip">🕐 {{ formatDate(post.published_at) }}</span>
                <span class="meta-chip">{{ post.created_by.full_name }}</span>
              </div>
            </div>
            <div v-if="!auth.isPult" class="card-actions">
              <button class="btn btn-ghost btn-sm" @click="openForm(post)">Изменить</button>
              <button class="btn btn-danger btn-sm" @click="removePost(post.id)">Удалить</button>
            </div>
          </div>

          <!-- Текст объявления -->
          <div v-if="post.content" class="post-section">
            <div class="post-section-label">Текст объявления</div>
            <p class="post-text">{{ post.content }}</p>
          </div>

          <!-- Комментарий -->
          <div v-if="post.comment" class="post-section">
            <div class="post-section-label">Комментарий</div>
            <p class="post-text">{{ post.comment }}</p>
          </div>

          <!-- Причина блокировки -->
          <div v-if="post.status === 'blocked' && post.block_reason" class="block-reason-section">
            <div class="block-reason-label">⛔ Причина блокировки</div>
            <p class="block-reason-text">{{ post.block_reason }}</p>
          </div>

          <!-- Медиафайлы -->
          <div class="post-media-section">
            <MediaUpload :entity-type="'job_post'" :entity-id="post.id" />
          </div>
        </div>
      </div>
      <div v-else class="empty-state"><div class="empty-icon">📋</div><p>Объявлений пока нет</p></div>

      <!-- Модал смены статуса -->
      <div v-if="statusModal" class="modal-overlay" @click.self="statusModal = null">
        <div class="modal">
          <h3 class="modal-title">Изменить статус</h3>
          <p style="font-size:13px;color:var(--text-secondary);margin-bottom:16px">
            {{ platformLabel(statusModal.platform) }} · {{ statusModal.published_at ? formatDate(statusModal.published_at) : 'без даты' }}
          </p>

          <div class="status-select-row">
            <button class="status-select-btn" :class="{ active: newStatus === 'active' }" @click="newStatus = 'active'">
              ✅ Размещено
            </button>
            <button class="status-select-btn status-select-btn--blocked" :class="{ active: newStatus === 'blocked' }" @click="newStatus = 'blocked'">
              🚫 Заблокировано
            </button>
          </div>

          <div v-if="newStatus === 'blocked'" style="margin-top:14px;display:flex;flex-direction:column;gap:12px">
            <div class="form-group">
              <label class="form-label">Причина блокировки *</label>
              <textarea v-model="blockReason" class="form-textarea" placeholder="Опишите причину..." style="min-height:72px" />
            </div>
            <div class="form-group">
              <label class="form-label">Скриншот блокировки</label>
              <div class="photo-upload-area">
                <div v-if="blockPhotoPreview" class="photo-preview">
                  <img :src="blockPhotoPreview" alt="preview" />
                  <button class="photo-remove-sm" @click="blockPhotoFile = null; blockPhotoPreview = null" type="button">✕</button>
                </div>
                <label v-else class="photo-upload-btn">
                  <input type="file" accept="image/*" @change="onBlockPhotoSelect" style="display:none" />
                  <span>📷 Прикрепить скриншот</span>
                </label>
              </div>
            </div>
          </div>

          <p v-if="statusError" class="form-error">{{ statusError }}</p>
          <div style="display:flex;gap:8px;margin-top:20px">
            <button class="btn btn-primary" @click="submitStatus" :disabled="savingStatus">
              {{ savingStatus ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button class="btn btn-ghost" @click="statusModal = null">Отмена</button>
          </div>
        </div>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import MediaUpload from '../components/MediaUpload.vue'
import { useJobPostsStore } from '../stores/jobPosts'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const store = useJobPostsStore()
const auth = useAuthStore()
const API = 'http://10.0.0.2:8000'

const platforms = [
  { value: 'olx',    icon: '🟠', label: 'OLX' },
  { value: 'workua', icon: '🔵', label: 'Work.UA' },
]

const platform = ref('olx')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)
const saving = ref(false)

const defaultForm = () => ({
  platform: 'olx', content: '', published_at: '',
  responses: 0, comment: '', photos: [],
})

const form = ref(defaultForm())
const filteredPosts = computed(() => store.posts.filter(p => p.platform === platform.value))

function selectPlatform(val) { platform.value = val; store.fetch(val) }
function platformIcon(val) { return platforms.find(p => p.value === val)?.icon || '📋' }
function platformLabel(val) { return platforms.find(p => p.value === val)?.label || val }

function onPhotosSelect(e) {
  for (const file of Array.from(e.target.files)) {
    form.value.photos.push({ file, preview: URL.createObjectURL(file) })
  }
  e.target.value = ''
}

function openForm(post = null) {
  editingId.value = post?.id || null
  form.value = {
    platform: post?.platform || platform.value,
    content: post?.content || '',
    published_at: post?.published_at ? post.published_at.slice(0, 16) : '',
    responses: post?.responses ?? 0,
    comment: post?.comment || '',
    photos: [],
  }
  formError.value = ''
  showForm.value = true
}

function resetForm() {
  showForm.value = false; editingId.value = null
  formError.value = ''; form.value = defaultForm()
}

async function submitForm() {
  formError.value = ''; saving.value = true
  try {
    const payload = {
      platform: form.value.platform,
      content: form.value.content || null,
      published_at: form.value.published_at || null,
      responses: form.value.responses,
      comment: form.value.comment || null,
      status: 'active',
    }
    let post
    if (editingId.value) post = await store.update(editingId.value, payload)
    else post = await store.create(payload)

    for (const photo of form.value.photos) {
      const fd = new FormData()
      fd.append('file', photo.file)
      await axios.post(`${API}/api/media/upload`, fd, {
        params: { entity_type: 'job_post', entity_id: post.id },
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    resetForm(); store.fetch(platform.value)
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Ошибка'
  } finally { saving.value = false }
}

async function removePost(id) {
  if (confirm('Удалить?')) await store.remove(id)
}

// Смена статуса
const statusModal = ref(null)
const newStatus = ref('active')
const blockReason = ref('')
const blockPhotoFile = ref(null)
const blockPhotoPreview = ref(null)
const statusError = ref('')
const savingStatus = ref(false)

function openStatusModal(post) {
  statusModal.value = post
  newStatus.value = post.status
  blockReason.value = post.block_reason || ''
  blockPhotoFile.value = null
  blockPhotoPreview.value = null
  statusError.value = ''
}

function onBlockPhotoSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  blockPhotoFile.value = file
  blockPhotoPreview.value = URL.createObjectURL(file)
  e.target.value = ''
}

async function submitStatus() {
  statusError.value = ''
  if (newStatus.value === 'blocked' && !blockReason.value.trim()) {
    statusError.value = 'Укажите причину блокировки'; return
  }
  savingStatus.value = true
  try {
    await store.update(statusModal.value.id, {
      status: newStatus.value,
      block_reason: newStatus.value === 'blocked' ? blockReason.value : null,
    })
    if (blockPhotoFile.value) {
      const fd = new FormData()
      fd.append('file', blockPhotoFile.value)
      await axios.post(`${API}/api/media/upload`, fd, {
        params: { entity_type: 'job_post', entity_id: statusModal.value.id },
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    statusModal.value = null
    store.fetch(platform.value)
  } catch (e) {
    statusError.value = e.response?.data?.detail || 'Ошибка'
  } finally { savingStatus.value = false }
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => store.fetch(platform.value))
</script>

<style scoped>
.post-card { transition:border-color 0.2s; }
.post-card:hover { border-color:rgba(110,231,183,0.2); }
.post-blocked { border-color:rgba(248,113,113,0.25) !important; }

.post-top { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:12px; }
.post-platform-name { font-size:14px; font-weight:600; color:var(--text-primary); }
.post-meta { display:flex; flex-wrap:wrap; gap:6px; }
.meta-chip { display:inline-flex; align-items:center; gap:4px; font-size:12px; color:var(--text-secondary); background:var(--bg-elevated); border-radius:999px; padding:2px 8px; }

/* Секции контента */
.post-section { margin-bottom:10px; }
.post-section-label {
  font-size:11px; font-weight:600; color:var(--text-muted);
  text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;
}
.post-text {
  font-size:13.5px; color:var(--text-primary);
  line-height:1.6; white-space:pre-wrap;
  background:var(--bg-elevated); border-radius:var(--radius-sm);
  padding:10px 12px; border:1px solid var(--border);
}

/* Блокировка */
.block-reason-section {
  margin-bottom:10px;
  background:var(--danger-dim);
  border:1px solid rgba(248,113,113,0.2);
  border-radius:var(--radius-sm);
  padding:10px 12px;
}
.block-reason-label { font-size:11px; font-weight:700; color:var(--danger); margin-bottom:4px; text-transform:uppercase; letter-spacing:0.05em; }
.block-reason-text { font-size:13px; color:var(--danger); line-height:1.5; }

.card-actions { display:flex; gap:6px; flex-shrink:0; }
.post-media-section { border-top:1px solid var(--border); padding-top:12px; margin-top:8px; }

/* Статус кнопка */
.status-badge { display:inline-flex; align-items:center; gap:5px; padding:2px 10px; border-radius:999px; font-size:11px; font-weight:600; cursor:pointer; border:none; transition:all 0.15s; font-family:inherit; }
.status-active { background:rgba(16,163,127,0.12); color:var(--accent); }
.status-active:hover { background:rgba(16,163,127,0.22); }
.status-blocked { background:var(--danger-dim); color:var(--danger); }
.status-blocked:hover { background:rgba(248,113,113,0.22); }
.status-edit-icon { font-size:10px; opacity:0.7; }

/* Модал */
.status-select-row { display:flex; gap:8px; }
.status-select-btn { flex:1; padding:10px; border-radius:var(--radius-sm); border:1px solid var(--border); background:var(--bg-elevated); color:var(--text-secondary); font-size:13px; font-weight:500; cursor:pointer; transition:all 0.18s; font-family:inherit; }
.status-select-btn:hover { border-color:var(--accent); color:var(--text-primary); }
.status-select-btn.active { background:var(--accent-dim); border-color:var(--accent); color:var(--accent); font-weight:600; }
.status-select-btn--blocked.active { background:var(--danger-dim); border-color:var(--danger); color:var(--danger); }

/* Фото */
.photo-previews { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
.photo-thumb { position:relative; width:90px; height:90px; border-radius:var(--radius-sm); overflow:hidden; border:1px solid var(--border); }
.photo-thumb img { width:100%; height:100%; object-fit:cover; }
.photo-remove { position:absolute; top:4px; right:4px; width:20px; height:20px; background:rgba(0,0,0,0.7); color:#fff; border:none; border-radius:50%; cursor:pointer; font-size:10px; display:flex; align-items:center; justify-content:center; }
.photo-remove:hover { background:var(--danger); }
.photo-add-btn { width:90px; height:90px; border:2px dashed var(--border); border-radius:var(--radius-sm); display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); font-size:28px; transition:all 0.15s; }
.photo-add-btn:hover { border-color:var(--accent); color:var(--accent); }

.photo-upload-area { display:flex; align-items:center; gap:10px; }
.photo-preview { position:relative; width:80px; height:80px; }
.photo-preview img { width:100%; height:100%; object-fit:cover; border-radius:var(--radius-sm); border:1px solid var(--border); }
.photo-remove-sm { position:absolute; top:-6px; right:-6px; width:18px; height:18px; background:var(--danger); color:#fff; border:none; border-radius:50%; cursor:pointer; font-size:10px; display:flex; align-items:center; justify-content:center; }
.photo-upload-btn { cursor:pointer; display:inline-flex; align-items:center; gap:6px; padding:8px 14px; background:var(--bg-elevated); border:1px dashed var(--border); border-radius:var(--radius-sm); font-size:13px; color:var(--text-secondary); transition:all 0.15s; }
.photo-upload-btn:hover { border-color:var(--accent); color:var(--accent); }

.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:200; display:flex; align-items:center; justify-content:center; padding:16px; backdrop-filter:blur(4px); }
.modal { background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius); padding:24px; width:100%; max-width:460px; max-height:85vh; overflow-y:auto; }
.modal-title { font-size:16px; font-weight:700; color:var(--text-primary); margin-bottom:4px; }
</style>
