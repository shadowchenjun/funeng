# 农业赋能平台

## 项目概述

农业赋能平台是一个专业的农产品管理和销售平台，采用现代化的技术栈构建，提供完整的产品管理、用户认证、权限控制等功能。

## 技术栈

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Element Plus** - 企业级UI组件库
- **Pinia** - Vue状态管理库
- **Vue Router** - 官方路由管理器
- **Axios** - HTTP请求库
- **Vite** - 现代化构建工具

### 后端
- **Python 3.9+** - 编程语言
- **FastAPI** - 现代化Web框架
- **SQLAlchemy** - ORM框架
- **MySQL 8.0** - 关系型数据库
- **JWT** - 身份认证
- **微信OAuth** - 第三方登录

## 功能特性

### 🎯 核心功能
- ✅ **用户认证系统** - 微信OAuth登录，JWT令牌管理
- ✅ **权限控制系统** - 基于角色的访问控制（RBAC）
- ✅ **产品管理系统** - 完整的CRUD操作，支持图片上传
- ✅ **分类管理系统** - 灵活的产品分类
- ✅ **图片管理系统** - 本地存储，压缩优化

### 🔐 权限体系
- **管理员（admin）** - 全部权限
- **编辑员（editor）** - 产品管理权限
- **查看员（viewer）** - 只读权限
- **客户（customer）** - 基础浏览权限

### 📱 界面特性
- 响应式设计，支持移动端
- 现代化UI界面
- 直观的操作体验
- 完整的错误处理

## 项目结构

```
funeng/
├── backend/                 # Python FastAPI后端
│   ├── main.py             # 应用入口
│   ├── requirements.txt    # Python依赖
│   ├── .env               # 环境配置
│   └── app/               # 应用核心
│       ├── api/           # API路由
│       ├── models/        # 数据模型
│       ├── schemas/       # 数据验证
│       ├── services/      # 业务逻辑
│       └── utils/         # 工具函数
├── frontend/               # Vue 3前端
│   ├── package.json       # 前端依赖
│   ├── vite.config.ts     # 构建配置
│   └── src/              # 源代码
│       ├── views/         # 页面组件
│       ├── components/    # 通用组件
│       ├── api/          # API调用
│       ├── stores/       # 状态管理
│       ├── router/       # 路由配置
│       ├── utils/        # 工具函数
│       └── types/        # 类型定义
├── database/              # 数据库脚本
│   ├── database_design.sql  # 数据库结构
│   └── init_data.sql      # 初始化数据
└── docs/                 # 项目文档
```

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- MySQL 8.0+

### 1. 克隆项目
```bash
git clone <repository-url>
cd funeng
```

### 2. 后端设置
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和微信OAuth
```

### 3. 数据库设置
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE agricultural_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入数据库结构
mysql -u root -p agricultural_platform < database/database_design.sql

# 导入初始化数据
mysql -u root -p agricultural_platform < database/init_data.sql
```

### 4. 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 开发模式运行
npm run dev
```

### 5. 启动服务
```bash
# 启动后端（在backend目录）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（在frontend目录）
npm run dev
```

### 6. 访问应用
- 前端地址：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 配置说明

### 后端配置（.env）
```env
# 数据库配置
DATABASE_URL=mysql+mysqlconnector://root:password@localhost:3306/agricultural_platform

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 微信OAuth配置
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
WECHAT_REDIRECT_URI=http://localhost:8000/api/auth/wechat/callback

# 文件上传配置
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### 前端配置
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

## API文档

启动后端服务后，可以访问：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## 开发指南

### 代码规范
- 前端使用TypeScript + ESLint + Prettier
- 后端遵循PEP 8规范
- 使用语义化的Git提交信息

### 分支管理
- `main` - 生产分支
- `develop` - 开发分支
- `feature/*` - 功能分支
- `hotfix/*` - 热修复分支

### 测试
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 部署

### Docker部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 生产环境部署
1. 配置生产环境变量
2. 构建前端静态文件
3. 配置Nginx反向代理
4. 使用Gunicorn部署FastAPI应用

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 发起Pull Request

## 许可证

MIT License

## 联系方式

- 邮箱：contact@funeng.com
- 文档：https://docs.funeng.com

---

**农业赋能平台 - 让农产品管理更简单** 🌾