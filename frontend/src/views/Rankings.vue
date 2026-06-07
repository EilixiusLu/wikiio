<template>
  <div class="rankings-page">
    <div class="page-header">
      <h1>排名</h1>
      <div class="site-selector">
        <label>选择站点</label>
        <select v-model="selectedSite" @change="onSiteChange">
          <option v-for="site in sites" :key="site.site_id" :value="site.site_id">
            {{ site.name }}
          </option>
        </select>
      </div>
    </div>

    <div class="tabs">
      <button :class="{ active: tab === 'rating' }" @click="switchTab('rating')">
        <i class="fa fa-star"></i> 评分榜
      </button>
      <button :class="{ active: tab === 'author_pages' }" @click="switchTab('author_pages')">
        <i class="fa fa-file-text-o"></i> 页面数榜
      </button>
      <button :class="{ active: tab === 'author_rating' }" @click="switchTab('author_rating')">
        <i class="fa fa-trophy"></i> 作者评分榜
      </button>
      <button
        v-if="currentSite?.has_ratepage"
        :class="{ active: tab === 'site_rating' }"
        @click="switchTab('site_rating')"
      >
        <i class="fa fa-globe"></i> 原站评分榜
      </button>
    </div>

    <div class="content">
      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="tab === 'rating'">
        <div v-if="ratingList.length === 0" class="empty">暂无评分数据</div>
        <TransitionGroup name="list" tag="div" class="rank-list" v-else>
          <div
            class="rank-item"
            v-for="(page, index) in ratingList"
            :key="page.id"
            @click="goToPage(page.id)"
          >
            <span class="rank-num">{{ index + 1 }}</span>
            <div class="rank-main">
              <div class="rank-title">{{ page.title }}</div>
              <div class="rank-meta">
                <span>{{ page.author || '未知' }}</span>
                <span>{{ page.word_count }} 字</span>
                <span>{{ formatDate(page.last_edited_at) }}</span>
              </div>
              <div class="rank-cats">
                <span class="cat-tag" v-for="cat in page.categories.slice(0,3)" :key="cat">
                  {{ cat }}
                </span>
              </div>
            </div>
            <div class="rank-score">
              <div class="score-num">{{ page.rating_avg.toFixed(1) }}</div>
              <div class="score-stars">
                <i
                  v-for="i in 5" :key="i"
                  class="fa fa-star star"
                  :class="{ filled: i <= Math.round(page.rating_avg) }"
                ></i>
              </div>
              <div class="score-count">{{ page.rating_count }} 人</div>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <div v-else-if="tab === 'site_rating'">
        <div v-if="siteRatingList.length === 0" class="empty">暂无原站评分数据</div>
        <TransitionGroup name="list" tag="div" class="rank-list" v-else>
          <div
            class="rank-item"
            v-for="(page, index) in siteRatingList"
            :key="page.id"
            @click="goToPage(page.id)"
          >
            <span class="rank-num">{{ index + 1 }}</span>
            <div class="rank-main">
              <div class="rank-title">{{ page.title }}</div>
              <div class="rank-meta">
                <span>{{ page.author || '未知' }}</span>
                <span>{{ page.word_count }} 字</span>
                <span>{{ formatDate(page.last_edited_at) }}</span>
              </div>
              <div class="rank-cats">
                <span class="cat-tag" v-for="cat in page.categories.slice(0,3)" :key="cat">
                  {{ cat }}
                </span>
              </div>
            </div>
            <div class="rank-score">
              <div class="score-num">{{ (page.site_rating_avg / 2).toFixed(1) }}</div>
              <div class="score-stars">
                <i
                  v-for="i in 5" :key="i"
                  class="fa fa-star star"
                  :class="{ filled: i <= Math.round(page.site_rating_avg / 2) }"
                ></i>
              </div>
              <div class="score-count">{{ page.site_rating_count }} 票</div>
            </div>
          </div>
        </TransitionGroup>
      </div>

      <TransitionGroup v-else name="list" tag="div" class="rank-list">
        <div
          class="rank-item"
          v-for="(author, index) in authorList"
          :key="author.author"
        >
          <span class="rank-num">{{ index + 1 }}</span>
          <div class="rank-main">
            <a :href="`/author/${author.author}`" class="rank-title">
              {{ author.author }}
            </a>
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
                <i
                  v-for="i in 5" :key="i"
                  class="fa fa-star star"
                  :class="{ filled: i <= Math.round(author.avg_rating) }"
                ></i>
              </div>
              <div class="score-count">{{ author.avg_rating.toFixed(1) }} 分</div>
            </template>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { pageAPI, siteAPI } from '../api/index.js'

