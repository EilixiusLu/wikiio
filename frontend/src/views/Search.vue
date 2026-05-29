<template>
  <div class="search-page">
    <div class="search-hero">
      <div class="search-bar">
        <input
          v-model="query"
          type="text"
          placeholder="搜索页面标题、作者或正文..."
          @keyup.enter="doSearch"
        />
        <button @click="doSearch">搜索</button>
      </div>
    </div>

    <div class="content">
      <!-- 筛选栏 -->
      <div class="filters">
        <div class="filter-group">
          <label>选择站点</label>
          <select v-model="selectedSite" @change="onSiteChange">
            <option value="">全部站点</option>
            <option v-for="site in sites" :key="site.site_id" :value="site.site_id">
              {{ site.name }}
            </option>
          </select>
        </div>
        <div class="filter-group" v-if="selectedSite">
          <label>分类筛选</label>
          <select v-model="selectedCategory" @change="doSearch">
            <option value="">全部分类</option>
            <option v-for="cat in categories" :key="cat.name" :value="cat.name">
              {{ cat.name }} ({{ cat.count }})
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label>排序</label>
          <select v-model="orderBy" @change="doSearch">
            <option value="last_edited_at">最新编辑</option>
            <option value="rating">评分最高</option>
            <option value="word_count">字数最多</option>
          </select>
        </div>
        <div class="filter-group">
          <label>
            <input type="checkbox" v-model="searchWikitext" @change="doSearch" />
            搜索正文内容
          </label>
        </div>
      </div>

      <!-- 搜索结果 -->
      <div class="results">
        <div v-if="loading" class="loading">搜索中...</div>

        <div v-else-if="searched">
          <div class="result-count" v-if="total > 0">
            共找到 {{ total }} 个结果
          </div>
          <div class="no-result" v-else>
            没有找到与"{{ lastQuery }}"相关的页面
          </div>

          <div
            class="result-item"
            v-for="page in results"
            :key="page.id"
            @click="goToPage(page.id)"
          >
            <div class="result-title">
              <span v-html="highlight(page.title)"></span>
              <span class="match-badge" v-for="m in page.match_in" :key="m">{{ m }}</span>
            </div>
            <div class="result-meta">
              <span>作者：<b>{{ page.author || '未知' }}</b></span>
              <span>{{ page.word_count }} 字</span>
              <span v-if="page.rating_count > 0">
                ★ {{ page.rating_avg.toFixed(1) }} ({{ page.rating_count }}人)
              </span>
              <span>{{ formatDate(page.last_edited_at) }}</span>
            </div>
            <!-- 正文匹配片段 -->
            <div class="snippet" v-if="page.snippet">
              <span v-html="highlight(page.snippet)"></span>
            </div>
            <div class="result-cats" v-if="page.categories.length">
              <span class="cat-tag" v-for="cat in page.categories.slice(0,4)" :key="cat">
                {{ cat }}
              </span>
            </div>
          </div>

          <!-- 分页 -->
          <div class="pagination" v-if="total > limit">
            <button :disabled="skip === 0" @click="prevPage">上一页</button>
            <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
            <button :disabled="skip + limit >= total" @click="nextPage">下一页</button>
          </div>
        </div>

        <!-- 未搜索时显示热门分类或提示 -->
        <div v-else class="categories-section">
          <template v-if="selectedSite">
            <h3>浏览分类</h3>
            <div class="cat-grid" v-if="categories.length > 0">
              <div
                class="cat-card"
                v-for="cat in categories"
                :key="cat.name"
                @click="browseCategory(cat.name)"
              >
                <div class="cat-name">{{ cat.name }}</div>
                <div class="cat-count">{{ cat.count }} 篇</div>
              </div>
            </div>
            <div v-else class="loading">该站点暂无分类数据</div>
          </template>
          <div v-else class="no-site-hint">
            <h3>请先选择一个站点</h3>
            <p class="hint-text">选择站点后可以按分类浏览，或在搜索框中输入关键词搜索全站内容</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { pageAPI, siteAPI } from '../api/index.js'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const query = ref('')
const lastQuery = ref('')
const selectedSite = ref('')
const selectedCategory = ref('')
const orderBy = ref('last_edited_at')
const results = ref([])
const total = ref(0)
const skip = ref(0)
const limit = 20
const loading = ref(false)
const searched = ref(false)
const sites = ref([])
const categories = ref([])
const searchWikitext = ref(true)

const currentPage = computed(() => Math.floor(skip.value / limit) + 1)
const totalPages = computed(() => Math.ceil(total.value / limit))

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

function goToPage(id) {
  router.push(`/page/${id}`)
}

function highlight(text) {
  if (!query.value) return text
  const escaped = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(escaped, 'gi'), match => `<mark>${match}</mark>`)
}

async function doSearch() {
  if (!query.value.trim() && !selectedCategory.value) return
  skip.value = 0
  await fetchResults()
}

