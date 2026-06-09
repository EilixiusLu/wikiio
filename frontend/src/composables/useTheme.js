import { ref, watchEffect } from 'vue'

const STORAGE_KEY = 'wikiio-theme'

// Module-level shared state — all components see the same theme
const theme = ref(localStorage.getItem(STORAGE_KEY) || 'system')

function resolveTheme(value) {
  if (value === 'dark') return 'dark'
  if (value === 'light') return 'light'
  // 'system': check browser preference
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(resolved) {
  document.documentElement.setAttribute('data-theme', resolved)
}

// Reactively apply the resolved theme whenever theme ref or system prefs change
watchEffect(() => {
  applyTheme(resolveTheme(theme.value))
})

// Listen for system preference changes when in 'system' mode
const mq = window.matchMedia('(prefers-color-scheme: dark)')
mq.addEventListener('change', () => {
  if (theme.value === 'system') {
    applyTheme(resolveTheme('system'))
  }
})

export function useTheme() {
  function toggle() {
    const current = resolveTheme(theme.value)
    const next = current === 'dark' ? 'light' : 'dark'
    theme.value = next
    localStorage.setItem(STORAGE_KEY, next)
  }

  function setExplicit(value) {
    theme.value = value
    localStorage.setItem(STORAGE_KEY, value)
  }

  return {
    theme,
    toggle,
    setExplicit,
  }
}
