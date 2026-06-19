<template>
  <div class="page">
    <Transition name="fade-up" appear>
      <article class="article">
        <h1>数据来源</h1>

        <section>
          <p class="lead">
            Wikiio 的所有数据均来自 Fandom 和 Miraheze 平台公开的 MediaWiki API，不会采集任何隐私或非公开信息。
          </p>
        </section>

        <section>
          <h2>Fandom</h2>
          <div class="platform-header">
            <img src="/fandom-logo.svg" alt="Fandom" class="platform-logo" />
            <div>
              <p>
                Fandom（原名 Wikia）是全球最大的维基托管平台，拥有超过 25 万个维基站点，
                涵盖游戏、影视、动漫、文学等领域。通过 MediaWiki API获取页面内容、
                编辑历史、分类信息。不过，Fandom不支持 RatePage 扩展，故而Fandom维基无原站评分。
              </p>
            </div>
          </div>

          <h3>采集数据</h3>
          <ul class="data-list">
            <li>
              <strong>页面内容</strong>
              <span>页面标题、正文（wikitext）、摘要、最后编辑时间</span>
            </li>
            <li>
              <strong>编辑历史</strong>
              <span>页面创建时间、编辑次数、最近编辑者</span>
            </li>
            <li>
              <strong>分类信息</strong>
              <span>页面所属分类、分类层级结构</span>
            </li>
            <li>
              <strong>作者信息</strong>
              <span>页面创建者、各版本编辑者用户名</span>
            </li>
          </ul>

          <div class="api-note">
            <i class="fa fa-info-circle"></i>
            API 端点格式：<code>https://{wiki}.fandom.com/api.php</code>
          </div>
        </section>

        <section>
          <h2>Miraheze</h2>
          <div class="platform-header">
            <img src="/miraheze-logo.svg" alt="Miraheze" class="platform-logo" />
            <div>
              <p>
                Miraheze 是一个由社区驱动、非营利性质的维基托管服务，基于 MediaWiki 软件。
                它以尊重隐私、无广告、完全免费的宗旨运营，目前托管了超过 5000 个维基站点。
                通过 MediaWiki API获取页面内容、编辑历史、分类信息及 RatePage 评分数据。
              </p>
            </div>
          </div>

          <h3>采集数据</h3>
          <ul class="data-list">
            <li>
              <strong>页面内容</strong>
              <span>页面标题、正文（wikitext）、摘要、最后编辑时间</span>
            </li>
            <li>
              <strong>编辑历史</strong>
              <span>页面创建时间、编辑次数、最近编辑者</span>
            </li>
            <li>
              <strong>分类信息</strong>
              <span>页面所属分类、分类层级结构</span>
            </li>
            <li>
              <strong>RatePage 评分</strong>
              <span>原站内置评分插件的投票数、平均分（如有启用）</span>
            </li>
            <li>
              <strong>作者信息</strong>
              <span>页面创建者、各版本编辑者用户名</span>
            </li>
          </ul>

          <div class="api-note">
            <i class="fa fa-info-circle"></i>
            API 端点格式：<code>https://{wiki}.miraheze.org/w/api.php</code>
          </div>
        </section>

        <section>
          <h2>更新频率</h2>
          <p>
            Wikiio 每 2 小时自动执行一次增量爬取，抓取自上次更新以来有变动的页面。
            新接入的站点会先执行一次全量爬取作为数据基准。
            站点之间的爬取间隔为 60 秒，以避免对目标服务器造成压力。
          </p>
        </section>

        <section>
          <h2>数据使用</h2>
          <p>
            所有原始数据的版权归原维基站点及其贡献者所有，遵循
            <a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank" rel="noopener">CC BY-SA 3.0</a>
            或
            <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>
            授权协议。Wikiio 仅对数据进行聚合、统计与展示，不修改原始内容。
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
  margin-top: var(--space-6);
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

/* ── 平台头部 ── */
.platform-header {
  display: flex;
  gap: var(--space-6);
  align-items: flex-start;
}

.platform-logo {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  margin-top: var(--space-1);
}

/* ── 数据列表 ── */
.data-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.data-list li {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-sm);
  padding: var(--space-4) var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.data-list li strong {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-ink);
}

.data-list li span {
  font-size: var(--text-xs);
  color: var(--color-muted);
  line-height: 1.5;
}

/* ── API 注释 ── */
.api-note {
  margin-top: var(--space-5);
  padding: var(--space-4) var(--space-5);
  background: var(--color-highlight);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.api-note code {
  background: var(--color-canvas);
  padding: var(--space-1) var(--space-2);
  border-radius: 4px;
  font-size: var(--text-xs);
  font-family: "SF Mono", "Cascadia Code", "Fira Code", monospace;
  color: var(--color-ink);
}

@media (max-width: 600px) {
  .article h1 { font-size: var(--text-2xl); }
  .article h2 { font-size: var(--text-lg); }
  .platform-header { flex-direction: column; gap: var(--space-3); }
}
</style>
