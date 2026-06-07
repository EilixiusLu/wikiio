<template>
  <div class="admin-page">
    <h1>后台管理</h1>

    <div class="stats-grid" v-if="stats">
      <div class="stat-card" v-for="(item, i) in statItems" :key="i">
        <div class="num">{{ item.value }}</div>
        <div class="label">{{ item.label }}</div>
      </div>
    </div>

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
        <TransitionGroup name="list" tag="div" v-else>
          <div
            v-for="(line, i) in logLines" :key="i"
            class="log-line"
            :class="getLogClass(line)"
          >{{ line }}</div>
        </TransitionGroup>
      </div>
      <div class="log-footer">
        <span class="log-count">
          共 {{ totalLines }} 行，显示最新 {{ logLines.length }} 行
        </span>
        <button class="btn-refresh" @click="loadLogs">刷新</button>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h2>接入管理</h2>
        <button class="btn-add" @click="showAddForm = !showAddForm">
          {{ showAddForm ? '收起' : '+ 接入新维基' }}
        </button>
      </div>

      <Transition name="fade-up">
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
              <label>RatePage</label>
              <select v-model="newSite.has_ratepage">
                <option :value="false">否</option>
                <option :value="true">是</option>
              </select>
            </div>
            <div class="form-group">
              <label>维基 URL *</label>
              <input v-model="newSite.base_url" placeholder="https://scpfoundation.fandom.com/zh" />
            </div>
            <div class="form-group">
              <label>维基名称 *</label>
              <input v-model="newSite.name" placeholder="SCP基金会中文Wiki" />
            </div>
            <div class="form-group">
              <label>维基编号 *</label>
              <input v-model="newSite.site_id" placeholder="scp-zh" />
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
      </Transition>

      <table class="site-table">
        <thead>
          <tr>
            <th>维基名称</th><th>site_id</th><th>平台</th>
            <th>语言</th><th>RatePage</th><th>状态</th><th>操作</th>
          </tr>
        </thead>
        <TransitionGroup name="list" tag="tbody">
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
              <button
                v-if="site.status === 'approved'"
                class="btn-action btn-crawl"
                @click="crawlSite(site.site_id, false)"
              >增量</button>
              <button
                v-if="site.status === 'approved'"
                class="btn-action btn-crawl-full"
                @click="crawlSite(site.site_id, true)"
              >全量</button>
              <button
                v-if="site.status === 'pending'"
                class="btn-action btn-approve"
                @click="approveSite(site.site_id)"
              >通过</button>
              <button
                v-if="site.status === 'pending'"
                class="btn-action btn-reject"
                @click="rejectSite(site.site_id)"
              >拒绝</button>
              <button
                v-if="site.status === 'approved'"
                class="btn-action btn-reject"
                @click="deleteSite(site.site_id)"
              >删除</button>
              <button
                v-if="site.status === 'rejected'"
                class="btn-action btn-approve"
                @click="approveSite(site.site_id)"
              >重新通过</button>
            </td>
          </tr>
        </TransitionGroup>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { adminAPI, siteAPI } from '../api/index.js'

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

const statItems = computed(() => {
  if (!stats.value) return []
  return [
    { label: '注册用户', value: stats.value.total_users },
    { label: '已验证用户', value: stats.value.verified_users },
    { label: '收录页面', value: stats.value.total_pages },
    { label: '评分总数', value: stats.value.total_ratings },
    { label: '接入站点', value: stats.value.total_sites },
  ]
})

function getLogClass(line) {
  if (line.includes('[ERROR]')) return 'log-error'
  if (line.includes('[WARNING]') || line.includes('status=4') || line.includes('status=5'))
    return 'log-warning'
  return 'log-info'
}
function statusLabel(s) {
  return { pending: '待审核', approved: '已接入', rejected: '已拒绝' }[s] || s
}

async function loadStats() { stats.value = await adminAPI.stats() }
async function loadLogs() {
  logLoading.value = true
  try {
    const r = await adminAPI.logs(logType.value, 200)
    logLines.value = r.lines
    totalLines.value = r.total_lines || 0
    await nextTick()
    if (logBox.value) logBox.value.scrollTop = logBox.value.scrollHeight
  } finally { logLoading.value = false }
}
async function switchLog(type) { logType.value = type; await loadLogs() }
async function loadSites() { sites.value = await adminAPI.sites() }
async function approveSite(siteId) { await adminAPI.approveSite(siteId); await loadSites() }
async function rejectSite(siteId) { await adminAPI.rejectSite(siteId); await loadSites() }

