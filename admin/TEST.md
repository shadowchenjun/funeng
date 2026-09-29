# 汤原农文旅云 - 后台管理系统测试用例

## 测试环境准备

```bash
# 1. 启动后端（本仓库 FastAPI，端口 8000）
npm run dev:backend

# 2. 启动管理后台（端口 3001，/api 代理到 8000）
npm run dev:admin
```

## 测试账号

- URL: http://localhost:3001
- 用户名: admin
- 密码: admin123456

## API 测试用例

### 1. 认证模块

```bash
# 1.1 管理员登录
curl -X POST http://localhost:8000/api/admin/auth/login \
  -d 'username=admin&password=admin123456'
# 期望: 返回 access_token 和 admin 用户信息

# 1.2 获取管理员信息
TOKEN="你的token"
curl http://localhost:8000/api/admin/auth/profile \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回当前管理员详细信息

# 1.3 登出
curl -X POST http://localhost:8000/api/admin/auth/logout \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回 {"message": "登出成功"}
```

### 2. 数据看板

```bash
# 2.1 获取看板统计
curl http://localhost:8000/api/admin/dashboard/stats \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回 users, land, adoption_orders, rental_orders, devices, products 统计数据

# 2.2 获取图表数据
curl "http://localhost:8000/api/admin/dashboard/charts?days=7" \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回 daily_orders, daily_revenue, land_usage, device_status, category_data
```

### 3. 土地管理

```bash
# 3.1 获取土地列表
curl "http://localhost:8000/api/admin/land/parcels?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回 { total, page, page_size, items: [...] }

# 3.2 获取租地订单
curl "http://localhost:8000/api/admin/land/rental-orders?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回租地订单列表
```

### 4. 认养管理

```bash
# 4.1 获取认养分类
curl http://localhost:8000/api/admin/adoption/categories \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回认养分类列表

# 4.2 获取认养配置
curl http://localhost:8000/api/admin/adoption/configs \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回认养配置列表

# 4.3 获取认养订单
curl "http://localhost:8000/api/admin/adoption/orders?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回认养订单列表
```

### 5. 设备管理

```bash
# 5.1 获取设备类型
curl http://localhost:8000/api/admin/device/types \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回设备类型列表

# 5.2 获取设备列表
curl "http://localhost:8000/api/admin/device/devices?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回设备列表
```

### 6. 溯源管理

```bash
# 6.1 获取溯源配置
curl http://localhost:8000/api/admin/traceability/configs \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回溯源配置列表
```

### 7. 用户管理

```bash
# 7.1 获取用户列表
curl "http://localhost:8000/api/admin/user/users?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回用户列表
```

### 8. 营销管理

```bash
# 8.1 获取优惠券
curl "http://localhost:8000/api/admin/marketing/coupons?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回优惠券列表
```

### 9. 管理员管理

```bash
# 9.1 获取管理员列表
curl http://localhost:8000/api/admin/admin-user/admins \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回管理员列表

# 9.2 获取角色列表
curl http://localhost:8000/api/admin/admin-user/roles \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回角色列表
```

### 10. 系统配置

```bash
# 10.1 获取系统配置
curl http://localhost:8000/api/admin/system/configs \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回系统配置列表

# 10.2 获取操作日志
curl "http://localhost:8000/api/admin/system/logs?page=1&page_size=50" \
  -H "Authorization: Bearer $TOKEN"
# 期望: 返回操作日志列表
```

## 前端功能测试

### 页面加载测试

1. 访问 http://localhost:3001/login
2. 输入用户名: admin
3. 输入密码: admin123456
4. 点击登录按钮
5. 期望: 跳转到首页看板 http://localhost:3001/dashboard

### 功能模块测试

| 模块 | 测试页面 | 检查项 |
|------|---------|--------|
| 数据看板 | /dashboard | 统计卡片、图表、快捷操作 |
| 认养管理 | /adoption | 分类、配置、订单Tab |
| 土地管理 | /land | 土地列表、租地订单 |
| 设备管理 | /device | 设备类型、设备列表 |
| 溯源管理 | /traceability | 溯源配置、节点、记录 |
| 用户管理 | /user | 用户列表、分组 |
| 营销管理 | /marketing | 优惠券、活动 |
| 管理员管理 | /admin | 管理员、角色 |
| 系统设置 | /settings | 系统配置、操作日志 |

### 样式检查

1. 左侧导航栏: 深蓝色背景 (#1e3a5f)，白色选中高亮
2. 登录页: 蓝色渐变背景，白色登录框
3. 卡片: 圆角 (12px)，阴影效果
4. 按钮: 统一圆角样式

## 冒烟测试清单

- [ ] 登录功能正常
- [ ] Token 能正常保存和携带
- [ ] 左侧导航菜单可点击切换
- [ ] 首页看板数据显示正常
- [ ] 各模块列表页面能正常加载
- [ ] 登出功能正常
- [ ] 无 404 资源请求错误
- [ ] 无 JavaScript 控制台错误

## 回归测试

每次代码修改后，执行以下关键测试:

1. `npm run build` - 确保构建成功
2. 登录 -> 登出 -> 再次登录
3. 访问所有菜单页面，确认无报错
4. 检查 Network 面板，确认无 404 请求
