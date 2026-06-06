<template>
  <div class="search-page">
    <section class="hero-search-section">
      <div class="search-bar-wrap">
        <i class="fa fa-search search-icon"></i>
        <input v-model="query" type="text" placeholder="搜索页面标题、作者或正文..." @keyup.enter="doSearch" />
        <button @click="doSearch">搜索</button>
      </div>
    </section>

    <div class="content">
      <div class="filters">
        <div class="filter-group">
          <label>选择站点</label>
          <select v-model="selectedSite" @change="onSiteChange">
            <option value="">全部站点</option>
            <option v-for="site in sites" :key="site.site_id" :value="site.site_id">{{ site.name }}</option>
          </select>
        </div>
        <div class="filter-group" v-if="selectedSite">
          <label>分类筛选</label>
          <select v-model="selectedCategory" @change="doSearch">
            <option value="">全部分类</option>
            <option v-for="cat in categories" :key="cat.name" :value="cat.name">{{ cat.name }} ({{ cat.count }})</option>
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
        <div class="filter-group filter-check">
          <label>
            <input type="checkbox" v-model="searchWikitext" @change="doSearch" />
            搜索正文内容
          </label>
        </div>
      </div>

      <div class="results" v-if="searched">
        <div v-if="loading" class="status-msg">搜索中...</div>
        <div v-else>
          <div class="result-count" v-if="total > 0">共找到 {{ total }} 个结果</div>
          <div class="no-result" v-else>没有找到与"{{ lastQuery }}"相关的页面</div>

          <div class="result-item" v-for="page in results" :key="page.id" @click="goToPage(page.id)">
            <div class="result-title">
              <span v-html="highlight(page.title)"></span>
              <span class="match-badge" v-for="m in page.match_in" :key="m">{{ m }}</span>
            </div>
            <div class="result-meta">
              <span>作者：<b>{{ page.author || '未知' }}</b></span>
              <span>{{ page.word_count }} 字</span>
              <span v-if="page.rating_count > 0"><i class="fa fa-star" style="color:var(--color-primary);"></i> {{ page.rating_avg.toFixed(1) }} ({{ page.rating_count }}人)</span>
              <span>{{ formatDate(page.last_edited_at) }}</span>
            </div>
            <div class="snippet" v-if="page.snippet"><span v-html="highlight(page.snippet)"></span></div>
            <div class="result-cats" v-if="page.categories.length">
              <span class="cat-tag" v-for="cat in page.categories.slice(0,4)" :key="cat">{{ cat }}</span>
            </div>
          </div>

          <div class="pagination" v-if="total > limit">
            <button :disabled="skip === 0" @click="prevPage">上一页</button>
            <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
            <button :disabled="skip + limit >= total" @click="nextPage">下一页</button>
          </div>
        </div>
      </div>

      <div v-else class="browse-section">
        <template v-if="selectedSite">
          <h3>浏览分类</h3>
          <div class="cat-grid" v-if="categories.length > 0">
            <div class="cat-card" v-for="cat in categories" :key="cat.name" @click="browseCategory(cat.name)">
              <div class="cat-name">{{ cat.name }}</div>
              <div class="cat-count">{{ cat.count }} 篇</div>
            </div>
          </div>
          <div v-else class="status-msg">该站点暂无分类数据</div>
        </template>
        <div v-else class="no-site-hint">
          <h3>请先选择一个站点</h3>
          <p>选择站点后可以按分类浏览，或在搜索框中输入关键词搜索全站内容</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { siteAPI, searchAPI } from '../api/index.js'

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

