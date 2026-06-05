<template>
  <div class="wiki-stats-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="site">

      <div class="site-header">
        <span class="platform-badge" :class="site.platform">
          {{ site.platform === 'fandom' ? 'Fandom' : 'Miraheze' }}
        </span>
        <h1>{{ site.name }}</h1>
        <p class="site-desc" v-if="site.description">{{ site.description }}</p>
        <a :href="site.base_url" target="_blank" class="site-link">访问维基 <i class="fa fa-arrow-right"></i></a>
      </div>

      <div class="stats-grid" v-if="stats">
        <div class="stat-card">
          <div class="stat-number">{{ stats.total_pages }}</div>
          <div class="stat-label">收录页面</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ formatNumber(stats.total_words) }}</div>
          <div class="stat-label">总字数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.total_authors }}</div>
          <div class="stat-label">创作者</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.total_revisions }}</div>
          <div class="stat-label">编辑次数</div>
        </div>
      </div>

      <div class="main-grid">
        <div class="section">
          <div class="section-header">
            <h2>最新页面</h2>
            <a :href="`/search?site=${siteId}`" class="more-link">查看更多 <i class="fa fa-arrow-right"></i></a>
          </div>
          <div v-if="pagesLoading" class="loading-sm">加载中...</div>
          <div v-else>
            <div class="page-item" v-for="page in pages" :key="page.id" @click="goToPage(page.id)">
              <div class="page-main">
                <div class="page-title">{{ page.title }}</div>
                <div class="page-meta">
                  <a :href="`/author/${page.author}`" class="author-link" @click.stop>{{ page.author || '未知' }}</a>
                  <span>{{ page.word_count }} 字</span>
                  <span>{{ formatDate(page.last_edited_at) }}</span>
                </div>
                <div class="page-cats">
                  <span class="cat-tag" v-for="cat in page.categories.slice(0,3)" :key="cat">{{ cat }}</span>
                </div>
              </div>
              <i class="fa fa-chevron-right more-arrow"></i>
            </div>
          </div>
          <div class="load-more" v-if="hasMore" @click="loadMore">加载更多</div>
        </div>

        <div class="section">
          <div class="section-header">
            <h2>创作者排名</h2>
            <a :href="`/rankings?site=${siteId}`" class="more-link">完整榜单 <i class="fa fa-arrow-right"></i></a>
          </div>
          <div class="author-item" v-for="(author, index) in topAuthors" :key="author.author">
            <span class="rank">{{ index + 1 }}</span>
            <a :href="`/author/${author.author}`" class="author-name">{{ author.author }}</a>
            <span class="author-count">{{ author.page_count }} 篇</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="error">站点不存在</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pageAPI, siteAPI } from '../api/index.js'

const route = useRoute()
const router = useRouter()
const siteId = route.params.siteId
const site = ref(null)
const stats = ref(null)
const pages = ref([])
const topAuthors = ref([])
const loading = ref(true)
const pagesLoading = ref(true)
const skip = ref(0)
const hasMore = ref(true)

function formatNumber(n) { return n ? n.toLocaleString('zh-CN') : '0' }
function formatDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '' }
function goToPage(id) { router.push(`/page/${id}`) }

async function loadPages() {
  pagesLoading.value = true
  try {
    const result = await pageAPI.list({ site_id: siteId, skip: skip.value, limit: 20 })
    pages.value.push(...result)
    hasMore.value = result.length === 20
    skip.value += result.length
  } finally { pagesLoading.value = false }
}

async function loadMore() { await loadPages() }

onMounted(async () => {
  try {
    const sites = await siteAPI.list()
    site.value = sites.find(s => s.site_id === siteId)
    if (!site.value) { loading.value = false; return }
    const [statsRes, authorsRes] = await Promise.all([pageAPI.stats(siteId), pageAPI.topAuthors(siteId, 10)])
    stats.value = statsRes
    topAuthors.value = authorsRes
    await loadPages()
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped>
.wiki-stats-page { max-width: 1100px; margin: 0 auto; padding: 60px 1.5rem; }

.site-header { text-align: center; margin-bottom: 48px; }
.platform-badge { display: inline-block; font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 4px; margin-bottom: 12px; }
.platform-badge.fandom { background: #e8f0fc; color: var(--color-primary); }
.platform-badge.miraheze { background: #e8f8f0; color: #27ae60; }
.site-header h1 { font-size: 28px; font-weight: 600; color: var(--color-ink); letter-spacing: -0.02em; margin-bottom: 8px; }
.site-desc { font-size: 17px; color: var(--color-muted); margin-bottom: 12px; }
.site-link { font-size: 14px; color: var(--color-primary); }
.site-link:hover { text-decoration: underline; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 48px; }
.stat-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: 24px; text-align: center;
}
.stat-number { font-size: 36px; font-weight: 600; color: var(--color-primary); }
.stat-label { font-size: 14px; color: var(--color-muted); margin-top: 8px; }

.main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 40px; }
.section {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: 24px;
}
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.section-header h2 { font-size: 21px; font-weight: 600; color: var(--color-ink); letter-spacing: -0.02em; }
.more-link { font-size: 14px; color: var(--color-primary); }

.page-item { display: flex; align-items: center; padding: 16px 0; border-bottom: 1px solid var(--color-hairline); cursor: pointer; }
.page-item:last-child { border-bottom: none; }
.page-main { flex: 1; min-width: 0; }
.page-title { font-size: 17px; font-weight: 500; color: var(--color-ink); margin-bottom: 4px; }
.page-meta { display: flex; gap: 12px; color: var(--color-muted); font-size: 14px; align-items: center; }
.author-link { color: var(--color-primary); }
.author-link:hover { text-decoration: underline; }
.page-cats { display: flex; gap: 4px; margin-top: 4px; }
.cat-tag { font-size: 12px; background: var(--color-parchment); padding: 1px 8px; border-radius: var(--radius-pill); color: var(--color-muted); }
.more-arrow { color: var(--color-muted); font-size: 14px; flex-shrink: 0; margin-left: 12px; }

.load-more { text-align: center; padding: 16px 0 0; color: var(--color-primary); cursor: pointer; font-size: 14px; }

.author-item { display: flex; align-items: center; padding: 14px 0; border-bottom: 1px solid var(--color-hairline); }
.author-item:last-child { border-bottom: none; }
.rank {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--color-parchment); color: var(--color-ink);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600; margin-right: 12px; flex-shrink: 0;
}
.author-name { flex: 1; color: var(--color-primary); font-size: 17px; }
.author-name:hover { text-decoration: underline; }
.author-count { color: var(--color-muted); font-size: 14px; }

.loading, .loading-sm, .error { text-align: center; padding: 40px 0; color: var(--color-muted); }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .main-grid { grid-template-columns: 1fr; }
}
</style>