onMounted(async () => {
  await Promise.all([loadStats(), loadLogs(), loadSites()])
})

const showAddForm = ref(false)
const addLoading = ref(false)
const addError = ref('')
const addSuccess = ref('')
const newSite = ref({
  platform: 'fandom', has_ratepage: false,
  base_url: '', name: '', site_id: '', language: 'zh', description: '',
})

async function addSite() {
  addError.value = ''
  addSuccess.value = ''
  if (!newSite.value.name || !newSite.value.site_id || !newSite.value.base_url) {
    addError.value = '请填写所有必填项'; return
  }
  addLoading.value = true
  try {
    await siteAPI.create({
      name: newSite.value.name, site_id: newSite.value.site_id,
      base_url: newSite.value.base_url, platform: newSite.value.platform,
      has_ratepage: newSite.value.has_ratepage, language: newSite.value.language,
      description: newSite.value.description,
    })
    addSuccess.value = `站点 ${newSite.value.name} 接入成功！`
    newSite.value = {
      platform: 'fandom', has_ratepage: false,
      base_url: '', name: '', site_id: '', language: 'zh', description: '',
    }
    await loadSites()
    setTimeout(() => { addSuccess.value = ''; showAddForm.value = false }, 2000)
  } catch (e) { addError.value = e.detail || '接入失败' }
  finally { addLoading.value = false }
}

async function crawlSite(siteId, full = false) {
  const type = full ? '全量爬取' : '增量更新'
  if (!confirm(`确定要对站点 ${siteId} 执行${type}吗？`)) return
  await siteAPI.triggerCrawl(siteId, full)
  alert(`${type}任务已提交！`)
}

async function deleteSite(siteId) {
  if (!confirm(`确定要删除站点 ${siteId} 吗？`)) return
  await siteAPI.delete(siteId)
  await loadSites()
}
</script>

<style scoped>
.admin-page { max-width: 1100px; margin: 0 auto; padding: var(--space-16) var(--space-6); }
.admin-page h1 {
  font-size: var(--text-2xl); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
  margin-bottom: var(--space-8);
}

.stats-grid {
  display: grid; grid-template-columns: repeat(5, 1fr);
  gap: var(--space-6); margin-bottom: var(--space-8);
}
.stat-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6); text-align: center;
  transition: background-color var(--duration-base) var(--ease-smooth),
              border-color var(--duration-base) var(--ease-smooth);
}
.stat-card:hover { border-color: var(--color-primary); background-color: var(--color-parchment); }
.num { font-size: var(--text-3xl); font-weight: 600; color: var(--color-primary); }
.label { font-size: var(--text-sm); color: var(--color-muted); margin-top: var(--space-2); }

.card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6); margin-bottom: var(--space-6);
}
.card-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: var(--space-4);
}
.card h2 {
  font-size: var(--text-lg); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
}

.log-tabs { display: flex; gap: var(--space-1); }
.log-tabs button {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-hairline);
  border-radius: 6px; background: var(--color-canvas);
  color: var(--color-muted); cursor: pointer;
  font-size: var(--text-sm); font-family: inherit;
  transition: background-color var(--duration-fast) var(--ease-smooth),
              color var(--duration-fast) var(--ease-smooth),
              border-color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.log-tabs button:hover { border-color: var(--color-primary); color: var(--color-primary); }
.log-tabs button.active {
  background: var(--color-primary); color: #fff;
  border-color: var(--color-primary);
}
.log-tabs button:active { transform: scale(0.96); }

