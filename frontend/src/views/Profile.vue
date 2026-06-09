<template>
  <div class="profile-page">
    <div class="content" v-if="authStore.user">
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
              <span class="badge verified" v-if="authStore.user.is_email_verified">
                <i class="fa fa-envelope-o"></i> 邮箱已验证
              </span>
              <span class="badge fandom" v-if="authStore.user.is_fandom_verified">
                <i class="fa fa-globe"></i> Fandom: {{ authStore.user.fandom_username }}
              </span>
              <span class="badge miraheze" v-if="authStore.user.is_miraheze_verified">
                <i class="fa fa-globe"></i> Miraheze: {{ authStore.user.miraheze_username }}
              </span>
            </div>
            <p class="user-email">{{ authStore.user.email }}</p>
          </div>
          <button class="btn-logout" @click="handleLogout">退出登录</button>
        </div>
        <div class="author-link" v-if="authStore.user.is_fandom_verified">
          <a :href="`/author/${authStore.user.fandom_username}`" class="btn-author">
            查看我的作者页 <i class="fa fa-arrow-right"></i>
          </a>
        </div>
      </div>

      <div class="bindings-grid">
        <div class="card">
          <h2><i class="fa fa-globe"></i> Fandom 账户绑定</h2>
          <div v-if="authStore.user.is_fandom_verified" class="bound-state">
            <div class="bound-info">
              <img
                v-if="authStore.user.fandom_avatar_url"
                :src="authStore.user.fandom_avatar_url"
                class="fandom-avatar"
              />
              <div>
                <p class="bound-name">{{ authStore.user.fandom_username }}</p>
                <p class="hint">已成功绑定</p>
              </div>
            </div>
            <button class="btn-danger" @click="handleUnbind">解除绑定</button>
          </div>
          <div v-else-if="!verifyCode">
            <p class="hint">绑定后可评分，头像同步为 Fandom 头像</p>
            <div class="form-row">
              <input v-model="fandomUsername" placeholder="输入你的 Fandom 用户名" />
              <button
                class="btn-primary"
                @click="startBind"
                :disabled="bindLoading"
              >{{ bindLoading ? '处理中...' : '开始绑定' }}</button>
            </div>
            <div class="error" v-if="bindError">{{ bindError }}</div>
          </div>
          <div v-else class="verify-step">
            <p class="hint">请完成以下验证：</p>
            <ol class="steps">
              <li>前往 <a :href="verifyUrl" target="_blank" class="link">{{ verifyPage }}</a></li>
              <li>编辑页面，将验证码填入内容并保存：
                <div class="code-box">
                  {{ verifyCode }}
                  <button class="copy-btn" @click="copyCode">
                    {{ codeCopied ? '已复制' : '复制' }}
                  </button>
                </div>
              </li>
              <li>完成后点击验证</li>
            </ol>
            <div class="verify-actions">
              <button
                class="btn-primary"
                @click="doVerify"
                :disabled="verifyLoading"
              >{{ verifyLoading ? '验证中...' : '我已填写，立即验证' }}</button>
              <button class="btn-text" @click="cancelBind">取消</button>
            </div>
            <div class="error" v-if="verifyError">{{ verifyError }}</div>
            <div class="success" v-if="verifySuccess">{{ verifySuccess }}</div>
          </div>
        </div>

        <div class="card">
          <h2><i class="fa fa-globe"></i> Miraheze 账户绑定</h2>
          <div v-if="authStore.user.is_miraheze_verified" class="bound-state">
            <div class="bound-info">
              <div class="mh-icon">M</div>
              <div>
                <p class="bound-name">{{ authStore.user.miraheze_username }}</p>
                <p class="hint">已成功绑定</p>
              </div>
            </div>
            <button class="btn-danger" @click="handleMirahezeUnbind">解除绑定</button>
          </div>
          <div v-else-if="!mhVerifyCode">
            <p class="hint">绑定后可以对 Miraheze 维基上的页面评分</p>
            <div class="form-row">
              <input v-model="mhUsername" placeholder="输入你的 Miraheze 用户名" />
              <button
                class="btn-primary"
                @click="startMirahezeBind"
                :disabled="mhBindLoading"
              >{{ mhBindLoading ? '处理中...' : '开始绑定' }}</button>
            </div>
            <div class="error" v-if="mhBindError">{{ mhBindError }}</div>
          </div>
          <div v-else class="verify-step">
            <p class="hint">请完成以下验证：</p>
            <ol class="steps">
              <li>前往 <a :href="mhVerifyUrl" target="_blank" class="link">{{ mhVerifyPage }}</a></li>
              <li>编辑页面，将验证码填入内容并保存：
                <div class="code-box">
                  {{ mhVerifyCode }}
                  <button class="copy-btn" @click="copyMhCode">
                    {{ mhCodeCopied ? '已复制' : '复制' }}
                  </button>
                </div>
              </li>
              <li>完成后点击验证</li>
            </ol>
            <div class="verify-actions">
              <button
                class="btn-primary"
                @click="doMirahezeVerify"
                :disabled="mhVerifyLoading"
              >{{ mhVerifyLoading ? '验证中...' : '我已填写，立即验证' }}</button>
              <button class="btn-text" @click="cancelMirahezeBind">取消</button>
            </div>
            <div class="error" v-if="mhVerifyError">{{ mhVerifyError }}</div>
            <div class="success" v-if="mhVerifySuccess">{{ mhVerifySuccess }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { userAPI } from '../api/index.js'

const router = useRouter()
const authStore = useAuthStore()

const roleLabel = computed(() => {
  const roles = ['普通用户', '已验证用户', '维基管理员', 'Wikiio管理员']
  return roles[authStore.user?.role || 0]
})
const roleBadgeClass = computed(() => {
  const classes = ['role-0', 'role-1', 'role-2', 'role-3']
  return classes[authStore.user?.role || 0]
})

// ---- Fandom bind ----
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

async function startBind() {
  if (!fandomUsername.value.trim()) return
  bindError.value = ''
  bindLoading.value = true
  try {
    const r = await userAPI.fandomBindStart(fandomUsername.value)
    verifyCode.value = r.verify_code
    verifyPage.value = r.target_page
    verifyUrl.value = r.target_url
  } catch (e) {
    bindError.value = e.detail || '发起绑定失败'
  } finally {
    bindLoading.value = false
  }
}

async function doVerify() {
  verifyError.value = ''
  verifySuccess.value = ''
  verifyLoading.value = true
  try {
    const r = await userAPI.fandomBindVerify()
    verifySuccess.value = r.message
    await authStore.fetchMe()
    verifyCode.value = ''
  } catch (e) {
    verifyError.value = e.detail || '验证失败'
  } finally {
    verifyLoading.value = false
  }
}

async function handleUnbind() {
  if (!confirm('确定要解除Fandom账户绑定吗？')) return
  try {
    await userAPI.fandomUnbind()
    await authStore.fetchMe()
  } catch { alert('解绑失败') }
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

// ---- Miraheze bind ----
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
    const r = await userAPI.mirahezeBindStart(mhUsername.value)
    mhVerifyCode.value = r.verify_code
    mhVerifyPage.value = r.target_page
    mhVerifyUrl.value = r.target_url
  } catch (e) {
    mhBindError.value = e.detail || '发起绑定失败'
  } finally {
    mhBindLoading.value = false
  }
}

