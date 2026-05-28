<template>
  <div class="admin-page">
    <h1>后台管理</h1>

    <!-- 系统统计 -->
    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <div class="num">{{ stats.total_users }}</div>
        <div class="label">注册用户</div>
      </div>
      <div class="stat-card">
        <div class="num">{{ stats.verified_users }}</div>
        <div class="label">已验证用户</div>
      </div>
      <div class="stat-card">
        <div class="num">{{ stats.total_pages }}</div>
        <div class="label">收录页面</div>
      </div>
      <div class="stat-card">
        <div class="num">{{ stats.total_ratings }}</div>
        <div class="label">评分总数</div>
      </div>
      <div class="stat-card">
        <div class="num">{{ stats.total_sites }}</div>
        <div class="label">接入站点</div>
      </div>
    </div>

    <!-- 日志查看器 -->
    <div class="card">
      <div class="card-header">
        <h2>日志查看</h2>
        <div class="log-tabs">
          <button
            v-for="t in logTypes" :key="t.key"
            :class="{ active: logType === t.key }"
            @click="switchLog(t.key)"
          >{{ t.label }}</button>
        </div>
      </div>
      <div class="log-box" ref="logBox">
        <div v-if="logLoading" class="log-loading">加载中...</div>
        <div v-else-if="logLines.length === 0" class="log-empty">暂无日志</div>
        <div v-else>
          <div
            v-for="(line, i) in logLines"
            :key="i"
            class="log-line"
            :class="getLogClass(line)"
          >{{ line }}</div>
        </div>
      </div>
      <div class="log-footer">
        <span class="log-count">共 {{ totalLines }} 行，显示最新 {{ logLines.length }} 行</span>
        <button class="btn-refresh" @click="loadLogs">刷新</button>
      </div>
    </div>

    <!-- 站点管理 -->
    <!-- 接入管理 -->
    <div class="card">
      <div class="card-header">
        <h2>接入管理</h2>
        <button class="btn-add" @click="showAddForm = !showAddForm">
          {{ showAddForm ? '收起' : '+ 接入新维基' }}
        </button>
      </div>

      <!-- 新增表单 -->
      <div class="add-form" v-if="showAddForm">
        <div class="form-grid">
          <div class="form-group">
            <label>平台 *</label>
            <select v-model="newSite.platform">
              <option value="fandom">Fandom</option>
              <option value="miraheze">Miraheze</option>
            </select>
          </div>
          <div class="form-group">
            <label>是否启用 RatePage 扩展</label>
            <select v-model="newSite.has_ratepage">
              <option :value="false">否</option>
              <option :value="true">是</option>
            </select>
          </div>
          <div class="form-group">
            <label>维基 URL *</label>
            <input v-model="newSite.base_url" placeholder="如 https://scpfoundation.fandom.com/zh" />
          </div>
          <div class="form-group">
            <label>维基名称 *</label>
            <input v-model="newSite.name" placeholder="如 SCP基金会中文Wiki" />
          </div>
          <div class="form-group">
            <label>维基编号 (site_id) *</label>
            <input v-model="newSite.site_id" placeholder="如 scp-zh" />
          </div>
          <div class="form-group">
            <label>语言</label>
            <input v-model="newSite.language" placeholder="zh" />
          </div>
          <div class="form-group full">
            <label>简介</label>
            <input v-model="newSite.description" placeholder="维基简介（选填）" />
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-submit" @click="addSite" :disabled="addLoading">
            {{ addLoading ? '提交中...' : '确认接入' }}
          </button>
          <span class="form-error" v-if="addError">{{ addError }}</span>
          <span class="form-success" v-if="addSuccess">{{ addSuccess }}</span>
        </div>
      </div>

      <!-- 站点列表 -->
      <table class="site-table">
        <thead>
          <tr>
            <th>维基名称</th>
            <th>site_id</th>
            <th>平台</th>
            <th>语言</th>
            <th>RatePage</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="site in sites" :key="site.site_id">
            <td>{{ site.name }}</td>
            <td><code>{{ site.site_id }}</code></td>
            <td>
              <span class="platform-badge" :class="site.platform">
                {{ site.platform === 'fandom' ? 'Fandom' : 'Miraheze' }}
              </span>
            </td>
            <td>{{ site.language }}</td>
            <td>{{ site.has_ratepage ? '✅' : '—' }}</td>
            <td>
              <span class="status-badge" :class="site.status">
                {{ statusLabel(site.status) }}
              </span>
            </td>
            <td class="actions">
              <button class="btn-crawl" @click="crawlSite(site.site_id)">爬取</button>
              <button class="btn-reject" @click="deleteSite(site.site_id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

