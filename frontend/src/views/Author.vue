<template>
  <div class="author-page">
    <template v-if="isOwnPage">
      <!-- ── 统一作者页（标签栏模式） ── -->
      <div class="wikiio-header-bar">
        <div class="wikiio-header-logos">
          <img src="/fandom-logo.svg" class="wikiio-header-logo" />
          <span class="wikiio-header-plus">+</span>
          <img src="/miraheze-logo.svg" class="wikiio-header-logo" />
        </div>
        <span>Wikiio 作者页</span>
      </div>

      <div class="author-header">
        <div class="author-avatar-wrap">
          <div class="author-avatar wikiio-avatar">
            {{ userData.username[0]?.toUpperCase() }}
          </div>
        </div>
        <div class="author-info">
          <h1>{{ userData.username }}</h1>
          <div class="author-badges">
            <span class="badge" v-if="userData.fandom_username">
              <i class="fa fa-globe"></i> Fandom: {{ userData.fandom_username }}
            </span>
            <span class="badge" v-if="userData.miraheze_username">
              <i class="fa fa-globe"></i> Miraheze: {{ userData.miraheze_username }}
            </span>
          </div>
        </div>
      </div>

      <div class="tabs">
        <button
          v-if="userData.fandom_username"
          :class="{ active: activeTab === 'fandom' }"
          @click="switchTab('fandom')"
        >
          <img src="/fandom-logo.svg" class="tab-icon" /> Fandom
        </button>
        <button
          v-if="userData.miraheze_username"
          :class="{ active: activeTab === 'miraheze' }"
          @click="switchTab('miraheze')"
        >
          <img src="/miraheze-logo.svg" class="tab-icon" /> Miraheze
        </button>
      </div>

      <!-- Fandom Tab -->
      <template v-if="activeTab === 'fandom' && userData.fandom_username">
        <div v-if="fdLoading" class="loading-sm">加载中...</div>
        <template v-else-if="fdStats">
          <Transition name="fade-up" appear>
            <div class="sites-stats">
              <div
                class="site-card"
                v-for="site in fdStats.sites" :key="site.site_id"
                :class="{ active: fdSelectedSite === site.site_id }"
                @click="fdSelectSite(site.site_id)"
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
          </Transition>

          <div class="pages-section">
            <div class="section-header">
              <h2>
                {{ fdSelectedSiteName ? fdSelectedSiteName + ' · ' : '全部站点 · ' }}
                {{ fdPagesData?.total || 0 }} 篇文章
              </h2>
              <button v-if="fdSelectedSite" class="btn-all" @click="fdSelectSite(null)">查看全部</button>
            </div>
            <div v-if="fdPagesLoading" class="loading-sm">加载中...</div>
            <div v-else-if="fdPagesData?.pages?.length === 0" class="empty">暂无文章</div>
            <TransitionGroup name="list" tag="div" class="page-list" v-else>
              <div class="page-item" v-for="page in fdPagesData?.pages" :key="page.id" @click="goToPage(page.id)">
                <div class="page-main">
                  <div class="page-title">{{ page.title }}</div>
                  <div class="page-meta">
                    <span class="site-badge">{{ fdSiteMap[page.site_id] || page.site_id }}</span>
                    <span>{{ page.word_count }} 字</span>
                    <span>{{ formatDate(page.last_edited_at) }}</span>
                  </div>
                  <div class="page-cats" v-if="page.categories?.length">
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
            </TransitionGroup>
            <div class="pagination" v-if="(fdPagesData?.total || 0) > fdPageLimit">
              <button :disabled="fdPageSkip === 0" @click="fdPrevPage">上一页</button>
              <span>第 {{ fdCurrentPage }} / {{ fdTotalPages }} 页</span>
              <button :disabled="fdPageSkip + fdPageLimit >= (fdPagesData?.total || 0)" @click="fdNextPage">下一页</button>
            </div>
          </div>
        </template>
      </template>

      <!-- Miraheze Tab -->
      <template v-if="activeTab === 'miraheze' && userData.miraheze_username">
        <div v-if="mhLoading" class="loading-sm">加载中...</div>
        <template v-else-if="mhStats">
          <Transition name="fade-up" appear>
            <div class="sites-stats">
              <div
                class="site-card"
                v-for="site in mhStats.sites" :key="site.site_id"
                :class="{ active: mhSelectedSite === site.site_id }"
                @click="mhSelectSite(site.site_id)"
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
          </Transition>

          <div class="pages-section">
            <div class="section-header">
              <h2>
                {{ mhSelectedSiteName ? mhSelectedSiteName + ' · ' : '全部站点 · ' }}
                {{ mhPagesData?.total || 0 }} 篇文章
              </h2>
              <button v-if="mhSelectedSite" class="btn-all" @click="mhSelectSite(null)">查看全部</button>
            </div>
            <div v-if="mhPagesLoading" class="loading-sm">加载中...</div>
            <div v-else-if="mhPagesData?.pages?.length === 0" class="empty">暂无文章</div>
            <TransitionGroup name="list" tag="div" class="page-list" v-else>
              <div class="page-item" v-for="page in mhPagesData?.pages" :key="page.id" @click="goToPage(page.id)">
                <div class="page-main">
                  <div class="page-title">{{ page.title }}</div>
                  <div class="page-meta">
                    <span class="site-badge">{{ mhSiteMap[page.site_id] || page.site_id }}</span>
                    <span>{{ page.word_count }} 字</span>
                    <span>{{ formatDate(page.last_edited_at) }}</span>
                  </div>
                  <div class="page-cats" v-if="page.categories?.length">
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
            </TransitionGroup>
            <div class="pagination" v-if="(mhPagesData?.total || 0) > mhPageLimit">
              <button :disabled="mhPageSkip === 0" @click="mhPrevPage">上一页</button>
              <span>第 {{ mhCurrentPage }} / {{ mhTotalPages }} 页</span>
              <button :disabled="mhPageSkip + mhPageLimit >= (mhPagesData?.total || 0)" @click="mhNextPage">下一页</button>
            </div>
          </div>
        </template>
      </template>

      <!-- Tab with no bound account shows a hint -->
      <div v-if="!userData.fandom_username && !userData.miraheze_username" class="empty">尚未绑定任何账户</div>
    </template>

    <!-- ── 非本人页面：传统作者页模式 ── -->
    <template v-else>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="stats">
        <Transition name="fade-up" appear>
          <div>
            <div class="author-header">
              <div class="author-avatar-wrap">
                <div class="author-avatar wikiio-avatar">
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
            <h2>{{ selectedSiteName ? selectedSiteName + ' · ' : '全部站点 · ' }}{{ pagesData?.total || 0 }} 篇文章</h2>
            <button v-if="selectedSite" class="btn-all" @click="selectSite(null)">查看全部</button>
          </div>
          <div v-if="pagesLoading" class="loading-sm">加载中...</div>
          <div v-else-if="pagesData?.pages?.length === 0" class="empty">暂无文章</div>
          <TransitionGroup name="list" tag="div" class="page-list" v-else>
            <div class="page-item" v-for="page in pagesData?.pages" :key="page.id" @click="goToPage(page.id)">
              <div class="page-main">
                <div class="page-title">{{ page.title }}</div>
                <div class="page-meta">
                  <span class="site-badge">{{ getSiteName(page.site_id) }}</span>
                  <span>{{ page.word_count }} 字</span>
                  <span>{{ formatDate(page.last_edited_at) }}</span>
                </div>
                <div class="page-cats" v-if="page.categories?.length">
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
          </TransitionGroup>
          <div class="pagination" v-if="(pagesData?.total || 0) > pageLimit">
            <button :disabled="pageSkip === 0" @click="prevPage">上一页</button>
            <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
            <button :disabled="pageSkip + pageLimit >= (pagesData?.total || 0)" @click="nextPage">下一页</button>
          </div>
        </div>
      </div>
      <div v-else class="error">找不到该作者</div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pageAPI, siteAPI } from '../api/index.js'
