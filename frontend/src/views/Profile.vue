<template>
  <div class="profile-page">
    <div class="content" v-if="authStore.user">

      <!-- 用户信息卡片 -->
      <div class="card user-card">
        <div class="user-header">
          <img
            v-if="authStore.user.fandom_avatar_url"
            :src="authStore.user.fandom_avatar_url"
            class="big-avatar"
          />
          <div v-else class="big-avatar-placeholder">
            {{ authStore.user.username?.[0]?.toUpperCase() }}
          </div>
          <div class="user-info">
            <h1>{{ authStore.user.username }}</h1>
            <div class="user-badges">
              <span class="badge" :class="roleBadgeClass">{{ roleLabel }}</span>
              <span class="badge verified" v-if="authStore.user.is_email_verified">邮箱已验证</span>
              <span class="badge fandom" v-if="authStore.user.is_fandom_verified">
                Fandom: {{ authStore.user.fandom_username }}
              </span>
              <span class="badge miraheze" v-if="authStore.user.is_miraheze_verified">
                Miraheze: {{ authStore.user.miraheze_username }}
              </span>
            </div>
            <p class="user-email">{{ authStore.user.email }}</p>
          </div>
        </div>

        <div class="author-link" v-if="authStore.user.is_fandom_verified">
          <a :href="`/author/${authStore.user.fandom_username}`" class="btn-author">
            查看我的作者页 →
          </a>
        </div>
        <button class="btn-logout" @click="handleLogout">退出登录</button>
      </div>

      <!-- Fandom 绑定卡片 -->
      <div class="card">
        <h2>Fandom 账户绑定</h2>

        <!-- 已绑定状态 -->
        <div v-if="authStore.user.is_fandom_verified" class="bound-state">
          <div class="bound-info">
            <img v-if="authStore.user.fandom_avatar_url" :src="authStore.user.fandom_avatar_url" class="fandom-avatar" />
            <div>
              <p><b>{{ authStore.user.fandom_username }}</b></p>
              <p class="hint">已成功绑定 Fandom 账户</p>
            </div>
          </div>
          <button class="btn-danger" @click="handleUnbind">解除绑定</button>
        </div>

        <!-- 未绑定：第一步 -->
        <div v-else-if="!verifyCode">
          <p class="hint">绑定 Fandom 账户后可以对页面评分，且头像将同步为 Fandom 头像。</p>
          <div class="form-row">
            <input v-model="fandomUsername" placeholder="输入你的 Fandom 用户名" />
            <button class="btn-primary" @click="startBind" :disabled="bindLoading">
              {{ bindLoading ? '处理中...' : '开始绑定' }}
            </button>
          </div>
          <div class="error" v-if="bindError">{{ bindError }}</div>
        </div>

        <!-- 未绑定：第二步（显示验证码） -->
        <div v-else class="verify-step">
          <p class="hint">请按照以下步骤完成验证：</p>
          <ol class="steps">
            <li>
              登录你的 Fandom 账户，前往以下页面：
              <a :href="verifyUrl" target="_blank" class="link">{{ verifyPage }}</a>
            </li>
            <li>
              编辑该页面，将以下验证码填入页面内容并保存：
              <div class="code-box">
                {{ verifyCode }}
                <button class="copy-btn" @click="copyCode">{{ codeCopied ? '已复制' : '复制' }}</button>
              </div>
            </li>
            <li>完成后点击下方按钮验证</li>
          </ol>
          <div class="verify-actions">
            <button class="btn-primary" @click="doVerify" :disabled="verifyLoading">
              {{ verifyLoading ? '验证中...' : '我已填写，立即验证' }}
            </button>
            <button class="btn-text" @click="cancelBind">取消</button>
          </div>
          <div class="error" v-if="verifyError">{{ verifyError }}</div>
          <div class="success" v-if="verifySuccess">{{ verifySuccess }}</div>
        </div>
      </div>

      <!-- Miraheze 账户绑定 -->
      <div class="card">
        <h2>Miraheze 账户绑定</h2>

        <!-- 已绑定 -->
        <div v-if="authStore.user.is_miraheze_verified" class="bound-state">
          <div class="bound-info">
            <div class="mh-icon">M</div>
            <div>
              <p><b>{{ authStore.user.miraheze_username }}</b></p>
              <p class="hint">已成功绑定 Miraheze 账户</p>
            </div>
          </div>
          <button class="btn-danger" @click="handleMirahezeUnbind">解除绑定</button>
        </div>

        <!-- 未绑定：第一步 -->
        <div v-else-if="!mhVerifyCode">
          <p class="hint">绑定 Miraheze 账户后可对 Miraheze 维基上的页面评分。</p>
          <div class="form-row">
            <input v-model="mhUsername" placeholder="输入你的 Miraheze 用户名" />
            <button class="btn-primary" @click="startMirahezeBind" :disabled="mhBindLoading">
              {{ mhBindLoading ? '处理中...' : '开始绑定' }}
            </button>
          </div>
          <div class="error" v-if="mhBindError">{{ mhBindError }}</div>
        </div>

        <!-- 未绑定：第二步 -->
        <div v-else class="verify-step">
          <p class="hint">请按照以下步骤完成验证：</p>
          <ol class="steps">
            <li>
              登录你的 Miraheze 账户，前往以下页面：
              <a :href="mhVerifyUrl" target="_blank" class="link">{{ mhVerifyPage }}</a>
            </li>
            <li>
              编辑该页面，将以下验证码填入页面内容并保存：
              <div class="code-box">
                {{ mhVerifyCode }}
                <button class="copy-btn" @click="copyMhCode">{{ mhCodeCopied ? '已复制' : '复制' }}</button>
              </div>
            </li>
            <li>完成后点击下方按钮验证</li>
          </ol>
          <div class="verify-actions">
            <button class="btn-primary" @click="doMirahezeVerify" :disabled="mhVerifyLoading">
              {{ mhVerifyLoading ? '验证中...' : '我已填写，立即验证' }}
            </button>
            <button class="btn-text" @click="cancelMirahezeBind">取消</button>
          </div>
          <div class="error" v-if="mhVerifyError">{{ mhVerifyError }}</div>
          <div class="success" v-if="mhVerifySuccess">{{ mhVerifySuccess }}</div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

