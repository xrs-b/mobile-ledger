# 🛠️ 技术选型文档

> 版本：1.0  
> 创建时间：2026-02-07  
> 状态：✅ 已确认

---

## 📋 技术栈总览

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **后端** | Python + FastAPI | 0.114+ | Web框架 |
| | SQLAlchemy | 2.0+ | ORM |
| | SQLite | 3.44+ | 数据库 |
| | Pydantic | 2.0+ | 数据验证 |
| | PyJWT | 2.8+ | 认证 |
| **前端** | Vue 3 | 3.4+ | 框架 |
| | Vant UI | 4.6+ | 组件库 |
| | ECharts | 5.5+ | 图表 |
| | Axios | 1.6+ | HTTP客户端 |
| | Pinia | 2.1+ | 状态管理 |
| | Vue Router | 4.2+ | 路由 |
| **部署** | Docker | 24.0+ | 容器化 |
| | Docker Compose | 2.24+ | 编排 |
| | PM2 | 5.3+ | 进程管理 |
| | Guardian | 5.0+ | 健康监控 |

---

## 🐍 后端技术详解

### FastAPI
```python
# 优点
- 自动生成Swagger/OpenAPI文档
- 异步支持（async/await）
- 高性能（接近Node.js）
- 类型提示 + Pydantic验证
- 易于学习
```

### 数据库设计
```
SQLite（轻量、嵌入式）
├── users（用户表）
├── categories（分类表）
├── ledger_records（记账记录表）
├── projects（项目表）
├── project_members（项目成员表）
└── system_config（系统配置表）
```

### 认证方案
- **JWT**：无状态认证
- **邀请码**：注册门槛
- **密码加密**：bcrypt

---

## 🎨 前端技术详解

### Vue 3 + Vant UI
```
Vant UI优势：
- 专为移动端设计
- 组件丰富
- 主题定制容易
- 文档完善
- 社区活跃
```

### ECharts图表
```
图表类型：
- 饼图（分类占比）
- 折线图（趋势变化）
- 柱状图（多期对比）
```

### 状态管理（Pinia）
```
Store设计：
- auth（认证状态）
- categories（分类数据）
- records（记账数据）
- projects（项目数据）
```

---

## 📁 项目结构

```
mobile-ledger/
├── backend/                 # Python后端
│   ├── app/
│   │   ├── main.py         # FastAPI入口
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── routers/        # API路由
│   │   ├── auth/          # JWT认证
│   │   └── services/       # 业务逻辑
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── views/         # 页面
│   │   ├── components/    # 组件
│   │   ├── stores/        # Pinia状态
│   │   ├── api/           # API封装
│   │   └── utils/         # 工具函数
│   ├── Dockerfile
│   └── package.json
├── data/                   # SQLite数据库
├── logs/                   # 日志目录
├── docker-compose.yml
└── README.md
```

---

## 🔧 开发工具

| 工具 | 用途 |
|------|------|
| **uv** | Python包管理 |
| **PDM** | Python依赖管理（备选） |
| **npm/pnpm** | Node包管理 |
| **Vue CLI / Vite** | 构建工具 |

---

## ✅ 确认状态

| 组件 | 选择 | 确认人 | 确认时间 |
|------|------|--------|----------|
| 后端框架 | FastAPI | 老细 | 2026-02-07 |
| ORM | SQLAlchemy | 老细 | 2026-02-07 |
| 数据库 | SQLite | 老细 | 2026-02-07 |
| 前端框架 | Vue 3 | 老细 | 2026-02-07 |
| UI组件库 | Vant UI | 老细 | 2026-02-07 |
| 图表库 | ECharts | 老细 | 2026-02-07 |
| 部署 | Docker Compose | 老细 | 2026-02-07 |
| 守护 | PM2 + Guardian | 老细 | 2026-02-07 |

---

> 📝 文档版本：1.0  
> 下次更新：开发过程中
