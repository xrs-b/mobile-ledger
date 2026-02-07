# 💰 Mobile Ledger

轻量级移动记账应用 | Vue 3 + FastAPI

## ✨ 功能特性

- **📝 记账** - 快速记录收支，支持二级分类
- **📊 统计** - 月度/年度统计，ECharts 图表展示
- **💰 预算** - 预算管理和超支提醒
- **🔐 安全** - JWT 认证，邀请码注册
- **📱 移动端** - 响应式设计，PWA 支持
- **🌐 跨平台** - Docker 部署

## 🏗️ 技术栈

### 后端
- **Python 3.11+**
- **FastAPI** - 高性能 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **Pydantic V2** - 数据验证
- **PyJWT** - JWT 认证
- **SQLite** - 轻量级数据库

### 前端
- **Vue 3** - 前端框架
- **Vant 4** - 移动端 UI
- **Pinia** - 状态管理
- **ECharts** - 图表库
- **Vite** - 构建工具

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd mobile-ledger
```

### 2. 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
cd scripts
python init_db.py

# 启动服务
cd ..
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**后端地址:** http://localhost:8000

### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**前端地址:** http://localhost:3000

### 4. Docker 部署（可选）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 📁 项目结构

```
mobile-ledger/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── database.py     # 数据库配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── routers/        # API 路由
│   │   ├── auth/           # 认证模块
│   │   ├── middleware/     # 中间件
│   │   └── utils/          # 工具函数
│   ├── scripts/
│   │   └── init_db.py      # 数据库初始化
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── main.js         # 应用入口
│   │   ├── App.vue         # 根组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态
│   │   ├── api/            # API 封装
│   │   ├── utils/          # 工具函数
│   │   ├── views/          # 页面组件
│   │   └── assets/         # 静态资源
│   ├── public/             # 公共资源
│   ├── vite.config.js
│   └── package.json
│
├── docs/                    # 文档
│   ├── PROJECT_SPEC.md
│   ├── TECH_STACK.md
│   ├── DATABASE_DESIGN.md
│   ├── API_DESIGN.md
│   ├── DEVELOPMENT_PLAN.md
│   ├── RECOVERY_PROTOCOL.md
│   └── API.md
│
└── docker-compose.yml
```

## 📚 API 文档

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔐 默认账户

首次启动会自动创建管理员账户：

| 字段 | 值 |
|------|-----|
| 用户名 | admin |
| 密码 | admin123 |

**建议首次登录后立即修改密码！**

## 🧪 测试

### 后端测试

```bash
cd backend
source .venv/bin/activate
pytest
```

### 前端测试

```bash
cd frontend
npm run test
```

## 📦 构建生产版本

### 前端构建

```bash
cd frontend
npm run build
```

### Docker 镜像构建

```bash
# 后端镜像
docker build -t mobile-ledger-backend ./backend

# 前端镜像
docker build -t mobile-ledger-frontend ./frontend
```

## 🐳 Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

## 📱 移动端

- 支持添加到主屏幕（PWA）
- iOS/Android 响应式适配
- 离线访问支持（需配置）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