const fandomUsername = ref('')
const verifyCode = ref('')
const verifyPage = ref('')
const verifyUrl = ref('')
const bindLoading = ref(false)
const verifyLoading = ref(false)
const bindError = ref('')
const verifyError = ref('')
const verifySuccess = ref('')
const codeCopied = ref(false)

const roleLabel = computed(() => {
  const roles = ['普通用户', '已验证用户', '维基管理员', 'Wikiio管理员']
  return roles[authStore.user?.role || 0]
})

const roleBadgeClass = computed(() => {
  const classes = ['role-0', 'role-1', 'role-2', 'role-3']
  return classes[authStore.user?.role || 0]
})

function getToken() {
  return localStorage.getItem('access_token')
}

async function startBind() {
  if (!fandomUsername.value.trim()) return
  bindError.value = ''
  bindLoading.value = true
  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/v1/users/fandom/bind/start?fandom_username=${encodeURIComponent(fandomUsername.value)}`,
      {},
      { headers: { Authorization: `Bearer ${getToken()}` } }
    )
    verifyCode.value = res.data.verify_code
    verifyPage.value = res.data.target_page
    verifyUrl.value = res.data.target_url
  } catch (e) {
    bindError.value = e.response?.data?.detail || '发起绑定失败'
  } finally {
    bindLoading.value = false
  }
}

async function doVerify() {
  verifyError.value = ''
  verifySuccess.value = ''
  verifyLoading.value = true
  try {
    const res = await axios.post(
      'http://127.0.0.1:8000/api/v1/users/fandom/bind/verify',
      {},
      { headers: { Authorization: `Bearer ${getToken()}` } }
    )
    verifySuccess.value = res.data.message
    await authStore.fetchMe()
    verifyCode.value = ''
  } catch (e) {
    verifyError.value = e.response?.data?.detail || '验证失败，请检查是否已填写验证码'
  } finally {
    verifyLoading.value = false
  }
}

async function handleUnbind() {
  if (!confirm('确定要解除Fandom账户绑定吗？')) return
  try {
    await axios.delete(
      'http://127.0.0.1:8000/api/v1/users/fandom/unbind',
      { headers: { Authorization: `Bearer ${getToken()}` } }
    )
    await authStore.fetchMe()
  } catch (e) {
    alert('解绑失败')
  }
}

function cancelBind() {
  verifyCode.value = ''
  verifyPage.value = ''
  verifyUrl.value = ''
  bindError.value = ''
}

async function copyCode() {
  await navigator.clipboard.writeText(verifyCode.value)
  codeCopied.value = true
  setTimeout(() => codeCopied.value = false, 2000)
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}

onMounted(async () => {
  await authStore.fetchMe()
})

const mhUsername = ref('')
const mhVerifyCode = ref('')
const mhVerifyPage = ref('')
const mhVerifyUrl = ref('')
const mhBindLoading = ref(false)
const mhVerifyLoading = ref(false)
const mhBindError = ref('')
const mhVerifyError = ref('')
const mhVerifySuccess = ref('')
const mhCodeCopied = ref(false)

async function startMirahezeBind() {
  if (!mhUsername.value.trim()) return
  mhBindError.value = ''
  mhBindLoading.value = true
  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/v1/users/miraheze/bind/start?miraheze_username=${encodeURIComponent(mhUsername.value)}`,
      {},
      { headers: { Authorization: `Bearer ${getToken()}` } }
    )
    mhVerifyCode.value = res.data.verify_code
    mhVerifyPage.value = res.data.target_page
    mhVerifyUrl.value = res.data.target_url
  } catch (e) {
    mhBindError.value = e.response?.data?.detail || '发起绑定失败'
  } finally {
    mhBindLoading.value = false
  }
}