const stats = ref(null)
const logType = ref('access')
const logLines = ref([])
const totalLines = ref(0)
const logLoading = ref(false)
const logBox = ref(null)
const sites = ref([])

const logTypes = [
  { key: 'access', label: '访问日志' },
  { key: 'crawler', label: '爬虫日志' },
  { key: 'rating', label: '评分日志' },
  { key: 'error', label: '错误日志' },
]

function getToken() {
  return localStorage.getItem('access_token')
}

function headers() {
  return { Authorization: `Bearer ${getToken()}` }
}

function getLogClass(line) {
  if (line.includes('[ERROR]')) return 'log-error'
  if (line.includes('[WARNING]')) return 'log-warning'
  if (line.includes('status=4') || line.includes('status=5')) return 'log-warning'
  return 'log-info'
}

function statusLabel(s) {
  return { pending: '待审核', approved: '已接入', rejected: '已拒绝' }[s] || s
}

async function loadStats() {
  const res = await axios.get('http://127.0.0.1:8000/api/v1/admin/stats', { headers: headers() })
  stats.value = res.data
}

async function loadLogs() {
  logLoading.value = true
  try {
    const res = await axios.get(
      `http://127.0.0.1:8000/api/v1/admin/logs/${logType.value}?lines=200`,
      { headers: headers() }
    )
    logLines.value = res.data.lines
    totalLines.value = res.data.total_lines || 0
    await nextTick()
    if (logBox.value) {
      logBox.value.scrollTop = logBox.value.scrollHeight
    }
  } finally {
    logLoading.value = false
  }
}

async function switchLog(type) {
  logType.value = type
  await loadLogs()
}

async function loadSites() {
  const res = await axios.get('http://127.0.0.1:8000/api/v1/sites/', { headers: headers() })
  sites.value = res.data
}

async function approveSite(siteId) {
  await axios.post(`http://127.0.0.1:8000/api/v1/admin/sites/${siteId}/approve`, {}, { headers: headers() })
  await loadSites()
}

async function rejectSite(siteId) {
  await axios.post(`http://127.0.0.1:8000/api/v1/admin/sites/${siteId}/reject`, {}, { headers: headers() })
  await loadSites()
}

onMounted(async () => {
  await Promise.all([loadStats(), loadLogs(), loadSites()])
})

const showAddForm = ref(false)
const addLoading = ref(false)
const addError = ref('')
const addSuccess = ref('')
const newSite = ref({
  platform: 'fandom',
  has_ratepage: false,
  base_url: '',
  name: '',
  site_id: '',
  language: 'zh',
  description: '',
})

async function addSite() {
  addError.value = ''
  addSuccess.value = ''
  if (!newSite.value.name || !newSite.value.site_id || !newSite.value.base_url) {
    addError.value = '请填写所有必填项'
    return
  }
  addLoading.value = true
  try {
    const params = new URLSearchParams({
      name: newSite.value.name,
      site_id: newSite.value.site_id,
      base_url: newSite.value.base_url,
      platform: newSite.value.platform,
      has_ratepage: newSite.value.has_ratepage,
      language: newSite.value.language,
      description: newSite.value.description,
    })
    await axios.post(
      `http://127.0.0.1:8000/api/v1/sites/?${params}`,
      {},
      { headers: headers() }
    )
    addSuccess.value = `站点 ${newSite.value.name} 接入成功！`
    newSite.value = { platform: 'fandom', has_ratepage: false, base_url: '', name: '', site_id: '', language: 'zh', description: '' }
    await loadSites()
    setTimeout(() => { addSuccess.value = ''; showAddForm.value = false }, 2000)
  } catch (e) {
    addError.value = e.response?.data?.detail || '接入失败'
  } finally {
    addLoading.value = false
  }
}

async function crawlSite(siteId) {
  if (!confirm(`确定要爬取站点 ${siteId} 吗？`)) return
  await axios.post(`http://127.0.0.1:8000/api/v1/sites/${siteId}/crawl`, {}, { headers: headers() })
  alert('爬取任务已启动！')
}

