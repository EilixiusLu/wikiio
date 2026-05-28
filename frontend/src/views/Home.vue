<template>
  <div class="home-page">
    <!-- Hero -->
    <div class="hero">
      <h1>Wikiio</h1>
      <p>Fandom / Miraheze 维基数据分析与评分平台</p>
      <div class="hero-search">
        <input v-model="searchQuery" type="text" placeholder="搜索页面标题、作者或正文..." @keyup.enter="goSearch" />
        <button @click="goSearch">搜索</button>
      </div>
    </div>

    <!-- 已接入维基 -->
    <div class="content">
      <h2>已接入维基</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="sites.length === 0" class="empty">暂无已接入的维基站点</div>
      <div class="site-grid" v-else>
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
            <span class="arrow">查看统计 →</span>
          </div>
        </div>
      </div>
    </div>
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
.home-page { min-height: 100vh; background: #f5f7fa; }

.hero {
  background: #1a1a2e;
  color: white;
  text-align: center;
  padding: 4rem 1rem 3rem;
}
.hero h1 { font-size: 2.8rem; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: -1px; }
.hero p { font-size: 1rem; opacity: 0.6; margin-bottom: 2rem; }
.hero-search { display: flex; max-width: 520px; margin: 0 auto; }
.hero-search input {
  flex: 1; padding: 0.75rem 1.2rem;
  border: none; border-radius: 6px 0 0 6px;
  font-size: 0.95rem; outline: none;
}
.hero-search button {
  padding: 0.75rem 1.5rem;
  background: #185897; color: white;
  border: none; border-radius: 0 6px 6px 0;
  font-size: 0.95rem; cursor: pointer;
}
.hero-search button:hover { background: #134a7f; }

.content { max-width: 1100px; margin: 0 auto; padding: 2.5rem 1rem; }
h2 { font-size: 1.2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 1.2rem; }
.loading { text-align: center; padding: 3rem; color: #888; }
.empty { text-align: center; padding: 3rem; color: #aaa; }

.site-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.2rem;
}
.site-card {
  background: white;
  border-radius: 10px;
  padding: 1.4rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
  border: 2px solid transparent;
}
.site-card:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  transform: translateY(-2px);
  border-color: #185897;
}
.card-top { display: flex; gap: 0.5rem; margin-bottom: 0.8rem; }
.platform-badge {
  font-size: 0.72rem; font-weight: 600;
  padding: 0.2rem 0.5rem; border-radius: 3px;
}
.platform-badge.fandom { background: #e8f0fc; color: #185897; }
.platform-badge.miraheze { background: #e8f8f0; color: #27ae60; }
.lang-badge {
  font-size: 0.72rem; background: #f5f5f5; color: #666;
  padding: 0.2rem 0.5rem; border-radius: 3px;
}
h3 { font-size: 1.05rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.4rem; }
.site-desc {
  font-size: 0.82rem; color: #888;
  margin-bottom: 1rem; line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.site-id { font-size: 0.75rem; color: #aaa; font-family: monospace; }
.arrow { font-size: 0.82rem; color: #185897; }
</style>