async function doMirahezeVerify() {
  mhVerifyError.value = ''
  mhVerifySuccess.value = ''
  mhVerifyLoading.value = true
  try {
    const r = await userAPI.mirahezeBindVerify()
    mhVerifySuccess.value = r.message
    await authStore.fetchMe()
    mhVerifyCode.value = ''
  } catch (e) {
    mhVerifyError.value = e.detail || '验证失败'
  } finally {
    mhVerifyLoading.value = false
  }
}

async function handleMirahezeUnbind() {
  if (!confirm('确定要解除Miraheze账户绑定吗？')) return
  try {
    await userAPI.mirahezeUnbind()
    await authStore.fetchMe()
  } catch { alert('解绑失败') }
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
.profile-page {
  background: var(--color-parchment);
  min-height: 100vh;
  padding: var(--space-16) 0;
}
.content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

/* ── 绑定卡片双栏网格 ── */
.bindings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}
.bindings-grid .card {
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
}

.card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-8);
  margin-bottom: var(--space-6);
}

.user-header {
  display: flex;
  gap: var(--space-5);
  align-items: flex-start;
}
.big-avatar,
.big-avatar-placeholder {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  flex-shrink: 0;
}
.big-avatar { object-fit: cover; }
.big-avatar-placeholder {
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-3xl);
  font-weight: 600;
}
.user-info { flex: 1; }
.user-info h1 {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-ink);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-2);
}
.user-email {
  font-size: var(--text-sm);
  color: var(--color-muted);
  margin-top: var(--space-2);
}
.btn-logout {
  position: absolute;
  top: var(--space-8);
  right: var(--space-8);
  font-size: var(--text-sm);
  background: none;
  border: 1px solid var(--color-hairline);
  color: var(--color-muted);
  padding: var(--space-1) var(--space-4);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: inherit;
  transition: border-color var(--duration-fast) var(--ease-smooth),
              color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-logout:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
}
.btn-logout:active { transform: scale(0.96); }
.user-card { position: relative; }
.user-badges {
  display: flex;
  gap: var(--space-1);
  flex-wrap: wrap;
}
.badge {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill);
  font-weight: 500;
}
.role-0 { background: var(--color-parchment); color: var(--color-muted); }
.role-1 { background: #e8f4fd; color: var(--color-primary); }
.role-2 { background: #e8f8f0; color: #27ae60; }
.role-3 { background: #fdf3e8; color: #e67e22; }
.verified { background: #e8f8f0; color: #27ae60; }
.fandom { background: #e8f4fd; color: var(--color-primary); }
.miraheze { background: #FFFBD8; color: #c5a800; }

.author-link { margin-top: var(--space-4); }
.btn-author {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--color-primary);
  padding: var(--space-2) var(--space-5);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-pill);
  transition: background-color var(--duration-fast) var(--ease-smooth),
              color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-author:hover {
  background: var(--color-primary);
  color: #fff;
  text-decoration: none;
}
.btn-author:active { transform: scale(0.96); }

.card h2 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-ink);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-5);
}

.bound-state {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.bound-info {
  display: flex;
  gap: var(--space-4);
  align-items: center;
}
.bound-name {
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--color-ink);
}
.fandom-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
}
.mh-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-parchment);
  color: var(--color-ink);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 20px;
}

