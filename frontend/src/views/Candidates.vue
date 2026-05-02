<template>
  <AppLayout>
    <div class="page-wrap">
      <div class="page-title-row">
        <h1 class="page-heading">Анкеты</h1>
        <div style="display:flex;gap:8px;align-items:center">
          <div class="tabs" style="margin:0">
            <button class="tab" :class="{ active: tab === 'candidates' }" @click="tab = 'candidates'">Анкеты</button>
            <button v-if="auth.isPult || auth.isAdmin" class="tab" :class="{ active: tab === 'templates' }" @click="tab = 'templates'">Шаблоны</button>
          </div>
          <button v-if="!auth.isPult && tab === 'candidates'" class="btn btn-primary" @click="openCandidateForm()">+ Добавить</button>
          <button v-if="tab === 'templates'" class="btn btn-primary" @click="openTemplateForm()">+ Шаблон</button>
        </div>
      </div>

      <!-- Фильтры анкет -->
      <div v-if="tab === 'candidates'" style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">
        <input v-model="search" @input="onSearch" class="form-input" style="flex:1;min-width:180px" placeholder="Поиск по имени..." />
        <select v-model="filterTemplate" @change="store.fetchCandidates(search, filterTemplate || null)" class="form-select" style="width:180px">
          <option value="">Все шаблоны</option>
          <option v-for="t in store.templates" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>

      <!-- Форма анкеты -->
      <div v-if="showCandidateForm" class="card-form">
        <h2>{{ editingCandidate ? 'Редактировать анкету' : 'Новая анкета' }}</h2>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">ФИО *</label>
            <input v-model="candidateForm.full_name" class="form-input" />
          </div>
          <div v-if="!editingCandidate" class="form-group">
            <label class="form-label">Шаблон *</label>
            <select v-model="candidateForm.template_id" @change="onTemplateSelect" class="form-select">
              <option value="">Выберите шаблон</option>
              <option v-for="t in store.templates" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
        </div>
        <div v-if="selectedTemplate" class="form-grid" style="margin-top:14px">
          <div v-for="field in selectedTemplate.fields" :key="field.key" class="form-group" :class="field.type === 'textarea' ? 'col-2' : ''">
            <label class="form-label">{{ field.label }}<span v-if="field.required" style="color:var(--danger)"> *</span></label>
            <textarea v-if="field.type === 'textarea'" v-model="candidateForm.fields[field.key]" class="form-textarea" />
            <select v-else-if="field.type === 'select'" v-model="candidateForm.fields[field.key]" class="form-select">
              <option value="">—</option>
              <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
            </select>
            <input v-else v-model="candidateForm.fields[field.key]" :type="field.type === 'date' ? 'date' : 'text'" class="form-input" />
          </div>
        </div>
        <p v-if="candidateError" class="form-error">{{ candidateError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitCandidate">Сохранить</button>
          <button class="btn btn-ghost" @click="resetCandidateForm">Отмена</button>
        </div>
      </div>

      <!-- Форма шаблона -->
      <div v-if="showTemplateForm" class="card-form">
        <h2>Конструктор шаблона</h2>
        <div class="form-group" style="margin-bottom:14px">
          <label class="form-label">Название шаблона *</label>
          <input v-model="templateForm.name" class="form-input" placeholder="Анкета менеджера" />
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
          <span class="form-label" style="margin:0">Поля</span>
          <button class="btn btn-ghost btn-sm" @click="addField">+ Добавить поле</button>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px">
          <div v-for="(field,idx) in templateForm.fields" :key="idx" class="card" style="padding:14px">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Название поля</label>
                <input v-model="field.label" class="form-input" placeholder="ФИО, Адрес..." />
              </div>
              <div class="form-group">
                <label class="form-label">Ключ (латин.)</label>
                <input v-model="field.key" class="form-input" placeholder="full_name, address..." />
              </div>
              <div class="form-group">
                <label class="form-label">Тип</label>
                <select v-model="field.type" class="form-select">
                  <option value="text">Текст</option>
                  <option value="textarea">Текстовая область</option>
                  <option value="date">Дата</option>
                  <option value="select">Выбор</option>
                </select>
              </div>
              <div class="form-group" style="justify-content:flex-end;flex-direction:row;align-items:center;gap:12px;padding-top:20px">
                <label style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);cursor:pointer">
                  <input type="checkbox" v-model="field.required" />
                  Обязательное
                </label>
                <button class="btn btn-danger btn-sm" @click="templateForm.fields.splice(idx,1)">Удалить</button>
              </div>
              <div v-if="field.type === 'select'" class="form-group col-2">
                <label class="form-label">Варианты (через запятую)</label>
                <input v-model="field.optionsRaw" class="form-input" placeholder="Да, Нет, Не знаю" />
              </div>
            </div>
          </div>
        </div>
        <p v-if="templateError" class="form-error">{{ templateError }}</p>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="btn btn-primary" @click="submitTemplate">Сохранить шаблон</button>
          <button class="btn btn-ghost" @click="showTemplateForm = false">Отмена</button>
        </div>
      </div>

      <!-- АНКЕТЫ -->
      <template v-if="tab === 'candidates'">
        <div v-if="store.loading" class="loading-state">Загрузка...</div>
        <div v-else-if="store.candidates.length" style="display:flex;flex-direction:column;gap:10px">
          <div v-for="c in store.candidates" :key="c.id" class="card cand-card">
            <div class="cand-top">
              <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                  <span style="font-size:14px;font-weight:600;color:var(--text-primary)">{{ c.full_name }}</span>
                  <span class="badge badge-blue">{{ c.template.name }}</span>
                </div>
                <div class="cand-fields">
                  <div v-for="field in c.template.fields" :key="field.key" class="cand-field">
                    <span class="cand-field-label">{{ field.label }}:</span>
                    <span class="cand-field-value">{{ c.fields[field.key] || '—' }}</span>
                  </div>
                </div>
                <p style="font-size:11px;color:var(--text-muted);margin-top:8px">{{ formatDate(c.created_at) }}</p>
              </div>
              <div v-if="!auth.isPult" class="card-actions">
                <button class="btn btn-ghost btn-sm" @click="openCandidateForm(c)">Изменить</button>
                <button class="btn btn-danger btn-sm" @click="removeCandidate(c.id)">Удалить</button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state"><div class="empty-icon">📋</div><p>Анкет пока нет</p></div>
      </template>

      <!-- ШАБЛОНЫ -->
      <template v-if="tab === 'templates'">
        <div v-if="store.templates.length" style="display:flex;flex-direction:column;gap:10px">
          <div v-for="t in store.templates" :key="t.id" class="card" style="display:flex;align-items:center;justify-content:space-between">
            <div>
              <div style="font-size:14px;font-weight:600;color:var(--text-primary)">{{ t.name }}</div>
              <div style="font-size:12px;color:var(--text-muted);margin-top:3px">{{ t.fields.length }} полей: {{ t.fields.map(f => f.label).join(', ') }}</div>
            </div>
            <button class="btn btn-danger btn-sm" @click="removeTemplate(t.id)">Удалить</button>
          </div>
        </div>
        <div v-else class="empty-state"><div class="empty-icon">🗂</div><p>Шаблонов пока нет</p></div>
      </template>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useCandidatesStore } from '../stores/candidates'
