# Wikiio
（开发中）
Fandom / Miraheze 维基数据分析与评分平台

## 项目架构

```
wikiio/
├── docker-compose.yml          # Docker Compose 编排（6 服务）
├── nginx/
│   └── wikiio.conf             # Nginx 配置（SPA 回退、API 代理、静态缓存）
├── backend/                    # Python FastAPI 后端
│   ├── Dockerfile              # Python 3.11-slim 构建镜像
│   ├── docker-entrypoint.sh    # 启动入口（等待 PG、执行迁移、启动 uvicorn）
│   ├── requirements.txt        # Python 依赖
│   ├── alembic.ini             # Alembic 迁移配置
│   ├── pytest.ini              # pytest 配置
│   ├── app/
│   │   ├── main.py             # FastAPI 应用入口（CORS、路由注册）
│   │   ├── config.py           # Pydantic Settings（数据库、Redis、CORS、爬虫参数）
│   │   ├── database.py         # SQLAlchemy 异步引擎 + get_db 依赖
│   │   ├── limiter.py          # SlowAPI 速率限制（200 req/min, 1000 req/hr）
│   │   ├── crawler/            # Celery 爬虫
│   │   │   ├── scheduler.py    # Celery 应用、Beat 定时任务
│   │   │   ├── tasks.py        # 爬虫任务（全量/增量爬取）
│   │   │   └── mediawiki.py    # MediaWiki API 客户端
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   │   ├── user.py         # 用户模型（Fandom/Miraheze 绑定）
│   │   │   ├── site.py         # 站点模型（Fandom/Miraheze 维基）
│   │   │   ├── page.py         # 页面模型（标题、作者、评分统计）
│   │   │   ├── revision.py     # 版本历史模型
│   │   │   └── rating.py       # 评分模型
│   │   ├── routers/            # FastAPI 路由
│   │   │   ├── auth.py         # /auth/* — 注册、登录、邮箱验证
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
│   │       ├── email.py        # 邮件发送
│   │       ├── logger.py       # 日志配置（TimedRotatingFileHandler）
│   │       └── security.py     # 密码哈希、JWT 令牌
│   ├── migrations/             # Alembic 数据库迁移
│   │   └── versions/
│   │       ├── acc2691a9780_add_platform_and_has_ratepage_to_sites.py
│   │       ├── 36369c50179e_add_miraheze_fields_to_users.py
│   │       ├── 5d3b7e9a1c8f_add_fulltext_indexes.py
│   │       ├── 6a8f9c1d2e3a_add_site_rating_to_pages.py
│   │       └── 0c4a2d8e1f3f_fix_miraheze_verified_not_null.py
│   └── tests/                  # pytest 测试（122 个）
│       ├── test_auth.py
│       ├── test_pages.py
│       ├── test_ratings.py
│       ├── test_search.py
│       ├── test_sites.py
│       ├── test_admin.py
│       ├── test_users.py
│       ├── test_schemas.py
│       └── test_security.py
├── frontend/                   # Vue 3 前端
│   ├── Dockerfile              # 多阶段构建（Node 22 → Nginx Alpine）
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
│       ├── router/index.js     # Vue Router（12 路由，auth guard）
│       ├── stores/
│       │   ├── auth.js         # Pinia 认证存储
│       │   └── counter.js      # 示例存储（废弃）
│       ├── composables/
│       │   └── useTheme.js     # 主题管理（浅色/深色/系统跟随）
│       ├── components/
│       │   ├── Navbar.vue      # 导航栏（响应式 + 移动端菜单）
│       │   └── Footer.vue      # 页脚
│       └── views/
│           ├── Home.vue        # / — 首页/维基列表
│           ├── Search.vue      # /search — 搜索页面
│           ├── WikiStats.vue   # /wiki/:siteId — 维基统计
│           ├── PageDetail.vue  # /page/:id — 页面详情
│           ├── Rankings.vue    # /rankings — 排行榜
│           ├── Author.vue      # /author/:author — 统一作者页
│           ├── FdAuthor.vue    # /fd-author/:author — Fandom 作者页
│           ├── MhAuthor.vue    # /mh-author/:author — Miraheze 作者页
│           ├── Login.vue       # /login
│           ├── Register.vue    # /register
│           ├── Profile.vue     # /profile — 个人中心
│           └── Admin.vue       # /admin — 后台管理
└── scripts/
    ├── backup.sh               # 备份脚本（待完善）
    └── deploy.sh               # 部署脚本（待完善）
```

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Python FastAPI | 0.136 |
| ORM | SQLAlchemy 2.0 (async) | 2.0.49 |
| 数据库 | PostgreSQL 16 | — |
| 缓存/消息队列 | Redis 7 + Celery 5.6 | — |
| 前端框架 | Vue 3 (Composition API) | 3.5 |
| 状态管理 | Pinia | 3.0 |
| 路由 | Vue Router | 5.0 |
| HTTP 客户端 | Axios | 1.15 |
| 构建工具 | Vite | 8 |
| 容器化 | Docker Compose | — |
| 反向代理 | Nginx (Alpine) | — |

## 功能特性

- **多平台支持**：接入 Fandom 和 Miraheze 维基站点
- **自动爬取**：全量/增量爬取页面内容、编辑历史、分类
- **评分系统**：五星评分 + 原站 RatePage 评分集成
- **全文搜索**：PostgreSQL tsvector 全文搜索 + trigram ILIKE 混合检索
- **排行榜**：评分榜、页面数榜、作者评分榜、原站评分榜
- **作者页**：统一作者页、Fandom 作者页、Miraheze 作者页
- **主题切换**：浅色/深色模式（系统跟随 + 手动切换）
- **苹果设计风格**：SF Pro 字体、hairline 边框、宽屏网格布局、流畅动效

## 快速开始

### 本地开发

```bash
# 后端
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # 编辑配置
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
docker compose up -d
```

启动 6 个服务：
- **postgres** — PostgreSQL 16 数据库
- **redis** — Redis 7 缓存 + Celery Broker
- **backend** — FastAPI 应用（:8000）
- **celery-worker** — Celery 异步任务执行器
- **celery-beat** — Celery 定时任务调度器
- **frontend** — Nginx 静态文件服务 + API 代理（:80）

### 数据库迁移

```bash
cd backend
alembic upgrade head
```

## API 概览

| 前缀 | 模块 | 主要端点 |
|------|------|---------|
| `/auth` | 认证 | 注册、登录、邮箱验证 |
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
