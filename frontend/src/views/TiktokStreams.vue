<template>
  <AppLayout>
    <div class="page-wrap">
      <div class="page-title-row">
        <h1 class="page-heading">TikTok</h1>
        <div style="display:flex;gap:8px;align-items:center">
          <div class="tabs" style="margin:0">
            <button class="tab" :class="{ active: tab === 'streams' }" @click="tab = 'streams'">🎙 Эфиры</button>
            <button class="tab" :class="{ active: tab === 'videos' }" @click="tab = 'videos'">🎵 Публикации</button>
          </div>
          <button v-if="tab === 'streams' && !auth.isPult" class="btn btn-primary" @click="openForm()">+ Добавить эфир</button>
          <button v-if="tab === 'videos' && auth.isAdmin && !ttConnected" class="btn btn-ghost" @click="connectTikTok">🔗 Подключить TikTok</button>
          <button v-if="tab === 'videos' && ttConnected" class="btn btn-ghost" @click="loadVideos">🔄 Обновить</button>
        </div>
      </div>

      <!-- ===== ЭФИРЫ ===== -->
      <template v-if="tab === 'streams'">
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
            <div class="stat-label">🎙 Эфиров</div>
          </div>
        </div>

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
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <span style="font-size:20px">🎙</span>
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
        <div v-else class="empty-state"><div class="empty-icon">🎙</div><p>Эфиров пока нет</p></div>
      </template>

      <!-- ===== ПУБЛИКАЦИИ ===== -->
      <template v-if="tab === 'videos'">
        <div v-if="!ttConnected && !videosLoading" class="empty-state">
          <div class="empty-icon">🔗</div>
          <p>TikTok аккаунт не подключён</p>
          <button v-if="auth.isAdmin" class="btn btn-primary" style="margin-top:16px" @click="connectTikTok">Подключить TikTok</button>
        </div>

        <template v-else>
          <!-- Сводная статистика по ВСЕМ видео -->
          <div v-if="allVideos.length" class="stats-row" style="margin-bottom:20px">
            <div class="stat-card">
              <div class="stat-value">{{ totalVideoViews.toLocaleString('ru-RU') }}</div>
              <div class="stat-label">👁 Просмотров</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ totalVideoLikes.toLocaleString('ru-RU') }}</div>
              <div class="stat-label">❤️ Лайков</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ totalVideoShares.toLocaleString('ru-RU') }}</div>
              <div class="stat-label">↗️ Репостов</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ totalVideoComments.toLocaleString('ru-RU') }}</div>
              <div class="stat-label">💬 Комментариев</div>
            </div>
          </div>

          <div v-if="videosLoading" class="loading-state">Загрузка публикаций...</div>
          <template v-else-if="allVideos.length">
            <!-- Сетка текущей страницы -->
            <div class="videos-grid">
              <a v-for="video in pagedVideos" :key="video.id" :href="video.share_url" target="_blank" class="video-card">
                <div class="video-cover">
                  <img :src="video.cover_image_url" :alt="video.title" loading="lazy" />
                </div>
                <div class="video-info">
                  <p class="video-title">{{ video.title || 'Без названия' }}</p>
                  <p class="video-date">{{ formatTimestamp(video.create_time) }}</p>
                  <div class="video-stats">
                    <span class="vstat">👁 {{ formatNum(video.view_count) }}</span>
                    <span class="vstat">❤️ {{ formatNum(video.like_count) }}</span>
                    <span class="vstat">↗️ {{ formatNum(video.share_count) }}</span>
                    <span class="vstat">💬 {{ formatNum(video.comment_count) }}</span>
                  </div>
                </div>
              </a>
            </div>

            <!-- Пагинация -->
            <div v-if="totalPages > 1" class="pagination">
              <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">←</button>
              <button
                v-for="p in visiblePages"
                :key="p"
                class="page-btn"
                :class="{ active: p === currentPage, dots: p === '...' }"
                :disabled="p === '...'"
                @click="p !== '...' && goToPage(p)"
              >{{ p }}</button>
              <button class="page-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">→</button>
              <span class="page-info">{{ (currentPage - 1) * perPage + 1 }}–{{ Math.min(currentPage * perPage, allVideos.length) }} из {{ allVideos.length }}</span>
            </div>
          </template>
          <div v-else class="empty-state"><div class="empty-icon">🎵</div><p>Публикаций нет</p></div>
        </template>
      </template>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useTiktokStreamsStore } from '../stores/tiktokStreams'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const store = useTiktokStreamsStore()
const auth = useAuthStore()
const API = import.meta.env.VITE_API_URL

const tab = ref('streams')
const ttConnected = ref(false)
const allVideos = ref([])
const videosLoading = ref(false)

const perPage = 20
const currentPage = ref(1)

// Эфиры
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)
const form = ref({ stream_date: '', views: 0, subscriptions: 0, inquiries: 0 })

const totalViews = computed(() => store.streams.reduce((s, r) => s + r.views, 0))
const totalSubscriptions = computed(() => store.streams.reduce((s, r) => s + r.subscriptions, 0))
const totalInquiries = computed(() => store.streams.reduce((s, r) => s + r.inquiries, 0))

