<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <div class="login-logo-icon">
          <svg width="32" height="32" viewBox="0 0 28 28" fill="none">
            <rect x="2" y="2" width="10" height="10" rx="2" fill="#6EE7B7" opacity="0.9"/>
            <rect x="16" y="2" width="10" height="10" rx="2" fill="#6EE7B7" opacity="0.5"/>
            <rect x="2" y="16" width="10" height="10" rx="2" fill="#6EE7B7" opacity="0.5"/>
            <rect x="16" y="16" width="10" height="10" rx="2" fill="#6EE7B7" opacity="0.9"/>
            <circle cx="14" cy="14" r="3" fill="#6EE7B7"/>
          </svg>
        </div>
        <div>
          <div class="login-title">Kasper Management</div>
          <div class="login-subtitle">Система управления офисом</div>
        </div>
      </div>

      <h2 class="login-heading">Вход в систему</h2>

      <div class="login-form">
        <div class="form-group">
          <label class="form-label">Email</label>
          <input v-model="email" type="text" class="form-input" placeholder="your@email.com" @keyup.enter="handleLogin" />
        </div>
        <div class="form-group">
          <label class="form-label">Пароль</label>
          <input v-model="password" type="password" class="form-input" placeholder="••••••••" @keyup.enter="handleLogin" />
        </div>
        <div v-if="error" class="login-error">{{ error }}</div>
        <button class="btn btn-primary login-btn" :disabled="loading" @click="handleLogin">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''; loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка входа'
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: var(--bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 36px 32px;
}

.login-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.login-logo-icon {
  width: 48px; height: 48px;
  background: var(--accent-dim);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.login-title { font-size: 16px; font-weight: 700; color: var(--text-primary); }
.login-subtitle { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.login-heading { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 20px; }

.login-form { display: flex; flex-direction: column; gap: 14px; }

.login-error {
  background: var(--danger-dim);
  border: 1px solid rgba(248,113,113,0.2);
  color: var(--danger);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 13px;
}

.login-btn { width: 100%; justify-content: center; padding: 11px; font-size: 14px; }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none !important; }
</style>