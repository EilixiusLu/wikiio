#!/bin/bash
# =============================================================================
# Wikiio 数据库备份脚本
# 使用 pg_dump 导出 PostgreSQL，压缩后上传至腾讯云 COS
# 保留最近 7 份备份，自动清理更早的文件
# =============================================================================
set -e

# ── 配置 ──
BACKUP_DIR="/opt/wikiio/backups"
DB_CONTAINER="wikiio-postgres"
DB_NAME="wikiio_db"
DB_USER="wikiio"
COS_BUCKET="cos://your-bucket-name"   # COS 存储桶名称
COS_REGION="ap-guangzhou"             # COS 地域
RETENTION_COUNT=7                     # 保留最近 N 份备份

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/wikiio_backup_$TIMESTAMP.sql.gz"

echo "=== Wikiio 数据库备份 ==="
echo "时间: $(date)"
echo ""

# ── 1. 创建备份目录 ──
mkdir -p "$BACKUP_DIR"

# ── 2. 导出并压缩 ──
echo "[1/3] 导出数据库..."
docker compose exec -T "$DB_CONTAINER" \
    pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner --no-acl \
    | gzip > "$BACKUP_FILE"

echo "  备份文件: $BACKUP_FILE"
echo "  大小: $(du -h "$BACKUP_FILE" | cut -f1)"

# ── 3. 上传至 COS ──
echo "[2/3] 上传至 COS..."

# ---- 方式 A: 使用 coscli ----
if command -v coscli &> /dev/null; then
    coscli cp "$BACKUP_FILE" "$COS_BUCKET/wikiio/backups/$(basename "$BACKUP_FILE")"
    echo "  已上传至 COS (coscli)"

# ---- 方式 B: 使用 coscmd ----
elif command -v coscmd &> /dev/null; then
    coscmd upload "$BACKUP_FILE" "wikiio/backups/$(basename "$BACKUP_FILE")"
    echo "  已上传至 COS (coscmd)"

# ---- 方式 C: 未配置 COS 工具 ----
else
    echo "  [警告] 未检测到 coscli 或 coscmd，跳过 COS 上传"
    echo "  手动上传: $BACKUP_FILE"
    echo "  安装指引: https://cloud.tencent.com/document/product/436/63143"
fi

# ── 4. 清理旧备份 ──
echo "[3/3] 清理旧备份（保留最近 $RETENTION_COUNT 份）..."

# 清理本地
LOCAL_COUNT=$(ls -1 "$BACKUP_DIR"/wikiio_backup_*.sql.gz 2>/dev/null | wc -l)
if [ "$LOCAL_COUNT" -gt "$RETENTION_COUNT" ]; then
    ls -1t "$BACKUP_DIR"/wikiio_backup_*.sql.gz \
        | tail -n +$((RETENTION_COUNT + 1)) \
        | xargs rm -f
    echo "  已清理 $((LOCAL_COUNT - RETENTION_COUNT)) 份本地旧备份"
else
    echo "  本地备份数 ($LOCAL_COUNT) 未超过保留阈值，无需清理"
fi

# 清理 COS（仅 coscli 支持）
if command -v coscli &> /dev/null; then
    COS_FILES=$(coscli ls "$COS_BUCKET/wikiio/backups/" 2>/dev/null | wc -l)
    if [ "$COS_FILES" -gt "$RETENTION_COUNT" ]; then
        coscli ls "$COS_BUCKET/wikiio/backups/" 2>/dev/null \
            | sort -r \
            | tail -n +$((RETENTION_COUNT + 1)) \
            | while read -r _ key; do
                coscli rm "$COS_BUCKET/$key"
            done
        echo "  已清理 COS 旧备份"
    fi
fi

echo ""
echo "=== 备份完成 ==="
