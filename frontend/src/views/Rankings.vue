<template>
  <div class="rankings-page">
    <div class="page-header">
      <h1>作者排名</h1>
      <div class="site-selector">
        <label>选择站点：</label>
        <select v-model="selectedSite" @change="onSiteChange">
          <option v-for="site in sites" :key="site.site_id" :value="site.site_id">
            {{ site.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Tab切换 -->
    <div class="tabs">
      <button :class="{ active: tab === 'rating' }" @click="switchTab('rating')">
        ★ 评分榜
      </button>
      <button :class="{ active: tab === 'author_pages' }" @click="switchTab('author_pages')">
        📄 作者页面数榜
      </button>
      <button :class="{ active: tab === 'author_rating' }" @click="switchTab('author_rating')">
        🏆 作者评分榜
      </button>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">加载中...</div>

      <!-- 评分榜 -->
      <div v-else-if="tab === 'rating'">
        <div v-if="ratingList.length === 0" class="empty">暂无评分数据，快去评分吧！</div>
        <div class="rank-list" v-else>
          <div class="rank-item" v-for="(page, index) in ratingList" :key="page.id" @click="goToPage(page.id)">
            <div class="rank-num" :class="rankClass(index)">{{ index + 1 }}</div>
            <div class="rank-main">
              <div class="rank-title">{{ page.title }}</div>
              <div class="rank-meta">
                <span>{{ page.author || '未知' }}</span>
                <span>{{ page.word_count }} 字</span>
                <span>{{ formatDate(page.last_edited_at) }}</span>
              </div>
              <div class="rank-cats">
                <span class="cat-tag" v-for="cat in page.categories.slice(0,3)" :key="cat">{{ cat }}</span>
              </div>
            </div>
            <div class="rank-score">
              <div class="score-num">{{ page.rating_avg.toFixed(1) }}</div>
              <div class="score-stars">
                <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(page.rating_avg) }">★</span>
              </div>
              <div class="score-count">{{ page.rating_count }} 人</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 作者页面数榜 / 作者评分榜 -->
      <div v-else>
        <div class="rank-list">
          <div class="rank-item author-item" v-for="(author, index) in authorList" :key="author.author">
            <div class="rank-num" :class="rankClass(index)">{{ index + 1 }}</div>
            <div class="rank-main">
              <div class="rank-title">{{ author.author }}</div>
              <div class="rank-meta">
                <span>{{ author.page_count }} 篇文章</span>
                <span>{{ author.total_words.toLocaleString() }} 字</span>
              </div>
            </div>
            <div class="rank-score">
              <div class="score-num">{{ author.page_count }}</div>
              <div class="score-label" v-if="tab === 'author_pages'">篇</div>
              <template v-else>
                <div class="score-stars">
                  <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(author.avg_rating) }">★</span>
                </div>
                <div class="score-count">{{ author.avg_rating.toFixed(1) }} 分</div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { pageAPI, siteAPI } from '../api/index.js'

const router = useRouter()
const tab = ref('rating')
const selectedSite = ref('')
const sites = ref([])
const ratingList = ref([])
const authorList = ref([])
const loading = ref(false)

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

function goToPage(id) {
  router.push(`/page/${id}`)
}

function rankClass(index) {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

async function loadData() {
  if (!selectedSite.value) return
  loading.value = true
  try {
    if (tab.value === 'rating') {
      ratingList.value = await pageAPI.rankingByRating(selectedSite.value)
    } else if (tab.value === 'author_pages') {
      authorList.value = await pageAPI.rankingByAuthor(selectedSite.value, 'page_count')
    } else {
      authorList.value = await pageAPI.rankingByAuthor(selectedSite.value, 'rating')
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function switchTab(t) {
  tab.value = t
  await loadData()
}

async function onSiteChange() {
  await loadData()
}

onMounted(async () => {
  try {
    sites.value = await siteAPI.list()
    if (sites.value.length > 0) {
      selectedSite.value = sites.value[0].site_id
      await loadData()
    }
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.rankings-page { max-width: 900px; margin: 0 auto; padding: 2rem 1rem; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
h1 { font-size: 1.5rem; font-weight: 700; }

.site-selector { display: flex; align-items: center; gap: 0.5rem; }
.site-selector label { color: #666; font-size: 0.9rem; }
.site-selector select {
  padding: 0.4rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  outline: none;
}
.site-selector select:focus { border-color: #185897; }

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 0;
}
.tabs button {
  padding: 0.6rem 1.2rem;
  border: none;
  background: none;
  color: #666;
  cursor: pointer;
  font-size: 0.9rem;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s;
}
.tabs button:hover { color: #185897; }
.tabs button.active { color: #185897; border-bottom-color: #185897; font-weight: 500; }

.loading { text-align: center; padding: 3rem; color: #888; }
.empty { text-align: center; padding: 3rem; color: #aaa; }

.rank-list { display: flex; flex-direction: column; gap: 0.8rem; }

.rank-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  border-radius: 8px;
  padding: 1rem 1.2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.rank-item:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
.author-item { cursor: default; }

.rank-num {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
  flex-shrink: 0;
}
.rank-num.gold { background: #ffd700; color: #7a5800; }
.rank-num.silver { background: #c0c0c0; color: #444; }
.rank-num.bronze { background: #cd7f32; color: white; }

.rank-main { flex: 1; min-width: 0; }
.rank-title {
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rank-meta { display: flex; gap: 1rem; color: #888; font-size: 0.82rem; margin-bottom: 0.3rem; }
.rank-cats { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.cat-tag {
  font-size: 0.72rem;
  background: #f0f0f0;
  padding: 0.1rem 0.4rem;
  border-radius: 8px;
  color: #666;
}

.rank-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  min-width: 70px;
}
.score-num { font-size: 1.6rem; font-weight: bold; color: #f5a623; line-height: 1; }
.score-stars .star { font-size: 0.85rem; color: #ddd; }
.score-stars .star.filled { color: #f5a623; }
.score-count { color: #aaa; font-size: 0.75rem; margin-top: 0.2rem; }
.score-label { color: #888; font-size: 0.85rem; }
</style>