import { useAuthStore } from '../stores/auth.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const authorName = computed(() => decodeURIComponent(route.params.author))

/* ── 检测是否为当前用户自己的页面 ── */
const isOwnPage = computed(() =>
  authStore.isLoggedIn && authStore.user?.username === authorName.value
)

const userData = computed(() => authStore.user)

/* ── 自己页面：tab 切换 ── */
const activeTab = ref('')

function switchTab(tab) {
  activeTab.value = tab
  if (tab === 'fandom') loadFdData()
  else if (tab === 'miraheze') loadMhData()
}

/* ── 公共 ── */
function formatDate(d) { if (!d) return ''; return new Date(d).toLocaleDateString('zh-CN') }
function goToPage(id) { router.push(`/page/${id}`) }

/* ── Fandom tab ── */
const fdStats = ref(null)
const fdPagesData = ref(null)
const fdSiteMap = ref({})
const fdLoading = ref(false)
const fdPagesLoading = ref(false)
const fdSelectedSite = ref(null)
const fdPageSkip = ref(0)
const fdPageLimit = 20

const fdSelectedSiteName = computed(() => fdSelectedSite.value ? fdSiteMap.value[fdSelectedSite.value] || fdSelectedSite.value : null)
const fdCurrentPage = computed(() => Math.floor(fdPageSkip.value / fdPageLimit) + 1)
const fdTotalPages = computed(() => Math.ceil((fdPagesData.value?.total || 0) / fdPageLimit))

