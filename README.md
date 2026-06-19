# Wikiio

基于 MediaWiki API 的 Fandom / Miraheze 维基数据分析与评分网站

## 项目架构

```
wikiio/
├── docker-compose.yml          # Docker Compose 编排（5 服务）
├── nginx/
│   └── wikiio.conf             # Nginx 配置（API 反向代理）
├── backend/                    # Python FastAPI 后端
│   ├── Dockerfile              # Python 3.11-slim 构建镜像
│   ├── docker-entrypoint.sh    # 启动入口（等待 PG、执行迁移、启动 uvicorn）
│   ├── requirements.txt        # Python 依赖
│   ├── alembic.ini             # Alembic 迁移配置
│   ├── pytest.ini              # pytest 配置
│   ├── app/
│   │   ├── main.py             # FastAPI 应用入口（CORS、路由注册）
│   │   ├── config.py           # Pydantic Settings（数据库、Redis、Resend、爬虫参数）
│   │   ├── database.py         # SQLAlchemy 异步引擎 + get_db 依赖
│   │   ├── limiter.py          # SlowAPI 速率限制
│   │   ├── crawler/            # Celery 爬虫
│   │   │   ├── scheduler.py    # Celery 应用、Beat 定时任务
│   │   │   ├── tasks.py        # 爬虫任务（全量/增量爬取）
│   │   │   └── mediawiki.py    # MediaWiki API 客户端（SSRF 防护）
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   │   ├── user.py         # 用户模型（Fandom/Miraheze 绑定、邮箱验证）
│   │   │   ├── site.py         # 站点模型（Fandom/Miraheze 维基）
│   │   │   ├── page.py         # 页面模型（标题、作者、评分统计）
│   │   │   ├── revision.py     # 版本历史模型
│   │   │   └── rating.py       # 评分模型
│   │   ├── routers/            # FastAPI 路由
│   │   │   ├── auth.py         # /auth/* — 注册、登录、邮箱验证（Resend）
│   │   │   ├── users.py        # /users/* — 个人资料、Fandom/MH 绑定
│   │   │   ├── sites.py        # /sites/* — 站点 CRUD、触发爬取
│   │   │   ├── pages.py        # /pages/* — 页面列表、详情、统计、排名
│   │   │   ├── ratings.py      # /ratings/* — 页面评分 CRUD
│   │   │   ├── search.py       # /search/* — 全文搜索、分类浏览
│   │   │   └── admin.py        # /admin/* — 统计、日志、站点审核
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   │   ├── page.py
│   │   │   ├── rating.py
│   │   │   ├── site.py
│   │   │   └── user.py
│   │   └── utils/              # 工具模块
│   │       ├── cache.py        # Redis 缓存（@cached 装饰器）
│   │       ├── email.py        # 邮件发送（Resend SDK）
│   │       ├── logger.py       # 日志配置（TimedRotatingFileHandler）
│   │       ├── security.py     # 密码哈希、JWT 令牌
│   │       └── url_validator.py # URL 安全校验（SSRF 防护）
│   ├── migrations/             # Alembic 数据库迁移
│   │   └── versions/
│   │       ├── acc2691a9780_add_platform_and_has_ratepage_to_sites.py
│   │       ├── 36369c50179e_add_miraheze_fields_to_users.py
│   │       ├── 5d3b7e9a1c8f_add_fulltext_indexes.py
│   │       ├── 6a8f9c1d2e3a_add_site_rating_to_pages.py
│   │       ├── 0c4a2d8e1f3f_fix_miraheze_verified_not_null.py
│   │       └── f03c0ab9ac4a_add_email_verify_token_expiry.py
│   └── tests/                  # pytest 测试（128 个）
│       ├── test_auth.py
│       ├── test_pages.py
│       ├── test_ratings.py
│       ├── test_search.py
│       ├── test_sites.py
│       ├── test_admin.py
│       ├── test_users.py
│       ├── test_schemas.py
│       └── test_security.py
├── frontend/                   # Vue 3 前端（静态部署至 EdgeOne Pages）
│   ├── package.json            # Vue 3.5, Pinia 3, Vue Router 5, Axios, Vite 8
│   ├── vite.config.js          # Vite 配置（@ 路径别名）
│   ├── public/                 # 静态资源
│   │   ├── fandom-logo.svg
│   │   ├── miraheze-logo.svg
│   │   ├── wikiio-logo.svg
│   │   └── favicon.ico
│   └── src/
│       ├── main.js             # 应用入口
│       ├── index.css           # 全局 CSS 变量系统 + 暗黑模式
│       ├── App.vue             # 根组件
│       ├── api/index.js        # Axios API 客户端
│       ├── router/index.js     # Vue Router（16 路由，Hash 模式，auth guard）
│       ├── stores/
│       │   └── auth.js         # Pinia 认证存储
│       ├── composables/
│       │   └── useTheme.js     # 主题管理（浅色/深色/系统跟随）
│       ├── components/
│       │   ├── Navbar.vue      # 导航栏（响应式 + 移动端菜单）
│       │   └── Footer.vue      # 页脚
│       └── views/
│           ├── Home.vue        # / — 首页/维基列表
│           ├── Search.vue      # /search — 搜索页面（XSS 安全高亮）
│           ├── WikiStats.vue   # /wiki/:siteId — 维基统计
│           ├── PageDetail.vue  # /page/:id — 页面详情
│           ├── Rankings.vue    # /rankings — 排行榜
│           ├── Author.vue      # /author/:author — 统一作者页
│           ├── FdAuthor.vue    # /fd-author/:author — Fandom 作者页
│           ├── MhAuthor.vue    # /mh-author/:author — Miraheze 作者页
│           ├── Login.vue       # /login
│           ├── Register.vue    # /register
│           ├── VerifyEmail.vue # /verify-email — 邮箱验证
│           ├── ResendVerification.vue # /resend-verification — 重发验证邮件
│           ├── About.vue       # /about — 关于 Wikiio
│           ├── DataSources.vue # /datasources — 数据来源
│           ├── Profile.vue     # /profile — 个人中心（Fandom/MH 绑定）
│           └── Admin.vue       # /admin — 后台管理
└── scripts/
    ├── backup.sh               # 数据库备份脚本（pg_dump → COS）
    ├── build-frontend.sh       # 前端构建脚本
    └── deploy.sh               # 部署脚本（前端构建 + 后端 SSH 部署）
```

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Python FastAPI | 0.136 |
| ORM | SQLAlchemy 2.0 (async) | 2.0.49 |
| 数据库 | PostgreSQL 16 | — |
| 缓存/消息队列 | Redis 7 + Celery 5.6 | — |
| 邮件服务 | Resend | — |
| 前端框架 | Vue 3 (Composition API) | 3.5 |
| 状态管理 | Pinia | 3.0 |
| 路由 | Vue Router 5 (Hash 模式) | 5.0 |
| HTTP 客户端 | Axios | 1.15 |
| 构建工具 | Vite | 8 |
| 容器化 | Docker Compose | — |
| 反向代理 | Nginx (Alpine) | — |

