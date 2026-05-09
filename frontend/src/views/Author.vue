<template>
  <div class="author-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="stats">

      <!-- 作者信息头部 -->
      <div class="author-header">
        <div class="author-avatar-wrap">
          <img
            v-if="authorProfile?.avatar_url"
            :src="authorProfile.avatar_url"
            class="author-avatar-img"
          />
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

      <!-- 各站点统计 -->
      <div class="sites-stats">
        <div
          class="site-card"
          v-for="site in stats.sites"
          :key="site.site_id"
          :class="{ active: selectedSite === site.site_id }"
          @click="selectSite(site.site_id)"
        >
          <div class="site-name">{{ site.site_name }}</div>
          <div class="site-nums">
            <div class="site-num">
              <div class="num">{{ site.page_count }}</div>
              <div class="num-label">篇</div>
            </div>
            <div class="site-num">
              <div class="num">{{ site.total_words.toLocaleString() }}</div>
              <div class="num-label">字</div>
            </div>
            <div class="site-num" v-if="site.total_ratings > 0">
              <div class="num">{{ site.avg_rating.toFixed(1) }}</div>
              <div class="num-label">均分</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 页面列表 -->
      <div class="pages-section">
        <div class="section-header">
          <h2>
            {{ selectedSiteName ? selectedSiteName + ' · ' : '全部站点 · ' }}
            {{ pagesData?.total || 0 }} 篇文章
          </h2>
          <button v-if="selectedSite" class="btn-all" @click="selectSite(null)">查看全部</button>
        </div>

        <div v-if="pagesLoading" class="loading">加载中...</div>
        <div v-else-if="pagesData?.pages?.length === 0" class="empty">暂无文章</div>
        <div v-else class="page-list">
          <div
            class="page-item"
            v-for="page in pagesData?.pages"
            :key="page.id"
            @click="goToPage(page.id)"
          >
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
            <div class="page-rating" v-if="page.rating_count > 0">
              <div class="rating-num">{{ page.rating_avg.toFixed(1) }}</div>
              <div class="rating-stars">
                <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(page.rating_avg) }">★</span>
              </div>
              <div class="rating-count">{{ page.rating_count }}人</div>
            </div>
            <div class="page-rating no-rating" v-else>
              <div class="rating-num">-</div>
              <div class="rating-count">暂无评分</div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
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

const selectedSiteName = computed(() => {
  if (!selectedSite.value) return null
  return sitesMap.value[selectedSite.value] || selectedSite.value
})

const currentPage = computed(() => Math.floor(pageSkip.value / pageLimit) + 1)
const totalPages = computed(() => Math.ceil((pagesData.value?.total || 0) / pageLimit))

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

function goToPage(id) {
  router.push(`/page/${id}`)
}

function getSiteName(siteId) {
  return sitesMap.value[siteId] || siteId
}

async function loadPages() {
  pagesLoading.value = true
  try {
    pagesData.value = await pageAPI.authorPages(
      authorName.value,
      selectedSite.value,
      pageSkip.value,
      pageLimit
    )
  } finally {
    pagesLoading.value = false
  }
}

async function selectSite(siteId) {
  selectedSite.value = siteId
  pageSkip.value = 0
  await loadPages()
}

async function prevPage() {
  pageSkip.value = Math.max(0, pageSkip.value - pageLimit)
  await loadPages()
}

async function nextPage() {
  pageSkip.value += pageLimit
  await loadPages()
}

onMounted(async () => {
  try {
    // 加载站点列表和作者统计
    const results = await Promise.all([
      siteAPI.list(),
      pageAPI.authorStats(authorName.value),
      pageAPI.authorProfile(authorName.value),
    ])

    sitesMap.value = Object.fromEntries(results[0].map(s => [s.site_id, s.name]))
    stats.value = results[1]
    authorProfile.value = results[2]
    await loadPages()
  } catch (e) {
    console.error(e)
    stats.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.author-page { max-width: 900px; margin: 0 auto; padding: 2rem 1rem; }
.loading { text-align: center; padding: 3rem; color: #888; }
.error { text-align: center; padding: 3rem; color: #e74c3c; }
.empty { text-align: center; padding: 2rem; color: #aaa; }

.author-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 1.2rem;
}
.author-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: #185897;
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; font-weight: bold; flex-shrink: 0;
}
h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }
.author-badges { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.badge {
  background: #e8f0fc;
  color: #185897;
  padding: 0.2rem 0.7rem;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 500;
}

.sites-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.2rem;
  flex-wrap: wrap;
}
.site-card {
  flex: 1;
  min-width: 160px;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.15s;
}
.site-card:hover { border-color: #185897; }
.site-card.active { border-color: #185897; background: #f0f5ff; }
.site-name { font-weight: 600; color: #333; margin-bottom: 0.8rem; font-size: 0.9rem; }
.site-nums { display: flex; gap: 1rem; }
.site-num { text-align: center; }
.num { font-size: 1.2rem; font-weight: bold; color: #185897; }
.num-label { font-size: 0.72rem; color: #888; }

.pages-section {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
h2 { font-size: 1rem; font-weight: 600; color: #333; }
.btn-all {
  font-size: 0.82rem;
  color: #185897;
  background: none;
  border: 1px solid #185897;
  border-radius: 4px;
  padding: 0.2rem 0.6rem;
  cursor: pointer;
}
.btn-all:hover { background: #185897; color: white; }

.page-list { display: flex; flex-direction: column; }
.page-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.page-item:last-child { border-bottom: none; }
.page-item:hover { background: #f9f9f9; margin: 0 -1rem; padding: 0.9rem 1rem; }

.page-main { flex: 1; min-width: 0; }
.page-title {
  font-weight: 500; color: #1a1a2e;
  margin-bottom: 0.3rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.page-meta { display: flex; gap: 0.8rem; color: #888; font-size: 0.8rem; margin-bottom: 0.3rem; align-items: center; }
.site-badge {
  background: #e8f0fc; color: #185897;
  padding: 0.1rem 0.4rem; border-radius: 3px;
  font-size: 0.72rem;
}
.page-cats { display: flex; gap: 0.3rem; }
.cat-tag {
  font-size: 0.72rem; background: #f0f0f0;
  padding: 0.1rem 0.4rem; border-radius: 8px; color: #666;
}

.page-rating {
  flex-shrink: 0;
  text-align: center;
  min-width: 60px;
}
.page-rating.no-rating .rating-num { color: #ccc; }
.rating-num { font-size: 1.3rem; font-weight: bold; color: #f5a623; line-height: 1; }
.rating-stars .star { font-size: 0.75rem; color: #ddd; }
.rating-stars .star.filled { color: #f5a623; }
.rating-count { font-size: 0.72rem; color: #aaa; margin-top: 0.1rem; }

.pagination {
  display: flex; justify-content: center;
  align-items: center; gap: 1rem; margin-top: 1.5rem;
}
.pagination button {
  padding: 0.4rem 1rem;
  background: #185897; color: white;
  border: none; border-radius: 4px; cursor: pointer;
}
.pagination button:disabled { background: #ddd; cursor: not-allowed; }

.author-avatar-wrap { flex-shrink: 0; }
.author-avatar-img {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
}
</style>