.log-box {
  background: #1d1d1f; border-radius: 12px;
  padding: var(--space-5); height: 400px;
  overflow-y: auto; font-family: SF Mono, Monaco, monospace;
  font-size: 13px; line-height: 1.6;
}
.log-line { white-space: pre-wrap; word-break: break-all; }
.log-info { color: #a8c7fa; }
.log-warning { color: #ffd97d; }
.log-error { color: #ff8a80; }
.log-loading, .log-empty { color: #666; text-align: center; padding: var(--space-8); }

.log-footer {
  display: flex; justify-content: space-between;
  align-items: center; margin-top: var(--space-3);
}
.log-count { font-size: var(--text-sm); color: var(--color-muted); }

.btn-refresh {
  padding: var(--space-1) var(--space-4);
  background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-pill);
  cursor: pointer; font-size: var(--text-sm); font-family: inherit;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-refresh:hover { opacity: 0.9; }
.btn-refresh:active { transform: scale(0.96); }

.site-table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
.site-table th {
  text-align: left; padding: var(--space-3) var(--space-2);
  border-bottom: 1px solid var(--color-hairline);
  color: var(--color-muted); font-weight: 500;
  font-size: var(--text-xs); text-transform: uppercase;
}
.site-table td { padding: var(--space-3) var(--space-2); border-bottom: 1px solid var(--color-hairline); }
.site-table code {
  background: var(--color-parchment);
  padding: var(--space-1) var(--space-2);
  border-radius: 4px; font-size: 13px;
}

.status-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill);
  font-size: var(--text-xs); font-weight: 500;
}
.status-badge.pending { background: #fff3cd; color: #856404; }
.status-badge.approved { background: #d1fae5; color: #065f46; }
.status-badge.rejected { background: #fee2e2; color: #991b1b; }

.actions { display: flex; gap: var(--space-1); }
.btn-action {
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--color-hairline); border-radius: 6px;
  cursor: pointer; font-size: 13px; font-family: inherit;
  background: var(--color-canvas);
  transition: background-color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-action:hover { background: var(--color-parchment); }
.btn-action:active { transform: scale(0.96); }
.btn-approve { color: #27ae60; border-color: #27ae60; }
.btn-approve:hover { background: #d1fae5; }
.btn-reject { color: var(--color-danger); border-color: var(--color-danger); }
.btn-reject:hover { background: #fee2e2; }
.btn-crawl { color: var(--color-primary); border-color: var(--color-primary); }
.btn-crawl:hover { background: #e8f0fc; }
.btn-crawl-full { color: #856404; border-color: #856404; }
.btn-crawl-full:hover { background: #fff3cd; }

.btn-add {
  padding: var(--space-2) var(--space-5);
  background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-pill);
  cursor: pointer; font-size: var(--text-sm); font-family: inherit;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-add:hover { opacity: 0.9; }
.btn-add:active { transform: scale(0.96); }

.add-form {
  background: var(--color-parchment); border-radius: 12px;
  padding: var(--space-6); margin-bottom: var(--space-5);
}
.form-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: var(--space-4); margin-bottom: var(--space-5);
}
.form-group { display: flex; flex-direction: column; gap: var(--space-1); }
.form-group.full { grid-column: span 2; }
.form-group label { font-size: var(--text-sm); color: var(--color-ink); font-weight: 500; }
.form-group input,
.form-group select {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-sm);
  font-size: var(--text-base); font-family: inherit;
  color: var(--color-ink); outline: none;
  background: var(--color-canvas);
  transition: border-color var(--duration-base) var(--ease-smooth);
}
.form-group input:focus,
.form-group select:focus { border-color: var(--color-primary); }

.form-actions { display: flex; align-items: center; gap: var(--space-4); }
.btn-submit {
  padding: var(--space-2) var(--space-3);
  background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-pill);
  cursor: pointer; font-size: var(--text-base); font-family: inherit;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-submit:hover { opacity: 0.9; }
.btn-submit:active { transform: scale(0.96); }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

.form-error { color: var(--color-danger); font-size: var(--text-sm); }
.form-success { color: var(--color-success); font-size: var(--text-sm); }

.platform-badge {
  font-size: var(--text-xs); font-weight: 600;
  padding: var(--space-1) var(--space-2); border-radius: 4px;
}
.platform-badge.fandom { background: #e8f0fc; color: var(--color-primary); }
.platform-badge.miraheze { background: #e8f8f0; color: #27ae60; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }
  .form-grid { grid-template-columns: 1fr; }
  .form-group.full { grid-column: span 1; }
}
</style>
