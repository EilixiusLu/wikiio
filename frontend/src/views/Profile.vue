<template>
  <div class="page">
    <div class="card">
      <h2>个人主页</h2>
      <div v-if="authStore.user">
        <p><strong>用户名：</strong>{{ authStore.user.username }}</p>
        <p><strong>邮箱：</strong>{{ authStore.user.email }}</p>
        <p><strong>邮箱验证：</strong>{{ authStore.user.is_email_verified ? '已验证' : '未验证' }}</p>
        <p><strong>Fandom绑定：</strong>{{ authStore.user.is_fandom_verified ? authStore.user.fandom_username : '未绑定' }}</p>
        <button @click="handleLogout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  await authStore.fetchMe()
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}
.card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}
h2 { margin-bottom: 1.5rem; }
p { margin-bottom: 0.8rem; }
button {
  padding: 0.6rem 1.5rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}
</style>