async function loadFdData() {
  if (!userData.value?.fandom_username) return
  fdLoading.value = true
  fdPageSkip.value = 0
  fdSelectedSite.value = null
  try {
    const [sites, stats] = await Promise.all([
      siteAPI.list(),
      pageAPI.authorStats(userData.value.fandom_username),
    ])
    fdSiteMap.value = Object.fromEntries(sites.map(s => [s.site_id, s.name]))
    fdStats.value = stats
    await fdLoadPages()
  } catch { fdStats.value = null }
  finally { fdLoading.value = false }
}
async function fdLoadPages() {
  fdPagesLoading.value = true
  try {
    fdPagesData.value = await pageAPI.authorPages(
      userData.value.fandom_username, fdSelectedSite.value, fdPageSkip.value, fdPageLimit
    )
  } finally { fdPagesLoading.value = false }
}
function fdSelectSite(siteId) { fdSelectedSite.value = siteId; fdPageSkip.value = 0; fdLoadPages() }
function fdPrevPage() { fdPageSkip.value = Math.max(0, fdPageSkip.value - fdPageLimit); fdLoadPages() }
function fdNextPage() { fdPageSkip.value += fdPageLimit; fdLoadPages() }

/* ── Miraheze tab ── */
const mhStats = ref(null)
const mhPagesData = ref(null)
const mhSiteMap = ref({})
const mhLoading = ref(false)
const mhPagesLoading = ref(false)
const mhSelectedSite = ref(null)
const mhPageSkip = ref(0)
const mhPageLimit = 20

const mhSelectedSiteName = computed(() => mhSelectedSite.value ? mhSiteMap.value[mhSelectedSite.value] || mhSelectedSite.value : null)
const mhCurrentPage = computed(() => Math.floor(mhPageSkip.value / mhPageLimit) + 1)
const mhTotalPages = computed(() => Math.ceil((mhPagesData.value?.total || 0) / mhPageLimit))

async function loadMhData() {
  if (!userData.value?.miraheze_username) return
  mhLoading.value = true
  mhPageSkip.value = 0
  mhSelectedSite.value = null
  try {
    const [sites, stats] = await Promise.all([
      siteAPI.list(),
      pageAPI.authorStats(userData.value.miraheze_username),
    ])
    mhSiteMap.value = Object.fromEntries(sites.map(s => [s.site_id, s.name]))
    mhStats.value = stats
    await mhLoadPages()
  } catch { mhStats.value = null }
  finally { mhLoading.value = false }
}
async function mhLoadPages() {
  mhPagesLoading.value = true
  try {
    mhPagesData.value = await pageAPI.authorPages(
      userData.value.miraheze_username, mhSelectedSite.value, mhPageSkip.value, mhPageLimit
    )
  } finally { mhPagesLoading.value = false }
}
function mhSelectSite(siteId) { mhSelectedSite.value = siteId; mhPageSkip.value = 0; mhLoadPages() }
function mhPrevPage() { mhPageSkip.value = Math.max(0, mhPageSkip.value - mhPageLimit); mhLoadPages() }
function mhNextPage() { mhPageSkip.value += mhPageLimit; mhLoadPages() }

/* ── 非本人页面：旧模式 ── */
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
function getSiteName(siteId) { return sitesMap.value[siteId] || siteId }

async function loadPages() {
  pagesLoading.value = true
  try {
    pagesData.value = await pageAPI.authorPages(authorName.value, selectedSite.value, pageSkip.value, pageLimit)
  } finally { pagesLoading.value = false }
}
function selectSite(siteId) { selectedSite.value = siteId; pageSkip.value = 0; loadPages() }
function prevPage() { pageSkip.value = Math.max(0, pageSkip.value - pageLimit); loadPages() }
function nextPage() { pageSkip.value += pageLimit; loadPages() }

onMounted(async () => {
  // 如果是自己页面，不需要 legacy 逻辑
  if (isOwnPage.value) {
    loading.value = false
    // 默认选中第一个有绑定的 tab
    if (userData.value?.fandom_username) activeTab.value = 'fandom'
    else if (userData.value?.miraheze_username) activeTab.value = 'miraheze'
    if (activeTab.value === 'fandom') await loadFdData()
    else if (activeTab.value === 'miraheze') await loadMhData()
    return
  }

  // Legacy 模式
  try {
    const [sites, s] = await Promise.all([
      siteAPI.list(),
      pageAPI.authorStats(authorName.value),
    ])
    sitesMap.value = Object.fromEntries(sites.map(s => [s.site_id, s.name]))
    stats.value = s
    await loadPages()
  } catch { stats.value = null }
  finally { loading.value = false }
})
</script>

<style scoped>
.author-page { max-width: 1200px; margin: 0 auto; padding: var(--space-16) var(--space-6); }