import { useAuthStore } from '../stores/auth'

const store = useCandidatesStore()
const auth = useAuthStore()

const tab = ref('candidates')
const search = ref('')
const filterTemplate = ref('')

// Шаблоны
const showTemplateForm = ref(false)
const templateError = ref('')
const templateForm = ref({ name:'', fields:[] })

function openTemplateForm() { templateForm.value = { name:'', fields:[] }; templateError.value = ''; showTemplateForm.value = true }
function addField() { templateForm.value.fields.push({ key:'', label:'', type:'text', required:false, optionsRaw:'' }) }

async function submitTemplate() {
  templateError.value = ''
  if (!templateForm.value.name.trim()) { templateError.value = 'Название обязательно'; return }
  if (!templateForm.value.fields.length) { templateError.value = 'Добавьте хотя бы одно поле'; return }
  for (const f of templateForm.value.fields) {
    if (!f.key.trim() || !f.label.trim()) { templateError.value = 'Заполните все поля'; return }
  }
  try {
    const fields = templateForm.value.fields.map(f => ({ key:f.key.trim(), label:f.label.trim(), type:f.type, required:f.required, options: f.optionsRaw ? f.optionsRaw.split(',').map(o=>o.trim()).filter(Boolean) : [] }))
    await store.createTemplate({ name: templateForm.value.name, fields })
    showTemplateForm.value = false
  } catch (e) { templateError.value = e.response?.data?.detail || 'Ошибка' }
}

