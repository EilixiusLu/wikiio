<template>
  <div class="detail-page">
    <div class="topbar">
      <span class="back" @click="router.back()">
        <i class="fa fa-arrow-left"></i> 返回
      </span>
      <a v-if="page" :href="wikiUrl" target="_blank" class="wiki-link">
        在维基上查看 <i class="fa fa-external-link"></i>
      </a>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="page">
      <Transition name="fade-up" appear>
        <div class="detail-grid">
          <!-- ── 通栏：标题 ── -->
          <div class="card grid-full">
            <h1>{{ page.title }}</h1>
            <div class="meta">
              <span>
                作者：
                <router-link
                  v-if="page.author" :to="`/author/${page.author}`"
                  class="author-link" @click.stop
                >{{ page.author }}</router-link>
                <b v-else>未知</b>
              </span>
              <span>字数：{{ page.word_count }}</span>
              <span>最后编辑：{{ formatDate(page.last_edited_at) }}</span>
              <span>#{{ route.params.id }}</span>
            </div>
            <div class="categories" v-if="page.categories.length">
              <span class="cat-tag" v-for="cat in page.categories" :key="cat">
                {{ cat }}
              </span>
            </div>
          </div>

          <!-- ── 通栏：评分双栏 ── -->
          <div class="ratings-row grid-full">
            <div class="rating-box">
              <h2>Wikiio评分</h2>
              <div class="rating-body">
                <div class="rating-left">
                  <div class="rating-score">{{ page.rating_avg.toFixed(1) }}</div>
                  <div class="rating-stars-display">
                    <i
                      v-for="i in 5" :key="i"
                      class="fa fa-star star"
                      :class="{ filled: i <= Math.round(page.rating_avg) }"
                    ></i>
                  </div>
                  <div class="rating-count">{{ page.rating_count }} 人评分</div>
                </div>

                <div class="rating-right">
                  <div v-if="!authStore.isLoggedIn" class="rating-hint">
                    <router-link to="/login">登录</router-link>后才能评分
                  </div>
                  <div
                    v-else-if="!authStore.user?.is_fandom_verified"
                    class="rating-hint"
                  >请先<router-link to="/profile">绑定Fandom账户</router-link>才能评分</div>
                  <div v-else>
                    <div class="my-rating-label">
                      {{ myScore ? '我的评分' : '点击评分' }}
                    </div>
                    <div class="stars-input">
                      <i
                        v-for="i in 5" :key="i"
                        class="fa fa-star star-input"
                        :class="{ filled: i <= (hoverScore || myScore) }"
                        @mouseenter="hoverScore = i"
                        @mouseleave="hoverScore = 0"
                        @click="submitRating(i)"
                      ></i>
                    </div>
                    <div class="rating-actions">
                      <span class="rating-score-label" v-if="myScore">{{ myScore }} 星</span>
                      <button v-if="myScore" class="btn-remove-rating" @click="removeRating">
                        撤销
                      </button>
                    </div>
                    <div class="rating-msg success" v-if="ratingMsg">{{ ratingMsg }}</div>
                    <div class="rating-msg error" v-if="ratingError">{{ ratingError }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="site-rating-card" v-if="siteRating">
              <h2>原站评分</h2>
              <div class="site-rating-body">
                <div class="site-rating-left">
                  <div class="site-rating-score">
                    {{ siteAvgDisplay }}
                  </div>
                  <div class="rating-stars-display">
                    <i
                      v-for="i in 5" :key="i"
                      class="fa fa-star star"
                      :class="{ filled: i <= Math.round(siteRating.avg_rating / 2) }"
                    ></i>
                  </div>
                  <div class="rating-count">{{ siteRating.total_votes }} 票</div>
                </div>
                <div class="site-rating-right" v-if="siteRating.distribution">
                  <span v-for="(count, star) in siteRating.distribution" :key="star" class="dist-item">
                    {{ star }}星: {{ count }}
                  </span>
                </div>
                <div class="site-rating-right" v-else>
                  <span class="dist-item">总分 {{ siteRating.total_points }}</span>
                </div>
              </div>
              <div class="site-rating-note">数据来源：原站 RatePage 扩展</div>
            </div>
          </div>

          <!-- ── 通栏：编辑历史 ── -->
          <div class="card grid-full">
            <h2>编辑历史</h2>
            <div class="chart-wrap" v-if="revisions.length">
              <EditTrendChart :chartData="editTrendData" />
            </div>
            <div v-if="revLoading" class="loading-sm">加载中...</div>
            <div v-else class="rev-list">
              <div
                class="rev-item"
                v-for="rev in revisions"
                :key="rev.rev_id"
              >
                <div class="rev-row">
                  <span class="rev-editor">{{ rev.editor }}</span>
                  <span class="rev-time">{{ formatDate(rev.timestamp) }}</span>
                </div>
                <div class="rev-comment">{{ rev.comment || '（无编辑摘要）' }}</div>
              </div>
            </div>
            <div class="rev-pagination" v-if="revTotal > revPageLimit">
              <button :disabled="revPageSkip === 0" @click="prevRevPage">上一页</button>
              <span>第 {{ currentRevPage }} / {{ totalRevPages }} 页</span>
              <button :disabled="revPageSkip + revPageLimit >= revTotal" @click="nextRevPage">下一页</button>
            </div>
          </div>

          <!-- ── 通栏：Wikitext 源代码 ── -->
          <div class="card grid-full">
            <div class="wikitext-header">
              <h2>Wikitext 源代码</h2>
              <button class="copy-btn" @click="copyWikitext">
                {{ copied ? '已复制！' : '复制' }}
              </button>
            </div>
            <pre class="wikitext">{{ page.wikitext }}</pre>
          </div>
        </div>
      </Transition>
    </div>

    <div v-else class="error">页面不存在</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pageAPI, siteAPI, ratingAPI } from '../api/index.js'
