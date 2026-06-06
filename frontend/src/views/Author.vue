<template>
  <div class="author-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="stats">
      <Transition name="fade-up" appear>
        <div>
          <div class="author-header">
            <div class="author-avatar-wrap">
              <img
                v-if="authorProfile?.avatar_url"
                :src="authorProfile.avatar_url"
                class="author-avatar-img"
              />
              <div v-else class="author-avatar">
                {{ authorName[0]?.toUpperCase() }}
              </div>
            </div>
            <div class="author-info">
              <h1>{{ authorName }}</h1>
              <div class="author-badges">
                <span class="badge"><i class="fa fa-file-text-o"></i> {{ stats.total_pages }} 篇</span>
                <span class="badge"><i class="fa fa-font"></i> {{ stats.total_words.toLocaleString() }} 字</span>
                <span class="badge badge-star" v-if="stats.total_ratings > 0">
                  <i class="fa fa-star"></i> {{ stats.total_ratings }} 次评分
                </span>
              </div>
            </div>
          </div>

          <div class="sites-stats">
            <div
              class="site-card"
              v-for="site in stats.sites" :key="site.site_id"
              :class="{ active: selectedSite === site.site_id }"
              @click="selectSite(site.site_id)"
            >
              <div class="site-name">{{ site.site_name }}</div>
              <div class="site-nums">
                <div class="site-num">
                  <div class="num">{{ site.page_count.toLocaleString() }}</div>
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
        </div>
      </Transition>

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
        <TransitionGroup name="list" tag="div" class="page-list" v-else>
          <div
            class="page-item"
            v-for="page in pagesData?.pages" :key="page.id"
            @click="goToPage(page.id)"
          >
            <div class="page-main">
              <div class="page-title">{{ page.title }}</div>
              <div class="page-meta">
                <span class="site-badge">{{ getSiteName(page.site_id) }}</span>
                <span>{{ page.word_count }} 字</span>
                <span>{{ formatDate(page.last_edited_at) }}</span>
              </div>
              <div class="page-cats" v-if="page.categories && page.categories.length">
                <span class="cat-tag" v-for="cat in page.categories.slice(0,3)" :key="cat">
                  {{ cat }}
                </span>
              </div>
            </div>
            <div class="page-rating" :class="{ 'no-rating': page.rating_count === 0 }">
              <div class="rating-num">
                {{ page.rating_count > 0 ? page.rating_avg.toFixed(1) : '—' }}
              </div>
              <div class="rating-stars" v-if="page.rating_count > 0">
                <i
                  v-for="i in 5" :key="i"
                  class="fa fa-star star"
                  :class="{ filled: i <= Math.round(page.rating_avg) }"
                ></i>
              </div>
              <div class="rating-count">
                {{ page.rating_count > 0 ? page.rating_count + '人' : '暂无评分' }}
              </div>
            </div>
          </div>
        </TransitionGroup>

        <div class="pagination" v-if="(pagesData?.total || 0) > pageLimit">
          <button :disabled="pageSkip === 0" @click="prevPage">上一页</button>
          <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
          <button
            :disabled="pageSkip + pageLimit >= (pagesData?.total || 0)"
            @click="nextPage"
          >下一页</button>
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

function formatDate(d) { if (!d) return ''; return new Date(d).toLocaleDateString('zh-CN') }
function goToPage(id) { router.push(`/page/${id}`) }
function getSiteName(siteId) { return sitesMap.value[siteId] || siteId }

async function loadPages() {
  pagesLoading.value = true
  try {
    pagesData.value = await pageAPI.authorPages(
      authorName.value, selectedSite.value, pageSkip.value, pageLimit
    )
  } finally { pagesLoading.value = false }
}
async function selectSite(siteId) { selectedSite.value = siteId; pageSkip.value = 0; await loadPages() }
async function prevPage() { pageSkip.value = Math.max(0, pageSkip.value - pageLimit); await loadPages() }
async function nextPage() { pageSkip.value += pageLimit; await loadPages() }

onMounted(async () => {
  try {
    const r = await Promise.all([
      siteAPI.list(),
      pageAPI.authorStats(authorName.value),
      pageAPI.authorProfile(authorName.value),
    ])
    sitesMap.value = Object.fromEntries(r[0].map(s => [s.site_id, s.name]))
    stats.value = r[1]
    authorProfile.value = r[2]
    await loadPages()
  } catch (e) { console.error(e); stats.value = null }
  finally { loading.value = false }
})
</script>

<style scoped>
.author-page { max-width: 900px; margin: 0 auto; padding: var(--space-16) var(--space-6); }

