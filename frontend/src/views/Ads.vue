<template>
  <AppLayout>
    <div class="page-wrap">
      <div class="page-title-row">
        <h1 class="page-heading">Реклама</h1>
        <button v-if="!auth.isPult" class="btn btn-primary" @click="openForm()">+ Добавить</button>
      </div>

      <div class="tabs">
        <button v-for="p in platforms" :key="p.value" class="tab" :class="{ active: platform === p.value }" @click="selectPlatform(p.value)">
          {{ p.icon }} {{ p.label }}
        </button>
      </div>

      <!-- Форма -->
      <div v-if="showForm" class="card-form">
        <h2>{{ editingId ? 'Редактировать' : 'Новая запись' }}</h2>
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
          <div class="form-group col-2">
            <label class="form-label">Описание</label>
            <textarea v-model="form.description" class="form-textarea" placeholder="Текст объявления, ссылка, заметки..." />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Фото / скриншоты</label>
            <div class="photo-upload-zone">
              <div class="photo-previews">
                <div v-for="(photo, idx) in form.photos" :key="idx" class="photo-thumb">
                  <img :src="photo.preview" :alt="'фото ' + (idx+1)" />
                  <button class="photo-remove" @click="removeNewPhoto(idx)" type="button">✕</button>
                </div>
                <label class="photo-add-btn">
                  <input type="file" accept="image/*" multiple @change="onPhotosSelect" style="display:none" />
                  <span>+</span>
                </label>
              </div>
              <p class="photo-hint">Можно выбрать несколько файлов сразу</p>
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
      <div v-else-if="filteredAds.length" style="display:flex;flex-direction:column;gap:10px">
        <div v-for="ad in filteredAds" :key="ad.id" class="card ad-card">
          <div class="ad-top">
            <div style="display:flex;align-items:flex-start;gap:10px;flex:1;min-width:0">
              <span style="font-size:22px;flex-shrink:0">{{ platformIcon(ad.platform) }}</span>
              <div style="flex:1;min-width:0">
                <div style="font-size:14px;font-weight:600;color:var(--text-primary)">{{ platformLabel(ad.platform) }}</div>
                <div class="ad-meta">
                  <span v-if="ad.published_at" class="meta-chip">🕐 {{ formatDate(ad.published_at) }}</span>
                  <span v-else class="meta-chip muted">Время не указано</span>
                  <span class="meta-chip">{{ ad.created_by.full_name }}</span>
                </div>
                <p v-if="ad.description" class="ad-description">{{ ad.description }}</p>
              </div>
            </div>
            <div v-if="!auth.isPult" class="card-actions">
              <button class="btn btn-ghost btn-sm" @click="openForm(ad)">Изменить</button>
              <button class="btn btn-danger btn-sm" @click="removeAd(ad.id)">Удалить</button>
            </div>
          </div>

          <!-- Медиафайлы -->
          <div class="ad-media-section">
            <MediaUpload :entity-type="'ad'" :entity-id="ad.id" />
          </div>
        </div>
      </div>
      <div v-else class="empty-state"><div class="empty-icon">📢</div><p>Записей пока нет</p></div>

      <!-- Лайтбокс -->
      <div v-if="lightbox" class="lightbox" @click="lightbox = null">
        <img :src="lightbox" alt="фото" />
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import MediaUpload from '../components/MediaUpload.vue'
import { useAdsStore } from '../stores/ads'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const store = useAdsStore()
const auth = useAuthStore()
const API = import.meta.env.VITE_API_URL

const platforms = [
  { value: 'telegram',  icon: '✈️', label: 'Telegram' },
  { value: 'facebook',  icon: '👥', label: 'Facebook' },
  { value: 'instagram', icon: '📸', label: 'Instagram' },
  { value: 'tiktok',   icon: '🎵', label: 'TikTok' },
]

const platform = ref('telegram')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)
const saving = ref(false)
const lightbox = ref(null)

const defaultForm = () => ({
  platform: 'telegram',
  published_at: '',
  description: '',
  photos: [], // { file, preview }
})

