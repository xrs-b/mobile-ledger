# 💾 数据库设计文档

> 版本：1.0  
> 创建时间：2026-02-07  
> 状态：✅ 已确认

---

## 📋 数据库总览

**数据库**：SQLite  
**位置**：`data/mobile_ledger.db`

---

## 📊 数据表设计

### 1. users（用户表）

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 账号 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| is_admin | BOOLEAN | DEFAULT FALSE | 是否管理员 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| invitation_code | VARCHAR(50) | | 使用的邀请码 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- `idx_users_username` (username)
- `idx_users_is_admin` (is_admin)

---

### 2. categories（分类表）

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 分类ID |
| user_id | INTEGER | DEFAULT NULL | 所属用户（NULL=系统默认） |
| name | VARCHAR(100) | NOT NULL | 分类名称 |
| parent_id | INTEGER | DEFAULT NULL | 父分类ID |
| icon | VARCHAR(255) | | 图标URL/emoji |
| type | VARCHAR(10) | NOT NULL | income/expense |
| is_system | BOOLEAN | DEFAULT FALSE | 是否系统分类 |
| sort_order | INTEGER | DEFAULT 0 | 排序 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- `idx_categories_user_id` (user_id)
- `idx_categories_parent_id` (parent_id)
- `idx_categories_type` (type)

**约束**：
- FOREIGN KEY (parent_id) REFERENCES categories(id)

---

### 3. ledger_records（记账记录表）

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 记录ID |
| user_id | INTEGER | NOT NULL | 所属用户 |
| category_id | INTEGER | NOT NULL | 分类ID |
| amount | DECIMAL(10,2) | NOT NULL | 金额 |
| type | VARCHAR(10) | NOT NULL | income/expense |
| remark | VARCHAR(500) | | 备注 |
| project_id | INTEGER | DEFAULT NULL | 关联项目（NULL=日常） |
| record_date | DATE | NOT NULL | 记录日期 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- `idx_records_user_id` (user_id)
- `idx_records_category_id` (category_id)
- `idx_records_project_id` (project_id)
- `idx_records_record_date` (record_date)

**约束**：
- FOREIGN KEY (category_id) REFERENCES categories(id)
- FOREIGN KEY (project_id) REFERENCES projects(id)

---

### 4. projects（项目表）

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 项目ID |
| user_id | INTEGER | NOT NULL | 所属用户 |
| name | VARCHAR(200) | NOT NULL | 项目名称 |
| description | VARCHAR(1000) | | 项目描述 |
| budget | DECIMAL(12,2) | DEFAULT 0 | 预算金额 |
| member_count | INTEGER | DEFAULT 1 | 参与人数 |
| start_date | DATE | | 开始日期 |
| end_date | DATE | | 结束日期 |
| status | VARCHAR(20) | DEFAULT active | active/completed/cancelled |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- `idx_projects_user_id` (user_id)
- `idx_projects_status` (status)
- `idx_projects_dates` (start_date, end_date)

---

### 5. system_config（系统配置表）

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 配置ID |
| config_key | VARCHAR(100) | UNIQUE | 配置键 |
| config_value | TEXT | | 配置值 |
| description | VARCHAR(500) | | 配置描述 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**默认配置**：
| config_key | config_value | description |
|------------|--------------|-------------|
| default_invitation_code | admin123 | 默认邀请码 |
| max_users | 1000 | 最大用户数 |
| demo_mode | false | 演示模式 |

---

### 6. invitation_codes（邀请码表）

| 字段 | 类型 | 约束 | 描述 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | ID |
| code | VARCHAR(50) | UNIQUE, NOT NULL | 邀请码 |
| is_used | BOOLEAN | DEFAULT FALSE | 是否已使用 |
| used_by | INTEGER | DEFAULT NULL | 使用者ID |
| used_at | DATETIME | | 使用时间 |
| created_by | INTEGER | NOT NULL | 创建者（管理员） |
| expires_at | DATETIME | | 过期时间 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引**：
- `idx_invitation_codes_code` (code)
- `idx_invitation_codes_is_used` (is_used)

---

## 🔗 表关系图

```
users (1) ────< (N) categories
     │
     │───< (N) ledger_records
     │          │
     │          └──< (N) projects
     │
     └───< (N) invitation_codes (created_by)

categories (1) ────< (N) ledger_records
```

---

## 📈 统计视图

### 日常消费统计视图
```sql
CREATE VIEW daily_stats AS
SELECT
    user_id,
    record_date,
    type,
    SUM(amount) as total_amount,
    COUNT(*) as record_count
FROM ledger_records
WHERE project_id IS NULL
GROUP BY user_id, record_date, type;
```

### 项目消费统计视图
```sql
CREATE VIEW project_stats AS
SELECT
    pr.id as project_id,
    pr.name,
    pr.budget,
    pr.member_count,
    pr.start_date,
    pr.end_date,
    COALESCE(SUM(lr.amount), 0) as total_spent,
    CASE
        WHEN pr.budget > 0
        THEN ROUND((COALESCE(SUM(lr.amount), 0) / pr.budget) * 100, 2)
        ELSE 0
    END as budget_usage_rate,
    CASE
        WHEN pr.member_count > 0
        THEN ROUND(COALESCE(SUM(lr.amount), 0) / pr.member_count, 2)
        ELSE 0
    END as per_person_cost
FROM projects pr
LEFT JOIN ledger_records lr ON pr.id = lr.project_id
GROUP BY pr.id;
```

---

## ✅ 确认状态

| 表名 | 状态 | 备注 |
|------|------|------|
| users | ✅ | 用户表 |
| categories | ✅ | 分类表 |
| ledger_records | ✅ | 记账记录表 |
| projects | ✅ | 项目表 |
| system_config | ✅ | 系统配置表 |
| invitation_codes | ✅ | 邀请码表 |

---

> 📝 文档版本：1.0  
> 下次更新：开发过程中