.author-header { display: flex; align-items: center; gap: var(--space-6); margin-bottom: var(--space-10); }
.author-avatar-wrap { flex-shrink: 0; }
.author-avatar, .author-avatar-img { width: 88px; height: 88px; border-radius: 50%; }
.author-avatar {
  background: linear-gradient(135deg, var(--color-primary), #3a7fc1);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: var(--text-3xl); font-weight: 600;
  box-shadow: 0 0 0 4px var(--color-parchment), 0 0 0 5px var(--color-hairline);
}
.author-avatar-img { object-fit: cover; }
.author-info h1 {
  font-size: var(--text-2xl); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
  margin-bottom: var(--space-3);
}
.author-badges { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.badge {
  background: #e8f0fc; color: var(--color-primary);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill); font-size: var(--text-sm); font-weight: 500;
}
.badge-star { background: #fff8e6; color: #b8860b; }
.badge i { margin-right: 2px; }

/* ── 站点卡片 ── */
.sites-stats { display: flex; gap: var(--space-4); margin-bottom: var(--space-10); flex-wrap: wrap; }
.site-card {
  flex: 1; min-width: 160px;
  background: var(--color-canvas);
  border: 2px solid transparent;
  border-radius: var(--radius-card);
  padding: var(--space-5); cursor: pointer;
  transition: background-color var(--duration-base) var(--ease-smooth),
              border-color var(--duration-base) var(--ease-smooth);
}
.site-card:hover { background-color: #e8f0fc; }
.site-card.active { border-color: var(--color-primary); background-color: #e8f0fc; }
.site-name { font-weight: 600; color: var(--color-ink); margin-bottom: var(--space-3); font-size: var(--text-sm); }
.site-nums { display: flex; gap: var(--space-4); }
.site-num { text-align: center; }
.num { font-size: var(--text-xl); font-weight: 600; color: var(--color-primary); }
.num-label { font-size: var(--text-xs); color: var(--color-muted); margin-top: var(--space-1); }

/* ── 页面列表 ── */
.pages-section {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6);
}
.section-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: var(--space-5);
}
.section-header h2 {
  font-size: var(--text-lg); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
}
.btn-all {
  font-size: var(--text-sm); color: var(--color-primary);
  background: none; border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm); padding: var(--space-1) var(--space-3);
  cursor: pointer; font-family: inherit;
  transition: background-color var(--duration-fast) var(--ease-smooth),
              color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.btn-all:hover { background: var(--color-primary); color: #fff; }
.btn-all:active { transform: scale(0.96); }

.page-list { display: flex; flex-direction: column; position: relative; }
.page-item {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-4) var(--space-4);
  border-radius: var(--radius-sm);
  margin: 0 calc(-1 * var(--space-4));
  cursor: pointer;
  transition: background-color var(--duration-base) var(--ease-smooth);
}
.page-item:hover { background-color: #e8f0fc; }
.page-main { flex: 1; min-width: 0; }
.page-title {
  font-size: var(--text-base); font-weight: 500; color: var(--color-ink);
  margin-bottom: var(--space-1);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.page-meta {
  display: flex; gap: var(--space-3);
  color: var(--color-muted); font-size: var(--text-sm); align-items: center;
}
.site-badge {
  background: #e8f0fc; color: var(--color-primary);
  padding: 1px var(--space-2); border-radius: 4px; font-size: var(--text-xs);
}
.page-cats { display: flex; gap: var(--space-1); }
.cat-tag {
  font-size: var(--text-xs);
  background: #d4e4fb; color: var(--color-primary);
  padding: 1px var(--space-2); border-radius: var(--radius-pill);
}
.page-rating { flex-shrink: 0; text-align: center; min-width: 64px; }
.page-rating.no-rating .rating-num { color: var(--color-hairline); }
.rating-num { font-size: var(--text-xl); font-weight: 600; color: var(--color-primary); line-height: 1; }
.rating-stars .star { font-size: var(--text-xs); color: var(--color-hairline); }
.rating-stars .star.filled { color: #f5a623; }
.rating-count { font-size: var(--text-xs); color: var(--color-muted); margin-top: var(--space-1); }

.pagination {
  display: flex; justify-content: center; align-items: center;
  gap: var(--space-4); margin-top: var(--space-6);
}
.pagination button {
  padding: var(--space-2) var(--space-5);
  background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-pill);
  cursor: pointer; font-family: inherit; font-size: var(--text-sm);
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.pagination button:hover { opacity: 0.9; }
.pagination button:active { transform: scale(0.96); }
.pagination button:disabled {
  background: var(--color-parchment);
  color: var(--color-muted); cursor: not-allowed; transform: none;
}
.pagination span { font-size: var(--text-sm); color: var(--color-muted); }

.loading, .empty, .error { text-align: center; padding: var(--space-10) 0; color: var(--color-muted); }
</style>