## 功能特性

- **多平台支持**：接入 Fandom 和 Miraheze 维基站点
- **自动爬取**：全量/增量爬取页面内容、编辑历史、分类
- **评分系统**：五星评分 + 原站 RatePage 评分集成
- **全文搜索**：PostgreSQL tsvector 全文搜索 + trigram ILIKE 混合检索（XSS 安全高亮）
- **排行榜**：评分榜、页面数榜、作者评分榜、原站评分榜
- **作者页**：统一作者页、Fandom 作者页、Miraheze 作者页
- **邮箱验证**：注册邮箱验证流程（Resend），24 小时令牌过期，防网关扫描
- **账户绑定**：Fandom / Miraheze 账户验证绑定
- **Redis 缓存**：高频 GET 端点自动缓存，写操作智能失效
- **速率限制**：注册 3/min、登录 5/min、重发验证 3/hour
- **安全防护**：SSRF 白名单校验、XSS 过滤、JWT Bearer 认证、API 越权检测
- **主题切换**：浅色/深色模式（系统跟随 + 手动切换）

## 快速开始

### 本地开发

```bash
# 后端
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env   # 编辑配置（数据库、Redis、Resend API Key 等）
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

前端开发服务器默认连接 `http://localhost:8000/api/v1`，可通过 `frontend/.env.development` 中的 `VITE_API_BASE_URL` 修改。

### Docker 部署（后端）

```bash
docker compose up -d
```

启动 5 个服务：
- **postgres** — PostgreSQL 16 数据库
- **redis** — Redis 7 缓存 + Celery Broker
- **backend** — FastAPI 应用（:8000）
- **celery-worker** — Celery 异步任务执行器
- **celery-beat** — Celery 定时任务调度器

前端独立构建部署：

```bash
cd frontend
npm ci && npm run build
# 将 dist/ 上传至 EdgeOne Pages 或其他静态托管服务
```

### 数据库迁移

```bash
cd backend
alembic upgrade head
```

## API 概览

| 前缀 | 模块 | 主要端点 |
|------|------|---------|
| `/auth` | 认证 | 注册、登录、邮箱验证、重发验证邮件 |
| `/users` | 用户 | 个人资料、Fandom/MH 账户绑定 |
| `/sites` | 站点 | 站点 CRUD、触发爬取 |
| `/pages` | 页面 | 列表、详情、统计、排名、作者查询 |
| `/ratings` | 评分 | 页面评分 CRUD |
| `/search` | 搜索 | 全文搜索、分类列表 |
| `/admin` | 管理 | 站点审核、日志查看、系统统计 |

完整 API 文档在 `/docs`（Swagger UI）。

## 日志轮转

- **方式**：TimedRotatingFileHandler（每天午夜轮转）
- **保留期**：30 天
- **兜底清理**：应用启动时 + Celery Beat 每周一 03:00
- **日志文件**：`logs/access.log`、`crawler.log`、`rating.log`、`error.log`

## 开源协议

MIT License