// Статистика по ВСЕМ видео
const totalVideoViews = computed(() => allVideos.value.reduce((s, v) => s + (v.view_count || 0), 0))
const totalVideoLikes = computed(() => allVideos.value.reduce((s, v) => s + (v.like_count || 0), 0))
const totalVideoShares = computed(() => allVideos.value.reduce((s, v) => s + (v.share_count || 0), 0))
const totalVideoComments = computed(() => allVideos.value.reduce((s, v) => s + (v.comment_count || 0), 0))

// Пагинация
const totalPages = computed(() => Math.ceil(allVideos.value.length / perPage))
const pagedVideos = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return allVideos.value.slice(start, start + perPage)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cur > 3) pages.push('...')
    for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) pages.push(i)
    if (cur < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

function goToPage(p) {
  currentPage.value = p
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function checkStatus() {
  try {
    const res = await axios.get(`${API}/api/tiktok/status`)
    ttConnected.value = res.data.connected
    if (ttConnected.value) loadVideos()
  } catch {}
}

async function loadVideos() {
  videosLoading.value = true
  currentPage.value = 1
  try {
    const res = await axios.get(`${API}/api/tiktok/videos`)
    ttConnected.value = res.data.connected
    allVideos.value = res.data.videos || []
  } catch {}
  finally { videosLoading.value = false }
}

async function connectTikTok() {
  try {
    const res = await axios.get(`${API}/api/tiktok/auth`)
    window.location.href = res.data.auth_url
  } catch {}
}

function openForm(stream = null) {
  editingId.value = stream?.id || null
  form.value = { stream_date: stream?.stream_date ? stream.stream_date.slice(0, 16) : '', views: stream?.views ?? 0, subscriptions: stream?.subscriptions ?? 0, inquiries: stream?.inquiries ?? 0 }
  formError.value = ''
  showForm.value = true
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

function formatDate(dt) { return new Date(dt).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }
function formatTimestamp(ts) { return new Date(ts * 1000).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' }) }
function formatNum(n) { if (!n) return 0; return n >= 1000 ? (n / 1000).toFixed(1) + 'K' : n }

onMounted(async () => {
  await store.fetch()
  await checkStatus()
  if (window.location.search.includes('connected=1')) {
    tab.value = 'videos'
    history.replaceState({}, '', window.location.pathname)
  }
})
</script>

<style scoped>
.stats-row { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:24px; }
@media (max-width:600px) { .stats-row { grid-template-columns:repeat(2,1fr); } }
.stat-card { background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius); padding:16px; text-align:center; }
.stat-value { font-size:24px; font-weight:700; color:var(--accent); margin-bottom:4px; }
.stat-label { font-size:12px; color:var(--text-muted); }

.stream-card { transition:border-color 0.2s; }
.stream-card:hover { border-color:rgba(110,231,183,0.2); }
.stream-top { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px; }
.stream-metrics { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; border-top:1px solid var(--border); padding-top:14px; }
.metric { text-align:center; background:var(--bg-elevated); border-radius:var(--radius-sm); padding:12px 8px; }
.metric-value { font-size:20px; font-weight:700; color:var(--text-primary); margin-bottom:3px; }
.metric-label { font-size:11px; color:var(--text-muted); }
.card-actions { display:flex; gap:6px; }

.videos-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); gap:14px; margin-bottom:24px; }
.video-card { background:var(--bg-surface); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; text-decoration:none; transition:all 0.18s ease; display:block; }
.video-card:hover { border-color:rgba(110,231,183,0.25); transform:translateY(-2px); box-shadow:var(--shadow); }
.video-cover { width:100%; aspect-ratio:3/4; overflow:hidden; background:var(--bg-elevated); }
.video-cover img { width:100%; height:100%; object-fit:cover; }
.video-info { padding:10px 12px; }
.video-title { font-size:12px; color:var(--text-primary); line-height:1.4; margin-bottom:4px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.video-date { font-size:11px; color:var(--text-muted); margin-bottom:8px; }
.video-stats { display:flex; flex-wrap:wrap; gap:6px; }
.vstat { font-size:11px; color:var(--text-secondary); background:var(--bg-elevated); border-radius:999px; padding:2px 7px; }

.pagination { display:flex; align-items:center; gap:6px; justify-content:center; flex-wrap:wrap; margin-top:8px; }
.page-btn { min-width:36px; height:36px; padding:0 10px; border-radius:var(--radius-sm); border:1px solid var(--border); background:var(--bg-surface); color:var(--text-secondary); font-size:13px; font-weight:500; cursor:pointer; transition:all 0.15s; font-family:inherit; }
.page-btn:hover:not(:disabled):not(.dots) { border-color:var(--accent); color:var(--accent); }
.page-btn.active { background:var(--accent-dim); border-color:var(--accent); color:var(--accent); font-weight:700; }
.page-btn:disabled:not(.dots) { opacity:0.4; cursor:not-allowed; }
.page-btn.dots { border:none; background:none; cursor:default; }
.page-info { font-size:12px; color:var(--text-muted); margin-left:8px; }
</style>