import { useAuthStore } from '../stores/auth.js'
import EditTrendChart from '../components/EditTrendChart.vue'

const route = useRoute()
const router = useRouter()
const page = ref(null)
const loading = ref(true)
const copied = ref(false)
const site = ref(null)

const wikiUrl = computed(() => {
  if (!page.value || !site.value) return '#'
  const base = site.value.base_url.replace(/\/+$/, '')
  return `${base}/wiki/${encodeURIComponent(page.value.slug)}`
})

function formatDate(d) { if (!d) return ''; return new Date(d).toLocaleDateString('zh-CN') }

async function copyWikitext() {
  if (!page.value?.wikitext) return
  await navigator.clipboard.writeText(page.value.wikitext)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

onMounted(async () => {
  try {
    page.value = await pageAPI.get(route.params.id)
    revPageSkip.value = 0
    if (page.value?.site_id) {
      try { site.value = await siteAPI.get(page.value.site_id) }
      catch { site.value = null }
    }
    await Promise.all([loadMyRating(), loadSiteRating(), loadRevisions()])
  } catch { page.value = null }
  finally { loading.value = false }
})

const authStore = useAuthStore()
const myScore = ref(0)
const hoverScore = ref(0)
const ratingMsg = ref('')
const ratingError = ref('')

async function loadMyRating() {
  if (!authStore.isLoggedIn) return
  try {
    const r = await ratingAPI.getMine(route.params.id)
    myScore.value = r.score || 0
  } catch {}
}

async function submitRating(score) {
  ratingError.value = ''
  ratingMsg.value = ''
  try {
    const r = await ratingAPI.rate(route.params.id, score)
    myScore.value = score
    page.value.rating_avg = r.rating_avg
    page.value.rating_count = r.rating_count
    ratingMsg.value = '评分成功！'
    setTimeout(() => ratingMsg.value = '', 2000)
  } catch (e) {
    ratingError.value = e.detail || e.message || '评分失败'
  }
}

async function removeRating() {
  try {
    await ratingAPI.delete(route.params.id)
    myScore.value = 0
    const r = await ratingAPI.get(route.params.id)
    page.value.rating_avg = r.rating_avg
    page.value.rating_count = r.rating_count
    ratingMsg.value = '已删除评分'
    setTimeout(() => ratingMsg.value = '', 2000)
  } catch {}
}

const siteRating = ref(null)

const siteAvgDisplay = computed(() => {
  if (!siteRating.value) return '0.0'
  if (siteRating.value.scale === 5) {
    return (siteRating.value.avg_rating / 2).toFixed(1)
  }
  return siteRating.value.avg_rating.toFixed(1)
})

async function loadSiteRating() {
  try {
    const r = await pageAPI.siteRating(route.params.id)
    if (r.available) siteRating.value = r
  } catch {}
}

/* ── 编辑历史分页（API 全量分页） ── */
const revPageLimit = 10
const revPageSkip = ref(0)
const revTotal = ref(0)
const revisions = ref([])
const revLoading = ref(false)

const currentRevPage = computed(() => Math.floor(revPageSkip.value / revPageLimit) + 1)

const totalRevPages = computed(() =>
  Math.ceil((revTotal.value || 0) / revPageLimit)
)

async function loadRevisions() {
  revLoading.value = true
  try {
    const data = await pageAPI.getRevisions(route.params.id, revPageSkip.value, revPageLimit)
    revisions.value = data.revisions
    revTotal.value = data.total
  } finally {
    revLoading.value = false
  }
}

function prevRevPage() {
  revPageSkip.value = Math.max(0, revPageSkip.value - revPageLimit)
  loadRevisions()
}

function nextRevPage() {
  revPageSkip.value += revPageLimit
  loadRevisions()
}

const editTrendData = computed(() => {
  const map = {}
  for (const rev of revisions.value) {
    if (!rev.timestamp) continue
    const d = new Date(rev.timestamp)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    map[key] = (map[key] || 0) + 1
  }
  return Object.entries(map)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, count]) => ({ date, count }))
})
</script>

