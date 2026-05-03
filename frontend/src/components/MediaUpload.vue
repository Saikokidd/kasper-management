<template>
  <div class="media-upload">

    <!-- Галерея изображений -->
    <div v-if="imageFiles.length" class="photo-gallery">
      <div v-for="f in imageFiles" :key="f.id" class="gallery-item">
        <img :src="photoUrl(f.path)" :alt="f.filename" @click="lightbox = photoUrl(f.path)" />
        <button v-if="canDelete" class="gallery-delete" @click="removeFile(f.id)">✕</button>
      </div>
    </div>

    <!-- Прочие файлы -->
    <div v-if="otherFiles.length" class="media-list">
      <div v-for="f in otherFiles" :key="f.id" class="media-item">
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

    <p v-if="loaded && !files.length" class="media-empty">Фото нет</p>

    <div v-if="unavailable" class="media-unavailable">
      ⚠️ Файловое хранилище временно недоступно
    </div>

    <div v-if="canUpload && !unavailable" class="media-upload-btn">
      <label class="media-upload-label">
        <input type="file" accept="image/*" multiple class="media-file-input" @change="uploadFiles" :disabled="uploading" />
        <span class="btn btn-ghost btn-sm">
          {{ uploading ? '⏳ Загрузка...' : '📷 Добавить фото' }}
        </span>
      </label>
      <p v-if="uploadError" class="form-error" style="margin-top:6px">{{ uploadError }}</p>
    </div>

    <!-- Лайтбокс -->
    <div v-if="lightbox" class="lightbox" @click="lightbox = null">
      <img :src="lightbox" alt="фото" />
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const lightbox = ref(null)

const canUpload = computed(() => !auth.isPult)
const canDelete = computed(() => !auth.isPult)

const IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']

function isImage(filename) {
  const ext = filename.split('.').pop().toLowerCase()
  return IMAGE_EXTS.includes(ext)
}

const imageFiles = computed(() => files.value.filter(f => isImage(f.filename)))
const otherFiles = computed(() => files.value.filter(f => !isImage(f.filename)))

// Статика отдаётся напрямую через /media/{path}
function photoUrl(path) { return `${API}/media/${path}` }
function downloadUrl(id) { return `${API}/api/media/download/${id}` }

async function loadFiles() {
  try {
    const res = await axios.get(`${API}/api/media`, {
      params: { entity_type: props.entityType, entity_id: props.entityId }
    })
    files.value = res.data
    unavailable.value = false
  } catch {
    unavailable.value = true
  } finally {
    loaded.value = true
  }
}

async function uploadFiles(e) {
  const selectedFiles = Array.from(e.target.files)
  if (!selectedFiles.length) return
  uploading.value = true
  uploadError.value = ''
  try {
    for (const file of selectedFiles) {
      const formData = new FormData()
      formData.append('file', file)
      const res = await axios.post(`${API}/api/media/upload`, formData, {
        params: { entity_type: props.entityType, entity_id: props.entityId },
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      files.value.unshift(res.data)
    }
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Ошибка загрузки'
    if (!err.response) unavailable.value = true
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

async function removeFile(id) {
  if (!confirm('Удалить фото?')) return
  try {
    await axios.delete(`${API}/api/media/${id}`)
    files.value = files.value.filter(f => f.id !== id)
  } catch {
    unavailable.value = true
  }
}

function fileIcon(name) {
  const ext = name.split('.').pop().toLowerCase()
  if (['doc', 'docx'].includes(ext)) return '📝'
  if (['xls', 'xlsx'].includes(ext)) return '📊'
  if (ext === 'pdf') return '📄'
  if (['mp4', 'mov', 'avi'].includes(ext)) return '🎥'
  return '📎'
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' Б'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' КБ'
  return (bytes / 1024 / 1024).toFixed(1) + ' МБ'
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(loadFiles)
</script>

<style scoped>
.media-upload { display:flex; flex-direction:column; gap:10px; }

.photo-gallery { display:flex; flex-wrap:wrap; gap:10px; }

.gallery-item {
  position:relative; width:100px; height:100px;
  border-radius:var(--radius-sm); overflow:hidden;
  border:1px solid var(--border); flex-shrink:0;
}

.gallery-item img {
  width:100%; height:100%; object-fit:cover;
  cursor:zoom-in; transition:opacity 0.15s, transform 0.15s;
  display:block;
}
.gallery-item img:hover { opacity:0.85; transform:scale(1.03); }

.gallery-delete {
  position:absolute; top:4px; right:4px;
  width:20px; height:20px;
  background:rgba(0,0,0,0.65); color:#fff;
  border:none; border-radius:50%; cursor:pointer;
  font-size:10px; display:flex; align-items:center; justify-content:center;
  transition:background 0.15s; opacity:0;
}
.gallery-item:hover .gallery-delete { opacity:1; }
.gallery-delete:hover { background:var(--danger); }

.media-list { display:flex; flex-direction:column; gap:6px; }
.media-item { display:flex; align-items:center; justify-content:space-between; gap:10px; background:var(--bg-elevated); border:1px solid var(--border); border-radius:var(--radius-sm); padding:8px 10px; }
.media-item-left { display:flex; align-items:center; gap:8px; min-width:0; flex:1; }
.media-file-icon { font-size:18px; flex-shrink:0; }
.media-file-info { min-width:0; }
.media-file-name { font-size:12.5px; color:var(--text-primary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.media-file-meta { font-size:11px; color:var(--text-muted); margin-top:1px; }
.media-item-actions { display:flex; gap:4px; flex-shrink:0; }

.media-empty { font-size:12px; color:var(--text-muted); }
.media-unavailable { font-size:12px; color:var(--warning); background:var(--warning-dim); border-radius:var(--radius-xs); padding:6px 10px; }
.media-upload-label { cursor:pointer; display:inline-block; }
.media-file-input { display:none; }

.lightbox { position:fixed; inset:0; background:rgba(0,0,0,0.92); z-index:500; display:flex; align-items:center; justify-content:center; cursor:zoom-out; padding:20px; }
.lightbox img { max-width:100%; max-height:100%; object-fit:contain; border-radius:var(--radius-sm); }
</style>
