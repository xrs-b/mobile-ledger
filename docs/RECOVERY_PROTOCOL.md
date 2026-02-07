# 🛡️ 断点续传协议

> 版本：1.0  
> 创建时间：2026-02-07  
> 状态：✅ 已确认

---

## 🎯 协议目的

确保开发任务即使异常中断，也能完美恢复继续。

---

## 📁 进度追踪文件

### 位置：`~/mobile-ledger/docs/PROGRESS.json`

### 格式结构
```json
{
  "version": "1.0",
  "last_updated": "2026-02-07T13:00:00Z",
  "current_phase": "Phase_1",
  "current_task": "1.1",
  "completed_tasks": [],
  "checkpoints": {
    "Phase_0": {
      "status": "completed",
      "completed_at": "2026-02-07T13:00:00Z",
      "summary": "文档制作完成"
    },
    "Phase_1": {
      "status": "in_progress",
      "tasks": {
        "1.1": {
          "status": "pending",
          "checklist": [],
          "files_created": [],
          "notes": ""
        }
      }
    }
  },
  "error_log": []
}
```

---

## 🔧 恢复命令

### 检查当前进度
```bash
cat ~/mobile-ledger/docs/PROGRESS.json | jq '.'
```

### 重置到某个节点
```bash
# 编辑 PROGRESS.json，将对应任务改为 pending
nano ~/mobile-ledger/docs/PROGRESS.json
```

### 查看错误日志
```bash
cat ~/mobile-ledger/docs/PROGRESS.json | jq '.error_log'
```

---

## 📋 每个任务的Checklist模板

### 创建任务时必须执行
```bash
# 1. 更新任务状态为 in_progress
# 2. 记录开始时间
# 3. 记录将要创建的文件列表
# 4. 记录详细checklist
```

### 任务完成时必须执行
```bash
# 1. 核对checklist
# 2. 记录完成时间
# 3. 标记任务为 completed
# 4. 备份关键代码
# 5. 更新当前任务指针
```

### 任务异常中断时
```bash
# 1. 记录错误信息
# 2. 记录中断位置
# 3. 记录已创建文件
# 4. 保存现场
```

---

## 🎯 任务状态枚举

| 状态 | 含义 | 触发条件 |
|------|------|----------|
| **pending** | 未开始 | 任务创建时 |
| **in_progress** | 进行中 | 任务开始时 |
| **completed** | 已完成 | 任务核对checklist后 |
| **blocked** | 被阻塞 | 依赖任务未完成 |
| **error** | 出错 | 异常中断时 |

---

## 📝 进度更新命令

### Phase 1任务1.1示例
```bash
# 更新文件
nano ~/mobile-ledger/docs/PROGRESS.json

# 更新内容
{
  "current_phase": "Phase_1",
  "current_task": "1.1",
  "checkpoints": {
    "Phase_1": {
      "tasks": {
        "1.1": {
          "status": "in_progress",
          "started_at": "2026-02-07T14:00:00Z",
          "checklist": [
            "[ ] 创建backend目录",
            "[ ] 创建虚拟环境",
            "[ ] 安装依赖",
            "[ ] 创建main.py",
            "[ ] 配置CORS",
            "[ ] 配置数据库连接",
            "[ ] 创建Dockerfile"
          ],
          "files_created": [],
          "notes": ""
        }
      }
    }
  }
}
```

---

## 🛡️ 预防措施

### 开发前
- [ ] 阅读需求文档
- [ ] 阅读技术选型文档
- [ ] 阅读数据库设计文档
- [ ] 阅读API设计文档
- [ ] 阅读开发计划文档
- [ ] 更新进度文件

### 开发中
- [ ] 每个文件创建前记录
- [ ] 每个步骤完成后标记
- [ ] 定期保存进度
- [ ] 重要代码本地备份

### 开发后
- [ ] 核对所有checklist
- [ ] 记录完成时间
- [ ] 更新当前任务指针
- [ ] 备份关键文件

---

## 🚨 异常处理流程

### 1. 记录错误
```bash
# 记录到 PROGRESS.json
ERROR_LOG=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "phase": "Phase_1",
  "task": "1.1",
  "error": "LLM request rejected...",
  "location": "文件创建中...",
  "files_created": ["file1.py", "file2.py"]
}
EOF
)
echo $ERROR_LOG >> ~/mobile-ledger/docs/PROGRESS.json
```

### 2. 分析错误
```bash
# 查看错误日志
cat ~/mobile-ledger/docs/PROGRESS.json | jq '.error_log[-1]'

# 确定恢复点
# - 如果文件已创建 → 从文件恢复
# - 如果未创建 → 从checklist恢复
```

### 3. 恢复执行
```bash
# 继续执行
# 1. 从中断点继续
# 2. 或重新开始任务
```

---

## 📂 文件备份策略

### 自动备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=~/mobile-ledger/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份代码
cp -r ~/mobile-ledger/backend $BACKUP_DIR/backend_$TIMESTAMP
cp -r ~/mobile-ledger/frontend $BACKUP_DIR/frontend_$TIMESTAMP
cp ~/mobile-ledger/docs/PROGRESS.json $BACKUP_DIR/PROGRESS_$TIMESTAMP.json

echo "Backup created: $TIMESTAMP"
```

### 手动备份
```bash
# 开发关键节点执行
cd ~/mobile-ledger
bash backup.sh
```

---

## ✅ 启动前Checklist

每个任务开始前必须确认：

- [ ] 已阅读相关文档
- [ ] 已更新PROGRESS.json
- [ ] 已记录checklist
- [ ] 已准备恢复方案
- [ ] 老细已确认开始

---

## 📋 当前状态

| 项目 | 状态 |
|------|------|
| 文档制作 | ✅ 已完成 |
| Phase 1 | ⏳ 待开始 |
| Phase 2 | ⏳ 待开始 |
| Phase 3 | ⏳ 待开始 |
| Phase 4 | ⏳ 待开始 |
| Phase 5 | ⏳ 待开始 |

---

> 📝 文档版本：1.0  
> 下次更新：每个Phase开始前
