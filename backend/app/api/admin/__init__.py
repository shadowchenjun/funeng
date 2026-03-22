"""
管理员API路由
"""
from fastapi import APIRouter
from app.api.admin import auth, dashboard, adoption, land, device, traceability, user, marketing, system, admin_user

router = APIRouter(prefix="/admin", tags=["管理员"])

router.include_router(auth.router, prefix="/auth", tags=["管理员认证"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["数据看板"])
router.include_router(adoption.router, prefix="/adoption", tags=["认养管理"])
router.include_router(land.router, prefix="/land", tags=["土地管理"])
router.include_router(device.router, prefix="/device", tags=["设备管理"])
router.include_router(traceability.router, prefix="/traceability", tags=["溯源管理"])
router.include_router(user.router, prefix="/user", tags=["用户管理"])
router.include_router(marketing.router, prefix="/marketing", tags=["营销管理"])
router.include_router(system.router, prefix="/system", tags=["系统配置"])
router.include_router(admin_user.router, prefix="/admin-user", tags=["管理员管理"])
