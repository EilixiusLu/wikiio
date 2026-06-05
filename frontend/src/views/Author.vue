<template>
  <div class="author-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="stats">
      <div class="author-header">
        <div class="author-avatar-wrap">
          <img v-if="authorProfile?.avatar_url" :src="authorProfile.avatar_url" class="author-avatar-img" />
          <div v-else class="author-avatar">{{ authorName[0]?.toUpperCase() }}</div>
        </div>
        <div class="author-info">
          <h1>{{ authorName }}</h1>
          <div class="author-badges">
            <span class="badge">{{ stats.total_pages }} 篇文章</span>
            <span class="badge">{{ stats.total_words.toLocaleString() }} 字</span>
            <span class="badge" v-if="stats.total_ratings > 0">{{ stats.total_ratings }} 次评分</span>
          </div>
        </div>
      </div>

      <div class="sites-stats">
        <div class="site-card" v-for="site in stats.sites" :key="site.site_id"
             :class="{ active: selectedSite === site.site_id }"
             @click="selectSite(site.site_id)">
          <div class="site-name">{{ site.site_name }}</div>
          <div class="site-nums">
            <div class="site-num"><div class="num">{{ site.page_count }}</div><div class="num-label">篇</div></div>
            <div class="site-num"><div class="num">{{ site.total_words.toLocaleString() }}</div><div class="num-label">字</div></div>
            <div class="site-num" v-if="site.total_ratings > 0"><div class="num">{{ site.avg_rating.toFixed(1) }}</div><div class="num-label">均分</div></div>
          </div>
        </div>
      </div>

      <div class="pages-section">
        <div class="section-header">
          <h2>{{ selectedSiteName ? selectedSiteName + ' · ' : '全部站点 · ' }}{{ pagesData?.total || 0 }} 篇文章</h2>
          <button v-if="selectedSite" class="btn-all" @click="selectSite(null)">查看全部</button>
        </div>

        <div v-if="pagesLoading" class="loading">加载中...</div>
        <div v-else-if="pagesData?.pages?.length === 0" class="empty">暂无文章</div>
        <div v-else class="page-list">
          <div class="page-item" v-for="page in pagesData?.pages" :key="page.id" @click="goToPage(page.id)">
            <div class="page-main">
              <div class="page-title">{{ page.title }}</div>
              <div class="page-meta">
                <span class="site-badge">{{ getSiteName(page.site_id) }}</span>
                <span>{{ page.word_count }} 字</span>
                <span>{{ formatDate(page.last_edited_at) }}</span>
              </div>
              <div class="page-cats" v-if="page.categories.length">
                <span class="cat-tag" v-for="cat in page.categories.slice(0,3)" :key="cat">{{ cat }}</span>
              </div>
            </div>
            <div class="page-rating" :class="{ 'no-rating': page.rating_count === 0 }">
              <div class="rating-num">{{ page.rating_count > 0 ? page.rating_avg.toFixed(1) : '—' }}</div>
              <div class="rating-stars" v-if="page.rating_count > 0">
                <i v-for="i in 5" :key="i" class="fa fa-star star" :class="{ filled: i <= Math.round(page.rating_avg) }"></i>
              </div>
              <div class="rating-count">{{ page.rating_count > 0 ? page.rating_count + '人' : '暂无评分' }}</div>
            </div>
          </div>
        </div>

        <div class="pagination" v-if="(pagesData?.total || 0) > pageLimit">
          <button :disabled="pageSkip === 0" @click="prevPage">上一页</button>
          <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
          <button :disabled="pageSkip + pageLimit >= (pagesData?.total || 0)" @click="nextPage">下一页</button>
        </div>
      </div>
    </div>
    <div v-else class="error">找不到该作者</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pageAPI, siteAPI } from '../api/index.js'

const route = useRoute()
const router = useRouter()
const authorProfile = ref(null)
const authorName = computed(() => decodeURIComponent(route.params.author))
const stats = ref(null)
const pagesData = ref(null)
const loading = ref(true)
const pagesLoading = ref(false)
const selectedSite = ref(null)
const sitesMap = ref({})
const pageSkip = ref(0)
const pageLimit = 20

const selectedSiteName = computed(() => selectedSite.value ? sitesMap.value[selectedSite.value] || selectedSite.value : null)
const currentPage = computed(() => Math.floor(pageSkip.value / pageLimit) + 1)
const totalPages = computed(() => Math.ceil((pagesData.value?.total || 0) / pageLimit))

function formatDate(d) { if (!d) return ''; return new Date(d).toLocaleDateString('zh-CN') }
function goToPage(id) { router.push(`/page/${id}`) }
function getSiteName(siteId) { return sitesMap.value[siteId] || siteId }

