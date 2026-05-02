import { ref, watch, onMounted } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'dark')

function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t)
  localStorage.setItem('theme', t)
}

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}

watch(theme, applyTheme)

export function useTheme() {
  onMounted(() => applyTheme(theme.value))
  return { theme, toggleTheme }
}