async function onSiteChange() {
  selectedCategory.value = ''
  // 切换站点时重新加载分类
  if (selectedSite.value) {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/v1/search/categories', {
        params: { site_id: selectedSite.value }
      })
      categories.value = res.data
    } catch {
      categories.value = []
    }
  } else {
    categories.value = []
  }
  await doSearch()
}

async function fetchResults() {
  loading.value = true
  searched.value = true
  lastQuery.value = query.value
  try {
    const params = {
      q: query.value || selectedCategory.value || ' ',
      site_id: selectedSite.value || undefined,
      skip: skip.value,
      limit,
      search_wikitext: searchWikitext.value,
      order_by: orderBy.value,
    }
    if (selectedCategory.value) params.category = selectedCategory.value

    const res = await axios.get('http://127.0.0.1:8000/api/v1/search/', { params })
    results.value = res.data.results
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function prevPage() {
  skip.value = Math.max(0, skip.value - limit)
  fetchResults()
}

function nextPage() {
  skip.value += limit
  fetchResults()
}

async function browseCategory(cat) {
  selectedCategory.value = cat
  query.value = ''
  await fetchResults()
}

onMounted(async () => {
  // 加载站点列表
  try {
    sites.value = await siteAPI.list()
    // 如果只有一个站点，自动选中；否则默认"全部站点"
    if (sites.value.length === 1) {
      selectedSite.value = sites.value[0].site_id
    }
  } catch (e) {
    console.error(e)
  }

  // 如果有选中的站点，加载其分类
  if (selectedSite.value) {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/v1/search/categories', {
        params: { site_id: selectedSite.value }
      })
      categories.value = res.data
    } catch (e) {
      console.error(e)
    }
  }

  // 如果URL带了搜索参数
  if (route.query.q) {
    query.value = route.query.q
    await doSearch()
  }
})
</script>

<style scoped>
.search-page { min-height: 100vh; background: #f5f7fa; }

.search-hero {
  background: #F0F0F0;
  padding: 2rem 1rem;
}
.search-bar { display: flex; max-width: 600px; margin: 0 auto; }
.search-bar input {
  flex: 1;
  padding: 0.75rem 1.2rem;
  border: none;
  border-radius: 6px 0 0 6px;
  font-size: 0.95rem;
  outline: none;
}
.search-bar button {
  padding: 0.75rem 1.5rem;
  background: #185897;
  color: white;
  border: none;
  border-radius: 0 6px 6px 0;
  cursor: pointer;
  font-size: 0.95rem;
}
.search-bar button:hover { background: #134a7f; }

.content { max-width: 1000px; margin: 0 auto; padding: 1.5rem 1rem; }

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.filter-group { display: flex; align-items: center; gap: 0.5rem; }
.filter-group label { color: #666; font-size: 0.9rem; }
.filter-group select {
  padding: 0.4rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.results { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.result-count { color: #888; margin-bottom: 1rem; font-size: 0.9rem; }
.no-result { text-align: center; padding: 3rem; color: #888; }
.loading { text-align: center; padding: 3rem; color: #888; }

.result-item {
  padding: 1rem 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.result-item:hover { background: #f9f9f9; margin: 0 -1rem; padding: 1rem; }
.result-title { font-size: 1.1rem; font-weight: 500; color: #333; margin-bottom: 0.4rem; }
.result-title :deep(mark) { background: #fff3cd; padding: 0 2px; border-radius: 2px; }
.result-meta { display: flex; gap: 1rem; color: #888; font-size: 0.85rem; margin-bottom: 0.4rem; }
.result-cats { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.cat-tag {
  font-size: 0.75rem;
  background: #f0f0f0;
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
  color: #666;
}

.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.5rem; }
.pagination button {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.pagination button:disabled { background: #ddd; cursor: not-allowed; }

.categories-section h3 { margin-bottom: 1rem; color: #333; }
.no-site-hint { text-align: center; padding: 2rem 0; }
.no-site-hint h3 { color: #888; margin-bottom: 0.5rem; }
.hint-text { color: #aaa; font-size: 0.9rem; }
.cat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.8rem; }
.cat-card {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  text-align: center;
  transition: background 0.2s;
}
.cat-card:hover { background: #e8ecff; }
.cat-name { font-weight: 500; color: #333; margin-bottom: 0.3rem; }
.cat-count { color: #888; font-size: 0.85rem; }

.match-badge {
  display: inline-block;
  font-size: 0.7rem;
  background: #e8ecff;
  color: #667eea;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  margin-left: 0.5rem;
  vertical-align: middle;
}
.snippet {
  font-size: 0.85rem;
  color: #666;
  background: #f9f9f9;
  padding: 0.4rem 0.7rem;
  border-left: 3px solid #667eea;
  margin: 0.4rem 0;
  border-radius: 0 4px 4px 0;
}
.snippet :deep(mark) { background: #fff3cd; padding: 0 2px; border-radius: 2px; }
</style>