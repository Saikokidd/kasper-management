<template>
  <AppLayout>
    <div class="page-wrap">

      <!-- Шапка -->
      <div class="page-title-row">
        <div style="display:flex;align-items:center;gap:12px">
          <button class="btn btn-ghost btn-sm" @click="$router.push('/candidates')">← Назад</button>
          <h1 class="page-heading">{{ candidate?.full_name || '...' }}</h1>
        </div>
        <div v-if="!auth.isPult && candidate" style="display:flex;gap:8px">
          <button class="btn btn-ghost" @click="openEdit">Изменить</button>
          <button class="btn btn-danger" @click="confirmDelete">Удалить</button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">Загрузка...</div>

      <div v-else-if="candidate">

        <!-- Мета -->
        <div class="card meta-card">
          <div class="meta-row">
            <div class="meta-item">
              <span class="detail-label">Шаблон</span>
              <span class="badge badge-blue">{{ candidate.template.name }}</span>
            </div>
            <div class="meta-item">
              <span class="detail-label">Добавил</span>
              <span class="detail-value">{{ candidate.created_by.full_name }}</span>
            </div>
            <div class="meta-item">
              <span class="detail-label">Дата</span>
              <span class="detail-value">{{ formatDate(candidate.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Поля анкеты -->
        <div class="card fields-card">
          <h2 class="section-title">Данные анкеты</h2>
          <div class="fields-grid">
            <div
              v-for="field in candidate.template.fields"
              :key="field.key"
              class="field-item"
              :class="{ 'field-full': field.type === 'textarea' || field.type === 'photo' }"
            >
              <span class="detail-label">{{ field.label }}</span>

              <!-- Фото поле -->
              <div v-if="field.type === 'photo'" class="photo-field">
                <div v-if="photosByField[field.key] && photosByField[field.key].length" class="photo-grid">
                  <div
                    v-for="photo in photosByField[field.key]"
                    :key="photo.id"
                    class="photo-item"
                  >
                    <img :src="mediaUrl(photo.path)" :alt="field.label" @click="openPhoto(mediaUrl(photo.path))" />
                    <button v-if="!auth.isPult" class="photo-delete" @click="deletePhoto(photo.id, field.key)">✕</button>
                  </div>
                  <label
                    v-if="photosByField[field.key].length < 3 && !auth.isPult"
                    class="photo-add"
                  >
                    <input type="file" accept="image/*" @change="uploadPhoto($event, field.key)" style="display:none" />
                    <span>+</span>
                  </label>
                </div>
                <label v-else-if="!auth.isPult" class="photo-upload-btn">
                  <input type="file" accept="image/*" @change="uploadPhoto($event, field.key)" style="display:none" />
                  <span>📷 Прикрепить фото</span>
                </label>
                <span v-else class="detail-value muted">Фото нет</span>
              </div>

              <!-- Обычное поле -->
              <span v-else class="detail-value">{{ candidate.fields[field.key] || '—' }}</span>
            </div>
          </div>
        </div>

      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📋</div>
        <p>Анкета не найдена</p>
      </div>

      <!-- Модал редактирования -->
      <div v-if="editModal" class="modal-overlay" @click.self="editModal = false">
        <div class="modal modal-large">
          <h3 class="modal-title">Редактировать анкету</h3>
          <div class="form-group" style="margin-bottom:14px">
            <label class="form-label">ФИО *</label>
            <input v-model="editForm.full_name" class="form-input" />
          </div>
          <div class="fields-grid" style="margin-top:14px">
            <div
              v-for="field in candidate.template.fields"
              :key="field.key"
              class="field-item"
              :class="{ 'field-full': field.type === 'textarea' || field.type === 'photo' }"
            >
              <label class="form-label">
                {{ field.label }}
                <span v-if="field.required" style="color:var(--danger)"> *</span>
              </label>
              <div v-if="field.type === 'photo'" style="font-size:12px;color:var(--text-muted)">
                Фото управляются на странице анкеты
              </div>
              <textarea v-else-if="field.type === 'textarea'" v-model="editForm.fields[field.key]" class="form-textarea" />
              <select v-else-if="field.type === 'select'" v-model="editForm.fields[field.key]" class="form-select">
                <option value="">—</option>
                <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <input v-else v-model="editForm.fields[field.key]" :type="field.type === 'date' ? 'date' : 'text'" class="form-input" />
            </div>
          </div>
          <p v-if="editError" class="form-error">{{ editError }}</p>
          <div style="display:flex;gap:8px;margin-top:20px">
            <button class="btn btn-primary" @click="submitEdit">Сохранить</button>
            <button class="btn btn-ghost" @click="editModal = false">Отмена</button>
          </div>
        </div>
      </div>

      <!-- Лайтбокс фото -->
      <div v-if="lightbox" class="lightbox" @click="lightbox = null">
        <img :src="lightbox" alt="фото" />
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const API = import.meta.env.VITE_API_URL
const id = route.params.id

const candidate = ref(null)
const loading = ref(true)
const photosByField = ref({})
const editModal = ref(false)
const editError = ref('')
const lightbox = ref(null)
const editForm = ref({ full_name: '', fields: {} })

function mediaUrl(path) { return `${API}/api/media/download/${path}` }

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadCandidate() {
  loading.value = true
  try {
    const res = await axios.get(`${API}/api/candidates/${id}`)
    candidate.value = res.data
    await loadPhotos()
  } catch {
    candidate.value = null
  } finally {
    loading.value = false
  }
}

async function loadPhotos() {
  if (!candidate.value) return
  const photoFields = candidate.value.template.fields.filter(f => f.type === 'photo')
  for (const field of photoFields) {
    try {
      const res = await axios.get(`${API}/api/media`, {
        params: { entity_type: `candidate_${field.key}`, entity_id: Number(id) }
      })
      photosByField.value[field.key] = res.data
    } catch {
      photosByField.value[field.key] = []
    }
  }
}

async function uploadPhoto(e, fieldKey) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await axios.post(`${API}/api/media/upload`, formData, {
      params: { entity_type: `candidate_${fieldKey}`, entity_id: Number(id) },
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (!photosByField.value[fieldKey]) photosByField.value[fieldKey] = []
    photosByField.value[fieldKey].push(res.data)
  } catch (err) {
    alert('Ошибка загрузки фото')
  }
  e.target.value = ''
}

async function deletePhoto(photoId, fieldKey) {
  if (!confirm('Удалить фото?')) return
  try {
    await axios.delete(`${API}/api/media/${photoId}`)
    photosByField.value[fieldKey] = photosByField.value[fieldKey].filter(p => p.id !== photoId)
  } catch {
    alert('Ошибка удаления')
  }
}

function openPhoto(url) { lightbox.value = url }

function openEdit() {
  editForm.value = {
    full_name: candidate.value.full_name,
    fields: { ...candidate.value.fields }
  }
  editError.value = ''
  editModal.value = true
}

async function submitEdit() {
  editError.value = ''
  if (!editForm.value.full_name.trim()) { editError.value = 'ФИО обязательно'; return }
  try {
    const res = await axios.patch(`${API}/api/candidates/${id}`, {
      full_name: editForm.value.full_name,
      fields: editForm.value.fields
    })
    candidate.value = res.data
    editModal.value = false
  } catch (e) {
    editError.value = e.response?.data?.detail || 'Ошибка'
  }
}

async function confirmDelete() {
  if (!confirm('Удалить анкету?')) return
  try {
    await axios.delete(`${API}/api/candidates/${id}`)
    router.push('/candidates')
  } catch {
    alert('Ошибка удаления')
  }
}

onMounted(loadCandidate)
</script>

<style scoped>
.meta-card { margin-bottom: 16px; }
.meta-row { display: flex; gap: 24px; flex-wrap: wrap; }
.meta-item { display: flex; flex-direction: column; gap: 4px; }

.fields-card { margin-bottom: 16px; }
.section-title { font-size: 15px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }

.fields-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
@media (max-width: 600px) { .fields-grid { grid-template-columns: 1fr; } }

.field-item { display: flex; flex-direction: column; gap: 6px; }
.field-full { grid-column: span 2; }
@media (max-width: 600px) { .field-full { grid-column: span 1; } }

.detail-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
}

.detail-value.muted { color: var(--text-muted); }

/* Фото */
.photo-field { display: flex; flex-direction: column; gap: 8px; }

.photo-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.photo-item {
  position: relative;
  width: 100px; height: 100px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
  flex-shrink: 0;
}

.photo-item img {
  width: 100%; height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: opacity 0.15s;
}
.photo-item img:hover { opacity: 0.85; }

.photo-delete {
  position: absolute; top: 4px; right: 4px;
  width: 20px; height: 20px;
  background: rgba(0,0,0,0.7); color: #fff;
  border: none; border-radius: 50%; cursor: pointer;
  font-size: 10px; display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.photo-delete:hover { background: var(--danger); }

.photo-add {
  width: 100px; height: 100px;
  border: 2px dashed var(--border);
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 28px;
  transition: all 0.15s;
  flex-shrink: 0;
}
.photo-add:hover { border-color: var(--accent); color: var(--accent); }

.photo-upload-btn {
  cursor: pointer; display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px; background: var(--bg-elevated);
  border: 1px dashed var(--border); border-radius: var(--radius-sm);
  font-size: 13px; color: var(--text-secondary); transition: all 0.15s;
  width: fit-content;
}
.photo-upload-btn:hover { border-color: var(--accent); color: var(--accent); }

/* Модал */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  z-index: 200; display: flex; align-items: center; justify-content: center;
  padding: 16px; backdrop-filter: blur(4px);
}
.modal {
  background: var(--bg-surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 24px; width: 100%; max-width: 440px;
  max-height: 85vh; overflow-y: auto;
}
.modal-large { max-width: 640px; }
.modal-title { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; }

/* Лайтбокс */
.lightbox {
  position: fixed; inset: 0; background: rgba(0,0,0,0.9);
  z-index: 300; display: flex; align-items: center; justify-content: center;
  cursor: zoom-out; padding: 20px;
}
.lightbox img { max-width: 100%; max-height: 100%; object-fit: contain; border-radius: var(--radius-sm); }
</style>
