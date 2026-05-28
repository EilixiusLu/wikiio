<template>
  <div class="wiki-stats-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="site">

      <!-- 站点头部 -->
      <div class="site-header">
        <div class="site-info">
          <div class="platform-badge" :class="site.platform">
            {{ site.platform === 'fandom' ? 'Fandom' : 'Miraheze' }}
          </div>
          <h1>{{ site.name }}</h1>
          <p class="site-desc" v-if="site.description">{{ site.description }}</p>
          <a :href="site.base_url" target="_blank" class="site-link">访问维基 →</a>
        </div>
      </div>

      <!-- 数据统计 -->
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
        <!-- 最新页面 -->
        <div class="section">
          <div class="section-header">
            <h2>最新页面</h2>
            <a :href="`/search?site=${siteId}`" class="more-link">查看更多</a>
          </div>
          <div v-if="pagesLoading" class="loading-sm">加载中...</div>
          <div v-else>
            <div class="page-item" v-for="page in pages" :key="page.id" @click="goToPage(page.id)">
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
          </div>
          <div class="load-more" v-if="hasMore" @click="loadMore">加载更多</div>
        </div>

        <!-- 创作者排名 -->
        <div class="section">
          <div class="section-header">
            <h2>创作者排名</h2>
            <a :href="`/rankings?site=${siteId}`" class="more-link">完整榜单</a>
          </div>
          <div class="author-item" v-for="(author, index) in topAuthors" :key="author.author">
            <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
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

function formatNumber(n) {
  return n ? n.toLocaleString('zh-CN') : '0'
}
function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('zh-CN') : ''
}
function goToPage(id) {
  router.push(`/page/${id}`)
}

async function loadPages() {
  pagesLoading.value = true
  try {
    const result = await pageAPI.list({ site_id: siteId, skip: skip.value, limit: 20 })
    pages.value.push(...result)
    hasMore.value = result.length === 20
    skip.value += result.length
  } finally {
    pagesLoading.value = false
  }
}

async function loadMore() {
  await loadPages()
}

onMounted(async () => {
  try {
    const sites = await siteAPI.list()
    site.value = sites.find(s => s.site_id === siteId)
    if (!site.value) { loading.value = false; return }

    const [statsRes, authorsRes] = await Promise.all([
      pageAPI.stats(siteId),
      pageAPI.topAuthors(siteId, 10),
    ])
    stats.value = statsRes
    topAuthors.value = authorsRes
    await loadPages()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.wiki-stats-page { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }
.loading { text-align: center; padding: 3rem; color: #888; }
.loading-sm { text-align: center; padding: 1rem; color: #888; }
.error { text-align: center; padding: 3rem; color: #e74c3c; }

.site-header {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.platform-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.platform-badge.fandom { background: #e8f0fc; color: #185897; }
.platform-badge.miraheze { background: #e8f8f0; color: #27ae60; }
h1 { font-size: 1.6rem; font-weight: 700; margin-bottom: 0.4rem; }
.site-desc { color: #888; font-size: 0.9rem; margin-bottom: 0.6rem; }
.site-link { color: #185897; font-size: 0.88rem; text-decoration: none; }
.site-link:hover { text-decoration: underline; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
.stat-number { font-size: 1.8rem; font-weight: bold; color: #185897; }
.stat-label { color: #888; font-size: 0.82rem; margin-top: 0.3rem; }

.main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }
.section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h2 { font-size: 1rem; font-weight: 600; color: #333; }
.more-link { font-size: 0.82rem; color: #185897; text-decoration: none; }

.page-item { padding: 0.8rem 0; border-bottom: 1px solid #f0f0f0; cursor: pointer; }
.page-item:last-child { border-bottom: none; }
.page-item:hover { background: #f9f9f9; margin: 0 -1rem; padding: 0.8rem 1rem; }
.page-title { font-weight: 500; color: #1a1a2e; margin-bottom: 0.3rem; }
.page-meta { display: flex; gap: 0.8rem; color: #888; font-size: 0.82rem; margin-bottom: 0.3rem; align-items: center; }
.author-link { color: #185897; text-decoration: none; }
.author-link:hover { text-decoration: underline; }
.page-cats { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.cat-tag { font-size: 0.72rem; background: #f0f0f0; padding: 0.1rem 0.4rem; border-radius: 8px; color: #666; }

.load-more { text-align: center; padding: 0.8rem; color: #185897; cursor: pointer; font-size: 0.88rem; }

.author-item { display: flex; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid #f0f0f0; }
.author-item:last-child { border-bottom: none; }
.rank {
  width: 24px; height: 24px; border-radius: 50%;
  background: #ddd; color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.72rem; font-weight: bold; margin-right: 0.8rem; flex-shrink: 0;
}
.rank-1 { background: #f5a623; }
.rank-2 { background: #9b9b9b; }
.rank-3 { background: #c47e3a; }
.author-name { flex: 1; color: #185897; text-decoration: none; font-size: 0.9rem; }
.author-name:hover { text-decoration: underline; }
.author-count { color: #888; font-size: 0.82rem; }
</style>