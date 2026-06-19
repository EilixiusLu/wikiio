<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <div class="navbar-left">
        <router-link to="/" class="navbar-logo">
          <img src="/wikiio-logo.svg" alt="Wikiio" class="logo-img" />
        </router-link>

        <!-- 桌面端导航链接 -->
        <div class="navbar-links">
          <router-link to="/" :class="{ active: route.path === '/' }">首页</router-link>
          <router-link to="/search" :class="{ active: route.path === '/search' }">搜索</router-link>
          <router-link to="/rankings" :class="{ active: route.path === '/rankings' }">排名</router-link>
          <router-link v-if="authStore.user?.role >= 3" to="/admin" :class="{ active: route.path === '/admin' }">管理</router-link>
        </div>
      </div>

      <div class="navbar-right">
        <router-link to="/search" class="nav-search-btn" title="搜索">
          <i class="fa fa-search"></i>
        </router-link>

        <button class="nav-search-btn theme-toggle" @click="toggleTheme" :title="themeLabel">
          <i class="fa" :class="resolvedTheme === 'dark' ? 'fa-sun-o' : 'fa-moon-o'"></i>
        </button>

        <div class="navbar-user">
          <template v-if="authStore.isLoggedIn">
            <div class="user-menu" @click="toggleMenu">
              <img
                v-if="authStore.user?.fandom_avatar_url"
                :src="authStore.user.fandom_avatar_url"
                class="avatar"
              />
              <div v-else class="avatar-placeholder">
                {{ authStore.user?.username?.[0]?.toUpperCase() }}
              </div>
              <span class="username">{{ authStore.user?.username }}</span>
              <i class="fa fa-chevron-down caret"></i>
              <Transition name="dropdown">
                <div class="dropdown" v-if="menuOpen" @click.stop>
                  <router-link to="/profile">个人主页</router-link>
                  <div class="divider"></div>
                  <a @click.prevent="handleLogout" href="#">退出登录</a>
                </div>
              </Transition>
            </div>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-nav">登录</router-link>
            <router-link to="/register" class="btn-nav-primary">注册</router-link>
          </template>
        </div>

        <button class="menu-toggle" @click="mobileOpen = !mobileOpen" aria-label="菜单">
          <span class="hamburger" :class="{ open: mobileOpen }">
            <span></span><span></span><span></span>
          </span>
        </button>
      </div>
    </div>

    <Transition name="slide">
      <div class="mobile-menu" v-if="mobileOpen" @click.self="mobileOpen = false">
        <router-link to="/" class="mobile-nav-main" @click="mobileOpen = false" :class="{ active: route.path === '/' }">首页</router-link>
        <router-link to="/search" class="mobile-nav-main" @click="mobileOpen = false" :class="{ active: route.path === '/search' }">搜索</router-link>
        <router-link to="/rankings" class="mobile-nav-main" @click="mobileOpen = false" :class="{ active: route.path === '/rankings' }">排名</router-link>
        <router-link v-if="authStore.user?.role >= 3" to="/admin" class="mobile-nav-main" @click="mobileOpen = false" :class="{ active: route.path === '/admin' }">管理</router-link>
        <div class="mobile-divider"></div>
        <template v-if="authStore.isLoggedIn">
          <router-link to="/profile" class="mobile-nav-sub" @click="mobileOpen = false">个人主页</router-link>
          <a href="#" class="mobile-nav-sub" @click.prevent="handleLogout">退出登录</a>
        </template>
        <template v-else>
          <router-link to="/login" class="mobile-nav-sub" @click="mobileOpen = false">登录</router-link>
          <router-link to="/register" class="mobile-nav-sub" @click="mobileOpen = false">注册</router-link>
        </template>
      </div>
    </Transition>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { useTheme } from '../composables/useTheme.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const menuOpen = ref(false)
const mobileOpen = ref(false)
const { theme, toggle: toggleTheme } = useTheme()

const resolvedTheme = computed(() => {
  if (theme.value === 'dark') return 'dark'
  if (theme.value === 'light') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
})

const themeLabel = computed(() =>
  resolvedTheme.value === 'dark' ? '切换为浅色模式' : '切换为深色模式'
)

function toggleMenu() { menuOpen.value = !menuOpen.value }
function handleLogout() {
  authStore.logout()
  menuOpen.value = false
  mobileOpen.value = false
  router.push('/')
}
function closeMenu(e) {
  if (!e.target.closest('.user-menu')) menuOpen.value = false
}

onMounted(() => {
  authStore.fetchMe()
  document.addEventListener('click', closeMenu)
})
onUnmounted(() => {
  document.removeEventListener('click', closeMenu)
})
</script>

<style scoped>
.navbar {
  position: sticky; top: 0; 
  z-index: 100;
  background: var(--color-canvas);
  border-bottom: 1px solid var(--color-hairline);
}
.navbar-inner {
  max-width: 1200px; margin: 0 auto; 
  padding: 0 var(--space-8);
  height: var(--size-nav);
  display: flex; align-items: center; 
  justify-content: space-between;
}
.navbar-left { display: flex; align-items: center; gap: var(--space-8); }
.navbar-logo { display: flex; align-items: center; flex-shrink: 0; }
.logo-img { height: 2.5rem; width: auto; }

