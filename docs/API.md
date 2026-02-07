# 移动账本 API 文档

## 概述

移动账本后端API基于FastAPI构建，提供完整的记账、统计和预算管理功能。

**基础URL:** `http://localhost:8000/api/v1`

**认证方式:** Bearer Token (JWT)

---

## 认证接口

### 注册用户
```
POST /api/v1/auth/register
```

**请求体:**
```json
{
  "username": "string",    // 4-50字符
  "password": "string",    // 6-128字符
  "invitation_code": "string"  // 邀请码
}
```

**响应:**
```json
{
  "user_id": 1,
  "username": "testadmin",
  "is_admin": true,
  "message": "注册成功"
}
```

### 登录
```
POST /api/v1/auth/login
```

**请求体:**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应:**
```json
{
  "token": "eyJhbG...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "testadmin",
    "is_admin": true
  }
}
```

### 获取用户信息
```
GET /api/v1/auth/profile
```
**需要认证**

---

## 分类接口

### 获取分类列表
```
GET /api/v1/categories
```

**参数:**
- `type`: income | expense
- `include_private`: boolean

### 获取分类树
```
GET /api/v1/categories/tree
```

### 创建分类
```
POST /api/v1/categories
```
**需要认证**

**请求体:**
```json
{
  "name": "string",
  "parent_id": null,
  "icon": "string",
  "type": "income | expense",
  "sort_order": 0
}
```

### 更新分类
```
PUT /api/v1/categories/{id}
```
**需要认证**

### 删除分类
```
DELETE /api/v1/categories/{id}
```
**需要认证** (仅限私有分类)

---

## 记账接口

### 获取记账列表
```
GET /api/v1/records
```
**需要认证**

**参数:**
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `type`: income | expense
- `category_id`: number
- `project_id`: number
- `page`: number
- `page_size`: number

### 获取记账汇总
```
GET /api/v1/records/summary
```
**需要认证**

### 创建记账
```
POST /api/v1/records
```
**需要认证**

**请求体:**
```json
{
  "amount": 100.0,
  "type": "income | expense",
  "category_id": 1,
  "remark": "string",
  "project_id": null,
  "record_date": "YYYY-MM-DD"
}
```

### 更新记账
```
PUT /api/v1/records/{id}
```
**需要认证**

### 删除记账
```
DELETE /api/v1/records/{id}
```
**需要认证**

---

## 项目接口

### 获取项目列表
```
GET /api/v1/projects
```
**需要认证**

**参数:**
- `status`: active | completed | cancelled
- `page`: number
- `page_size`: number

### 获取项目详情
```
GET /api/v1/projects/{id}
```
**需要认证**

### 创建项目
```
POST /api/v1/projects
```
**需要认证**

**请求体:**
```json
{
  "name": "string",
  "description": "string",
  "budget": 10000,
  "member_count": 3,
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD"
}
```

### 更新项目
```
PUT /api/v1/projects/{id}
```
**需要认证**

### 删除项目
```
DELETE /api/v1/projects/{id}
```
**需要认证**

---

## 统计接口

### 概览统计
```
GET /api/v1/statistics/overview
```
**需要认证**

**响应:**
```json
{
  "today_income": 5000.0,
  "today_expense": 200.0,
  "today_balance": 4800.0,
  "month_income": 5000.0,
  "month_expense": 200.0,
  "month_balance": 4800.0,
  "active_projects": 2,
  "recent_records_count": 4
}
```

### 每日统计
```
GET /api/v1/statistics/daily
```
**需要认证**

**参数:**
- `year`: 2024
- `month`: 1-12

### 月度统计
```
GET /api/v1/statistics/monthly
```
**需要认证**

**参数:**
- `year`: 2024

### 年度统计
```
GET /api/v1/statistics/yearly
```
**需要认证**

**参数:**
- `year`: 2024

### 分类统计
```
GET /api/v1/statistics/category
```
**需要认证**

**参数:**
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `type`: income | expense

### 趋势分析
```
GET /api/v1/statistics/trend
```
**需要认证**

**参数:**
- `days`: 1-365 (默认30)
- `type`: income | expense | both

### 仪表盘
```
GET /api/v1/statistics/dashboard
```
**需要认证**

**参数:**
- `days`: 1-30 (默认7)

### 月度对比
```
GET /api/v1/statistics/compare/months
```
**需要认证**

**参数:**
- `month1`: 1-12
- `year1`: 2020-2100
- `month2`: 1-12
- `year2`: 2020-2100

### 分类对比
```
GET /api/v1/statistics/compare/categories
```
**需要认证**

---

## 预算接口

### 获取预算列表
```
GET /api/v1/budgets
```
**需要认证**

### 创建预算
```
POST /api/v1/budgets
```
**需要认证**

**请求体:**
```json
{
  "category_id": null,
  "name": "月度预算",
  "amount": 5000,
  "period": "monthly",
  "alert_threshold": 80
}
```

### 获取预算详情
```
GET /api/v1/budgets/{id}
```
**需要认证**

### 更新预算
```
PUT /api/v1/budgets/{id}
```
**需要认证**

### 删除预算
```
DELETE /api/v1/budgets/{id}
```
**需要认证**

### 预算摘要
```
GET /api/v1/budgets/summary/current
```
**需要认证**

### 预算预警
```
GET /api/v1/budgets/alerts
```
**需要认证**

---

## 健康检查

### 简单检查
```
GET /health
```

### 详细检查
```
GET /health/detailed
```

---

## 错误响应

**格式:**
```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "错误信息"
  }
}
```

**常见错误码:**
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 响应头

所有API响应包含以下头:
- `X-Process-Time`: 请求处理时间(秒)
- `Content-Type`: application/json

---

## 默认邀请码

- `admin123`

---

## 测试账号

- 用户名: `testadmin`
- 密码: `test123`

**注意:** 第一个注册的用户自动成为管理员。
