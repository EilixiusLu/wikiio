<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <!-- 左侧：Logo -->
      <a href="/" class="navbar-logo">
        <span class="logo-icon">W</span>
        <span class="logo-text">Wikiio</span>
      </a>

      <!-- 中间：导航链接 -->
      <div class="navbar-links">
        <a href="/" :class="{ active: route.path === '/' }">首页</a>
        <a href="/search" :class="{ active: route.path === '/search' }">搜索</a>
        <a v-if="authStore.user?.role >= 3" href="/admin" :class="{ active: route.path === '/admin' }">管理</a>
      </div>

      <!-- 右侧：用户区域 -->
      <div class="navbar-user">
        <template v-if="authStore.isLoggedIn">
          <a href="/search" class="nav-icon-btn" title="搜索">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </a>
          <div class="user-menu" @click="toggleMenu">
            <img v-if="authStore.user?.fandom_avatar_url" :src="authStore.user.fandom_avatar_url" class="avatar" />
            <div v-else class="avatar-placeholder">{{ authStore.user?.username?.[0]?.toUpperCase() }}</div>
            <span class="username">{{ authStore.user?.username }}</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5z"/></svg>
            <div class="dropdown" v-if="menuOpen">
              <a href="/profile">个人主页</a>
              <div class="divider"></div>
              <a @click.prevent="handleLogout" href="#">退出登录</a>
            </div>
          </div>
        </template>
        <template v-else>
          <a href="/login" class="btn-login">登录</a>
          <a href="/register" class="btn-register">注册</a>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const menuOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function handleLogout() {
  authStore.logout()
  menuOpen.value = false
  router.push('/')
}

function closeMenu(e) {
  if (!e.target.closest('.user-menu')) {
    menuOpen.value = false
  }
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
  position: sticky;
  top: 0;
  z-index: 100;
  background: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 4rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  flex-shrink: 0;
}
.logo-icon {
  width: 30px;
  height: 30px;
  background: #185897;
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1rem;
}
.logo-text {
  color: #1a1a2e;
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: 0.5px;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}
.navbar-links a {
  color: #444;
  text-decoration: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: all 0.15s;
}
.navbar-links a:hover { color: #185897; background: #f0f5ff; }
.navbar-links a.active { color: #185897; background: #e8f0fc; font-weight: 500; }

.navbar-user {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-shrink: 0;
}

.nav-icon-btn {
  color: #555;
  display: flex;
  align-items: center;
  padding: 0.4rem;
  border-radius: 4px;
  transition: all 0.15s;
}
.nav-icon-btn:hover { color: #185897; background: #f0f5ff; }

.user-menu {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  color: #333;
  font-size: 0.9rem;
  position: relative;
  transition: background 0.15s;
}
.user-menu:hover { background: #f0f5ff; }

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}
.avatar-placeholder {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #185897;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  min-width: 140px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  overflow: hidden;
}
.dropdown a {
  display: block;
  padding: 0.6rem 1rem;
  color: #333;
  text-decoration: none;
  font-size: 0.88rem;
  transition: background 0.15s;
}
.dropdown a:hover { background: #f0f5ff; color: #185897; }
.divider { height: 1px; background: #e8e8e8; }

.btn-login {
  color: #333;
  text-decoration: none;
  font-size: 0.9rem;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  transition: all 0.15s;
}
.btn-login:hover { color: #185897; background: #f0f5ff; }

.btn-register {
  background: #185897;
  color: white;
  text-decoration: none;
  font-size: 0.9rem;
  padding: 0.4rem 1rem;
  border-radius: 4px;
  transition: background 0.15s;
}
.btn-register:hover { background: #134a7f; }
</style>