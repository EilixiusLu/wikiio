<template>
  <div class="page">
    <Transition name="fade-up" appear>
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
        <button class="btn-primary" @click="handleRegister" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        <p>已有账号？<a href="/login">立即登录</a></p>
      </div>
    </Transition>
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
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
}
.card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-10);
  width: 100%;
  max-width: 420px;
}
.card h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--space-6);
  letter-spacing: -0.02em;
}
.form-group { margin-bottom: var(--space-5); }
.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-ink);
  margin-bottom: var(--space-1);
}
.form-group input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  font-family: inherit;
  color: var(--color-ink);
  outline: none;
  background: var(--color-canvas);
  transition: border-color var(--duration-base) var(--ease-smooth);
}
.form-group input:focus { border-color: var(--color-primary); }

.btn-primary {
  width: 100%;
  padding: var(--space-3);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-pill);
  font-size: var(--text-base);
  font-family: inherit;
  cursor: pointer;
  margin-top: var(--space-2);
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-primary:hover { opacity: 0.9; }
.btn-primary:active { transform: scale(0.96); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.error {
  color: var(--color-danger);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}
.success {
  color: var(--color-success);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}
.card p {
  text-align: center;
  margin-top: var(--space-5);
  font-size: var(--text-sm);
  color: var(--color-muted);
}
.card p a { color: var(--color-primary); }
</style>