<style scoped>
.detail-page { max-width: 1200px; margin: 0 auto; padding: var(--space-16) var(--space-6); }

.topbar {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: var(--space-8);
}
.back { color: var(--color-primary); cursor: pointer; font-size: var(--text-base); }
.wiki-link {
  font-size: var(--text-sm); color: var(--color-primary);
  border: 1px solid var(--color-primary);
  padding: var(--space-1) var(--space-4);
  border-radius: var(--radius-pill);
  transition: background-color var(--duration-fast) var(--ease-smooth),
              color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.wiki-link:hover { background: var(--color-primary); color: #fff; text-decoration: none; }
.wiki-link:active { transform: scale(0.96); }

/* ── 双栏网格 ── */
.detail-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-8);
  align-items: start;
}

/* 通栏卡片：标题 + 评分横跨两列 */
.grid-full { grid-column: 1 / -1; }

/* 主栏卡片：Wikitext 锁定左侧 */
.grid-main { grid-column: 1; }

/* 侧栏卡片：编辑历史锁定右侧 */
.grid-side { grid-column: 2; }

/* ── 评分双栏 ── */
.ratings-row {
  display: flex;
  gap: var(--space-6);
}
.ratings-row > .rating-box { flex: 1; }
.ratings-row > .site-rating-card { flex: 1; }

/* ── 卡片基础 ── */
.card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-8);
}
.card h1 {
  font-size: var(--text-2xl); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
  margin-bottom: var(--space-4);
}
.card h2 {
  font-size: var(--text-lg); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
  margin-bottom: var(--space-4);
}

.meta {
  display: flex; gap: var(--space-5);
  color: var(--color-muted); font-size: var(--text-sm);
  margin-bottom: var(--space-4); flex-wrap: wrap;
}
.categories { display: flex; gap: var(--space-1); flex-wrap: wrap; margin-bottom: 0; }
.cat-tag {
  background: var(--color-parchment);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill);
  font-size: var(--text-sm); color: var(--color-muted);
}