.wikiio-header-bar {
  display: flex; align-items: center; gap: var(--space-3);
  margin-bottom: var(--space-10);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-hairline);
}
.wikiio-header-logos { display: flex; align-items: center; gap: var(--space-1); }
.wikiio-header-logo { width: 22px; height: 22px; }
.wikiio-header-plus { font-size: var(--text-sm); color: var(--color-muted); margin: 0 var(--space-1); }
.wikiio-header-bar span { font-size: var(--text-base); font-weight: 600; color: var(--color-muted); }

.author-header { display: flex; align-items: center; gap: var(--space-6); margin-bottom: var(--space-10); }
.author-avatar-wrap { flex-shrink: 0; }
.author-avatar { width: 88px; height: 88px; border-radius: 50%; }
.wikiio-avatar {
  background: linear-gradient(135deg, #185897, #3a7fc1);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: var(--text-3xl); font-weight: 600;
  box-shadow: 0 0 0 4px var(--color-parchment), 0 0 0 5px var(--color-hairline);
}
.author-info h1 {
  font-size: var(--text-2xl); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
  margin-bottom: var(--space-3);
}
.author-badges { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.badge {
  background: var(--color-highlight); color: var(--color-primary);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill); font-size: var(--text-sm); font-weight: 500;
}
.badge-star { background: var(--color-badge-warm); color: var(--color-badge-warm-text); }
.badge i { margin-right: 2px; }

/* ── Tabs ── */
.tabs {
  display: flex; gap: var(--space-1);
  margin-bottom: var(--space-8);
  border-bottom: 1px solid var(--color-hairline);
}
.tabs button {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-5);
  border: none; background: none;
  color: var(--color-muted); cursor: pointer;
  font-size: var(--text-sm); font-family: inherit;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color var(--duration-fast) var(--ease-smooth),
              border-color var(--duration-fast) var(--ease-smooth);
}
.tabs button:hover { color: var(--color-primary); }
.tabs button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  font-weight: 500;
}
.tab-icon { width: 16px; height: 16px; }

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
.site-card:hover { background-color: var(--color-highlight); }
.site-card.active { border-color: var(--color-primary); background-color: var(--color-highlight); }
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
.section-header h2 { font-size: var(--text-lg); font-weight: 600; color: var(--color-ink); letter-spacing: -0.02em; }
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

.page-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-6); position: relative; }
.page-item {
  display: flex; align-items: center; gap: var(--space-4);
  flex-wrap: wrap;
  padding: var(--space-6); border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color var(--duration-base) var(--ease-smooth);
}
.page-item:hover { background-color: var(--color-highlight); }
.page-main { flex: 1 1 200px; min-width: 0; }
.page-title {
  font-size: var(--text-base); font-weight: 500; color: var(--color-ink);
  margin-bottom: var(--space-1);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.page-meta { display: flex; gap: var(--space-3); color: var(--color-muted); font-size: var(--text-sm); align-items: center; }
.site-badge {
  background: var(--color-highlight); color: var(--color-primary);
  padding: 1px var(--space-2); border-radius: 4px; font-size: var(--text-xs);
}
.page-cats { display: flex; gap: var(--space-1); }
.cat-tag {
  font-size: var(--text-xs);
  background: var(--color-tag); color: var(--color-primary);
  padding: 1px var(--space-2); border-radius: var(--radius-pill);
}
.page-rating { flex-shrink: 0; text-align: center; min-width: 60px; }
.page-rating.no-rating .rating-num { color: var(--color-hairline); }
.rating-num { font-size: var(--text-xl); font-weight: 600; color: var(--color-primary); line-height: 1; }
.rating-stars .star { font-size: var(--text-xs); color: var(--color-hairline); }
.rating-stars .star.filled { color: var(--color-star); }
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
  background: var(--color-parchment); color: var(--color-muted); cursor: not-allowed; transform: none;
}
.pagination span { font-size: var(--text-sm); color: var(--color-muted); }

.loading, .loading-sm, .empty, .error { text-align: center; padding: var(--space-10) 0; color: var(--color-muted); }
.loading-sm { padding: var(--space-6) 0; }

@media (max-width: 1024px) {
  .page-list { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .page-item { flex-direction: column; align-items: flex-start; gap: 0; }
  .page-main { flex: 1 1 auto; width: 100%; }
  .page-title { white-space: normal; word-break: break-word; }
  .page-rating {
    display: flex; flex-direction: row; align-items: center;
    gap: var(--space-3); width: 100%;
    padding-top: var(--space-3); margin-top: var(--space-1);
    border-top: 1px solid var(--color-hairline);
  }
  .page-rating .rating-num { font-size: 1rem; }
  .page-rating .rating-stars .star { font-size: 0.9rem; }
}
</style>
