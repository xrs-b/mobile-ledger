# 🌐 API设计文档

> 版本：1.0  
> 创建时间：2026-02-07  
> 状态：✅ 已确认

---

## 📋 API基础信息

| 项目 | 值 |
|------|------|
| **Base URL** | `/api/v1` |
| **认证方式** | JWT Bearer Token |
| **状态码** | HTTP标准 |
| **返回格式** | JSON |

---

## 🔐 认证模块

### POST /auth/register - 用户注册

**Request**
```json
{
  "username": "string (4-50)",
  "password": "string (6-128)",
  "invitation_code": "string"
}
```

**Response 201**
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "username": "test_user",
    "is_admin": true
  }
}
```

**Response 400**
```json
{
  "code": 400,
  "message": "邀请码无效"
}
```

---

### POST /auth/login - 用户登录

**Request**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response 200**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "test_user",
      "is_admin": true
    }
  }
}
```

---

## 👤 用户模块

### GET /users/profile - 获取个人信息

**Response 200**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "test_user",
    "is_admin": true,
    "created_at": "2026-02-07T10:00:00"
  }
}
```

---

## 🏷️ 分类模块

### GET /categories - 获取分类列表

**Query Parameters**
| 参数 | 类型 | 描述 |
|------|------|------|
| type | string | income/expense (可选) |
| parent_id | integer | 父分类ID (可选) |
| include_private | boolean | 是否包含私有分类 (默认true) |

**Response 200**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "餐饮",
      "parent_id": null,
      "type": "expense",
      "icon": "🍔",
      "is_system": true,
      "children": [
        {
          "id": 2,
          "name": "早餐",
          "parent_id": 1,
          "icon": "🥪",
          "type": "expense"
        }
      ]
    }
  ]
}
```

---

### POST /categories - 创建分类

**Request**
```json
{
  "name": "自定义分类",
  "parent_id": 1,
  "type": "expense",
  "icon": "⭐"
}
```

---

## 💰 记账模块

### GET /records - 获取记账列表

**Query Parameters**
| 参数 | 类型 | 描述 |
|------|------|------|
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |
| type | string | income/expense |
| category_id | integer | 分类ID |
| project_id | integer | 项目ID |
| page | integer | 页码 (默认1) |
| page_size | integer | 每页数量 (默认20) |

**Response 200**
```json
{
  "code": 200,
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "records": [
      {
        "id": 1,
        "amount": 50.00,
        "type": "expense",
        "remark": "XX餐厅",
        "category": {
          "id": 2,
          "name": "午餐",
          "icon": "🍱"
        },
        "project": null,
        "record_date": "2026-02-07",
        "created_at": "2026-02-07T10:00:00"
      }
    ]
  }
}
```

---

### POST /records - 创建记账

**Request**
```json
{
  "amount": 35.00,
  "type": "expense",
  "category_id": 2,
  "remark": "XX麻辣烫",
  "project_id": null,
  "record_date": "2026-02-07"
}
```

**项目记账示例**
```json
{
  "amount": 5000.00,
  "type": "expense",
  "category_id": 4,
  "remark": "东京之旅-机票",
  "project_id": 1,
  "record_date": "2026-02-07"
}
```

---

## 📊 项目模块

### GET /projects - 获取项目列表

**Query Parameters**
| 参数 | 类型 | 描述 |
|------|------|------|
| status | string | active/completed/cancelled |
| page | integer | 页码 |
| page_size | integer | 每页数量 |

**Response 200**
```json
{
  "code": 200,
  "data": {
    "projects": [
      {
        "id": 1,
        "name": "东京之旅",
        "description": "2026年春节日本游",
        "budget": 20000.00,
        "member_count": 4,
        "start_date": "2026-01-25",
        "end_date": "2026-02-05",
        "status": "active",
        "stats": {
          "total_spent": 15000.00,
          "budget_usage_rate": 75.00,
          "per_person_cost": 3750.00
        }
      }
    ]
  }
}
```

---

### POST /projects - 创建项目

**Request**
```json
{
  "name": "东京之旅",
  "description": "2026年春节日本游",
  "budget": 20000.00,
  "member_count": 4,
  "start_date": "2026-01-25",
  "end_date": "2026-02-05"
}
```

---

## 📈 统计模块

### GET /stats/dashboard - 仪表盘数据

**Query Parameters**
| 参数 | 类型 | 描述 |
|------|------|------|
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |

**Response 200**
```json
{
  "code {
    "total_in": 200,
  "data":come": 15000.00,
    "total_expense": 8000.00,
    "balance": 7000.00,
    "category_distribution": [
      {
        "category_name": "餐饮",
        "amount": 2000.00,
        "percentage": 25.00,
        "icon": "🍔"
      }
    ],
    "daily_trend": [
      {
        "date": "2026-02-01",
        "income": 500.00,
        "expense": 200.00
      }
    ],
    "project_summary": [
      {
        "project_name": "东京之旅",
        "budget": 20000.00,
        "spent": 15000.00,
        "usage_rate": 75.00
      }
    ]
  }
}
```

---

### GET /stats/by-category - 按分类统计

**Query Parameters**
| 参数 | 类型 | 描述 |
|------|------|------|
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |
| type | string | income/expense |

---

### GET /stats/by-project - 按项目统计

---

## ⚙️ 管理后台模块（仅管理员）

### GET /admin/users - 用户管理列表

**Response 200**
```json
{
  "code": 200,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "admin",
        "is_admin": true,
        "is_active": true,
        "created_at": "2026-02-07T10:00:00",
        "last_login": "2026-02-07T12:00:00"
      }
    ],
    "total": 10
  }
}
```

---

### PUT /admin/users/:id/disable - 禁用用户

---

### GET /admin/categories - 分类管理

---

### POST /admin/invitation-codes - 生成邀请码

**Request**
```json
{
  "count": 5,
  "expires_at": "2026-12-31"
}
```

---

## ❌ 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 数据验证错误 |
| 500 | 服务器错误 |

---

## ✅ 确认状态

| 模块 | 状态 | 备注 |
|------|------|------|
| 认证模块 | ✅ | 注册/登录 |
| 用户模块 | ✅ | 个人信息 |
| 分类模块 | ✅ | CRUD |
| 记账模块 | ✅ | CRUD |
| 项目模块 | ✅ | CRUD |
| 统计模块 | ✅ | 多维度报表 |
| 管理模块 | ✅ | 用户/分类/邀请码 |

---

> 📝 文档版本：1.0  
> 下次更新：开发过程中