function formatDate(d) { if (!d) return ''; return new Date(d).toLocaleDateString('zh-CN') }
function goToPage(id) { router.push(`/page/${id}`) }
function highlight(text) {
  if (!query.value) return text
  const escaped = query.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(escaped, 'gi'), m => `<mark>${m}</mark>`)
}
async function doSearch() { if (!query.value.trim() && !selectedCategory.value) return; skip.value = 0; await fetchResults() }
async function onSiteChange() {
  selectedCategory.value = ''
  if (selectedSite.value) { try { categories.value = await searchAPI.categories(selectedSite.value) } catch { categories.value = [] } }
  else { categories.value = [] }
  await doSearch()
}
async function fetchResults() {
  loading.value = true; searched.value = true; lastQuery.value = query.value
  try {
    const params = { q: query.value || selectedCategory.value || ' ', site_id: selectedSite.value || undefined, skip: skip.value, limit, search_wikitext: searchWikitext.value, order_by: orderBy.value }
    if (selectedCategory.value) params.category = selectedCategory.value
    const res = await searchAPI.search(params); results.value = res.results; total.value = res.total
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}
function prevPage() { skip.value = Math.max(0, skip.value - limit); fetchResults() }
function nextPage() { skip.value += limit; fetchResults() }
async function browseCategory(cat) { selectedCategory.value = cat; query.value = ''; await fetchResults() }

onMounted(async () => {
  try { sites.value = await siteAPI.list(); if (sites.value.length === 1) selectedSite.value = sites.value[0].site_id } catch (e) { console.error(e) }
  if (selectedSite.value) { try { categories.value = await searchAPI.categories(selectedSite.value) } catch (e) { console.error(e) } }
  if (route.query.q) { query.value = route.query.q; await doSearch() }
})
</script>

<style scoped>
.search-page { min-height: 100vh; }

.hero-search-section { background: var(--color-parchment); padding: var(--space-16) 0 var(--space-10); text-align: center; }
.search-bar-wrap { display: flex; align-items: center; max-width: 600px; margin: 0 auto; background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-pill); height: var(--size-input); overflow: hidden; }
.search-icon { color: var(--color-muted); margin-left: var(--space-4); font-size: var(--text-base); flex-shrink: 0; }
.search-bar-wrap input { flex: 1; border: none; outline: none; padding: 0 var(--space-3); font-size: var(--text-base); font-family: inherit; color: var(--color-ink); background: transparent; }
.search-bar-wrap input::placeholder { color: var(--color-muted); }
.search-bar-wrap button { background: var(--color-primary); color: #fff; border: none; padding: 0 var(--space-7, 1.75rem); height: 100%; font-size: var(--text-base); cursor: pointer; font-family: inherit; white-space: nowrap; flex-shrink: 0; }
.search-bar-wrap button:hover { opacity: 0.9; }

.content { max-width: 1000px; margin: 0 auto; padding: var(--space-8) var(--space-6); }

.filters { display: flex; gap: var(--space-4); flex-wrap: wrap; margin-bottom: var(--space-8); background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-card); padding: var(--space-5) var(--space-6); }
.filter-group { display: flex; align-items: center; gap: var(--space-2); font-size: var(--text-sm); }
.filter-group label { color: var(--color-muted); white-space: nowrap; }
.filter-group select { padding: var(--space-1) var(--space-3); border: 1px solid var(--color-hairline); border-radius: var(--radius-sm); font-size: var(--text-sm); font-family: inherit; color: var(--color-ink); outline: none; background: var(--color-canvas); }
.filter-group select:focus { border-color: var(--color-primary); }
.filter-check label { display: flex; align-items: center; gap: var(--space-1); cursor: pointer; }

.results { background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-card); padding: var(--space-6); }
.result-count { font-size: var(--text-sm); color: var(--color-muted); margin-bottom: var(--space-4); }
.no-result, .status-msg { text-align: center; padding: var(--space-12) 0; color: var(--color-muted); }
.result-item { padding: var(--space-5) 0; border-bottom: 1px solid var(--color-hairline); cursor: pointer; }
.result-item:last-child { border-bottom: none; }
.result-title { font-size: var(--text-base); font-weight: 500; color: var(--color-ink); margin-bottom: var(--space-2); }
.result-title :deep(mark) { background: #fff3cd; padding: 0 2px; border-radius: 2px; }
.result-meta { display: flex; gap: var(--space-4); color: var(--color-muted); font-size: var(--text-sm); margin-bottom: var(--space-2); flex-wrap: wrap; }
.result-cats { display: flex; gap: var(--space-1); flex-wrap: wrap; }
.cat-tag { font-size: var(--text-xs); background: var(--color-parchment); padding: 1px var(--space-2); border-radius: var(--radius-pill); color: var(--color-muted); }
.match-badge { display: inline-block; font-size: var(--text-xs); background: #e8f0fc; color: var(--color-primary); padding: 1px var(--space-1); border-radius: 4px; margin-left: var(--space-2); vertical-align: middle; }
.snippet { font-size: var(--text-sm); color: var(--color-muted); background: var(--color-parchment); padding: var(--space-2) var(--space-3); border-left: 3px solid var(--color-primary); margin: var(--space-2) 0; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; }
.snippet :deep(mark) { background: #fff3cd; padding: 0 2px; border-radius: 2px; }
.pagination { display: flex; justify-content: center; align-items: center; gap: var(--space-4); margin-top: var(--space-6); }
.pagination button { padding: var(--space-2) var(--space-5); background: var(--color-primary); color: #fff; border: none; border-radius: var(--radius-pill); cursor: pointer; font-family: inherit; font-size: var(--text-sm); }
.pagination button:disabled { background: var(--color-parchment); color: var(--color-muted); cursor: not-allowed; }
.pagination span { font-size: var(--text-sm); color: var(--color-muted); }
.browse-section { background: var(--color-canvas); border: 1px solid var(--color-hairline); border-radius: var(--radius-card); padding: var(--space-6); }
.browse-section h3 { font-size: var(--text-lg); font-weight: 600; color: var(--color-ink); margin-bottom: var(--space-4); }
.cat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: var(--space-3); }
.cat-card { background: var(--color-parchment); border-radius: 12px; padding: var(--space-4); text-align: center; cursor: pointer; transition: background 0.2s; }
.cat-card:hover { background: #e8ecff; }
.cat-name { font-weight: 500; color: var(--color-ink); font-size: var(--text-sm); margin-bottom: var(--space-1); }
.cat-count { color: var(--color-muted); font-size: var(--text-sm); }
.no-site-hint { text-align: center; padding: var(--space-10) 0; }
.no-site-hint h3 { color: var(--color-muted); margin-bottom: var(--space-2); }
.no-site-hint p { color: var(--color-muted); font-size: var(--text-sm); }
</style>