/* ── Wikiio 评分 ── */
.rating-box {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6);
}
.rating-box h2 {
  font-size: var(--text-lg); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
  margin-bottom: var(--space-5);
}
.rating-body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-6);
  padding: var(--space-5);
  background: var(--color-parchment);
  border-radius: 12px;
}
.rating-left {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
}
.rating-score {
  font-size: var(--text-3xl); font-weight: 600;
  color: var(--color-primary); line-height: 1;
}
.rating-stars-display .star { font-size: var(--text-sm); color: var(--color-hairline); }
.rating-stars-display .star.filled { color: var(--color-primary); }
.rating-count { color: var(--color-muted); font-size: var(--text-sm); white-space: nowrap; }
.rating-right { width: 100%; }
.rating-hint { font-size: var(--text-sm); color: var(--color-muted); }
.rating-hint a { color: var(--color-primary); }
.my-rating-label {
  font-size: var(--text-sm); color: var(--color-muted);
  margin-bottom: var(--space-1);
}
.stars-input { display: flex; gap: var(--space-1); }
.star-input {
  font-size: var(--text-3xl); color: var(--color-hairline);
  cursor: pointer;
  transition: color var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.star-input.filled { color: var(--color-primary); }
.star-input:hover { transform: scale(1.12); }
.star-input.filled:hover { transform: scale(1.08); }
.rating-actions {
  display: flex; align-items: center; gap: var(--space-3);
  margin-top: var(--space-2);
}
.rating-score-label { font-size: var(--text-sm); color: var(--color-muted); }
.btn-remove-rating {
  font-size: var(--text-sm); color: var(--color-muted);
  background: none; border: none; cursor: pointer;
  transition: color var(--duration-fast) var(--ease-smooth);
}
.btn-remove-rating:hover { color: var(--color-danger); }
.rating-msg { font-size: var(--text-sm); margin-top: var(--space-1); }
.rating-msg.success { color: var(--color-success); }
.rating-msg.error { color: var(--color-danger); }

/* ── 原站评分 ── */
.site-rating-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6);
}
.site-rating-card h2 {
  font-size: var(--text-lg); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
  margin-bottom: var(--space-5);
}
.site-rating-body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-6);
  padding: var(--space-5);
  background: var(--color-parchment);
  border-radius: 12px;
}
.site-rating-left {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
}
.site-rating-score {
  font-size: var(--text-3xl); font-weight: 600;
  color: var(--color-primary); line-height: 1;
}
.site-rating-right {
  display: flex; gap: var(--space-2);
  flex-wrap: wrap; align-items: center;
  width: 100%;
}
.dist-item {
  font-size: var(--text-xs);
  background: var(--color-canvas);
  padding: 1px var(--space-2);
  border-radius: var(--radius-pill);
  border: 1px solid var(--color-hairline);
}
.site-rating-note {
  color: var(--color-muted); font-size: var(--text-xs);
  margin-top: var(--space-3);
}

/* ── 编辑历史 ── */
.chart-wrap {
  height: 240px;
  margin-bottom: var(--space-6);
}
.rev-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}
.rev-item {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  transition: background-color var(--duration-base) var(--ease-smooth);
}
.rev-item:hover { background-color: var(--color-highlight); }
.rev-row {
  display: flex; justify-content: space-between;
  margin-bottom: var(--space-1);
}
.rev-editor { font-weight: 500; font-size: var(--text-base); color: var(--color-ink); }
.rev-time { color: var(--color-muted); font-size: var(--text-sm); }
.rev-comment { color: var(--color-muted); font-size: var(--text-sm); }

.rev-pagination {
  display: flex; justify-content: center;
  align-items: center; gap: var(--space-4);
  margin-top: var(--space-6);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-hairline);
}
.rev-pagination button {
  padding: var(--space-2) var(--space-5);
  background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-pill);
  cursor: pointer; font-family: inherit; font-size: var(--text-sm);
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.rev-pagination button:hover { opacity: 0.9; }
.rev-pagination button:active { transform: scale(0.96); }
.rev-pagination button:disabled {
  background: var(--color-parchment);
  color: var(--color-muted); cursor: not-allowed; transform: none;
}
.rev-pagination span { font-size: var(--text-sm); color: var(--color-muted); }

/* ── Wikitext ── */
.wikitext-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: var(--space-4);
}
.copy-btn {
  padding: var(--space-2) var(--space-5);
  background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-pill);
  font-size: var(--text-sm); cursor: pointer;
  transition: opacity var(--duration-fast) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}
.copy-btn:hover { opacity: 0.9; }
.copy-btn:active { transform: scale(0.96); }

.wikitext {
  background: var(--color-parchment); border-radius: var(--radius-sm);
  padding: var(--space-5); font-family: SF Mono, Monaco, Courier New, monospace;
  font-size: var(--text-sm); line-height: 1.6;
  overflow-x: auto; white-space: pre-wrap;
  word-break: break-all; max-height: 500px; overflow-y: auto;
}

.loading, .error { text-align: center; padding: var(--space-16) 0; color: var(--color-muted); }
.author-link { color: var(--color-primary); font-weight: 500; }
.author-link:hover { text-decoration: underline; }

/* ── 移动端 ── */
@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: var(--space-6);
  }

  .grid-full, .grid-main, .grid-side {
    grid-column: auto;
  }

  .ratings-row {
    flex-direction: column;
    gap: var(--space-4);
  }

  .rev-list {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }
}
</style>
