# Architecture — funeng

## Overview

**现代农业赋能平台** — 为农业产业链提供数字化管理工具。前端 Vue 3 + TypeScript，后端 Python FastAPI + SQLite，支持冷链物流、智慧农业、供应链金融等核心业务。

**关键设计决策：**
- 前后端分离，通过 RESTful API 通信
- 单数据库（SQLite）简化部署
- 模块化业务划分（每个业务模块独立 API + Model + View）

---

## Directory Structure

```
funeng/
├── backend/
│   ├── app/
│   │   ├── api/          # RESTful API 路由
│   │   ├── models/       # SQLAlchemy 数据模型
│   │   └── schemas/      # Pydantic 请求/响应模式
│   ├── main.py           # FastAPI 入口
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/        # 页面视图
│   │   ├── components/   # 可复用组件
│   │   ├── router/       # Vue Router 配置
│   │   └── stores/       # Pinia 状态管理
│   └── package.json
└── README.md
```

---

## Layer Rules

```
frontend/views  →  backend/api     ← HTTP API 调用（allowed）
backend/api     →  backend/models  ← 数据库访问（allowed）
backend/models  →  backend/api     ← FORBIDDEN（禁止循环依赖）
frontend/views  →  frontend/stores ← 状态管理（allowed）
```

**依赖方向：**
```
用户请求 → Frontend Views → Backend API → Backend Models → SQLite
           ↑                                                    ↓
           └──────────── Response ─────────────────────────────┘
```

---

## Key Packages

### 后端 API 模块

| 模块 | 文件 | 职责 |
|------|------|------|
| **认证** | `api/auth.py` | JWT 登录/注册/权限验证 |
| **用户管理** | `api/users.py` | 用户 CRUD、角色管理 |
| **分类管理** | `api/categories.py` | 农产品分类管理 |
| **产品管理** | `api/products.py` | 农产品 CRUD、库存管理 |
| **冷链物流** | `api/cold_chain.py` | 冷链订单、收货单、物流跟踪 |
| **智慧农业** | `api/smart_agriculture.py` | 环境监测、设备管理、农事记录 |
| **数字营销** | `api/digital_marketing.py` | 营销内容、推广活动 |
| **供应链金融** | `api/supply_chain_finance.py` | 贷款申请、信用评估 |
| **仪表盘** | `api/dashboard.py` | 数据统计、图表数据 |

### 后端数据模型

| 模型 | 文件 | 对应表 |
|------|------|--------|
| 用户 | `models/user.py` | users |
| 分类 | `models/category.py` | categories |
| 产品 | `models/product.py` | products |
| 智慧农业 | `models/smart_agriculture.py` | 多个表 |
| 管理员 | `models/admin.py` | admins |

### 前端视图模块

| 视图 | 文件 | 对应 API |
|------|------|----------|
| 登录/注册 | `LoginView.vue` / `RegisterView.vue` | `/api/auth/*` |
| 首页 | `HomeView.vue` | 多个 |
| 仪表盘 | `DashboardView.vue` | `/api/dashboard` |
| 冷链物流 | `ColdChain.vue` (73KB) | `/api/cold_chain/*` |
| 智慧农业 | `SmartAgriculture.vue` | `/api/smart_agriculture/*` |
| 数字营销 | `DigitalMarketing.vue` | `/api/digital_marketing/*` |
| 供应链金融 | `SupplyChainFinance.vue` | `/api/supply_chain_finance/*` |
| 产品管理 | `ProductsView.vue` | `/api/products/*` |
| 分类管理 | `CategoriesView.vue` | `/api/categories/*` |

---

## Dependency Injection

**后端（FastAPI）：**
- 使用 FastAPI 的 `Depends()` 进行依赖注入
- 数据库会话：`get_db()` 通过 `Depends` 注入到每个 API
- 当前用户：`get_current_user()` 从 JWT Token 解析

**示例：**
```python
@router.get("/products")
def read_products(db: Session = Depends(get_db), 
                  current_user: User = Depends(get_current_user)):
    # db 和 current_user 自动注入
    pass
```

**前端（Vue 3 + Pinia）：**
- 使用 Pinia stores 进行全局状态管理
- 组件通过 `useStore()` 获取状态
- API 调用封装在 stores 中

---

## Key Invariants

1. **API 必须验证用户身份** — 所有需要登录的接口必须使用 `Depends(get_current_user)`
2. **数据库操作必须参数化** — 禁止字符串拼接 SQL，防止注入攻击
3. **前端禁止直接访问数据库** — 所有数据必须通过 API 获取
4. **错误必须统一处理** — API 错误返回统一格式 `{ code, message, data }`
5. **敏感操作必须记录日志** — 登录、删除、修改权限等操作必须写日志
6. **冷链订单状态机不可逆** — 已完成的订单不能回退到待处理状态
7. **所有金额计算使用 Decimal** — 禁止使用 float 计算金额，防止精度丢失

---

## Data Flow Example

**冷链物流下单流程：**

```
用户 → ColdChain.vue 
       ↓ (POST /api/cold_chain/orders)
    auth.py (验证 JWT)
       ↓
    cold_chain.py (创建订单)
       ↓
    models/product.py (扣减库存)
    models/cold_chain.py (创建订单记录)
       ↓
    SQLite (事务提交)
       ↓
    返回订单 ID
```

---

*最后更新：2026-03-30 | 维护者：龙大师团队*