async function doMirahezeVerify() {
  mhVerifyError.value = ''
  mhVerifySuccess.value = ''
  mhVerifyLoading.value = true
  try {
    const res = await axios.post(
      'http://127.0.0.1:8000/api/v1/users/miraheze/bind/verify',
      {},
      { headers: { Authorization: `Bearer ${getToken()}` } }
    )
    mhVerifySuccess.value = res.data.message
    await authStore.fetchMe()
    mhVerifyCode.value = ''
  } catch (e) {
    mhVerifyError.value = e.response?.data?.detail || '验证失败'
  } finally {
    mhVerifyLoading.value = false
  }
}

async function handleMirahezeUnbind() {
  if (!confirm('确定要解除Miraheze账户绑定吗？')) return
  try {
    await axios.delete(
      'http://127.0.0.1:8000/api/v1/users/miraheze/unbind',
      { headers: { Authorization: `Bearer ${getToken()}` } }
    )
    await authStore.fetchMe()
  } catch {
    alert('解绑失败')
  }
}

function cancelMirahezeBind() {
  mhVerifyCode.value = ''
  mhVerifyPage.value = ''
  mhVerifyUrl.value = ''
  mhBindError.value = ''
}

async function copyMhCode() {
  await navigator.clipboard.writeText(mhVerifyCode.value)
  mhCodeCopied.value = true
  setTimeout(() => mhCodeCopied.value = false, 2000)
}
</script>

<style scoped>
.profile-page { max-width: 720px; margin: 0 auto; padding: 2rem 1rem; }

.card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 1.5rem;
}