async function deleteSite(siteId) {
  if (!confirm(`确定要删除站点 ${siteId} 吗？此操作不可恢复！`)) return
  await axios.delete(`http://127.0.0.1:8000/api/v1/sites/${siteId}`, { headers: headers() })
  await loadSites()
}
</script>

<style scoped>
.admin-page { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }
h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.2rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.num { font-size: 1.8rem; font-weight: bold; color: #185897; }
.label { color: #888; font-size: 0.82rem; margin-top: 0.3rem; }

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 1.5rem;
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h2 { font-size: 1rem; font-weight: 600; color: #333; margin-bottom: 1rem; }

.log-tabs { display: flex; gap: 0.4rem; }
.log-tabs button {
  padding: 0.3rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #666;
  cursor: pointer;
  font-size: 0.82rem;
}
.log-tabs button.active { background: #185897; color: white; border-color: #185897; }

.log-box {
  background: #1a1a2e;
  border-radius: 6px;
  padding: 1rem;
  height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.78rem;
  line-height: 1.6;
}
.log-line { padding: 0.1rem 0; white-space: pre-wrap; word-break: break-all; }
.log-info { color: #a8c7fa; }
.log-warning { color: #ffd97d; }
.log-error { color: #ff8a80; }
.log-loading, .log-empty { color: #666; text-align: center; padding: 2rem; }

.log-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.8rem;
}
.log-count { font-size: 0.82rem; color: #888; }
.btn-refresh {
  padding: 0.3rem 0.8rem;
  background: #185897;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.82rem;
}

.site-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.site-table th { text-align: left; padding: 0.6rem; border-bottom: 2px solid #f0f0f0; color: #888; font-weight: 500; }
.site-table td { padding: 0.7rem 0.6rem; border-bottom: 1px solid #f5f5f5; }
.site-table code { background: #f5f5f5; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 0.82rem; }

.status-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 500;
}
.status-badge.pending { background: #fff3cd; color: #856404; }
.status-badge.approved { background: #d1fae5; color: #065f46; }
.status-badge.rejected { background: #fee2e2; color: #991b1b; }

.actions { display: flex; gap: 0.4rem; }
.btn-approve {
  padding: 0.2rem 0.6rem;
  background: #d1fae5; color: #065f46;
  border: none; border-radius: 3px; cursor: pointer; font-size: 0.8rem;
}
.btn-reject {
  padding: 0.2rem 0.6rem;
  background: #fee2e2; color: #991b1b;
  border: none; border-radius: 3px; cursor: pointer; font-size: 0.8rem;
}

.btn-add {
  padding: 0.4rem 1rem;
  background: #185897; color: white;
  border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem;
}
.add-form {
  background: #f9f9f9; border-radius: 8px;
  padding: 1.2rem; margin-bottom: 1.2rem;
}
.form-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 0.8rem; margin-bottom: 1rem;
}
.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
.form-group.full { grid-column: span 2; }
.form-group label { font-size: 0.82rem; color: #555; font-weight: 500; }
.form-group input, .form-group select {
  padding: 0.5rem 0.8rem;
  border: 1px solid #ddd; border-radius: 4px;
  font-size: 0.88rem; outline: none;
}
.form-group input:focus, .form-group select:focus { border-color: #185897; }
.form-actions { display: flex; align-items: center; gap: 1rem; }
.btn-submit {
  padding: 0.5rem 1.2rem;
  background: #185897; color: white;
  border: none; border-radius: 4px; cursor: pointer;
}
.btn-submit:disabled { background: #aaa; cursor: not-allowed; }
.form-error { color: #e74c3c; font-size: 0.85rem; }
.form-success { color: #27ae60; font-size: 0.85rem; }
.btn-crawl {
  padding: 0.2rem 0.6rem;
  background: #e8f0fc; color: #185897;
  border: none; border-radius: 3px; cursor: pointer; font-size: 0.8rem;
}
.platform-badge {
  font-size: 0.75rem; font-weight: 600;
  padding: 0.2rem 0.5rem; border-radius: 3px;
}
.platform-badge.fandom { background: #e8f0fc; color: #185897; }
.platform-badge.miraheze { background: #e8f8f0; color: #27ae60; }
</style>