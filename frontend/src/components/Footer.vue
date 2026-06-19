<template>
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-grid">
        <div class="footer-col">
          <h4>站点功能</h4>
          <router-link to="/">维基统计</router-link>
          <router-link to="/search">页面搜索</router-link>
          <router-link to="/rankings">作者排名</router-link>
        </div>
        <div class="footer-col">
          <h4>关于</h4>
          <router-link to="/about">关于 Wikiio</router-link>
          <router-link to="/datasources">数据来源</router-link>
          <a href="https://github.com/EilixiusLu/wikiio" target="_blank" rel="noopener">GitHub</a>
        </div>
        <div class="footer-col">
          <h4>Wikiio</h4>
          <p class="footer-brand">Fandom / Miraheze 维基数据分析与评分网站</p>
          <p class="footer-brand">Wikiio仅为维基社群提供非营利性的第三方数据统计与技术分析服务，所有展示文本之版权均遵循原维基授权协议</p>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; 2026 EilixiusLu / Chhokmah Lu. All rights reserved.</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer { background: var(--color-parchment); border-top: 1px solid var(--color-hairline); padding: var(--space-16) 0; margin-top: var(--space-16); }
.footer-inner { max-width: 1100px; margin: 0 auto; padding: 0 var(--space-6); }
.footer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-10); margin-bottom: var(--space-10); }
.footer-col { display: flex; flex-direction: column; gap: var(--space-2); }
.footer-col h4 { font-size: var(--text-sm); font-weight: 600; color: var(--color-ink); margin-bottom: var(--space-2); }
.footer-col a { font-size: var(--text-xs); color: var(--color-muted); }
.footer-col a:hover { color: var(--color-ink); }
.footer-brand { font-size: var(--text-xs); color: var(--color-muted); line-height: 1.5; }
.footer-bottom { border-top: 1px solid var(--color-hairline); padding-top: var(--space-5); }
.footer-bottom span { font-size: var(--text-xs); color: var(--color-muted); }
@media (max-width: 600px) { .footer-grid { grid-template-columns: 1fr; gap: var(--space-6); } }
</style>
