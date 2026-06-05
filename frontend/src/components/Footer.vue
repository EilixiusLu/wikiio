<template>
  <footer class="footer">
    <div class="footer-inner">
      <div class="footer-grid">
        <div class="footer-col">
          <h4>产品功能</h4>
          <a href="/">维基统计</a>
          <a href="/search">页面搜索</a>
          <a href="/rankings">作者排名</a>
        </div>
        <div class="footer-col">
          <h4>关于</h4>
          <a href="/">关于 Wikiio</a>
          <a href="/">数据来源</a>
          <a href="/">联系方式</a>
        </div>
        <div class="footer-col">
          <h4>Wikiio</h4>
          <p class="footer-brand">Fandom / Miraheze 维基数据分析与评分平台</p>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; 2026 Wikiio. All rights reserved.</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: var(--color-parchment);
  border-top: 1px solid var(--color-hairline);
  padding: 64px 0;
  margin-top: 60px;
}
.footer-inner { max-width: 1100px; margin: 0 auto; padding: 0 1.5rem; }
.footer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; margin-bottom: 40px; }
.footer-col { display: flex; flex-direction: column; gap: 8px; }
.footer-col h4 { font-size: 14px; font-weight: 600; color: var(--color-ink); margin-bottom: 8px; }
.footer-col a { font-size: 12px; color: var(--color-muted); }
.footer-col a:hover { color: var(--color-ink); }
.footer-brand { font-size: 12px; color: var(--color-muted); line-height: 1.5; }
.footer-bottom { border-top: 1px solid var(--color-hairline); padding-top: 20px; }
.footer-bottom span { font-size: 12px; color: var(--color-muted); }
@media (max-width: 600px) {
  .footer-grid { grid-template-columns: 1fr; gap: 24px; }
}
</style>