.btn-danger {
  font-size: var(--text-sm);
  background: none;
  border: 1px solid var(--color-danger);
  color: var(--color-danger);
  padding: var(--space-1) var(--space-4);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: inherit;
  transition: background-color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-danger:hover { background: #fee; }
.btn-danger:active { transform: scale(0.96); }

.hint {
  color: var(--color-muted);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}

.form-row {
  display: flex;
  gap: var(--space-3);
}
.form-row input {
  flex: 1;
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  font-family: inherit;
  color: var(--color-ink);
  outline: none;
  background: var(--color-canvas);
  transition: border-color var(--duration-base) var(--ease-smooth);
}
.form-row input:focus { border-color: var(--color-primary); }

.btn-primary {
  padding: var(--space-2) var(--space-6);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-pill);
  font-size: var(--text-base);
  cursor: pointer;
  font-family: inherit;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-primary:hover { opacity: 0.9; }
.btn-primary:active { transform: scale(0.96); }
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.steps {
  padding-left: var(--space-5);
  color: var(--color-ink);
  font-size: var(--text-sm);
  line-height: 1.7;
  margin-bottom: var(--space-4);
}
.steps li { margin-bottom: var(--space-2); }
.link { color: var(--color-primary); word-break: break-all; }

.code-box {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--color-parchment);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  font-family: SF Mono, monospace;
  font-size: var(--text-base);
  margin-top: var(--space-2);
  word-break: break-all;
}
.copy-btn {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-sm);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-pill);
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.copy-btn:hover { opacity: 0.9; }
.copy-btn:active { transform: scale(0.96); }

.verify-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  margin-top: var(--space-4);
}
.btn-text {
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  font-size: var(--text-sm);
  font-family: inherit;
}

.error {
  color: var(--color-danger);
  font-size: var(--text-sm);
  margin-top: var(--space-3);
}
.success {
  color: var(--color-success);
  font-size: var(--text-sm);
  margin-top: var(--space-3);
}

@media (max-width: 768px) {
  .bindings-grid {
    grid-template-columns: 1fr;
  }

  .user-header { flex-wrap: wrap; }
  .form-row { flex-wrap: wrap; }
}
</style>
