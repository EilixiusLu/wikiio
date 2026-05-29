<template>
  <div class="detail-page">
    <div class="topbar">
      <span class="back" @click="router.back()">← 返回</span>
      <a v-if="page" :href="wikiUrl" target="_blank" class="wiki-link">在维基上查看 →</a>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="page">
      <!-- 基本信息卡片 -->
      <div class="card">
        <h1>{{ page.title }}</h1>
        <div class="meta">
           <span>作者：
            <a v-if="page.author" :href="`/author/${page.author}`" class="author-link" @click.stop>
              {{ page.author }}
            </a>
            <b v-else>未知</b>
          </span>
          <span>字数：{{ page.word_count }}</span>
          <span>最后编辑：{{ formatDate(page.last_edited_at) }}</span>
        </div>
        <div class="categories" v-if="page.categories.length">
          <span class="cat-tag" v-for="cat in page.categories" :key="cat">{{ cat }}</span>
        </div>
        <!-- 评分区域 -->
        <div class="rating-box">
          <div class="rating-left">
            <div class="rating-score">{{ page.rating_avg.toFixed(1) }}</div>
            <div class="rating-stars-display">
              <span
                v-for="i in 5" :key="i"
                class="star"
                :class="{ filled: i <= Math.round(page.rating_avg) }"
              >★</span>
            </div>
            <div class="rating-count">{{ page.rating_count }} 人评分</div>
          </div>

          <div class="rating-right">
            <!-- 未登录 -->
            <div v-if="!authStore.isLoggedIn" class="rating-hint">
              <a href="/login">登录</a>后才能评分
            </div>
            <!-- 已登录但未绑定Fandom -->
            <div v-else-if="!authStore.user?.is_fandom_verified" class="rating-hint">
              请先<a href="/profile">绑定Fandom账户</a>才能评分
            </div>
            <!-- 已登录已绑定，可以评分 -->
            <div v-else>
              <div class="my-rating-label">
                {{ myScore ? '我的评分' : '点击评分' }}
              </div>
              <div class="stars-input">
                <span
                  v-for="i in 5" :key="i"
                  class="star-input"
                  :class="{
                    filled: i <= (hoverScore || myScore),
                    hovered: i <= hoverScore
                  }"
                  @mouseenter="hoverScore = i"
                  @mouseleave="hoverScore = 0"
                  @click="submitRating(i)"
                >★</span>
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

        <!-- 原站评分（仅RatePage维基显示） -->
      <div class="card site-rating-card" v-if="siteRating">
        <h2>原站评分</h2>
        <div class="site-rating-box">
          <div class="site-rating-left">
            <div class="site-rating-score">{{ siteRating.avg_rating.toFixed(1) }}</div>
            <div class="site-rating-label">/ 10</div>
          </div>
          <div class="site-rating-right">
            <div class="site-rating-bar-wrap">
              <div class="site-rating-bar" :style="{ width: (siteRating.avg_rating / 10 * 100) + '%' }"></div>
            </div>
            <div class="site-rating-meta">
              <span>{{ siteRating.total_votes }} 票</span>
              <span>总分 {{ siteRating.total_points }}</span>
            </div>
          </div>
        </div>
        <div class="site-rating-note">数据来源：原站 RatePage 扩展</div>
      </div>
      </div>

      <!-- 编辑历史卡片 -->
      <div class="card">
        <h2>编辑历史</h2>
        <div class="rev-item" v-for="rev in page.recent_revisions" :key="rev.rev_id">
          <div class="rev-row">
            <span class="rev-editor">{{ rev.editor }}</span>
            <span class="rev-time">{{ formatDate(rev.timestamp) }}</span>
          </div>
          <div class="rev-comment">{{ rev.comment || '（无编辑摘要）' }}</div>
        </div>
      </div>

      <!-- Wikitext 源代码卡片 -->
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
import { pageAPI, siteAPI } from '../api/index.js'
import { ratingAPI } from '../api/index.js'
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
  const slug = encodeURIComponent(page.value.slug)
  return `${base}/wiki/${slug}`
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

async function copyWikitext() {
  if (!page.value?.wikitext) return
  await navigator.clipboard.writeText(page.value.wikitext)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

onMounted(async () => {
  try {
    page.value = await pageAPI.get(route.params.id)
    // 根据 page.site_id 加载站点信息，用于动态维基链接
    if (page.value?.site_id) {
      try {
        site.value = await siteAPI.get(page.value.site_id)
      } catch {
        // 站点加载失败时用 fallback
        site.value = null
      }
    }
    await Promise.all([loadMyRating(), loadSiteRating()])
  } catch {
    page.value = null
  } finally {
    loading.value = false
  }
})

const authStore = useAuthStore()
const myScore = ref(0)
const hoverScore = ref(0)
const ratingMsg = ref('')
const ratingError = ref('')

async function loadMyRating() {
  if (!authStore.isLoggedIn) return
  try {
    const res = await ratingAPI.getMine(route.params.id)
    myScore.value = res.score || 0
  } catch {}
}

async function submitRating(score) {
  ratingError.value = ''
  ratingMsg.value = ''
  try {
    const res = await ratingAPI.rate(route.params.id, score)
    myScore.value = score
    page.value.rating_avg = res.rating_avg
    page.value.rating_count = res.rating_count
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
    const res = await ratingAPI.get(route.params.id)
    page.value.rating_avg = res.rating_avg
    page.value.rating_count = res.rating_count
    ratingMsg.value = '已删除评分'
    setTimeout(() => ratingMsg.value = '', 2000)
  } catch {}
}

const siteRating = ref(null)

async function loadSiteRating() {
  try {
    const res = await pageAPI.siteRating(route.params.id)
    if (res.available) {
      siteRating.value = res
    }
  } catch {}
}
</script>

<style scoped>
.detail-page { max-width: 860px; margin: 0 auto; padding: 2rem 1rem; }

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e8e8e8;
}
.back {
  color: #185897;
  cursor: pointer;
  font-size: 0.9rem;
}
.wiki-link {
  color: #185897;
  text-decoration: none;
  font-size: 0.9rem;
  border: 1px solid #185897;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
}
.wiki-link:hover { background: #185897; color: white; }

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 1.5rem;
}

