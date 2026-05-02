<template>
  <div class="media-upload">
    <div v-if="files.length" class="media-list">
      <div v-for="f in files" :key="f.id" class="media-item">
        <div class="media-item-left">
          <span class="media-file-icon">{{ fileIcon(f.filename) }}</span>
          <div class="media-file-info">
            <p class="media-file-name">{{ f.filename }}</p>
            <p class="media-file-meta">{{ formatSize(f.size) }} · {{ formatDate(f.uploaded_at) }}</p>
          </div>
        </div>
        <div class="media-item-actions">
          <a :href="downloadUrl(f.id)" target="_blank" class="btn btn-ghost btn-sm">Скачать</a>
          <button v-if="canDelete" @click="removeFile(f.id)" class="btn btn-danger btn-sm">✕</button>
        </div>
      </div>
    </div>

    <p v-else-if="loaded" class="media-empty">Файлов нет</p>

    <div v-if="unavailable" class="media-unavailable">
      ⚠️ Файловое хранилище временно недоступно
    </div>

    <div v-if="canUpload && !unavailable" class="media-upload-btn">
      <label class="media-upload-label">
        <input type="file" class="media-file-input" @change="uploadFile" :disabled="uploading" />
        <span class="btn btn-ghost btn-sm">
          {{ uploading ? '⏳ Загрузка...' : '📎 Прикрепить файл' }}
        </span>
      </label>
      <p v-if="uploadError" class="form-error" style="margin-top:6px">{{ uploadError }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  entityType: { type: String, required: true },
  entityId: { type: Number, required: true },
})

const API = 'http://10.0.0.2:8000'
const auth = useAuthStore()

const files = ref([])
const loaded = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const unavailable = ref(false)

const canUpload = computed(() => !auth.isPult)
const canDelete = computed(() => !auth.isPult)

async function loadFiles() {
  try {
    const res = await axios.get(`${API}/api/media`, { params: { entity_type: props.entityType, entity_id: props.entityId } })
    files.value = res.data
    unavailable.value = false
  } catch { unavailable.value = true }
  finally { loaded.value = true }
}

async function uploadFile(e) {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true; uploadError.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await axios.post(`${API}/api/media/upload`, formData, {
      params: { entity_type: props.entityType, entity_id: props.entityId },
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    files.value.unshift(res.data)
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Ошибка загрузки'
    if (!err.response) unavailable.value = true
  } finally { uploading.value = false; e.target.value = '' }
}

async function removeFile(id) {
  if (!confirm('Удалить файл?')) return
  try { await axios.delete(`${API}/api/media/${id}`); files.value = files.value.filter(f => f.id !== id) }
  catch { unavailable.value = true }
}

function downloadUrl(id) { return `${API}/api/media/download/${id}` }

function fileIcon(name) {
  const ext = name.split('.').pop().toLowerCase()
  if (['jpg','jpeg','png','gif','webp'].includes(ext)) return '🖼'
  if (ext === 'pdf') return '📄'
  if (['doc','docx'].includes(ext)) return '📝'
  if (['xls','xlsx'].includes(ext)) return '📊'
  if (['mp4','mov','avi'].includes(ext)) return '🎥'
  return '📎'
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' Б'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' КБ'
  return (bytes / 1024 / 1024).toFixed(1) + ' МБ'
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' })
}

onMounted(loadFiles)
</script>

<style scoped>
.media-upload { display: flex; flex-direction: column; gap: 8px; }

.media-list { display: flex; flex-direction: column; gap: 6px; }

.media-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
}

.media-item-left { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1; }
.media-file-icon { font-size: 18px; flex-shrink: 0; }
.media-file-info { min-width: 0; }
.media-file-name { font-size: 12.5px; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.media-file-meta { font-size: 11px; color: var(--text-muted); margin-top: 1px; }
.media-item-actions { display: flex; gap: 4px; flex-shrink: 0; }

.media-empty { font-size: 12px; color: var(--text-muted); }

.media-unavailable {
  font-size: 12px;
  color: var(--warning);
  background: var(--warning-dim);
  border-radius: var(--radius-xs);
  padding: 6px 10px;
}

.media-upload-label { cursor: pointer; display: inline-block; }
.media-file-input { display: none; }
</style>