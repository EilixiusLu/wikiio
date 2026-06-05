<template>
  <div class="page">
    <div class="card">
      <h2>登录 Wikiio</h2>
      <div v-if="error" class="error">{{ error }}</div>
      <div class="form-group">
        <label>邮箱</label>
        <input v-model="email" type="email" placeholder="your@email.com" />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="请输入密码" />
      </div>
      <button class="btn-primary" @click="handleLogin" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      <p>还没有账号？<a href="/register">立即注册</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try { await authStore.login(email.value, password.value); router.push('/profile') }
  catch (err) { error.value = err.detail || '登录失败，请检查邮箱和密码' }
  finally { loading.value = false }
}
</script>

<style scoped>
.page { min-height: 80vh; display: flex; align-items: center; justify-content: center; padding: 2rem; }
.card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: 40px;
  width: 100%; max-width: 420px;
}
h2 { font-size: 24px; font-weight: 600; color: var(--color-ink); margin-bottom: 24px; letter-spacing: -0.02em; }
.form-group { margin-bottom: 20px; }
label { display: block; font-size: 14px; font-weight: 500; color: var(--color-ink); margin-bottom: 6px; }
input {
  width: 100%; padding: 12px 16px;
  border: 1px solid var(--color-hairline);
  border-radius: 8px; font-size: 17px; font-family: inherit;
  color: var(--color-ink); outline: none; background: var(--color-canvas);
}
input:focus { border-color: var(--color-primary); }
.btn-primary {
  width: 100%; padding: 12px;
  background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-pill);
  font-size: 17px; font-family: inherit; cursor: pointer;
  margin-top: 8px; transition: opacity 0.15s;
}
.btn-primary:hover { opacity: 0.9; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.error { color: #e74c3c; font-size: 14px; margin-bottom: 16px; }
p { text-align: center; margin-top: 20px; font-size: 14px; color: var(--color-muted); }
p a { color: var(--color-primary); }
</style>
