<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
      <router-link to="/" class="text-gray-400 hover:text-gray-600">← Назад</router-link>
      <h1 class="text-xl font-bold text-gray-900">Анкеты / Личные дела</h1>
    </nav>

    <main class="max-w-5xl mx-auto px-6 py-8">

      <!-- Вкладки -->
      <div class="flex gap-2 mb-6">
        <button @click="tab = 'candidates'"
          :class="tab === 'candidates' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          📋 Анкеты
        </button>
        <button v-if="auth.isManager || auth.isAdmin" @click="tab = 'templates'"
          :class="tab === 'templates' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200'"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          🗂 Шаблоны
        </button>
      </div>

      <!-- АНКЕТЫ -->
      <template v-if="tab === 'candidates'">
        <div class="flex gap-3 mb-6">
          <input v-model="search" @input="onSearch" type="text" placeholder="Поиск по имени..."
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
          <select v-model="filterTemplate" @change="store.fetchCandidates(search, filterTemplate || null)"
            class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Все шаблоны</option>
            <option v-for="t in store.templates" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
          <button v-if="!auth.isManager" @click="openCandidateForm()"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap">
            + Добавить
          </button>
        </div>

        <!-- Форма анкеты -->
        <div v-if="showCandidateForm" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
          <h2 class="font-semibold text-gray-800 mb-4">{{ editingCandidate ? 'Редактировать анкету' : 'Новая анкета' }}</h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">ФИО *</label>
              <input v-model="candidateForm.full_name" type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div v-if="!editingCandidate">
              <label class="block text-sm font-medium text-gray-700 mb-1">Шаблон *</label>
              <select v-model="candidateForm.template_id" @change="onTemplateSelect"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">Выберите шаблон</option>
                <option v-for="t in store.templates" :key="t.id" :value="t.id">{{ t.name }}</option>
              </select>
            </div>
          </div>

          <!-- Динамические поля шаблона -->
          <div v-if="selectedTemplate" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="field in selectedTemplate.fields" :key="field.key"
              :class="field.type === 'textarea' ? 'md:col-span-2' : ''">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                {{ field.label }}<span v-if="field.required" class="text-red-400 ml-1">*</span>
              </label>
              <textarea v-if="field.type === 'textarea'" v-model="candidateForm.fields[field.key]" rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <select v-else-if="field.type === 'select'" v-model="candidateForm.fields[field.key]"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">—</option>
                <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <input v-else v-model="candidateForm.fields[field.key]"
                :type="field.type === 'date' ? 'date' : 'text'"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
          </div>

          <div v-if="candidateError" class="text-red-500 text-sm mt-3">{{ candidateError }}</div>
          <div class="flex gap-3 mt-4">
            <button @click="submitCandidate"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Сохранить
            </button>
            <button @click="resetCandidateForm"
              class="text-gray-500 hover:text-gray-700 px-4 py-2 rounded-lg text-sm transition-colors">
              Отмена
            </button>
          </div>
        </div>

        <div v-if="store.loading" class="text-center py-12 text-gray-400">Загрузка...</div>

        <div v-else-if="store.candidates.length" class="space-y-3">
          <div v-for="c in store.candidates" :key="c.id"
            class="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-sm transition-shadow">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="font-semibold text-gray-900">{{ c.full_name }}</h3>
                  <span class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{{ c.template.name }}</span>
                </div>
                <div class="grid grid-cols-2 gap-x-6 gap-y-1">
                  <div v-for="field in c.template.fields" :key="field.key" class="text-sm">
                    <span class="text-gray-400">{{ field.label }}:</span>
                    <span class="text-gray-700 ml-1">{{ c.fields[field.key] || '—' }}</span>
                  </div>
                </div>
                <p class="text-xs text-gray-300 mt-2">{{ formatDate(c.created_at) }}</p>
              </div>
              <div v-if="!auth.isManager" class="flex gap-2 ml-4">
                <button @click="openCandidateForm(c)"
                  class="text-xs text-blue-500 hover:text-blue-700 px-2 py-1 rounded transition-colors">
                  Ред.
                </button>
                <button @click="removeCandidate(c.id)"
                  class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-16 text-gray-400">
          <p class="text-4xl mb-3">📋</p>
          <p>Анкет пока нет</p>
        </div>
      </template>

      <!-- ШАБЛОНЫ -->
      <template v-if="tab === 'templates'">
        <div class="flex justify-end mb-6">
          <button @click="openTemplateForm()"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            + Новый шаблон
          </button>
        </div>

        <!-- Форма шаблона -->
        <div v-if="showTemplateForm" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
          <h2 class="font-semibold text-gray-800 mb-4">Конструктор шаблона</h2>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Название шаблона *</label>
            <input v-model="templateForm.name" type="text" placeholder="Например: Анкета менеджера"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>

          <div class="mb-4">
            <div class="flex items-center justify-between mb-3">
              <p class="text-sm font-medium text-gray-700">Поля</p>
              <button @click="addField"
                class="text-xs text-blue-600 hover:text-blue-800 font-medium transition-colors">
                + Добавить поле
              </button>
            </div>

            <div class="space-y-3">
              <div v-for="(field, idx) in templateForm.fields" :key="idx"
                class="border border-gray-200 rounded-lg p-3 bg-gray-50">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-2">
                  <input v-model="field.label" type="text" placeholder="Название поля"
                    class="px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
                  <input v-model="field.key" type="text" placeholder="Ключ (латин.)"
                    class="px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
                  <select v-model="field.type"
                    class="px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500">
                    <option value="text">Текст</option>
                    <option value="textarea">Текстовая область</option>
                    <option value="date">Дата</option>
                    <option value="select">Выбор</option>
                  </select>
                  <div class="flex items-center gap-2">
                    <label class="flex items-center gap-1 text-xs text-gray-600">
                      <input type="checkbox" v-model="field.required" class="rounded" />
                      Обяз.
                    </label>
                    <button @click="templateForm.fields.splice(idx, 1)"
                      class="text-red-400 hover:text-red-600 text-xs ml-auto transition-colors">
                      Удалить
                    </button>
                  </div>
                </div>
                <div v-if="field.type === 'select'">
                  <input v-model="field.optionsRaw" type="text" placeholder="Варианты через запятую: Да, Нет, Не знаю"
                    class="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500" />
                </div>
              </div>
            </div>
          </div>

          <div v-if="templateError" class="text-red-500 text-sm mt-2">{{ templateError }}</div>
          <div class="flex gap-3 mt-4">
            <button @click="submitTemplate"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Сохранить шаблон
            </button>
            <button @click="showTemplateForm = false"
              class="text-gray-500 hover:text-gray-700 px-4 py-2 rounded-lg text-sm transition-colors">
              Отмена
            </button>
          </div>
        </div>

        <!-- Список шаблонов -->
        <div v-if="store.templates.length" class="space-y-3">
          <div v-for="t in store.templates" :key="t.id"
            class="bg-white border border-gray-200 rounded-xl p-5">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="font-semibold text-gray-900">{{ t.name }}</h3>
                <p class="text-sm text-gray-400 mt-1">{{ t.fields.length }} полей: {{ t.fields.map(f => f.label).join(', ') }}</p>
              </div>
              <button @click="removeTemplate(t.id)"
                class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded transition-colors">
                Удалить
              </button>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-16 text-gray-400">
          <p class="text-4xl mb-3">🗂</p>
          <p>Шаблонов пока нет</p>
        </div>
      </template>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const templateForm = ref({ name: '', fields: [] })