const router = useRouter()
const tab = ref('rating')
const selectedSite = ref('')
const sites = ref([])
const ratingList = ref([])
const authorList = ref([])
const siteRatingList = ref([])
const loading = ref(false)

const currentSite = computed(() => sites.value.find(s => s.site_id === selectedSite.value))

function formatDate(d) { if (!d) return ''; return new Date(d).toLocaleDateString('zh-CN') }
function goToPage(id) { router.push(`/page/${id}`) }

async function loadData() {
  if (!selectedSite.value) return
  loading.value = true
  try {
    if (tab.value === 'rating') {
      ratingList.value = await pageAPI.rankingByRating(selectedSite.value)
    } else if (tab.value === 'author_pages') {
      authorList.value = await pageAPI.rankingByAuthor(selectedSite.value, 'page_count')
    } else if (tab.value === 'author_rating') {
      authorList.value = await pageAPI.rankingByAuthor(selectedSite.value, 'rating')
    } else if (tab.value === 'site_rating') {
      siteRatingList.value = await pageAPI.rankingBySiteRating(selectedSite.value)
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function switchTab(t) { tab.value = t; await loadData() }
async function onSiteChange() { await loadData() }

onMounted(async () => {
  try {
    sites.value = await siteAPI.list()
    if (sites.value.length > 0) { selectedSite.value = sites.value[0].site_id; await loadData() }
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.rankings-page { max-width: 900px; margin: 0 auto; padding: var(--space-16) var(--space-6); }

.page-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: var(--space-8);
}
.page-header h1 {
  font-size: var(--text-2xl); font-weight: 600;
  color: var(--color-ink); letter-spacing: -0.02em;
}
.site-selector { display: flex; align-items: center; gap: var(--space-2); font-size: var(--text-sm); }
.site-selector label { color: var(--color-muted); }
.site-selector select {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-hairline); border-radius: var(--radius-sm);
  font-size: var(--text-sm); font-family: inherit;
  color: var(--color-ink); outline: none; background: var(--color-canvas);
  transition: border-color var(--duration-fast) var(--ease-smooth);
}
.site-selector select:focus { border-color: var(--color-primary); }

.tabs {
  display: flex; gap: var(--space-1);
  margin-bottom: var(--space-8);
  border-bottom: 1px solid var(--color-hairline);
}
.tabs button {
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

.rank-list { display: flex; flex-direction: column; position: relative; }
.rank-item {
  display: flex; align-items: center; gap: var(--space-4);
  background: var(--color-canvas);
  border: 2px solid transparent;
  border-radius: var(--radius-card);
  padding: var(--space-5) var(--space-6);
  margin-bottom: var(--space-3); cursor: pointer;
  transition: background-color var(--duration-base) var(--ease-smooth),
              border-color var(--duration-base) var(--ease-smooth);
}
.rank-item:hover { border-color: var(--color-primary); background-color: #e8f0fc; }

.rank-num {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--color-parchment); color: var(--color-ink);
  display: flex; align-items: center; justify-content: center;
  font-size: var(--text-base); font-weight: 600; flex-shrink: 0;
}
.rank-main { flex: 1; min-width: 0; }
.rank-title {
  font-size: var(--text-base); font-weight: 500; color: var(--color-ink);
  margin-bottom: var(--space-1);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  display: block;
}
.rank-meta { display: flex; gap: var(--space-3); color: var(--color-muted); font-size: var(--text-sm); }
.rank-cats { display: flex; gap: var(--space-1); margin-top: var(--space-1); }
.cat-tag {
  font-size: var(--text-xs); background: var(--color-parchment);
  padding: 1px var(--space-2); border-radius: var(--radius-pill);
  color: var(--color-muted);
}
.rank-score {
  display: flex; flex-direction: column;
  align-items: center; flex-shrink: 0; min-width: 70px;
}
.score-num { font-size: var(--text-2xl); font-weight: 600; color: var(--color-primary); line-height: 1; }
.score-stars .star { font-size: var(--text-xs); color: var(--color-hairline); }
.score-stars .star.filled { color: var(--color-primary); }
.score-count { color: var(--color-muted); font-size: var(--text-xs); margin-top: var(--space-1); }
.score-label { color: var(--color-muted); font-size: var(--text-sm); }

.loading, .empty { text-align: center; padding: var(--space-16) 0; color: var(--color-muted); }

@media (max-width: 600px) {
  .page-header { flex-direction: column; gap: var(--space-4); align-items: flex-start; }
  .tabs { flex-wrap: wrap; }
  .rank-item { flex-wrap: wrap; padding: var(--space-4); }
}
</style>