async function loadPages() {
  pagesLoading.value = true
  try { pagesData.value = await pageAPI.authorPages(authorName.value, selectedSite.value, pageSkip.value, pageLimit) }
  finally { pagesLoading.value = false }
}
async function selectSite(siteId) { selectedSite.value = siteId; pageSkip.value = 0; await loadPages() }
async function prevPage() { pageSkip.value = Math.max(0, pageSkip.value - pageLimit); await loadPages() }
async function nextPage() { pageSkip.value += pageLimit; await loadPages() }

onMounted(async () => {
  try {
    const results = await Promise.all([siteAPI.list(), pageAPI.authorStats(authorName.value), pageAPI.authorProfile(authorName.value)])
    sitesMap.value = Object.fromEntries(results[0].map(s => [s.site_id, s.name]))
    stats.value = results[1]
    authorProfile.value = results[2]
    await loadPages()
  } catch (e) { console.error(e); stats.value = null }
  finally { loading.value = false }
})
</script>

<style scoped>
.author-page { max-width: 900px; margin: 0 auto; padding: 60px 1.5rem; }

.author-header { display: flex; align-items: center; gap: 24px; margin-bottom: 40px; }
.author-avatar-wrap { flex-shrink: 0; }
.author-avatar, .author-avatar-img { width: 80px; height: 80px; border-radius: 50%; }
.author-avatar { background: var(--color-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: 600; }
.author-avatar-img { object-fit: cover; }
.author-info h1 { font-size: 28px; font-weight: 600; color: var(--color-ink); letter-spacing: -0.02em; margin-bottom: 12px; }
.author-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.badge { background: #e8f0fc; color: var(--color-primary); padding: 4px 12px; border-radius: var(--radius-pill); font-size: 14px; font-weight: 500; }

.sites-stats { display: flex; gap: 16px; margin-bottom: 40px; flex-wrap: wrap; }
.site-card {
  flex: 1; min-width: 160px;
  background: var(--color-canvas); border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card); padding: 20px; cursor: pointer; transition: border-color 0.2s;
}
.site-card:hover, .site-card.active { border-color: var(--color-primary); }
.site-name { font-weight: 600; color: var(--color-ink); margin-bottom: 12px; font-size: 14px; }
.site-nums { display: flex; gap: 16px; }
.site-num { text-align: center; }
.num { font-size: 24px; font-weight: 600; color: var(--color-primary); }
.num-label { font-size: 12px; color: var(--color-muted); margin-top: 2px; }

.pages-section {
  background: var(--color-canvas); border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card); padding: 24px;
}
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.section-header h2 { font-size: 21px; font-weight: 600; color: var(--color-ink); letter-spacing: -0.02em; }
.btn-all { font-size: 14px; color: var(--color-primary); background: none; border: 1px solid var(--color-primary); border-radius: 8px; padding: 4px 12px; cursor: pointer; font-family: inherit; }
.btn-all:hover { background: var(--color-primary); color: #fff; }

.page-list { display: flex; flex-direction: column; }
.page-item { display: flex; align-items: center; gap: 16px; padding: 16px 0; border-bottom: 1px solid var(--color-hairline); cursor: pointer; }
.page-item:last-child { border-bottom: none; }
.page-main { flex: 1; min-width: 0; }
.page-title { font-size: 17px; font-weight: 500; color: var(--color-ink); margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.page-meta { display: flex; gap: 12px; color: var(--color-muted); font-size: 14px; align-items: center; }
.site-badge { background: #e8f0fc; color: var(--color-primary); padding: 1px 8px; border-radius: 4px; font-size: 12px; }
.page-cats { display: flex; gap: 4px; }
.cat-tag { font-size: 12px; background: var(--color-parchment); padding: 1px 8px; border-radius: var(--radius-pill); color: var(--color-muted); }

.page-rating { flex-shrink: 0; text-align: center; min-width: 64px; }
.page-rating.no-rating .rating-num { color: var(--color-hairline); }
.rating-num { font-size: 24px; font-weight: 600; color: var(--color-primary); line-height: 1; }
.rating-stars .star { font-size: 10px; color: var(--color-hairline); }
.rating-stars .star.filled { color: var(--color-primary); }
.rating-count { font-size: 12px; color: var(--color-muted); margin-top: 2px; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 24px; }
.pagination button { padding: 8px 20px; background: var(--color-primary); color: #fff; border: none; border-radius: var(--radius-pill); cursor: pointer; font-family: inherit; font-size: 14px; }
.pagination button:disabled { background: var(--color-parchment); color: var(--color-muted); cursor: not-allowed; }
.pagination span { font-size: 14px; color: var(--color-muted); }

.loading, .empty, .error { text-align: center; padding: 40px 0; color: var(--color-muted); }
</style>
