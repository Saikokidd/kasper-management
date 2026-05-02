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
          <div class="form-group">
            <label class="form-label">Статус</label>
            <select v-model="form.status" class="form-select">
              <option value="active">✅ Размещено</option>
              <option value="blocked">🚫 Заблокировано</option>
            </select>
          </div>
          <div v-if="form.status === 'blocked'" class="form-group col-2">
            <label class="form-label">Причина блокировки</label>
            <input v-model="form.block_reason" class="form-input" />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Текст объявления</label>
            <textarea v-model="form.content" class="form-textarea" placeholder="Текст, ссылка, описание..." />
          </div>
          <div class="form-group col-2">
            <label class="form-label">Комментарий</label>
            <textarea v-model="form.comment" class="form-textarea" rows="2" />
          </div>
        </div>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitForm">Сохранить</button>
          <button class="btn btn-ghost" @click="resetForm">Отмена</button>
        </div>
      </div>

      <div v-if="store.loading" class="loading-state">Загрузка...</div>
      <div v-else-if="filteredPosts.length" style="display:flex;flex-direction:column;gap:10px">
        <div v-for="post in filteredPosts" :key="post.id" class="card post-card" :class="{ 'post-blocked': post.status === 'blocked' }">
          <div class="post-top">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap">
                <span style="font-size:18px">{{ platformIcon(post.platform) }}</span>
                <span style="font-size:14px;font-weight:600;color:var(--text-primary)">{{ platformLabel(post.platform) }}</span>
                <span class="badge" :class="post.status === 'active' ? 'badge-green' : 'badge-red'">
                  {{ post.status === 'active' ? '✅ Размещено' : '🚫 Заблокировано' }}
                </span>
                <span class="badge badge-blue">📨 {{ post.responses }} откликов</span>
              </div>
              <div class="interview-meta">
                <span v-if="post.published_at" class="meta-chip">🕐 {{ formatDate(post.published_at) }}</span>
                <span class="meta-chip">{{ post.created_by.full_name }}</span>
              </div>
              <p v-if="post.content" style="font-size:13px;color:var(--text-secondary);margin-top:8px;line-height:1.5">{{ post.content }}</p>
              <p v-if="post.comment" style="font-size:12px;color:var(--text-muted);margin-top:4px;font-style:italic">💬 {{ post.comment }}</p>
              <p v-if="post.block_reason" style="font-size:12px;color:var(--danger);margin-top:4px">⛔ {{ post.block_reason }}</p>
            </div>
            <div v-if="!auth.isPult" class="card-actions">
              <button class="btn btn-ghost btn-sm" @click="openForm(post)">Изменить</button>
              <button class="btn btn-danger btn-sm" @click="removePost(post.id)">Удалить</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state"><div class="empty-icon">📋</div><p>Объявлений пока нет</p></div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useJobPostsStore } from '../stores/jobPosts'
import { useAuthStore } from '../stores/auth'

const store = useJobPostsStore()
const auth = useAuthStore()

const platforms = [
  { value:'olx', icon:'🟠', label:'OLX' },
  { value:'workua', icon:'🔵', label:'Work.UA' },
]

const platform = ref('olx')
const showForm = ref(false)
const formError = ref('')
const editingId = ref(null)
const form = ref({ platform:'olx', content:'', published_at:'', responses:0, comment:'', status:'active', block_reason:'' })

const filteredPosts = computed(() => store.posts.filter(p => p.platform === platform.value))

function selectPlatform(val) { platform.value = val; store.fetch(val) }
function platformIcon(val) { return platforms.find(p => p.value === val)?.icon || '📋' }
function platformLabel(val) { return platforms.find(p => p.value === val)?.label || val }

function openForm(post = null) {
  editingId.value = post?.id || null
  form.value = { platform: post?.platform || platform.value, content: post?.content || '', published_at: post?.published_at ? post.published_at.slice(0,16) : '', responses: post?.responses ?? 0, comment: post?.comment || '', status: post?.status || 'active', block_reason: post?.block_reason || '' }
  formError.value = ''; showForm.value = true
}
function resetForm() { showForm.value = false; editingId.value = null; formError.value = '' }

async function submitForm() {
  formError.value = ''
  try {
    const payload = { ...form.value, published_at: form.value.published_at || null, block_reason: form.value.status === 'blocked' ? form.value.block_reason || null : null }
    if (editingId.value) await store.update(editingId.value, payload)
    else await store.create(payload)
    resetForm(); store.fetch(platform.value)
  } catch (e) { formError.value = e.response?.data?.detail || 'Ошибка' }
}

async function removePost(id) { if (confirm('Удалить?')) await store.remove(id) }

function formatDate(dt) { return new Date(dt).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) }

onMounted(() => store.fetch(platform.value))
</script>

<style scoped>
.post-card { transition: border-color 0.2s; }
.post-card:hover { border-color: rgba(110,231,183,0.2); }
.post-blocked { border-color: rgba(248,113,113,0.2) !important; }
.post-top { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }
.interview-meta { display:flex; flex-wrap:wrap; gap:6px; }
.meta-chip { display:inline-flex; align-items:center; gap:4px; font-size:12px; color:var(--text-secondary); background:var(--bg-elevated); border-radius:999px; padding:2px 8px; }
.card-actions { display:flex; gap:6px; flex-shrink:0; }
</style>