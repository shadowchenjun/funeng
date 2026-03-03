"""
现代农业赋能平台 - 后端入口
支持 SQLite 本地开发和 Supabase 云端生产环境
"""
import os
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 根据环境选择数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_SUPABASE = bool(DATABASE_URL and ("postgresql" in DATABASE_URL or "postgres" in DATABASE_URL))

if USE_SUPABASE:
    from app.database_supabase import engine, get_db
else:
    from app.database import engine, get_db

from app.api import auth, products, categories, dashboard
from app.api import smart_agriculture, digital_marketing, cold_chain, supply_chain_finance, users

# 根据环境选择上传模块
USE_OSS = os.getenv("OSS_ENABLED", "false").lower() == "true"

if USE_OSS:
    from app.api.upload_oss import router as upload_router
else:
    from app.api.upload import router as upload_router

from app.models import base

# 创建数据库表（不插入数据，因为已经在 Supabase 中）
try:
    base.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️ 创建表时出错: {e}")

app = FastAPI(
    title="现代农业赋能平台 API",
    description="现代农业赋能平台后端服务",
    version="1.0.0"
)

# 配置CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://*.trycloudflare.com",
    "https://*.loca.lt",
    "https://*.vercel.app",
]

CUSTOM_DOMAIN = os.getenv("CUSTOM_DOMAIN", "")
if CUSTOM_DOMAIN:
    ALLOWED_ORIGINS.append(f"https://{CUSTOM_DOMAIN}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(products.router, prefix="/api/products", tags=["产品管理"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])
app.include_router(upload_router, prefix="/api/upload", tags=["文件上传"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(smart_agriculture.router, prefix="/api/smart-agriculture", tags=["智慧农业"])
app.include_router(digital_marketing.router, prefix="/api/digital-marketing", tags=["数字营销"])
app.include_router(cold_chain.router, prefix="/api/cold-chain", tags=["数字冷链物联"])
app.include_router(supply_chain_finance.router, prefix="/api/supply-chain-finance", tags=["供应链金融"])

@app.get("/")
async def root():
    return {"message": "现代农业赋能平台 API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
