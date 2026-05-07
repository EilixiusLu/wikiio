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
    <div class="card">
      <h2>站点管理</h2>
      <table class="site-table">
        <thead>
          <tr>
            <th>站点名称</th>
            <th>site_id</th>
            <th>语言</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="site in sites" :key="site.site_id">
            <td>{{ site.name }}</td>
            <td><code>{{ site.site_id }}</code></td>
            <td>{{ site.language }}</td>
            <td>
              <span class="status-badge" :class="site.status">
                {{ statusLabel(site.status) }}
              </span>
            </td>
            <td class="actions">
              <button
                v-if="site.status === 'pending'"
                class="btn-approve"
                @click="approveSite(site.site_id)"
              >通过</button>
              <button
                v-if="site.status === 'pending'"
                class="btn-reject"
                @click="rejectSite(site.site_id)"
              >拒绝</button>
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
  const res = await axios.get('http://127.0.0.1:8000/api/v1/admin/sites', { headers: headers() })
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
</style>