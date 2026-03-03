"""
现代农业赋能平台 - 后端入口
支持 SQLite 本地开发和 Supabase 云端生产环境
"""
import os
import sys

print("="*50, file=sys.stderr)
print("🚀 启动应用...", file=sys.stderr)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 调试：打印环境变量
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...", file=sys.stderr)

# 根据环境选择数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_SUPABASE = bool(DATABASE_URL and ("postgresql" in DATABASE_URL or "postgres" in DATABASE_URL))

print(f"USE_SUPABASE: {USE_SUPABASE}", file=sys.stderr)

if USE_SUPABASE:
    from app.database_supabase import engine, get_db
    print("🔗 连接到 Supabase 云数据库", file=sys.stderr)
else:
    from app.database import engine, get_db
    print("🔗 连接到 SQLite 本地数据库", file=sys.stderr)

from app.api import auth, products, categories, dashboard
from app.api import smart_agriculture, digital_marketing, cold_chain, supply_chain_finance, users

# 根据环境选择上传模块
USE_OSS = os.getenv("OSS_ENABLED", "false").lower() == "true"

if USE_OSS:
    from app.api.upload_oss import router as upload_router
    print("☁️ 阿里云 OSS 已启用", file=sys.stderr)
else:
    from app.api.upload import router as upload_router
    print("💾 本地文件存储已启用", file=sys.stderr)

from app.models import base
from app.models.user import User
from app.models.smart_agriculture import FarmInfo, Land, Crop
from app.models.product import Product
from app.models.category import Category
import bcrypt

# 创建数据库表
print("📋 正在创建数据库表...", file=sys.stderr)
try:
    base.Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功", file=sys.stderr)
except Exception as e:
    print(f"❌ 创建数据库表失败: {e}", file=sys.stderr)

# 创建默认数据
def seed_default_data():
    print("🌱 开始初始化默认数据...", file=sys.stderr)
    db = next(get_db())
    try:
        # 1. 创建默认账号
        if not db.query(User).filter(User.username == "johnnychenjun").first():
            hashed = bcrypt.hashpw("test123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            default_user = User(
                username="johnnychenjun",
                email="johnnychenjun@test.com",
                hashed_password=hashed,
                is_active=True,
                is_admin=True
            )
            db.add(default_user)
            db.commit()
            print("✅ 默认账号已创建: johnnychenjun / test123456", file=sys.stderr)
        else:
            print("ℹ️ 用户已存在", file=sys.stderr)
        
        # 2. 创建默认分类
        if not db.query(Category).first():
            categories_data = [
                {"name": "新鲜蔬菜", "icon": "🥬", "description": "新鲜采摘的蔬菜"},
                {"name": "新鲜水果", "icon": "🍎", "description": "新鲜水果"},
                {"name": "土特产", "icon": "🎁", "description": "地方特产"},
                {"name": "肉禽蛋", "icon": "🥩", "description": "新鲜肉类和禽蛋"},
                {"name": "粮油米面", "icon": "🌾", "description": "粮食和食用油"},
            ]
            for cd in categories_data:
                cat = Category(name=cd["name"], icon=cd["icon"], description=cd["description"])
                db.add(cat)
            db.commit()
            print("✅ 默认分类已创建", file=sys.stderr)
        
        # 3. 创建默认产品
        if not db.query(Product).first():
            cats = {c.name: c.id for c in db.query(Category).all()}
            products_data = [
                {"name": "有机西红柿", "category_id": cats.get("新鲜蔬菜"), "price": 12.8, "stock": 100},
                {"name": "新鲜黄瓜", "category_id": cats.get("新鲜蔬菜"), "price": 8.5, "stock": 150},
                {"name": "有机生菜", "category_id": cats.get("新鲜蔬菜"), "price": 6.0, "stock": 80},
                {"name": "红富士苹果", "category_id": cats.get("新鲜水果"), "price": 15.0, "stock": 200},
            ]
            for pd in products_data:
                if pd["category_id"]:
                    product = Product(
                        name=pd["name"],
                        category_id=pd["category_id"],
                        price=pd["price"],
                        stock=pd["stock"],
                        image_url="",
                        description=f"优质{pd['name']}"
                    )
                    db.add(product)
            db.commit()
            print("✅ 默认产品已创建", file=sys.stderr)
            
    except Exception as e:
        print(f"⚠️ 初始化数据时出错: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

# 启动时初始化数据
seed_default_data()

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

app = app
# Vercel Serverless