.user-card { position: relative; }
.user-header { display: flex; gap: 1.5rem; align-items: center; }
.big-avatar { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; }
.big-avatar-placeholder {
  width: 72px; height: 72px; border-radius: 50%;
  background: #185897; color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; font-weight: bold; flex-shrink: 0;
}
.user-info h1 { font-size: 1.4rem; margin-bottom: 0.5rem; }
.user-email { color: #888; font-size: 0.85rem; margin-top: 0.3rem; }

.user-badges { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-weight: 500;
}
.role-0 { background: #f0f0f0; color: #666; }
.role-1 { background: #e8f4fd; color: #185897; }
.role-2 { background: #e8f8f0; color: #27ae60; }
.role-3 { background: #fdf3e8; color: #e67e22; }
.verified { background: #e8f8f0; color: #27ae60; }
.fandom { background: #e8f4fd; color: #185897; }
.miraheze { background: #FFFBD8; color: #e4c600; }

.btn-logout {
  position: absolute; top: 1.5rem; right: 1.5rem;
  padding: 0.4rem 1rem;
  background: #fee; color: #e74c3c;
  border: 1px solid #fcc; border-radius: 4px;
  cursor: pointer; font-size: 0.85rem;
}
.btn-logout:hover { background: #fdd; }

h2 { font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: #333; }

.bound-state { display: flex; justify-content: space-between; align-items: center; }
.bound-info { display: flex; gap: 1rem; align-items: center; }
.fandom-avatar { width: 48px; height: 48px; border-radius: 50%; }

.hint { color: #888; font-size: 0.88rem; margin-bottom: 1rem; }

.form-row { display: flex; gap: 0.8rem; }
.form-row input {
  flex: 1; padding: 0.6rem 0.9rem;
  border: 1px solid #ddd; border-radius: 4px;
  font-size: 0.9rem; outline: none;
}
.form-row input:focus { border-color: #185897; }

.steps { padding-left: 1.5rem; color: #444; font-size: 0.9rem; }
.steps li { margin-bottom: 1rem; line-height: 1.7; }
.link { color: #185897; word-break: break-all; }

.code-box {
  display: flex; align-items: center; gap: 0.8rem;
  background: #f5f7fa; border: 1px solid #e0e0e0;
  border-radius: 4px; padding: 0.6rem 1rem;
  font-family: monospace; font-size: 0.9rem;
  margin-top: 0.5rem; word-break: break-all;
}

/* .verify-step { } */
.verify-actions { display: flex; gap: 1rem; align-items: center; margin-top: 1rem; }

.btn-primary {
  padding: 0.6rem 1.2rem;
  background: #185897; color: white;
  border: none; border-radius: 4px;
  cursor: pointer; font-size: 0.9rem;
}
.btn-primary:hover { background: #134a7f; }
.btn-primary:disabled { background: #aaa; cursor: not-allowed; }

.btn-danger {
  padding: 0.4rem 1rem;
  background: #fee; color: #e74c3c;
  border: 1px solid #fcc; border-radius: 4px;
  cursor: pointer; font-size: 0.85rem;
}
.btn-danger:hover { background: #fdd; }

.btn-text { background: none; border: none; color: #888; cursor: pointer; font-size: 0.9rem; }
.btn-text:hover { color: #333; }

.copy-btn {
  padding: 0.2rem 0.6rem; font-size: 0.8rem;
  background: #185897; color: white;
  border: none; border-radius: 3px; cursor: pointer;
  white-space: nowrap; flex-shrink: 0;
}

.error { color: #e74c3c; font-size: 0.88rem; margin-top: 0.8rem; }
.success { color: #27ae60; font-size: 0.88rem; margin-top: 0.8rem; }

.author-link { margin-top: 1rem; }
.btn-author {
  display: inline-block;
  padding: 0.5rem 1.2rem;
  background: #185897;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9rem;
}
.btn-author:hover { background: #134a7f; }
</style>