async function removeTemplate(id) { if (confirm('Удалить шаблон?')) await store.deleteTemplate(id) }

// Анкеты
const showCandidateForm = ref(false)
const candidateError = ref('')
const editingCandidate = ref(null)
const candidateForm = ref({ full_name:'', template_id:'', fields:{} })

const selectedTemplate = computed(() => {
  const id = editingCandidate.value ? editingCandidate.value.template.id : candidateForm.value.template_id
  return store.templates.find(t => t.id === Number(id)) || null
})

function onTemplateSelect() { candidateForm.value.fields = {} }

function openCandidateForm(candidate = null) {
  editingCandidate.value = candidate
  if (candidate) {
    candidateForm.value = { full_name: candidate.full_name, template_id: candidate.template.id, fields: { ...candidate.fields } }
  } else {
    candidateForm.value = { full_name:'', template_id:'', fields:{} }
  }
  candidateError.value = ''; showCandidateForm.value = true
}

function resetCandidateForm() { showCandidateForm.value = false; editingCandidate.value = null; candidateError.value = '' }

async function submitCandidate() {
  candidateError.value = ''
  if (!candidateForm.value.full_name.trim()) { candidateError.value = 'ФИО обязательно'; return }
  if (!editingCandidate.value && !candidateForm.value.template_id) { candidateError.value = 'Выберите шаблон'; return }
  try {
    if (editingCandidate.value) await store.updateCandidate(editingCandidate.value.id, { full_name: candidateForm.value.full_name, fields: candidateForm.value.fields })
    else await store.createCandidate({ full_name: candidateForm.value.full_name, template_id: Number(candidateForm.value.template_id), fields: candidateForm.value.fields })
    resetCandidateForm()
  } catch (e) { candidateError.value = e.response?.data?.detail || 'Ошибка' }
}

async function removeCandidate(id) { if (confirm('Удалить анкету?')) await store.removeCandidate(id) }

let searchTimer = null
function onSearch() { clearTimeout(searchTimer); searchTimer = setTimeout(() => store.fetchCandidates(search.value, filterTemplate.value || null), 400) }

function formatDate(dt) { return new Date(dt).toLocaleString('ru-RU', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) }

onMounted(async () => { await store.fetchTemplates(); await store.fetchCandidates() })
</script>

<style scoped>
.cand-card { transition: border-color 0.2s; }
.cand-card:hover { border-color: rgba(110,231,183,0.2); }
.cand-top { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }
.cand-fields { display:grid; grid-template-columns:repeat(2,1fr); gap:4px 16px; }
@media (max-width:500px) { .cand-fields { grid-template-columns:1fr; } }
.cand-field { font-size:13px; }
.cand-field-label { color:var(--text-muted); }
.cand-field-value { color:var(--text-secondary); margin-left:4px; }
.card-actions { display:flex; gap:6px; flex-shrink:0; }
</style>