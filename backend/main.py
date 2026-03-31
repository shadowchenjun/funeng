"""
现代农业赋能平台 - 后端入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, products, categories, dashboard
from app.api import smart_agriculture, digital_marketing, cold_chain, supply_chain_finance, upload, users
from app.api.admin import router as admin_router
from app.api.analytics_platform import router as analytics_platform_router  # Sprint 2 性能优化
from app.models import base, admin
from app.models.user import User
from app.models.smart_agriculture import FarmInfo, Land, Crop
from app.models.product import Product
from app.models.category import Category
from app.models.admin import AdminUser, AdminRole
from app.database import engine, get_db
import bcrypt

# 创建数据库表
base.Base.metadata.create_all(bind=engine)

# 创建默认数据（如果不存在）- 不会删除已有数据
def seed_default_data():
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
            print("✅ 默认账号已创建: johnnychenjun / test123456")
        
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
            print("✅ 默认分类已创建")
        
        # 3. 创建默认产品
        if not db.query(Product).first():
            # 获取分类ID
            cats = {c.name: c.id for c in db.query(Category).all()}
            
            products_data = [
                {"name": "有机西红柿", "category_id": cats.get("新鲜蔬菜"), "price": 12.8, "stock": 100, "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400"},
                {"name": "新鲜黄瓜", "category_id": cats.get("新鲜蔬菜"), "price": 8.5, "stock": 150, "image_url": "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400"},
                {"name": "有机生菜", "category_id": cats.get("新鲜蔬菜"), "price": 6.0, "stock": 80, "image_url": "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400"},
                {"name": "红富士苹果", "category_id": cats.get("新鲜水果"), "price": 15.0, "stock": 200, "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400"},
                {"name": "新鲜草莓", "category_id": cats.get("新鲜水果"), "price": 35.0, "stock": 50, "image_url": "https://images.unsplash.com/photo-1518635017498-87f514b751ba?w=400"},
                {"name": "赣南脐橙", "category_id": cats.get("新鲜水果"), "price": 18.0, "stock": 120, "image_url": "https://images.unsplash.com/photo-1547514701-42782101795e?w=400"},
                {"name": "农家腊肉", "category_id": cats.get("土特产"), "price": 68.0, "stock": 30, "image_url": "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400"},
                {"name": "高山茶叶", "category_id": cats.get("土特产"), "price": 128.0, "stock": 25, "image_url": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400"},
                {"name": "土鸡蛋", "category_id": cats.get("肉禽蛋"), "price": 2.5, "stock": 500, "image_url": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?w=400"},
                {"name": "新鲜猪肉", "category_id": cats.get("肉禽蛋"), "price": 32.0, "stock": 80, "image_url": "https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=400"},
                {"name": "东北大米", "category_id": cats.get("粮油米面"), "price": 55.0, "stock": 200, "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"},
                {"name": "花生油", "category_id": cats.get("粮油米面"), "price": 45.0, "stock": 60, "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400"},
            ]
            for pd in products_data:
                if pd["category_id"]:
                    product = Product(
                        name=pd["name"],
                        category_id=pd["category_id"],
                        price=pd["price"],
                        stock=pd["stock"],
                        image_url=pd["image_url"],
                        description=f"优质{pd['name']}，产地直销"
                    )
                    db.add(product)
            db.commit()
            print("✅ 默认产品已创建")
        
        # 4. 创建默认农场
        if not db.query(FarmInfo).first():
            farm = FarmInfo(
                name="智慧生态农场",
                address="山东省济南市历城区",
                lat=36.65,
                lng=117.12,
                total_area=120,
                manager="张建国",
                phone="138****8888",
                coords="36.65°N, 117.12°E",
                status="normal",
                description="专注于有机农业的现代化农场",
                established_date="2020-01-01"
            )
            db.add(farm)
            db.commit()
            db.refresh(farm)
            
            # 创建默认地块
            lands_data = [
                {"name": "A区大棚1", "area": 15, "crop": "西红柿", "crops": "西红柿,黄瓜", "status": "normal"},
                {"name": "B区大棚2", "area": 20, "crop": "黄瓜", "crops": "黄瓜,茄子", "status": "normal"},
                {"name": "C区露天", "area": 30, "crop": "小麦", "crops": "小麦,玉米", "status": "normal"},
                {"name": "D区露天", "area": 25, "crop": "玉米", "crops": "玉米,大豆", "status": "normal"},
            ]
            for ld in lands_data:
                land = Land(name=ld["name"], area=ld["area"], crop=ld["crop"], crops=ld["crops"], farm_id=farm.id, status=ld["status"])
                db.add(land)
            
            # 创建默认作物
            crops_data = [
                {"name": "小麦", "category": "粮食", "planting_season": "秋季", "growth_days": 240, "yield_per_mu": 800},
                {"name": "玉米", "category": "粮食", "planting_season": "春季", "growth_days": 120, "yield_per_mu": 1000},
                {"name": "水稻", "category": "粮食", "planting_season": "夏季", "growth_days": 150, "yield_per_mu": 1200},
                {"name": "西红柿", "category": "蔬菜", "planting_season": "春季", "growth_days": 90, "yield_per_mu": 5000},
                {"name": "黄瓜", "category": "蔬菜", "planting_season": "春季", "growth_days": 60, "yield_per_mu": 4000},
                {"name": "茄子", "category": "蔬菜", "planting_season": "春季", "growth_days": 80, "yield_per_mu": 3500},
                {"name": "大豆", "category": "粮食", "planting_season": "夏季", "growth_days": 100, "yield_per_mu": 300},
            ]
            for cd in crops_data:
                crop = Crop(name=cd["name"], category=cd["category"], planting_season=cd["planting_season"], growth_days=cd["growth_days"], yield_per_mu=cd["yield_per_mu"], status="active")
                db.add(crop)
            
            db.commit()
            print("✅ 默认农场和作物已创建")

        # 5. 创建默认管理员角色
        if not db.query(AdminRole).first():
            admin_role = AdminRole(
                name="超级管理员",
                code="super_admin",
                description="系统超级管理员，拥有所有权限",
                permissions='["*"]'
            )
            db.add(admin_role)
            db.commit()
            print("✅ 默认管理员角色已创建")

        # 6. 创建默认管理员账号
        if not db.query(AdminUser).first():
            role = db.query(AdminRole).filter(AdminRole.code == "super_admin").first()
            hashed = bcrypt.hashpw("admin123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            default_admin = AdminUser(
                username="admin",
                email="admin@funeng.com",
                hashed_password=hashed,
                full_name="系统管理员",
                is_active=True,
                role_id=role.id if role else None
            )
            db.add(default_admin)
            db.commit()
            print("✅ 默认管理员账号已创建: admin / admin123456")

    except Exception as e:
        print(f"⚠️ 初始化数据时出错: {e}")
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://*.trycloudflare.com", "https://*.loca.lt"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(products.router, prefix="/api/products", tags=["产品管理"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(smart_agriculture.router, prefix="/api/smart-agriculture", tags=["智慧农业"])
app.include_router(digital_marketing.router, prefix="/api/digital-marketing", tags=["数字营销"])
app.include_router(cold_chain.router, prefix="/api/cold-chain", tags=["数字冷链物联"])
app.include_router(supply_chain_finance.router, prefix="/api/supply-chain-finance", tags=["供应链金融"])
app.include_router(admin_router)
app.include_router(analytics_platform_router, prefix="/api", tags=["平台分析(优化)"])  # Sprint 2

@app.get("/")
async def root():
    return {"message": "现代农业赋能平台 API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
