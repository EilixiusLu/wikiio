<template>
  <div class="home-page">
    <section class="hero">
      <h1 class="hero-title">Wikiio</h1>
      <p class="hero-sub">Fandom / Miraheze 维基数据分析与评分平台</p>
      <div class="hero-search">
        <i class="fa fa-search search-icon"></i>
        <input v-model="searchQuery" type="text" placeholder="搜索页面标题、作者或正文..." @keyup.enter="goSearch" />
        <button @click="goSearch">搜索</button>
      </div>
    </section>

    <section class="content">
      <h2 class="section-title">已接入维基</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="sites.length === 0" class="empty">暂无已接入的维基站点</div>
      <div class="site-grid" v-else>
        <div class="site-card" v-for="site in sites" :key="site.site_id" @click="goToSite(site.site_id)">
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
      </div>
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
  if (searchQuery.value.trim()) router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
  else router.push('/search')
}
function goToSite(siteId) { router.push(`/wiki/${siteId}`) }

onMounted(async () => {
  try { sites.value = await siteAPI.list() } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped>
.home-page { min-height: 100vh; }

.hero {
  background: var(--color-parchment);
  text-align: center;
  padding: 80px 0;
}
.hero-title { font-size: 56px; font-weight: 600; color: var(--color-ink); letter-spacing: -0.02em; }
.hero-sub { font-size: 21px; color: var(--color-muted); margin-top: 16px; }
.hero-search {
  display: flex; align-items: center;
  max-width: 600px; margin: 32px auto 0;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-pill);
  height: 44px;
  overflow: hidden;
}
.search-icon { color: var(--color-muted); margin-left: 16px; font-size: 16px; }
.hero-search input {
  flex: 1; border: none; outline: none;
  font-size: 17px; padding: 0 12px;
  font-family: inherit; color: var(--color-ink);
  background: transparent;
}
.hero-search input::placeholder { color: var(--color-muted); }
.hero-search button {
  background: var(--color-primary); color: #fff;
  border: none; padding: 0 28px; height: 100%;
  font-size: 17px; cursor: pointer; font-family: inherit;
  white-space: nowrap;
}
.hero-search button:hover { opacity: 0.9; }

.content { max-width: 1100px; margin: 0 auto; padding: 60px 1.5rem; }
.section-title { font-size: 24px; font-weight: 600; color: var(--color-ink); margin-bottom: 24px; letter-spacing: -0.02em; }
.loading, .empty { text-align: center; padding: 40px 0; color: var(--color-muted); }

.site-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; }
.site-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: 24px;
  cursor: pointer;
  transition: border-color 0.2s;
}
.site-card:hover { border-color: var(--color-primary); }
.card-top { display: flex; gap: 8px; margin-bottom: 12px; }
.platform-badge {
  font-size: 12px; font-weight: 600;
  padding: 2px 8px; border-radius: 4px;
}
.platform-badge.fandom { background: #e8f0fc; color: var(--color-primary); }
.platform-badge.miraheze { background: #e8f8f0; color: #27ae60; }
.lang-badge { font-size: 12px; background: var(--color-parchment); color: var(--color-muted); padding: 2px 8px; border-radius: 4px; }
.site-card h3 { font-size: 17px; font-weight: 600; color: var(--color-ink); margin-bottom: 8px; }
.site-desc { font-size: 14px; color: var(--color-muted); line-height: 1.5; margin-bottom: 16px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.site-id { font-size: 12px; color: var(--color-muted); font-family: monospace; }
.arrow { font-size: 14px; color: var(--color-primary); }

@media (max-width: 600px) {
  .hero { padding: 48px 1rem; }
  .hero-title { font-size: 36px; }
  .hero-sub { font-size: 17px; }
  .hero-search { max-width: 100%; }
  .hero-search input { font-size: 15px; padding: 0 12px; }
  .hero-search button { font-size: 15px; padding: 0 18px; }
}
</style>