h1 { font-size: 1.5rem; margin-bottom: 1rem; }
h2 { font-size: 1.1rem; margin-bottom: 1rem; color: #333; }

.meta { display: flex; gap: 1.5rem; color: #888; font-size: 0.9rem; margin-bottom: 1rem; flex-wrap: wrap; }
.categories { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.cat-tag {
  background: #f0f0f0;
  padding: 0.2rem 0.7rem;
  border-radius: 10px;
  font-size: 0.8rem;
  color: #555;
}

.rating-box {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1.2rem;
  background: #f9f9f9;
  border-radius: 8px;
  flex-wrap: wrap;
}
.rating-left { display: flex; flex-direction: column; align-items: center; gap: 0.3rem; }
.rating-score { font-size: 2.5rem; font-weight: bold; color: #f5a623; line-height: 1; }
.rating-stars-display .star { font-size: 1.2rem; color: #ddd; }
.rating-stars-display .star.filled { color: #f5a623; }
.rating-count { color: #888; font-size: 0.8rem; }

.rating-right { flex: 1; }
.rating-hint { font-size: 0.88rem; color: #888; }
.rating-hint a { color: #185897; }

.my-rating-label { font-size: 0.85rem; color: #666; margin-bottom: 0.4rem; }
.stars-input { display: flex; gap: 0.2rem; }
.star-input {
  font-size: 2rem;
  color: #ddd;
  cursor: pointer;
  transition: color 0.1s, transform 0.1s;
}
.star-input.filled { color: #f5a623; }
.star-input.hovered { color: #f5a623; transform: scale(1.15); }

.rating-actions { display: flex; align-items: center; gap: 0.8rem; margin-top: 0.4rem; }
.rating-score-label { font-size: 0.85rem; color: #666; }
.btn-remove-rating {
  font-size: 0.78rem; color: #aaa;
  background: none; border: none; cursor: pointer; padding: 0;
}
.btn-remove-rating:hover { color: #e74c3c; }
.rating-msg { font-size: 0.85rem; margin-top: 0.4rem; }
.rating-msg.success { color: #27ae60; }
.rating-msg.error { color: #e74c3c; }

.rev-item { padding: 0.7rem 0; border-bottom: 1px solid #f0f0f0; }
.rev-item:last-child { border-bottom: none; }
.rev-row { display: flex; justify-content: space-between; margin-bottom: 0.2rem; }
.rev-editor { font-weight: 500; font-size: 0.9rem; }
.rev-time { color: #aaa; font-size: 0.8rem; }
.rev-comment { color: #888; font-size: 0.85rem; }

.wikitext-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.copy-btn {
  padding: 0.3rem 0.8rem;
  background: #185897;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.copy-btn:hover { background: #185897dd; }

.wikitext {
  background: #f8f8f8;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.82rem;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 500px;
  overflow-y: auto;
}

.loading { text-align: center; padding: 3rem; color: #888; }
.error { text-align: center; padding: 3rem; color: #e74c3c; }

.author-link { color: #185897; font-weight: 500; text-decoration: none; }
.author-link:hover { text-decoration: underline; }

.site-rating-card h2 { margin-bottom: 1rem; }
.site-rating-box { display: flex; align-items: center; gap: 1.5rem; }
.site-rating-left { display: flex; align-items: baseline; gap: 0.3rem; flex-shrink: 0; }
.site-rating-score { font-size: 2.8rem; font-weight: bold; color: #185897; line-height: 1; }
.site-rating-label { font-size: 1rem; color: #aaa; }
.site-rating-right { flex: 1; }
.site-rating-bar-wrap {
  height: 8px; background: #f0f0f0;
  border-radius: 4px; overflow: hidden; margin-bottom: 0.5rem;
}
.site-rating-bar {
  height: 100%; background: #185897;
  border-radius: 4px; transition: width 0.5s ease;
}
.site-rating-meta { display: flex; gap: 1rem; color: #888; font-size: 0.85rem; }
.site-rating-note { color: #bbb; font-size: 0.75rem; margin-top: 0.8rem; }
</style>