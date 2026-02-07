#!/bin/bash
# backup.sh - 移动账本项目备份脚本

BACKUP_DIR=~/mobile-ledger/backups
PROJECT_DIR=~/mobile-ledger
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "🚀 开始备份: $TIMESTAMP"

# 备份代码目录
if [ -d "$PROJECT_DIR/backend" ]; then
    echo "📦 备份 backend..."
    cp -r $PROJECT_DIR/backend $BACKUP_DIR/backend_$TIMESTAMP
fi

if [ -d "$PROJECT_DIR/frontend" ]; then
    echo "📦 备份 frontend..."
    cp -r $PROJECT_DIR/frontend $BACKUP_DIR/frontend_$TIMESTAMP
fi

# 备份文档
if [ -d "$PROJECT_DIR/docs" ]; then
    echo "📚 备份 docs..."
    cp -r $PROJECT_DIR/docs $BACKUP_DIR/docs_$TIMESTAMP
fi

# 备份数据库
if [ -f "$PROJECT_DIR/data/mobile_ledger.db" ]; then
    echo "💾 备份数据库..."
    cp $PROJECT_DIR/data/mobile_ledger.db $BACKUP_DIR/mobile_ledger_$TIMESTAMP.db
fi

# 备份docker配置
if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
    echo "🐳 备份 docker-compose.yml..."
    cp $PROJECT_DIR/docker-compose.yml $BACKUP_DIR/docker-compose_$TIMESTAMP.yml
fi

# 清理旧备份（保留最近10个）
echo "🧹 清理旧备份..."
ls -1d $BACKUP_DIR/*_$TIMESTAMP 2>/dev/null | head -10 | while read backup; do
    echo "  保留: $(basename $backup)"
done

echo ""
echo "✅ 备份完成: $TIMESTAMP"
echo "📂 备份位置: $BACKUP_DIR"
