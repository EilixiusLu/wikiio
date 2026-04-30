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
          <span>作者：<b>{{ page.author || '未知' }}</b></span>
          <span>字数：{{ page.word_count }}</span>
          <span>最后编辑：{{ formatDate(page.last_edited_at) }}</span>
        </div>
        <div class="categories" v-if="page.categories.length">
          <span class="cat-tag" v-for="cat in page.categories" :key="cat">{{ cat }}</span>
        </div>
        <div class="rating-box">
          <div class="rating-score">{{ page.rating_avg.toFixed(1) }}</div>
          <div class="rating-stars">
            <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(page.rating_avg) }">★</span>
          </div>
          <div class="rating-count">{{ page.rating_count }} 人评分</div>
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
import { pageAPI } from '../api/index.js'

const route = useRoute()
const router = useRouter()

const page = ref(null)
const loading = ref(true)
const copied = ref(false)

const wikiUrl = computed(() => {
  if (!page.value) return '#'
  return `https://scpfoundation.fandom.com/zh/wiki/${encodeURIComponent(page.value.slug)}`
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
  } catch {
    page.value = null
  } finally {
    loading.value = false
  }
})
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
  gap: 1rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
}
.rating-score { font-size: 2.5rem; font-weight: bold; color: #f5a623; }
.star { font-size: 1.5rem; color: #ddd; }
.star.filled { color: #f5a623; }
.rating-count { color: #888; font-size: 0.9rem; }

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
</style>