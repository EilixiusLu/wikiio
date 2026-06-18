#!/bin/bash
# =============================================================================
# Wikiio 部署脚本
# =============================================================================
set -e

SERVER_HOST="your-server-ip"          # 腾讯云服务器公网 IP
SERVER_USER="root"                     # SSH 用户
PROJECT_DIR="/opt/wikiio"             # 服务器上项目路径

echo "=== Wikiio 部署 ==="
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 1. 前端构建与上传（本地/CI 执行）
# ─────────────────────────────────────────────────────────────────────────────
echo ">>> [1/2] 前端构建..."
bash "$(dirname "$0")/build-frontend.sh"

echo ""
echo ">>> 上传前端至 EdgeOne Pages..."
echo "    请通过以下方式上传 frontend/dist/ 目录:"
echo "    1. EdgeOne Pages 控制台: https://console.cloud.tencent.com/edgeone/pages"
echo "    2. 或使用 EdgeOne CLI (如有配置):"
echo "       # edgeone pages deploy frontend/dist/ --project wikiio"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 2. 后端部署（SSH 到服务器执行）
# ─────────────────────────────────────────────────────────────────────────────
echo ">>> [2/2] 后端部署 (SSH → Docker Compose)..."

ssh "$SERVER_USER@$SERVER_HOST" << 'REMOTE_SCRIPT'
set -e

cd /opt/wikiio

echo "  [2.1] 拉取最新代码..."
git pull

echo "  [2.2] 重建并启动后端服务..."
docker compose up -d --build \
    postgres \
    redis \
    backend \
    celery-worker \
    celery-beat

echo "  [2.3] 运行数据库迁移..."
docker compose exec backend alembic upgrade head

echo "  [2.4] 清理旧镜像..."
docker image prune -f

echo ""
echo "=== 后端部署完成 ==="
docker compose ps
REMOTE_SCRIPT

echo ""
echo "=== 全部部署完成 ==="
