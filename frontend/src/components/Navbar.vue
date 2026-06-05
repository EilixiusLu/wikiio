<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <a href="/" class="navbar-logo">
        <img src="/wikiio-logo.svg" alt="Wikiio" class="logo-img" />
      </a>
      <div class="navbar-links">
        <a href="/" :class="{ active: route.path === '/' }">首页</a>
        <a href="/search" :class="{ active: route.path === '/search' }">搜索</a>
        <a href="/rankings" :class="{ active: route.path === '/rankings' }">排名</a>
        <a v-if="authStore.user?.role >= 3" href="/admin" :class="{ active: route.path === '/admin' }">管理</a>
      </div>
      <div class="navbar-user">
        <template v-if="authStore.isLoggedIn">
          <div class="user-menu" @click="toggleMenu">
            <img v-if="authStore.user?.fandom_avatar_url" :src="authStore.user.fandom_avatar_url" class="avatar" />
            <div v-else class="avatar-placeholder">{{ authStore.user?.username?.[0]?.toUpperCase() }}</div>
            <span class="username">{{ authStore.user?.username }}</span>
            <i class="fa fa-chevron-down" style="font-size:10px;"></i>
            <div class="dropdown" v-if="menuOpen">
              <a href="/profile">个人主页</a>
              <div class="divider"></div>
              <a @click.prevent="handleLogout" href="#">退出登录</a>
            </div>
          </div>
        </template>
        <template v-else>
          <a href="/login" class="btn-nav">登录</a>
          <a href="/register" class="btn-nav-primary">注册</a>
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

function toggleMenu() { menuOpen.value = !menuOpen.value }
function handleLogout() { authStore.logout(); menuOpen.value = false; router.push('/') }
function closeMenu(e) { if (!e.target.closest('.user-menu')) menuOpen.value = false }

onMounted(() => { authStore.fetchMe(); document.addEventListener('click', closeMenu) })
onUnmounted(() => { document.removeEventListener('click', closeMenu) })
</script>

<style scoped>
.navbar {
  position: sticky; top: 0; z-index: 100;
  background: var(--color-canvas);
  border-bottom: 1px solid var(--color-hairline);
}
.navbar-inner {
  max-width: 1200px; margin: 0 auto; padding: 0 2rem;
  height: 64px;
  display: flex; align-items: center; justify-content: space-between;
}
.navbar-logo { display: flex; align-items: center; flex-shrink: 0; }
.logo-img { height: 40px; width: auto; }
.navbar-links { display: flex; align-items: center; gap: 24px; }
.navbar-links a {
  color: var(--color-muted); font-size: 14px;
  padding: 4px 0; transition: color 0.15s; font-weight: 500;
}
.navbar-links a:hover, .navbar-links a.active { color: var(--color-primary); text-decoration: none; }
.navbar-user { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
.btn-nav { color: var(--color-muted); padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: 500; transition: 0.15s; }
.btn-nav:hover { color: var(--color-primary); text-decoration: none; background: var(--color-parchment); }
.btn-nav-primary {
  background: var(--color-primary); color: #fff;
  padding: 6px 18px; border-radius: var(--radius-pill);
  font-size: 14px; font-weight: 500; transition: opacity 0.15s;
}
.btn-nav-primary:hover { opacity: 0.9; text-decoration: none; }
.user-menu { display: flex; align-items: center; gap: 6px; cursor: pointer; position: relative; padding: 4px 8px; border-radius: 6px; }
.user-menu:hover { background: var(--color-parchment); }
.username { color: var(--color-ink); font-size: 14px; }
.avatar { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
.avatar-placeholder {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--color-primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600;
}
.dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  background: var(--color-canvas); border: 1px solid var(--color-hairline);
  border-radius: 12px; min-width: 150px; overflow: hidden; z-index: 200;
}
.dropdown a { display: block; padding: 10px 16px; color: var(--color-ink); font-size: 15px; }
.dropdown a:hover { background: var(--color-parchment); text-decoration: none; }
.divider { height: 1px; background: var(--color-hairline); }
</style>