function openTemplateForm() {
  templateForm.value = { name: '', fields: [] }
  templateError.value = ''
  showTemplateForm.value = true
}

function addField() {
  templateForm.value.fields.push({
    key: '', label: '', type: 'text', required: false, optionsRaw: ''
  })
}

async function submitTemplate() {
  templateError.value = ''
  if (!templateForm.value.name.trim()) {
    templateError.value = 'Название обязательно'
    return
  }
  if (!templateForm.value.fields.length) {
    templateError.value = 'Добавьте хотя бы одно поле'
    return
  }
  for (const f of templateForm.value.fields) {
    if (!f.key.trim() || !f.label.trim()) {
      templateError.value = 'Заполните название и ключ для всех полей'
      return
    }
  }
  try {
    const fields = templateForm.value.fields.map(f => ({
      key: f.key.trim(),
      label: f.label.trim(),
      type: f.type,
      required: f.required,
      options: f.optionsRaw ? f.optionsRaw.split(',').map(o => o.trim()).filter(Boolean) : []
    }))
    await store.createTemplate({ name: templateForm.value.name, fields })
    showTemplateForm.value = false
  } catch (e) {
    templateError.value = e.response?.data?.detail || 'Ошибка сохранения'
  }
}

async function removeTemplate(id) {
  if (confirm('Удалить шаблон?')) await store.deleteTemplate(id)
}

// Анкеты
const showCandidateForm = ref(false)
const candidateError = ref('')
const editingCandidate = ref(null)
const candidateForm = ref({ full_name: '', template_id: '', fields: {} })

const selectedTemplate = computed(() => {
  const id = editingCandidate.value
    ? editingCandidate.value.template.id
    : candidateForm.value.template_id
  return store.templates.find(t => t.id === Number(id)) || null
})

function onTemplateSelect() {
  candidateForm.value.fields = {}
}

function openCandidateForm(candidate = null) {
  editingCandidate.value = candidate
  if (candidate) {
    candidateForm.value = {
      full_name: candidate.full_name,
      template_id: candidate.template.id,
      fields: { ...candidate.fields }
    }
  } else {
    candidateForm.value = { full_name: '', template_id: '', fields: {} }
  }
  candidateError.value = ''
  showCandidateForm.value = true
}

function resetCandidateForm() {
  showCandidateForm.value = false
  editingCandidate.value = null
  candidateError.value = ''
}

async function submitCandidate() {
  candidateError.value = ''
  if (!candidateForm.value.full_name.trim()) {
    candidateError.value = 'ФИО обязательно'
    return
  }
  if (!editingCandidate.value && !candidateForm.value.template_id) {
    candidateError.value = 'Выберите шаблон'
    return
  }
  try {
    if (editingCandidate.value) {
      await store.updateCandidate(editingCandidate.value.id, {
        full_name: candidateForm.value.full_name,
        fields: candidateForm.value.fields
      })
    } else {
      await store.createCandidate({
        full_name: candidateForm.value.full_name,
        template_id: Number(candidateForm.value.template_id),
        fields: candidateForm.value.fields
      })
    }
    resetCandidateForm()
  } catch (e) {
    candidateError.value = e.response?.data?.detail || 'Ошибка сохранения'
  }
}

async function removeCandidate(id) {
  if (confirm('Удалить анкету?')) await store.removeCandidate(id)
}

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => store.fetchCandidates(search.value, filterTemplate.value || null), 400)
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

onMounted(async () => {
  await store.fetchTemplates()
  await store.fetchCandidates()
})
</script>