const form = ref(defaultForm())
const filteredAds = computed(() => store.ads.filter(a => a.platform === platform.value))

function selectPlatform(val) {
  platform.value = val
  store.fetch(val)
}

function platformIcon(val) { return platforms.find(p => p.value === val)?.icon || '📢' }
function platformLabel(val) { return platforms.find(p => p.value === val)?.label || val }

function openForm(ad = null) {
  editingId.value = ad?.id || null
  form.value = {
    platform: ad?.platform || platform.value,
    published_at: ad?.published_at ? ad.published_at.slice(0, 16) : '',
    description: ad?.description || '',
    photos: [],
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

function onPhotosSelect(e) {
  const files = Array.from(e.target.files)
  for (const file of files) {
    form.value.photos.push({
      file,
      preview: URL.createObjectURL(file)
    })
  }
  e.target.value = ''
}

function removeNewPhoto(idx) {
  form.value.photos.splice(idx, 1)
}

async function submitForm() {
  formError.value = ''
  saving.value = true
  try {
    const payload = {
      platform: form.value.platform,
      published_at: form.value.published_at || null,
      description: form.value.description || null,
    }

    let ad
    if (editingId.value) {
      ad = await store.update(editingId.value, payload)
    } else {
      ad = await store.create(payload)
    }

    // Загружаем фото
    for (const photo of form.value.photos) {
      const formData = new FormData()
      formData.append('file', photo.file)
      await axios.post(`${API}/api/media/upload`, formData, {
        params: { entity_type: 'ad', entity_id: ad.id },
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }

    resetForm()
    store.fetch(platform.value)
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Ошибка'
  } finally {
    saving.value = false
  }
}

async function removeAd(id) {
  if (confirm('Удалить запись?')) await store.remove(id)
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => store.fetch(platform.value))
</script>

<style scoped>
.ad-card { transition: border-color 0.2s; }
.ad-card:hover { border-color: rgba(110,231,183,0.2); }

.ad-top { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px; }

.ad-meta { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; }
.meta-chip { display:inline-flex; align-items:center; gap:4px; font-size:12px; color:var(--text-secondary); background:var(--bg-elevated); border-radius:999px; padding:2px 8px; }
.meta-chip.muted { color:var(--text-muted); }

.ad-description { font-size:13px; color:var(--text-secondary); margin-top:8px; line-height:1.5; white-space:pre-wrap; }

.card-actions { display:flex; gap:6px; flex-shrink:0; }

.ad-media-section { border-top:1px solid var(--border); padding-top:12px; margin-top:4px; }

/* Фото в форме */
.photo-upload-zone { display:flex; flex-direction:column; gap:8px; }

.photo-previews { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }

.photo-thumb {
  position:relative; width:90px; height:90px;
  border-radius:var(--radius-sm); overflow:hidden;
  border:1px solid var(--border); flex-shrink:0;
}
.photo-thumb img { width:100%; height:100%; object-fit:cover; }

.photo-remove {
  position:absolute; top:4px; right:4px;
  width:20px; height:20px;
  background:rgba(0,0,0,0.7); color:#fff;
  border:none; border-radius:50%; cursor:pointer;
  font-size:10px; display:flex; align-items:center; justify-content:center;
  transition:background 0.15s;
}
.photo-remove:hover { background:var(--danger); }

.photo-add-btn {
  width:90px; height:90px;
  border:2px dashed var(--border);
  border-radius:var(--radius-sm);
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; color:var(--text-muted); font-size:28px;
  transition:all 0.15s; flex-shrink:0;
}
.photo-add-btn:hover { border-color:var(--accent); color:var(--accent); }

.photo-hint { font-size:11px; color:var(--text-muted); margin:0; }

/* Лайтбокс */
.lightbox { position:fixed; inset:0; background:rgba(0,0,0,0.9); z-index:300; display:flex; align-items:center; justify-content:center; cursor:zoom-out; padding:20px; }
.lightbox img { max-width:100%; max-height:100%; object-fit:contain; border-radius:var(--radius-sm); }
</style>