/* ── 桌面端导航链接 ── */
.navbar-links { display: flex; align-items: center; gap: var(--space-6); }
.navbar-links a {
  color: var(--color-muted);
  font-size: var(--text-sm);
  padding: var(--space-1) 0;
  font-weight: 500;
  position: relative;
}
.navbar-links a::after {
  content: '';
  position: absolute;
  bottom: -2px; left: 0;
  width: 0; height: 1.5px;
  background: var(--color-primary);
  border-radius: 2px;
  transition: width var(--duration-base) var(--ease-apple);
}
.navbar-links a:hover,
.navbar-links a.active { color: var(--color-primary); text-decoration: none; }
.navbar-links a:hover::after,
.navbar-links a.active::after { width: 100%; }

/* ── 右侧区域 ── */
.navbar-right { display: flex; align-items: center; gap: var(--space-3); flex-shrink: 0; }
.nav-search-btn {
  color: var(--color-muted); font-size: var(--text-base);
  width: var(--size-input); height: var(--size-input);
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-sm);
  transition: background-color var(--duration-fast) var(--ease-smooth),
              color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.nav-search-btn:hover { color: var(--color-primary); background: var(--color-parchment); text-decoration: none; }
.nav-search-btn:active { transform: scale(0.92); }

.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
}

.menu-toggle {
  display: none; background: none; border: none;
  cursor: pointer; padding: var(--space-2);
  transition: transform var(--duration-fast) var(--ease-apple);
}
.menu-toggle:active { transform: scale(0.92); }

/* ── 用户菜单 ── */
.navbar-user { display: flex; align-items: center; gap: var(--space-3); }
.btn-nav {
  color: var(--color-muted); padding: var(--space-1) var(--space-3);
  border-radius: 6px; font-size: var(--text-sm); font-weight: 500;
  transition: background-color var(--duration-fast) var(--ease-smooth),
              color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-nav:hover { color: var(--color-primary); text-decoration: none; background: var(--color-parchment); }
.btn-nav:active { transform: scale(0.96); }

.btn-nav-primary {
  background: var(--color-primary); color: #fff;
  padding: var(--space-1) var(--space-5); border-radius: var(--radius-pill);
  font-size: var(--text-sm); font-weight: 500;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-nav-primary:hover { opacity: 0.9; text-decoration: none; }
.btn-nav-primary:active { transform: scale(0.96); }

.user-menu {
  display: flex; align-items: center; gap: var(--space-1);
  cursor: pointer; position: relative;
  padding: var(--space-1) var(--space-2); border-radius: 6px;
  transition: background-color var(--duration-fast) var(--ease-smooth);
}
.user-menu:hover { background: var(--color-parchment); }
.username { color: var(--color-ink); font-size: var(--text-sm); }
.caret { font-size: var(--text-xs); color: var(--color-muted); }
.avatar { width: var(--size-avatar); height: var(--size-avatar); border-radius: 50%; object-fit: cover; }
.avatar-placeholder {
  width: var(--size-avatar); height: var(--size-avatar); border-radius: 50%;
  background: var(--color-primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: var(--text-xs); font-weight: 600;
}

/* ── 下拉菜单 ── */
.dropdown {
  position: absolute; top: calc(100% + var(--space-2)); right: 0;
  background: var(--color-canvas); border: 1px solid var(--color-hairline);
  border-radius: 12px; min-width: 150px; overflow: hidden; z-index: 200;
}
.dropdown a {
  display: block; padding: var(--space-2) var(--space-4);
  color: var(--color-ink); font-size: var(--text-sm);
  transition: background-color var(--duration-fast) var(--ease-smooth);
}
.dropdown a:hover { background: var(--color-parchment); text-decoration: none; }
.divider { height: 1px; background: var(--color-hairline); }

/* ── 移动端菜单 ── */
.mobile-menu {
  display: none;
  position: fixed;
  top: var(--size-nav);
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-canvas);
  z-index: 199;
  overflow-y: auto;
  padding: var(--space-10) var(--space-8);
}

/* 主导航链接: 大字体冲击 */
.mobile-nav-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-ink);
  line-height: 1.5;
  margin-bottom: var(--space-6);
  transition: opacity var(--duration-fast) var(--ease-apple);
}
.mobile-nav-main:active { opacity: 0.6; }

/* 次级导航链接: 降级处理 */
.mobile-nav-sub {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--color-muted);
  line-height: 1.5;
  margin-bottom: var(--space-5);
  transition: opacity var(--duration-fast) var(--ease-apple);
}
.mobile-nav-sub:active { opacity: 0.6; }

/* 分割线: 视觉缓冲留白, 不画线 */
.mobile-divider {
  height: var(--space-10);
}

/* ── 汉堡图标 ── */
.hamburger { display: flex; flex-direction: column; gap: 4px; width: 22px; }
.hamburger span {
  display: block; height: 2px; background: var(--color-ink);
  border-radius: 2px;
  transition: transform var(--duration-base) var(--ease-apple),
              opacity var(--duration-base) var(--ease-smooth);
}
.hamburger.open span:nth-child(1) { transform: translateY(6px) rotate(45deg); }
.hamburger.open span:nth-child(2) { opacity: 0; }
.hamburger.open span:nth-child(3) { transform: translateY(-6px) rotate(-45deg); }

/* ── 移动端过渡 ── */
.slide-enter-active,
.slide-leave-active {
  transition:
    opacity var(--duration-base) var(--ease-apple),
    transform var(--duration-base) var(--ease-apple);
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(calc(var(--space-3) * -1));
}

@media (max-width: 768px) {
  .navbar-links { display: none; }
  .navbar-user .username { display: none; }
  .menu-toggle { display: flex; align-items: center; justify-content: center; }
  .mobile-menu { display: block; }
}
</style>
