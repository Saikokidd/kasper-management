<template>
  <div class="app-shell" :class="{ 'sidebar-open': sidebarOpen }">

    <!-- Overlay мобилка -->
    <div class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <!-- САЙДБАР -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect x="2" y="2" width="10" height="10" rx="2" fill="var(--accent)" opacity="0.9"/>
            <rect x="16" y="2" width="10" height="10" rx="2" fill="var(--accent)" opacity="0.5"/>
            <rect x="2" y="16" width="10" height="10" rx="2" fill="var(--accent)" opacity="0.5"/>
            <rect x="16" y="16" width="10" height="10" rx="2" fill="var(--accent)" opacity="0.9"/>
            <circle cx="14" cy="14" r="3" fill="var(--accent)"/>
          </svg>
        </div>
        <div class="logo-text">
          <span class="logo-title">Kasper</span>
          <span class="logo-sub">Management</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label">Рабочее пространство</div>
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          active-class="nav-item--active"
          @click="sidebarOpen = false"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- Нижняя часть сайдбара -->
      <div class="sidebar-bottom">

        <!-- Переключатель темы -->
        <div class="theme-switcher">
          <span class="theme-label">
            <span>{{ theme === 'dark' ? '🌙' : '☀️' }}</span>
            {{ theme === 'dark' ? 'Тёмная тема' : 'Светлая тема' }}
          </span>
          <button class="theme-toggle" @click="toggleTheme" :class="{ 'theme-toggle--on': theme === 'light' }">
            <span class="theme-toggle-thumb"></span>
          </button>
        </div>

        <!-- Пользователь -->
        <div class="sidebar-user">
          <div class="user-avatar">{{ userInitials }}</div>
          <div class="user-info">
            <span class="user-name">{{ auth.user?.full_name }}</span>
            <span class="user-role">{{ roleLabel }}</span>
          </div>
          <button class="user-logout" @click="handleLogout" title="Выйти">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- ОСНОВНОЙ КОНТЕНТ -->
    <div class="main-wrapper">
      <!-- Топбар мобилка -->
      <header class="topbar">
        <button class="burger" @click="sidebarOpen = !sidebarOpen">
          <span></span><span></span><span></span>
        </button>
        <div class="topbar-logo">
          <svg width="20" height="20" viewBox="0 0 28 28" fill="none">
            <rect x="2" y="2" width="10" height="10" rx="2" fill="var(--accent)" opacity="0.9"/>
            <rect x="16" y="2" width="10" height="10" rx="2" fill="var(--accent)" opacity="0.5"/>
            <rect x="2" y="16" width="10" height="10" rx="2" fill="var(--accent)" opacity="0.5"/>
            <rect x="16" y="16" width="10" height="10" rx="2" fill="var(--accent)" opacity="0.9"/>
            <circle cx="14" cy="14" r="3" fill="var(--accent)"/>
          </svg>
          <span>Kasper</span>
        </div>
        <!-- Переключатель темы в топбаре (мобилка) -->
        <button class="topbar-theme-btn" @click="toggleTheme" :title="theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'">
          {{ theme === 'dark' ? '☀️' : '🌙' }}
        </button>
      </header>

      <main class="main-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useTheme } from '../composables/useTheme'

const router = useRouter()
const auth = useAuthStore()
const sidebarOpen = ref(false)
const { theme, toggleTheme } = useTheme()

const roleLabel = computed(() => ({
  admin: 'Администратор',
  pult: 'Руководство',
  hr: 'HR-специалист'
}[auth.user?.role] || ''))

const userInitials = computed(() => {
  const name = auth.user?.full_name || ''
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}

const navItems = [
  {
    to: '/',
    label: 'Главная',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`
  },
  {
    to: '/interviews',
    label: 'Собеседования',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`
  },
  {
    to: '/inscriptions',
    label: 'Прописи',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>`
  },
  {
    to: '/candidates',
    label: 'Анкеты',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`
  },
  {
    to: '/tasks',
    label: 'Задачи',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>`
  },
  {
    to: '/ads',
    label: 'Реклама',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>`
  },
  {
    to: '/job-posts',
    label: 'Объявления',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`
  },
  {
    to: '/tiktok',
    label: 'TikTok эфиры',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>`
  },
]
</script>

<style>
/* ─── GLOBAL SHELL STYLES (не scoped — нужны везде) ─── */
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg-base);
}

