<template>
  <div class="page">
    <div class="card">
      <h2>注册 Wikiio</h2>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">{{ success }}</div>
      <div class="form-group">
        <label>邮箱</label>
        <input v-model="email" type="email" placeholder="your@email.com" />
      </div>
      <div class="form-group">
        <label>用户名</label>
        <input v-model="username" type="text" placeholder="3-20个字符，字母数字下划线" />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="至少8个字符" />
      </div>
      <button @click="handleRegister" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
      <p>已有账号？<a href="/login">立即登录</a></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth.js'

const authStore = useAuthStore()

const email = ref('')
const username = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await authStore.register(email.value, username.value, password.value)
    success.value = '注册成功！请前往登录。'
  } catch (err) {
    error.value = err.detail || '注册失败，请稍后再试'
  } finally {
    loading.value = false
  }
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
h2 { margin-bottom: 1.5rem; text-align: center; }
.form-group { margin-bottom: 1rem; }
label { display: block; margin-bottom: 0.3rem; font-weight: 500; }
input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 0.7rem;
  background: #185897;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 0.5rem;
}
button:disabled { background: #aaa; cursor: not-allowed; }
.error { color: red; margin-bottom: 1rem; font-size: 0.9rem; }
.success { color: green; margin-bottom: 1rem; font-size: 0.9rem; }
p { text-align: center; margin-top: 1rem; }
a { color: #185897; }
</style>