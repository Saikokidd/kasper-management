<template>
  <AppLayout>
    <div class="page-wrap">

      <div class="dash-header">
        <div>
          <h1 class="dash-heading">Добро пожаловать<span>,</span></h1>
          <p class="dash-name">{{ auth.user?.full_name }}</p>
        </div>
        <div class="dash-role-badge">{{ roleLabel }}</div>
      </div>

      <div class="cards-grid">
        <router-link v-for="section in sections" :key="section.name" :to="section.to" class="section-card">
          <div class="card-icon-wrap">
            <span>{{ section.icon }}</span>
          </div>
          <div class="card-body">
            <h3 class="card-title">{{ section.name }}</h3>
            <p class="card-desc">{{ section.desc }}</p>
          </div>
          <div class="card-arrow">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"/>
              <polyline points="12 5 19 12 12 19"/>
            </svg>
          </div>
        </router-link>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const roleLabel = computed(() => ({
  admin: 'Администратор',
  pult: 'Руководство',
  hr: 'HR-специалист'
}[auth.user?.role] || ''))

const sections = [
  { icon: '📅', name: 'Собеседования', desc: 'Календарь и список кандидатов', to: '/interviews' },
  { icon: '✍️', name: 'Прописи', desc: 'Ручной поиск в соцсетях', to: '/inscriptions' },
  { icon: '📋', name: 'Анкеты', desc: 'Личные дела сотрудников', to: '/candidates' },
  { icon: '✅', name: 'Задачи', desc: 'План на день, неделю, месяц', to: '/tasks' },
  { icon: '📢', name: 'Реклама', desc: 'Публикации в соцсетях', to: '/ads' },
  { icon: '📄', name: 'Объявления', desc: 'OLX и Work.UA', to: '/job-posts' },
  { icon: '🎵', name: 'TikTok', desc: 'Статистика эфиров', to: '/tiktok' },
]
</script>

<style scoped>
.dash-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 12px;
}

.dash-heading {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.dash-heading span { color: var(--accent); }

.dash-name {
  font-size: 15px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.dash-role-badge {
  background: var(--accent-dim);
  color: var(--accent);
  border: 1px solid rgba(110,231,183,0.2);
  border-radius: 999px;
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  margin-top: 4px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.section-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  text-decoration: none;
}

.section-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--accent-dim) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.2s;
}

.section-card:hover {
  border-color: rgba(110,231,183,0.25);
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}

.section-card:hover::before { opacity: 1; }

.card-icon-wrap {
  width: 42px; height: 42px;
  background: var(--bg-elevated);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.card-body {
  flex: 1;
  position: relative;
  z-index: 1;
  min-width: 0;
}

.card-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 3px;
}

.card-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.card-arrow {
  color: var(--text-muted);
  flex-shrink: 0;
  position: relative;
  z-index: 1;
  transition: color 0.2s, transform 0.2s;
}

.section-card:hover .card-arrow {
  color: var(--accent);
  transform: translateX(3px);
}

@media (max-width: 480px) {
  .cards-grid { grid-template-columns: 1fr; }
  .dash-heading { font-size: 22px; }
}
</style>