.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  z-index: 100;
  transition: transform 0.28s cubic-bezier(0.4,0,0.2,1), background 0.2s, border-color 0.2s;
}

.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  z-index: 90;
  backdrop-filter: blur(2px);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 16px;
  border-bottom: 1px solid var(--border);
}

.logo-icon {
  flex-shrink: 0;
  width: 36px; height: 36px;
  background: var(--accent-dim);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}

.logo-text { display: flex; flex-direction: column; line-height: 1.1; }
.logo-title { font-size: 15px; font-weight: 700; color: var(--text-primary); }
.logo-sub { font-size: 10px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); }

.sidebar-nav {
  flex: 1;
  padding: 16px 10px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-section-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 0 8px 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13.5px;
  font-weight: 500;
  transition: all 0.18s ease;
  text-decoration: none;
}

.nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.nav-item--active { background: var(--accent-dim); color: var(--accent); }
.nav-item--active .nav-icon { opacity: 1; }
.nav-item:hover .nav-icon { opacity: 1; }

.nav-icon {
  width: 18px; height: 18px;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  opacity: 0.65;
}

.nav-label { flex: 1; }

/* ─── SIDEBAR BOTTOM ─── */
.sidebar-bottom {
  border-top: 1px solid var(--border);
}

/* ─── THEME SWITCHER ─── */
.theme-switcher {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
}

.theme-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: var(--text-secondary);
  font-weight: 500;
}

.theme-toggle {
  position: relative;
  width: 36px; height: 20px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.25s, border-color 0.25s;
  flex-shrink: 0;
}

.theme-toggle--on {
  background: var(--accent);
  border-color: var(--accent);
}

.theme-toggle-thumb {
  position: absolute;
  top: 2px; left: 2px;
  width: 14px; height: 14px;
  background: var(--text-muted);
  border-radius: 50%;
  transition: transform 0.25s, background 0.25s;
}

.theme-toggle--on .theme-toggle-thumb {
  transform: translateX(16px);
  background: #fff;
}

[data-theme="dark"] .theme-toggle--on .theme-toggle-thumb {
  background: #0f1117;
}

/* ─── USER ─── */
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
}

.user-avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent) 0%, #3B82F6 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

[data-theme="dark"] .user-avatar { color: #0f1117; }

.user-avatar.small { width: 28px; height: 28px; font-size: 10px; }
.user-info { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.user-name { font-size: 12.5px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: 10.5px; color: var(--text-muted); }

.user-logout {
  background: none; border: none; cursor: pointer;
  color: var(--text-muted); padding: 4px; border-radius: 6px;
  display: flex; align-items: center;
  transition: color 0.15s, background 0.15s;
}
.user-logout:hover { color: var(--danger); background: var(--danger-dim); }

/* ─── MAIN ─── */
.main-wrapper {
  margin-left: var(--sidebar-width);
  flex: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  transition: background 0.2s;
}

/* ─── TOPBAR (mobile) ─── */
.topbar {
  display: none;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: var(--topbar-height);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 50;
  transition: background 0.2s;
}

.topbar-logo { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 15px; color: var(--text-primary); }

.burger {
  background: none; border: none; cursor: pointer;
  display: flex; flex-direction: column; gap: 4px; padding: 6px;
}
.burger span { display: block; width: 20px; height: 2px; background: var(--text-secondary); border-radius: 2px; }

.topbar-theme-btn {
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 16px;
  padding: 5px 8px;
  line-height: 1;
  transition: background 0.15s;
}
.topbar-theme-btn:hover { background: var(--bg-hover); }

.main-content { flex: 1; }

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); }
  .app-shell.sidebar-open .sidebar { transform: translateX(0); }
  .app-shell.sidebar-open .sidebar-overlay { display: block; }
  .topbar { display: flex; }
  .main-wrapper { margin-left: 0; }
}
</style>