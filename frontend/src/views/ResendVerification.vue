<template>
  <div class="page">
    <Transition name="fade-up" appear>
      <div class="card">
        <h2>重新发送验证邮件</h2>

        <!-- 发送成功 -->
        <template v-if="sent">
          <div class="status-icon">📧</div>
          <p class="success-msg">{{ message }}</p>
          <router-link to="/login" class="btn-link">返回登录</router-link>
        </template>

        <!-- 表单 -->
        <template v-else>
          <p class="desc">请输入注册时使用的邮箱地址，我们将重新发送验证邮件。</p>
          <div v-if="error" class="error">{{ error }}</div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="email" type="email" placeholder="your@email.com" @keyup.enter="handleResend" />
          </div>
          <button class="btn-primary" @click="handleResend" :disabled="loading">
            {{ loading ? '发送中...' : '发送验证邮件' }}
          </button>
          <p><router-link to="/login">返回登录</router-link></p>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authAPI } from '../api/index.js'

const email = ref('')
const loading = ref(false)
const error = ref('')
const sent = ref(false)
const message = ref('')

async function handleResend() {
  error.value = ''
  if (!email.value.trim()) {
    error.value = '请输入邮箱地址'
    return
  }
  loading.value = true
  try {
    const data = await authAPI.resendVerification(email.value)
    sent.value = true
    message.value = data.message
  } catch (err) {
    error.value = err.detail || '发送失败，请稍后再试'
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
  text-align: center;
}
.card h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--space-4);
  letter-spacing: -0.02em;
}
.desc {
  font-size: var(--text-sm);
  color: var(--color-muted);
  line-height: 1.6;
  margin-bottom: var(--space-5);
}
.status-icon { font-size: 48px; margin-bottom: var(--space-4); }
.success-msg {
  font-size: var(--text-sm);
  color: var(--color-ink);
  margin-bottom: var(--space-6);
}
.form-group { margin-bottom: var(--space-5); text-align: left; }
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
.card p {
  text-align: center;
  margin-top: var(--space-5);
  font-size: var(--text-sm);
  color: var(--color-muted);
}
.card p a, .btn-link { color: var(--color-primary); }
</style>
