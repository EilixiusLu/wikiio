<template>
  <div class="page">
    <Transition name="fade-up" appear>
      <div class="card">
        <!-- 无 token -->
        <template v-if="!token">
          <div class="status-icon">❓</div>
          <h2>链接无效</h2>
          <p>验证链接缺少必要参数，请检查邮件中的完整链接，或重新发送验证邮件。</p>
          <router-link to="/resend-verification" class="btn-primary">重新发送验证邮件</router-link>
        </template>

        <!-- 验证成功 -->
        <template v-else-if="verified">
          <div class="status-icon">✅</div>
          <h2>邮箱验证成功！</h2>
          <p>现在可以登录了，即将自动跳转...</p>
          <router-link to="/login" class="btn-primary">立即登录</router-link>
        </template>

        <!-- 验证失败 -->
        <template v-else-if="error">
          <div class="status-icon">❌</div>
          <h2>验证失败</h2>
          <p class="error-msg">{{ error }}</p>
          <router-link to="/resend-verification" class="btn-primary">重新发送验证邮件</router-link>
        </template>

        <!-- 初始状态：等待用户点击确认 -->
        <template v-else>
          <div class="status-icon">📧</div>
          <h2>验证你的邮箱</h2>
          <p>点击下方按钮以完成邮箱验证。</p>
          <button class="btn-primary" @click="doVerify" :disabled="loading">
            {{ loading ? '验证中...' : '确认验证' }}
          </button>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authAPI } from '../api/index.js'

const route = useRoute()
const router = useRouter()
const token = ref('')
const loading = ref(false)
const error = ref('')
const verified = ref(false)

onMounted(() => {
  // 只读取 query 参数，不自动发起验证请求
  token.value = route.query.token || ''
})

async function doVerify() {
  loading.value = true
  error.value = ''
  try {
    await authAPI.verifyEmail(token.value)
    verified.value = true
    // 3 秒后自动跳转登录
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (err) {
    error.value = err.detail || '验证失败，链接可能已过期或无效'
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
.card p {
  font-size: var(--text-sm);
  color: var(--color-muted);
  line-height: 1.6;
  margin-bottom: var(--space-6);
}
.status-icon { font-size: 48px; margin-bottom: var(--space-4); }
.error-msg {
  color: var(--color-danger) !important;
}

.btn-primary {
  display: inline-block;
  padding: var(--space-3) var(--space-8);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-pill);
  font-size: var(--text-base);
  font-family: inherit;
  cursor: pointer;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
  text-decoration: none;
}
.btn-primary:hover { opacity: 0.9; text-decoration: none; }
.btn-primary:active { transform: scale(0.96); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
</style>
