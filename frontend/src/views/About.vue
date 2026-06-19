<template>
  <div class="page">
    <Transition name="fade-up" appear>
      <article class="article">
        <h1>关于 Wikiio</h1>

        <section>
          <p class="lead">
            Wikiio 是一个基于MediaWiki API的非营利性的第三方维基数据分析与评分网站，目前主要服务于托管在 Fandom 和 Miraheze
            上使用MediaWiki软件维基的页面质量评估、作者贡献统计与全文搜索。
          </p>
        </section>

        <section>
          <h2>项目背景</h2>
          <p>
            Fandom 和 Miraheze 承载了数以万计的维基站点，涵盖游戏、影视、文学等各个领域。
            尽管存在WikiApiary这样的数据统计平台，然而，由于MediaWiki API的复杂性，其社群长期缺乏响应的跨站点的数据分析与内容质量评估工具——
            读者难以评定页面质量，编辑者也缺乏对自己贡献的量化反馈。
          </p>
          <p>
            Wikiio 通过定期调用维基站点的公开MediaWiki API，为每个站点生成
            多维数据统计，同时提供全文搜索、作者排名、部分编辑历史追溯等功能，
            帮助维基社群更好地了解内容质量与贡献分布。
          </p>
        </section>

        <section>
          <h2>核心功能</h2>
          <div class="feature-grid">
            <div class="feature-card">
              <h3>多维数据</h3>
              <p>为接入 Wikiio 的网站统计页面长度/数量、编辑历史、分类覆盖、原站 RatePage 评分等多维数据</p>
            </div>
            <div class="feature-card">
              <h3>全文搜索</h3>
              <p>基于 PostgreSQL 全文搜索引擎，支持中文分词与模糊匹配，跨站点快速检索页面标题与正文。</p>
            </div>
            <div class="feature-card">
              <h3>作者排名</h3>
              <p>按页面数、编辑量、评分总和等维度对作者进行排名，帮助社群发现核心贡献者。</p>
            </div>
            <div class="feature-card">
              <h3>跨站评分</h3>
              <p>注册并验证账号的用户可以对页面进行五星评分，结合原站评分形成综合质量参考。</p>
            </div>
            <div class="feature-card">
              <h3>多平台支持</h3>
              <p>同时接入 Fandom 和 Miraheze 两大维基托管平台，统一呈现跨站数据。</p>
            </div>
            <div class="feature-card">
              <h3>深色模式</h3>
              <p>支持浅色/深色主题切换，跟随系统偏好，保护夜间阅读体验。</p>
            </div>
          </div>
        </section>

        <section>
          <h2>版权声明</h2>
          <p>
            Wikiio 仅为维基社群提供非营利性的第三方数据统计与技术分析服务。
            平台展示的所有文本内容之版权均遵循原维基站点（Fandom、Miraheze）的授权协议（CC BY-SA 3.0/4.0）。
            原始页面数据均来自各平台的公开 MediaWiki API。
          </p>
          <p>
            Wikiio <b>不会</b>对任何未申请接入 Wikiio 的站点进行任何爬取。
          </p>
        </section>

        <section>
          <h2>申请接入</h2>
          <p>
            目前 Wikiio 仅接受托管于 Fandom 或 Miraheze 的维基申请接入，申请者必须是该站点的管理员或行政员。
            任何申请接入的维基需保证其内容不涉及任何违反中华人民共和国相关法律及所在国法律的文本，如有上述情形，该站点将被立即取消接入。
          </p>
          <p>
            申请接入可以发邮件至维护者 EilixiusLu / Chhokmah Lu 的邮箱chhokmahlu@outlook.com，并附上网站链接、
            网站正式名称、简短的网站描述、纯英文与符号的维基识别编号（如scp-fd）、是否启用RatePage扩展和自身作为
            网站管理人员之证明。
          </p>
        </section>
      </article>
    </Transition>
  </div>
</template>

<style scoped>
.page {
  min-height: 80vh;
  padding: var(--space-16) var(--space-8);
  display: flex;
  justify-content: center;
}

.article {
  max-width: 760px;
  width: 100%;
}

.article h1 {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-ink);
  letter-spacing: -0.03em;
  margin-bottom: var(--space-10);
}

.article h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-ink);
  letter-spacing: -0.02em;
  margin-top: var(--space-12);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-hairline);
}

.article h3 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--space-1);
}

.article h4 {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-3);
}

.article p {
  font-size: var(--text-base);
  color: var(--color-muted);
  line-height: 1.7;
  margin-bottom: var(--space-4);
}

.lead {
  font-size: var(--text-lg) !important;
  color: var(--color-ink) !important;
  line-height: 1.6 !important;
}

/* ── 功能卡片网格 ── */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-5);
  margin-top: var(--space-4);
}

.feature-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-card);
  padding: var(--space-6);
  transition: border-color var(--duration-base) var(--ease-smooth);
}

.feature-card:hover {
  border-color: var(--color-primary);
}

.feature-card p {
  font-size: var(--text-sm);
  margin-bottom: 0;
}

/* ── 技术栈 ── */
.tech-stack {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
  margin-top: var(--space-4);
}

.tech-group ul {
  list-style: none;
  padding: 0;
}

.tech-group li {
  font-size: var(--text-sm);
  color: var(--color-muted);
  line-height: 1.8;
  position: relative;
  padding-left: var(--space-4);
}

.tech-group li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.6em;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
  opacity: 0.5;
}

@media (max-width: 600px) {
  .feature-grid,
  .tech-stack {
    grid-template-columns: 1fr;
  }
  .article h1 { font-size: var(--text-2xl); }
  .article h2 { font-size: var(--text-lg); }
}
</style>
