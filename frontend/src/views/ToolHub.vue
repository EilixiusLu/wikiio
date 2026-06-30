<template>
  <div class="tool-hub-page">
    <h1>Wikiio 工具箱</h1>

    <div class="tools-grid">
      <div class="tool-card" @click="router.push('/tools/scp-fd-category')">
        <div class="tool-icon">
          <i class="fa fa-tags"></i>
        </div>
        <div class="tool-body">
          <h2>SCP-FD 分类代码生成器</h2>
          <p>快速生成符合规范的页面分类 WikiText 代码，支持条件联动。</p>
        </div>
        <i class="fa fa-chevron-right tool-arrow"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.tool-hub-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-16) var(--space-6);
}

.tool-hub-page h1 {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-ink);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-10);
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}

.tool-card {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6);
  cursor: pointer;
  transition: background-color var(--duration-base) var(--ease-smooth),
              border-color var(--duration-base) var(--ease-smooth),
              transform var(--duration-fast) var(--ease-apple);
}

.tool-card:hover {
  background-color: var(--color-highlight);
  border-color: var(--color-primary);
}

.tool-card:active {
  transform: scale(0.98);
}

.tool-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--color-highlight);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.25rem;
}

.tool-body {
  flex: 1;
  min-width: 0;
}

.tool-body h2 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--space-1);
}

.tool-body p {
  font-size: var(--text-sm);
  color: var(--color-muted);
  line-height: 1.5;
}

.tool-arrow {
  color: var(--color-muted);
  font-size: var(--text-sm);
  flex-shrink: 0;
  transition: transform var(--duration-fast) var(--ease-apple);
}

.tool-card:hover .tool-arrow {
  transform: translateX(3px);
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .tools-grid {
    grid-template-columns: 1fr;
  }
}
</style>
