# Mobile Ledger - Frontend

Mobile-first记账应用前端，基于 Vue 3 + Vant UI。

## 技术栈

- **Vue 3** - 前端框架
- **Vant 4** - 移动端 UI 组件库
- **Pinia** - 状态管理
- **Vue Router 4** - 路由管理
- **ECharts** - 图表库
- **Vite** - 构建工具

## 启动开发服务器

```bash
cd frontend
npm install
npm run dev
```

## 构建生产版本

```bash
cd frontend
npm run build
```

## 配置说明

### API 代理
开发环境通过 Vite 代理将 `/api` 请求转发到后端服务：
- 后端地址: `http://localhost:8000`
- 前端地址: `http://localhost:3000`

### 移动端适配
- 使用 `amfe-flexible` 实现 rem 适配
- 基于 375px 设计稿，rootValue: 37.5
- Viewport meta 标签已配置

### PWA 支持
- 支持添加到主屏幕
- 支持离线访问（需配置 Service Worker）
- iOS/Android 图标已配置

## 页面结构

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录 | `/login` | 用户登录 |
| 注册 | `/register` | 用户注册 |
| 首页 | `/dashboard` | 月度概览 |
| 记一笔 | `/add` | 新增记账 |
| 账单 | `/records` | 账单列表 |
| 统计 | `/statistics` | 图表统计 |
| 预算 | `/budget` | 预算管理 |
| 我的 | `/profile` | 个人中心 |

## API 集成

所有 API 请求通过 `src/api/request.js` 封装：
- 自动携带 JWT Token
- 自动处理错误响应
- 配置代理避免跨域
