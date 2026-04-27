<template>
  <div class="home">
    <div class="hero">
      <h1>Wikiio</h1>
      <p>Fandom 维基数据分析与评分平台</p>
      <div class="buttons" v-if="!authStore.isLoggedIn">
        <a href="/register" class="btn-primary">立即注册</a>
        <a href="/login" class="btn-secondary">登录</a>
      </div>
      <div class="search-quick">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索页面..."
          @keyup.enter="goSearch"
        />
        <button @click="goSearch">搜索</button>
      </div>
    </div>

    <div class="content">
      <!-- 数据统计卡片 -->
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
        <!-- 最新页面列表 -->
        <div class="section">
          <h2>最新页面</h2>
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else>
            <div
              class="page-item"
              v-for="page in pages"
              :key="page.id"
              @click="goToPage(page.id)"
            >
              <div class="page-title">{{ page.title }}</div>
              <div class="page-meta">
                <span>作者：{{ page.author || '未知' }}</span>
                <span>{{ page.word_count }} 字</span>
                <span>{{ formatDate(page.last_edited_at) }}</span>
              </div>
              <div class="page-cats" v-if="page.categories.length">
                <span class="cat-tag" v-for="cat in page.categories.slice(0,3)" :key="cat">
                  {{ cat }}
                </span>
              </div>
            </div>
          </div>
          <div class="load-more" v-if="hasMore" @click="loadMore">加载更多</div>
        </div>

        <!-- 作者排名 -->
        <div class="section">
          <h2>创作者排名</h2>
          <div v-if="topAuthors.length">
            <div class="author-item" v-for="(author, index) in topAuthors" :key="author.author">
              <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
              <span class="author-name">{{ author.author }}</span>
              <span class="author-count">{{ author.page_count }} 篇</span>
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
import { useAuthStore } from '../stores/auth.js'
import { pageAPI } from '../api/index.js'

const router = useRouter()
const authStore = useAuthStore()

const SITE_ID = 'scp-zh'
const stats = ref(null)
const pages = ref([])
const topAuthors = ref([])
const loading = ref(true)
const skip = ref(0)
const hasMore = ref(true)

function formatNumber(n) {
  if (!n) return '0'
  return n.toLocaleString('zh-CN')
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

function goToPage(id) {
  router.push(`/page/${id}`)
}

async function loadPages() {
  loading.value = true
  try {
    const result = await pageAPI.list({
      site_id: SITE_ID,
      skip: skip.value,
      limit: 20,
      order_by: 'last_edited_at'
    })
    pages.value.push(...result)
    hasMore.value = result.length === 20
    skip.value += result.length
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  await loadPages()
}

onMounted(async () => {
  try {
    stats.value = await pageAPI.stats(SITE_ID)
    topAuthors.value = await pageAPI.topAuthors(SITE_ID, 10)
    await loadPages()
  } catch (e) {
    console.error(e)
  }
})

const searchQuery = ref('')
function goSearch() {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
  } else {
    router.push('/search')
  }
}
</script>

<style scoped>
.home { min-height: 100vh; background: #f5f7fa; }
.hero {
  background: linear-gradient(135deg, #c7c7c7 0%, #858585 100%);
  color: white;
  text-align: center;
  padding: 3rem 1rem;
}
.hero h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
.hero p { font-size: 1.1rem; opacity: 0.9; margin-bottom: 1.5rem; }
.buttons { display: flex; gap: 1rem; justify-content: center; }
.btn-primary {
  padding: 0.7rem 2rem;
  background: white;
  color: #141414;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
}
.btn-secondary {
  padding: 0.7rem 2rem;
  border: 2px solid white;
  color: white;
  border-radius: 4px;
  text-decoration: none;
}

.content { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-number { font-size: 2rem; font-weight: bold; color: #667eea; }
.stat-label { color: #888; margin-top: 0.3rem; }

.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}
.section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.section h2 { margin-bottom: 1rem; font-size: 1.1rem; color: #333; }

.page-item {
  padding: 0.8rem 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.page-item:hover { background: #f9f9f9; margin: 0 -1rem; padding: 0.8rem 1rem; }
.page-title { font-weight: 500; color: #333; margin-bottom: 0.3rem; }
.page-meta { font-size: 0.8rem; color: #888; display: flex; gap: 1rem; margin-bottom: 0.3rem; }
.page-cats { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.cat-tag {
  font-size: 0.75rem;
  background: #f0f0f0;
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
  color: #666;
}

.author-item {
  display: flex;
  align-items: center;
  padding: 0.6rem 0;
  border-bottom: 1px solid #f0f0f0;
}
.rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ddd;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
  margin-right: 0.8rem;
  flex-shrink: 0;
}
.rank-1 { background: #f5a623; }
.rank-2 { background: #9b9b9b; }
.rank-3 { background: #c47e3a; }
.author-name { flex: 1; }
.author-count { color: #888; font-size: 0.85rem; }

.load-more {
  text-align: center;
  padding: 1rem;
  color: #667eea;
  cursor: pointer;
  margin-top: 0.5rem;
}
.loading { text-align: center; color: #888; padding: 2rem; }

.search-quick { display: flex; gap: 0.5rem; justify-content: center; margin-top: 1rem; max-width: 500px; margin-left: auto; margin-right: auto; }
.search-quick input { flex: 1; padding: 0.6rem 1rem; border: none; border-radius: 4px; font-size: 1rem; }
.search-quick button { padding: 0.6rem 1.2rem; background: #4a3f8f; color: white; border: 2px solid white; border-radius: 4px; cursor: pointer; }
</style>