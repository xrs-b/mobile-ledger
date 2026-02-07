# 📁 项目文档清单

## 核心文档

| 文档 | 文件 | 描述 |
|------|------|------|
| 📋 需求规格 | PROJECT_SPEC.md | 完整功能需求 |
| 🛠️ 技术选型 | TECH_STACK.md | 技术栈说明 |
| 💾 数据库设计 | DATABASE_DESIGN.md | 数据表结构 |
| 🌐 API设计 | API_DESIGN.md | 接口文档 |
| 📅 开发计划 | DEVELOPMENT_PLAN.md | 开发任务清单 |
| 🛡️ 断点续传 | RECOVERY_PROTOCOL.md | 进度追踪与恢复 |
| 📊 进度状态 | PROGRESS.json | 当前开发进度 |

## 使用指南

### 查看需求
```bash
cat PROJECT_SPEC.md
```

### 查看当前进度
```bash
cat PROGRESS.json | jq '.'
```

### 查看开发计划
```bash
cat DEVELOPMENT_PLAN.md
```

### 断点续传
```bash
# 查看恢复协议
cat RECOVERY_PROTOCOL.md

# 检查进度
cat PROGRESS.json | jq '.current_phase, .current_task'
```

## 目录结构

```
docs/
├── PROJECT_SPEC.md      # 需求规格
├── TECH_STACK.md        # 技术选型
├── DATABASE_DESIGN.md   # 数据库设计
├── API_DESIGN.md       # API设计
├── DEVELOPMENT_PLAN.md  # 开发计划
├── RECOVERY_PROTOCOL.md # 断点续传
└── PROGRESS.json       # 进度状态
```

---

> 最后更新：2026-02-07
