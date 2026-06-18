#!/bin/bash
# =============================================================================
# Wikiio 前端构建脚本
# 将 Vue 3 项目编译为静态文件，产物位于 frontend/dist/
# 构建完成后请上传至 EdgeOne Pages 控制台
# =============================================================================
set -e

echo "=== Wikiio 前端构建 ==="
cd "$(dirname "$0")/../frontend"

echo "[1/2] 安装依赖..."
npm ci

echo "[2/2] 构建生产版本..."
npm run build

echo ""
echo "=== 构建完成 ==="
echo "产物目录: $(pwd)/dist/"
echo ""
echo "下一步: 将 dist/ 目录上传至 EdgeOne Pages"
echo "  - EdgeOne Pages 控制台: https://console.cloud.tencent.com/edgeone/pages"
