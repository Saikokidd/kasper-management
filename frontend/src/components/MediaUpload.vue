<template>
  <div>
    <div v-if="files.length" class="space-y-2 mb-3">
      <div v-for="f in files" :key="f.id"
        class="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
        <div class="flex items-center gap-2 min-w-0">
          <span class="text-lg">{{ fileIcon(f.filename) }}</span>
          <div class="min-w-0">
            <p class="text-sm text-gray-700 truncate">{{ f.filename }}</p>
            <p class="text-xs text-gray-400">{{ formatSize(f.size) }} · {{ formatDate(f.uploaded_at) }}</p>
          </div>
        </div>
        <div class="flex gap-2 ml-2 shrink-0">
          <a :href="downloadUrl(f.id)" target="_blank"
            class="text-xs text-blue-500 hover:text-blue-700 px-2 py-1 rounded transition-colors">
            Скачать
          </a>
          <button v-if="canDelete" @click="removeFile(f.id)"
            class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
            Удалить
          </button>
        </div>
      </div>
    </div>

    <div v-else-if="loaded" class="text-sm text-gray-400 mb-3">Файлов нет</div>

    <div v-if="unavailable" class="text-xs text-amber-500 bg-amber-50 px-3 py-2 rounded-lg mb-3">
      ⚠️ Файловое хранилище временно недоступно
    </div>

    <div v-if="canUpload && !unavailable">
      <label class="flex items-center gap-2 cursor-pointer text-sm text-blue-600 hover:text-blue-800 transition-colors">
        <input type="file" class="hidden" @change="uploadFile" :disabled="uploading" />
        <span>{{ uploading ? '⏳ Загрузка...' : '📎 Прикрепить файл' }}</span>
      </label>
      <p v-if="uploadError" class="text-xs text-red-500 mt-1">{{ uploadError }}</p>
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

const API = 'http://localhost:8000'
const auth = useAuthStore()

const files = ref([])
const loaded = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const unavailable = ref(false)

const canUpload = computed(() => !auth.isManager)
const canDelete = computed(() => !auth.isManager)

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

async function uploadFile(e) {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true
  uploadError.value = ''
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
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

async function removeFile(id) {
  if (!confirm('Удалить файл?')) return
  try {
    await axios.delete(`${API}/api/media/${id}`)
    files.value = files.value.filter(f => f.id !== id)
  } catch {
    unavailable.value = true
  }
}

function downloadUrl(id) {
  return `${API}/api/media/download/${id}`
}

function fileIcon(name) {
  const ext = name.split('.').pop().toLowerCase()
  if (['jpg','jpeg','png','gif','webp'].includes(ext)) return '🖼'
  if (['pdf'].includes(ext)) return '📄'
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
  return new Date(dt).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}

onMounted(loadFiles)
</script>
