# Conventions — funeng

## 命名规范

### 后端（Python）

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 模块文件 | `snake_case` | `smart_agriculture.py` |
| 类名 | `PascalCase` | `Product`, `ColdChainOrder` |
| 函数/方法 | `snake_case` | `get_current_user()`, `create_order()` |
| 变量 | `snake_case` | `current_user`, `order_id` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_UPLOAD_SIZE`, `JWT_ALGORITHM` |

### 前端（TypeScript + Vue）

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 组件文件 | `PascalCase.vue` | `ImageUpload.vue` |
| 视图文件 | `PascalCase` + `View.vue` | `LoginView.vue`, `ColdChain.vue` |
| 变量/函数 | `camelCase` | `currentUser`, `handleLogin()` |
| 类型/接口 | `PascalCase` | `User`, `Order`, `ProductList` |
| 常量 | `UPPER_SNAKE_CASE` | `API_BASE_URL`, `MAX_FILE_SIZE` |
| Store | `camelCase` + `Store` | `useUserStore()`, `useOrderStore()` |

---

## 代码风格

### Python（后端）

```python
# ✅ 正确 - 类型注解 + 文档字符串
from typing import Optional
from fastapi import Depends, HTTPException

def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    """获取产品详情
    
    Args:
        product_id: 产品 ID
        db: 数据库会话
        
    Returns:
        Product: 产品对象
        
    Raises:
        HTTPException: 404 产品不存在
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
```

**规范：**
- ✅ 所有函数必须有类型注解
- ✅ 所有公共 API 必须有 docstring
- ✅ 使用 `HTTPException` 而非通用 `Exception`
- ✅ 遵循 PEP 8 风格

### TypeScript（前端）

```typescript
// ✅ 正确 - 类型注解 + 错误处理
interface Product {
  id: number
  name: string
  price: number
}

async function fetchProducts(): Promise<Product[]> {
  try {
    const response = await fetch('/api/products')
    if (!response.ok) throw new Error('Fetch failed')
    return await response.json()
  } catch (error) {
    console.error('Failed to fetch products:', error)
    return []
  }
}
```

**规范：**
- ✅ 所有函数必须有返回类型注解
- ✅ 所有 API 调用必须有错误处理
- ✅ 使用 `async/await` 而非 Promise 链
- ✅ 使用 `const` 而非 `let`

### Vue 组件

**规范：**
- ✅ 使用 `<script setup lang="ts">` 语法糖
- ✅ 使用 Composition API 而非 Options API
- ✅ 使用 Pinia stores 而非 Vuex
- ✅ 使用 `scoped` 样式

---

## 文件组织

### 后端

```
backend/app/
├── api/          # API 路由（按业务模块划分）
├── models/       # SQLAlchemy 模型
└── schemas/      # Pydantic 模式
```

### 前端

```
frontend/src/
├── views/        # 页面视图
├── components/   # 可复用组件
├── router/       # 路由配置
├── stores/       # Pinia 状态管理
└── assets/       # 静态资源
```

---

## Git Commit 规范

```
<type>(<scope>): <subject>

# type: feat | fix | docs | style | refactor | test | chore
# scope: 模块名（可选）
# subject: 简短描述（50 字符内）
```

**示例：**
```bash
# ✅ 正确
feat(cold-chain): 添加收货单功能
fix(auth): 修复 JWT 过期时间计算错误
docs: 更新 API 文档
refactor(smart-agriculture): 拆分大组件

# ❌ 错误
update code
fix bug
add new feature
```

---

## API 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": { "id": 1, "name": "产品 A" }
}
```

### 错误响应
```json
{
  "code": 404,
  "message": "产品不存在",
  "data": null
}
```

### 列表响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

---

*最后更新：2026-03-30 | 维护者：龙大师团队*
