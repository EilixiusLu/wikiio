<template>
  <div class="detail-page">
    <div class="topbar">
      <span class="back" @click="router.back()"><i class="fa fa-arrow-left"></i> 返回</span>
      <a v-if="page" :href="wikiUrl" target="_blank" class="wiki-link">在维基上查看 <i class="fa fa-external-link"></i></a>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="page">
      <div class="card">
        <h1>{{ page.title }}</h1>
        <div class="meta">
          <span>作者：<a v-if="page.author" :href="`/author/${page.author}`" class="author-link" @click.stop>{{ page.author }}</a><b v-else>未知</b></span>
          <span>字数：{{ page.word_count }}</span>
          <span>最后编辑：{{ formatDate(page.last_edited_at) }}</span>
        </div>
        <div class="categories" v-if="page.categories.length">
          <span class="cat-tag" v-for="cat in page.categories" :key="cat">{{ cat }}</span>
        </div>

        <div class="rating-box">
          <div class="rating-left">
            <div class="rating-score">{{ page.rating_avg.toFixed(1) }}</div>
            <div class="rating-stars-display">
              <i v-for="i in 5" :key="i" class="fa fa-star star" :class="{ filled: i <= Math.round(page.rating_avg) }"></i>
            </div>
            <div class="rating-count">{{ page.rating_count }} 人评分</div>
          </div>
          <div class="rating-right">
            <div v-if="!authStore.isLoggedIn" class="rating-hint"><a href="/login">登录</a>后才能评分</div>
            <div v-else-if="!authStore.user?.is_fandom_verified" class="rating-hint">请先<a href="/profile">绑定Fandom账户</a>才能评分</div>
            <div v-else>
              <div class="my-rating-label">{{ myScore ? '我的评分' : '点击评分' }}</div>
              <div class="stars-input">
                <i v-for="i in 5" :key="i" class="fa fa-star star-input" :class="{ filled: i <= (hoverScore || myScore) }" @mouseenter="hoverScore = i" @mouseleave="hoverScore = 0" @click="submitRating(i)"></i>
              </div>
              <div class="rating-actions">
                <span class="rating-score-label" v-if="myScore">{{ myScore }} 星</span>
                <button v-if="myScore" class="btn-remove-rating" @click="removeRating">撤销</button>
              </div>
              <div class="rating-msg success" v-if="ratingMsg">{{ ratingMsg }}</div>
              <div class="rating-msg error" v-if="ratingError">{{ ratingError }}</div>
            </div>
          </div>
        </div>

        <div class="card site-rating-card" v-if="siteRating">
          <h2>原站评分</h2>
          <div class="site-rating-box">
            <div class="site-rating-left">
              <div class="site-rating-score">{{ siteRating.avg_rating.toFixed(1) }}</div>
              <div class="site-rating-label">/ 10</div>
            </div>
            <div class="site-rating-right">
              <div class="site-rating-bar-wrap"><div class="site-rating-bar" :style="{ width: (siteRating.avg_rating / 10 * 100) + '%' }"></div></div>
              <div class="site-rating-meta"><span>{{ siteRating.total_votes }} 票</span><span>总分 {{ siteRating.total_points }}</span></div>
            </div>
          </div>
          <div class="site-rating-note">数据来源：原站 RatePage 扩展</div>
        </div>
      </div>

      <div class="card">
        <h2>编辑历史</h2>
        <div class="rev-item" v-for="rev in page.recent_revisions" :key="rev.rev_id">
          <div class="rev-row"><span class="rev-editor">{{ rev.editor }}</span><span class="rev-time">{{ formatDate(rev.timestamp) }}</span></div>
          <div class="rev-comment">{{ rev.comment || '（无编辑摘要）' }}</div>
        </div>
      </div>

      <div class="card">
        <div class="wikitext-header">
          <h2>Wikitext 源代码</h2>
          <button class="copy-btn" @click="copyWikitext">{{ copied ? '已复制！' : '复制' }}</button>
        </div>
        <pre class="wikitext">{{ page.wikitext }}</pre>
      </div>
    </div>

    <div v-else class="error">页面不存在</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pageAPI, siteAPI, ratingAPI } from '../api/index.js'
import { useAuthStore } from '../stores/auth.js'

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
  copied.value = true; setTimeout(() => copied.value = false, 2000)
}

onMounted(async () => {
  try {
    page.value = await pageAPI.get(route.params.id)
    if (page.value?.site_id) { try { site.value = await siteAPI.get(page.value.site_id) } catch { site.value = null } }
    await Promise.all([loadMyRating(), loadSiteRating()])
  } catch { page.value = null }
  finally { loading.value = false }
})

const authStore = useAuthStore()
const myScore = ref(0)
const hoverScore = ref(0)
const ratingMsg = ref('')
const ratingError = ref('')

async function loadMyRating() { if (!authStore.isLoggedIn) return; try { const res = await ratingAPI.getMine(route.params.id); myScore.value = res.score || 0 } catch {} }

async function submitRating(score) {
  ratingError.value = ''; ratingMsg.value = ''
  try { const res = await ratingAPI.rate(route.params.id, score); myScore.value = score; page.value.rating_avg = res.rating_avg; page.value.rating_count = res.rating_count; ratingMsg.value = '评分成功！'; setTimeout(() => ratingMsg.value = '', 2000) }
  catch (e) { ratingError.value = e.detail || e.message || '评分失败' }
}

