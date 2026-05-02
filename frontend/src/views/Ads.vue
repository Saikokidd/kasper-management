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
        </div>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitForm">Сохранить</button>
          <button class="btn btn-ghost" @click="resetForm">Отмена</button>
        </div>
      </div>

      <div v-if="store.loading" class="loading-state">Загрузка...</div>
      <div v-else-if="filteredAds.length" style="display:flex;flex-direction:column;gap:10px">
        <div v-for="ad in filteredAds" :key="ad.id" class="card ad-card">
          <div class="ad-top">
            <div style="display:flex;align-items:center;gap:10px">
              <span style="font-size:22px">{{ platformIcon(ad.platform) }}</span>
              <div>
                <div style="font-size:14px;font-weight:600;color:var(--text-primary)">{{ platformLabel(ad.platform) }}</div>
                <div class="interview-meta" style="margin-top:4px">
                  <span v-if="ad.published_at" class="meta-chip">🕐 {{ formatDate(ad.published_at) }}</span>
                  <span v-else class="meta-chip muted">Время не указано</span>
                  <span class="meta-chip">{{ ad.created_by.full_name }}</span>
                </div>
              </div>
            </div>
            <div v-if="!auth.isPult" class="card-actions">
              <button class="btn btn-ghost btn-sm" @click="openForm(ad)">Изменить</button>
              <button class="btn btn-danger btn-sm" @click="removeAd(ad.id)">Удалить</button>
            </div>
          </div>
          <div style="border-top:1px solid var(--border);padding-top:12px;margin-top:12px">
            <p style="font-size:11px;font-weight:600;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.05em">Скрины</p>
            <MediaUpload entity-type="ad" :entity-id="ad.id" />
          </div>
        </div>
      </div>
      <div v-else class="empty-state"><div class="empty-icon">📢</div><p>Записей пока нет</p></div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import MediaUpload from '../components/MediaUpload.vue'
import { useAdsStore } from '../stores/ads'
import { useAuthStore } from '../stores/auth'

const store = useAdsStore()
const auth = useAuthStore()

const platforms = [
  { value:'telegram', icon:'✈️', label:'Telegram' },
  { value:'facebook', icon:'👥', label:'Facebook' },
  { value:'instagram', icon:'📸', label:'Instagram' },
  { value:'tiktok', icon:'🎵', label:'TikTok' },
]

const platform = ref('telegram')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)
const form = ref({ platform:'telegram', published_at:'' })

const filteredAds = computed(() => store.ads.filter(a => a.platform === platform.value))

function selectPlatform(val) { platform.value = val; store.fetch(val) }
function platformIcon(val) { return platforms.find(p => p.value === val)?.icon || '📢' }
function platformLabel(val) { return platforms.find(p => p.value === val)?.label || val }

function openForm(ad = null) {
  editingId.value = ad?.id || null
  form.value = { platform: ad?.platform || platform.value, published_at: ad?.published_at ? ad.published_at.slice(0,16) : '' }
  formError.value = ''; showForm.value = true
}
function resetForm() { showForm.value = false; editingId.value = null; formError.value = '' }

async function submitForm() {
  formError.value = ''
  try {
    const payload = { ...form.value, published_at: form.value.published_at || null }
    if (editingId.value) await store.update(editingId.value, { published_at: payload.published_at })
    else await store.create(payload)
    resetForm(); store.fetch(platform.value)
  } catch (e) { formError.value = e.response?.data?.detail || 'Ошибка' }
}

async function removeAd(id) { if (confirm('Удалить запись?')) await store.remove(id) }

function formatDate(dt) { return new Date(dt).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) }

onMounted(() => store.fetch(platform.value))
</script>

<style scoped>
.ad-card { transition: border-color 0.2s; }
.ad-card:hover { border-color: rgba(110,231,183,0.2); }
.ad-top { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }
.interview-meta { display:flex; flex-wrap:wrap; gap:6px; }
.meta-chip { display:inline-flex; align-items:center; gap:4px; font-size:12px; color:var(--text-secondary); background:var(--bg-elevated); border-radius:999px; padding:2px 8px; }
.meta-chip.muted { color:var(--text-muted); }
.card-actions { display:flex; gap:6px; flex-shrink:0; }
</style>