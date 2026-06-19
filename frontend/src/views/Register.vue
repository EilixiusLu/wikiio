<template>
  <div class="page">
    <Transition name="fade-up" appear>
      <!-- 注册成功提示卡片 -->
      <div class="card" v-if="registeredEmail">
        <div class="success-icon">✉️</div>
        <h2>注册成功！</h2>
        <p class="verify-hint">
          我们已向 <strong>{{ registeredEmail }}</strong> 发送了一封验证邮件，
          请在 <strong>24 小时</strong> 内点击邮件中的链接激活账户。
        </p>
        <p class="spam-hint">（如未收到，请检查垃圾邮件文件夹）</p>
        <router-link to="/resend-verification" class="btn-link">重新发送验证邮件</router-link>
      </div>

      <!-- 注册表单 -->
      <div class="card" v-else>
        <h2>注册 Wikiio</h2>
        <div v-if="error" class="error">{{ error }}</div>
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
        <p>已有账号？<router-link to="/login">立即登录</router-link></p>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authAPI } from '../api/index.js'

const email = ref('')
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const registeredEmail = ref('')

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    const data = await authAPI.register({
      email: email.value,
      username: username.value,
      password: password.value,
    })
    registeredEmail.value = data.email
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
  text-align: center;
}
.card h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--space-6);
  letter-spacing: -0.02em;
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
  font-size: var(--text-sm);
  color: var(--color-muted);
  margin-top: var(--space-5);
}
.card p a { color: var(--color-primary); }

.success-icon { font-size: 48px; margin-bottom: var(--space-4); }
.verify-hint {
  font-size: var(--text-sm);
  color: var(--color-ink);
  line-height: 1.6;
  margin-top: var(--space-4);
}
.spam-hint {
  font-size: var(--text-xs);
  color: var(--color-muted);
  margin-top: var(--space-2);
}
.btn-link {
  display: inline-block;
  margin-top: var(--space-5);
  color: var(--color-primary);
  font-size: var(--text-sm);
}
.btn-link:hover { text-decoration: underline; }
</style>