async function removeRating() {
  try { await ratingAPI.delete(route.params.id); myScore.value = 0; const res = await ratingAPI.get(route.params.id); page.value.rating_avg = res.rating_avg; page.value.rating_count = res.rating_count; ratingMsg.value = '已删除评分'; setTimeout(() => ratingMsg.value = '', 2000) }
  catch {}
}

const siteRating = ref(null)
async function loadSiteRating() { try { const res = await pageAPI.siteRating(route.params.id); if (res.available) siteRating.value = res } catch {} }
</script>

<style scoped>
.detail-page { max-width: 860px; margin: 0 auto; padding: 60px 1.5rem; }

.topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.back { color: var(--color-primary); cursor: pointer; font-size: 17px; }
.wiki-link { font-size: 14px; color: var(--color-primary); border: 1px solid var(--color-primary); padding: 6px 14px; border-radius: var(--radius-pill); transition: all 0.15s; }
.wiki-link:hover { background: var(--color-primary); color: #fff; text-decoration: none; }

.card { background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-card); padding: 32px; margin-bottom: 24px; }

h1 { font-size: 28px; font-weight: 600; color: var(--color-ink); letter-spacing: -0.02em; margin-bottom: 16px; }
h2 { font-size: 21px; font-weight: 600; color: var(--color-ink); letter-spacing: -0.02em; margin-bottom: 16px; }

.meta { display: flex; gap: 20px; color: var(--color-muted); font-size: 14px; margin-bottom: 16px; flex-wrap: wrap; }
.categories { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 20px; }
.cat-tag { background: var(--color-parchment); padding: 4px 12px; border-radius: var(--radius-pill); font-size: 14px; color: var(--color-muted); }

.rating-box { display: flex; align-items: center; gap: 32px; padding: 24px; background: var(--color-parchment); border-radius: 12px; flex-wrap: wrap; }
.rating-left { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.rating-score { font-size: 48px; font-weight: 600; color: var(--color-primary); line-height: 1; }
.rating-stars-display .star { font-size: 16px; color: var(--color-hairline); }
.rating-stars-display .star.filled { color: var(--color-primary); }
.rating-count { color: var(--color-muted); font-size: 14px; }
.rating-right { flex: 1; }
.rating-hint { font-size: 14px; color: var(--color-muted); }
.rating-hint a { color: var(--color-primary); }
.my-rating-label { font-size: 14px; color: var(--color-muted); margin-bottom: 6px; }
.stars-input { display: flex; gap: 4px; }
.star-input { font-size: 32px; color: var(--color-hairline); cursor: pointer; transition: color 0.1s, transform 0.1s; }
.star-input.filled { color: var(--color-primary); transform: scale(1.1); }
.rating-actions { display: flex; align-items: center; gap: 12px; margin-top: 8px; }
.rating-score-label { font-size: 14px; color: var(--color-muted); }
.btn-remove-rating { font-size: 14px; color: var(--color-muted); background: none; border: none; cursor: pointer; }
.btn-remove-rating:hover { color: #e74c3c; }
.rating-msg { font-size: 14px; margin-top: 4px; }
.rating-msg.success { color: #27ae60; }
.rating-msg.error { color: #e74c3c; }

.site-rating-card { margin-top: 0; background: var(--color-parchment); border: none; }
.site-rating-box { display: flex; align-items: center; gap: 24px; }
.site-rating-left { display: flex; align-items: baseline; gap: 4px; flex-shrink: 0; }
.site-rating-score { font-size: 48px; font-weight: 600; color: var(--color-primary); line-height: 1; }
.site-rating-label { font-size: 17px; color: var(--color-muted); }
.site-rating-right { flex: 1; }
.site-rating-bar-wrap { height: 8px; background: var(--color-hairline); border-radius: 4px; overflow: hidden; margin-bottom: 8px; }
.site-rating-bar { height: 100%; background: var(--color-primary); border-radius: 4px; transition: width 0.5s ease; }
.site-rating-meta { display: flex; gap: 16px; color: var(--color-muted); font-size: 14px; }
.site-rating-note { color: var(--color-muted); font-size: 12px; margin-top: 12px; }

.rev-item { padding: 16px 0; border-bottom: 1px solid var(--color-hairline); }
.rev-item:last-child { border-bottom: none; }
.rev-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
.rev-editor { font-weight: 500; font-size: 17px; color: var(--color-ink); }
.rev-time { color: var(--color-muted); font-size: 14px; }
.rev-comment { color: var(--color-muted); font-size: 14px; }

.wikitext-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.copy-btn { padding: 8px 20px; background: var(--color-primary); color: #fff; border: none; border-radius: var(--radius-pill); font-size: 14px; cursor: pointer; }
.copy-btn:hover { opacity: 0.9; }

.wikitext { background: var(--color-parchment); border-radius: 8px; padding: 20px; font-family: SF Mono, Monaco, Courier New, monospace; font-size: 14px; line-height: 1.6; overflow-x: auto; white-space: pre-wrap; word-break: break-all; max-height: 500px; overflow-y: auto; }

.loading, .error { text-align: center; padding: 60px 0; color: var(--color-muted); }
.author-link { color: var(--color-primary); font-weight: 500; }
.author-link:hover { text-decoration: underline; }
</style>
