<template>
  <div class="detail-page">
    <div class="back" @click="router.back()">← 返回</div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="page" class="content">
      <div class="main-card">
        <h1>{{ page.title }}</h1>
        <div class="meta">
          <span>作者：{{ page.author || '未知' }}</span>
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

      <div class="side-card">
        <h3>最近编辑历史</h3>
        <div class="rev-item" v-for="rev in page.recent_revisions" :key="rev.rev_id">
          <div class="rev-editor">{{ rev.editor }}</div>
          <div class="rev-comment">{{ rev.comment || '（无编辑摘要）' }}</div>
          <div class="rev-time">{{ formatDate(rev.timestamp) }}</div>
        </div>
      </div>
    </div>

    <div v-else class="error">页面不存在</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { pageAPI } from '../api/index.js'

const route = useRoute()
const router = useRouter()

const page = ref(null)
const loading = ref(true)

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
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
.detail-page { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }
.back { color: #667eea; cursor: pointer; margin-bottom: 1rem; }
.loading { text-align: center; padding: 3rem; color: #888; }
.error { text-align: center; padding: 3rem; color: #e74c3c; }

.content { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }

.main-card, .side-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
h1 { font-size: 1.5rem; margin-bottom: 1rem; }
.meta { display: flex; gap: 1.5rem; color: #888; font-size: 0.9rem; margin-bottom: 1rem; }
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

.side-card h3 { margin-bottom: 1rem; font-size: 1rem; }
.rev-item { padding: 0.7rem 0; border-bottom: 1px solid #f0f0f0; }
.rev-editor { font-weight: 500; font-size: 0.9rem; }
.rev-comment { color: #888; font-size: 0.8rem; margin: 0.2rem 0; }
.rev-time { color: #aaa; font-size: 0.75rem; }
</style>