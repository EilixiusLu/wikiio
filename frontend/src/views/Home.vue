<template>
  <div class="home-page">
    <section class="hero">
      <Transition name="fade-up" appear>
        <div>
          <h1 class="hero-title">Wikiio</h1>
          <p class="hero-sub">Fandom / Miraheze 维基数据分析与评分平台</p>
          <div class="hero-search">
            <i class="fa fa-search search-icon"></i>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索页面标题、作者或正文..."
              @keyup.enter="goSearch"
            />
            <button @click="goSearch">搜索</button>
          </div>
        </div>
      </Transition>
    </section>

    <section class="content">
      <h2 class="section-title">已接入维基</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="sites.length === 0" class="empty">暂无已接入的维基站点</div>
      <TransitionGroup name="list" tag="div" class="site-grid" v-else>
        <div
          class="site-card"
          v-for="site in sites"
          :key="site.site_id"
          @click="goToSite(site.site_id)"
        >
          <div class="card-top">
            <span class="platform-badge" :class="site.platform">
              {{ site.platform === 'fandom' ? 'Fandom' : 'Miraheze' }}
            </span>
            <span class="lang-badge">{{ site.language }}</span>
          </div>
          <h3>{{ site.name }}</h3>
          <p class="site-desc" v-if="site.description">{{ site.description }}</p>
          <div class="card-footer">
            <span class="site-id">{{ site.site_id }}</span>
            <span class="arrow">查看统计 <i class="fa fa-arrow-right"></i></span>
          </div>
        </div>
      </TransitionGroup>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { siteAPI } from '../api/index.js'

const router = useRouter()
const sites = ref([])
const loading = ref(true)
const searchQuery = ref('')

function goSearch() {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
  } else {
    router.push('/search')
  }
}
function goToSite(siteId) {
  router.push(`/wiki/${siteId}`)
}

onMounted(async () => {
  try {
    sites.value = await siteAPI.list()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-page { min-height: 100vh; }

.hero {
  background: var(--color-parchment);
  text-align: center;
  padding: var(--space-20) 0;
}
.hero-title {
  font-size: var(--text-5xl);
  font-weight: 600;
  color: var(--color-ink);
  letter-spacing: -0.02em;
}
.hero-sub {
  font-size: var(--text-lg);
  color: var(--color-muted);
  margin-top: var(--space-4);
}
.hero-search {
  display: flex; align-items: center;
  max-width: 600px; margin: var(--space-8) auto 0;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-pill);
  height: var(--size-input);
  overflow: hidden;
  transition: border-color var(--duration-base) var(--ease-smooth);
}
.hero-search:focus-within { border-color: var(--color-primary); }
.search-icon { color: var(--color-muted); margin-left: var(--space-4); font-size: var(--text-base); flex-shrink: 0; }
.hero-search input {
  flex: 1; border: none; outline: none;
  padding: 0 var(--space-3);
  font-size: var(--text-base); font-family: inherit;
  color: var(--color-ink); background: transparent;
}
.hero-search input::placeholder { color: var(--color-muted); }
.hero-search button {
  background: var(--color-primary); color: #fff;
  border: none; padding: 0 var(--space-7, 1.75rem);
  height: 100%; font-size: var(--text-base);
  cursor: pointer; font-family: inherit;
  white-space: nowrap; flex-shrink: 0;
  transition: opacity var(--duration-fast) var(--ease-smooth);
}
.hero-search button:hover { opacity: 0.9; }

.content {
  max-width: 1100px;
  margin: 0 auto;
  padding: var(--space-16) var(--space-6);
}
.section-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--space-6);
  letter-spacing: -0.02em;
}
.loading, .empty { text-align: center; padding: var(--space-10) 0; color: var(--color-muted); }

.site-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-6);
  position: relative;
}
.site-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6);
  cursor: pointer;
  transition: background-color var(--duration-base) var(--ease-smooth),
              border-color var(--duration-base) var(--ease-smooth);
}
.site-card:hover { border-color: var(--color-primary); background-color: var(--color-parchment); }

.card-top { display: flex; gap: var(--space-2); margin-bottom: var(--space-3); }
.platform-badge {
  font-size: var(--text-xs); font-weight: 600;
  padding: var(--space-1) var(--space-2); border-radius: 4px;
}
.platform-badge.fandom { background: #e8f0fc; color: var(--color-primary); }
.platform-badge.miraheze { background: #e8f8f0; color: #27ae60; }
.lang-badge {
  font-size: var(--text-xs);
  background: var(--color-parchment);
  color: var(--color-muted);
  padding: var(--space-1) var(--space-2);
  border-radius: 4px;
}
.site-card h3 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--space-2);
}
.site-desc {
  font-size: var(--text-sm); color: var(--color-muted);
  line-height: 1.5; margin-bottom: var(--space-4);
  display: -webkit-box;
  -webkit-box-orient: vertical; overflow: hidden;
}
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.site-id { font-size: var(--text-xs); color: var(--color-muted); font-family: monospace; }
.arrow { font-size: var(--text-sm); color: var(--color-primary); }

@media (max-width: 600px) {
  .hero { padding: var(--space-12) var(--space-4); }
  .hero-title { font-size: var(--text-3xl); }
  .hero-sub { font-size: var(--text-base); }
  .hero-search { max-width: 100%; }
  .hero-search input { font-size: var(--text-sm); padding: 0 var(--space-3); }
  .hero-search button { font-size: var(--text-sm); padding: 0 var(--space-4); }
}
</style>
