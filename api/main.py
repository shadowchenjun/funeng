"""
现代农业赋能平台 - 后端入口
使用 Supabase Python SDK
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, products, categories, dashboard
from app.api import smart_agriculture, digital_marketing, cold_chain, supply_chain_finance, users

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
