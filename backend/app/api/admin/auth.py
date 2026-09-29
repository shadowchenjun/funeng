"""
管理员认证API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt

from app.config import ADMIN_SECRET_KEY as SECRET_KEY, JWT_ALGORITHM as ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.models.admin import AdminUser, AdminOperationLog
from app.schemas.admin import ProfileUpdate, PasswordChange, apply_update

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证"
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )


def get_current_admin(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    username = token.get("sub")
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员不存在"
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员账号已被禁用"
        )
    return admin


def serialize_role(role) -> Optional[dict]:
    """登录与 profile 接口统一的角色结构"""
    if role is None:
        return None
    return {
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "permissions": role.permissions
    }


def log_operation(db: Session, admin_id: int, action: str, resource: str, resource_id: int = None, detail: str = None):
    log = AdminOperationLog(
        admin_user_id=admin_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        detail=detail
    )
    db.add(log)
    db.commit()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """管理员登录"""
    admin = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()

    if not admin:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not bcrypt.checkpw(form_data.password.encode('utf-8'), admin.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not admin.is_active:
        raise HTTPException(status_code=401, detail="账号已被禁用")

    # 更新最后登录时间
    admin.last_login = datetime.now()
    db.commit()

    # 创建token
    access_token = create_access_token(data={"sub": admin.username, "is_admin": True})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "email": admin.email,
            "avatar": admin.avatar,
            "role": serialize_role(admin.role)
        }
    }


@router.post("/logout")
def logout(current_admin: AdminUser = Depends(get_current_admin)):
    """管理员登出"""
    return {"message": "登出成功"}


@router.get("/profile")
def get_profile(current_admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    """获取当前管理员信息"""
    admin = db.query(AdminUser).filter(AdminUser.id == current_admin.id).first()
    return {
        "id": admin.id,
        "username": admin.username,
        "full_name": admin.full_name,
        "email": admin.email,
        "phone": admin.phone,
        "avatar": admin.avatar,
        "role": serialize_role(admin.role),
        "last_login": admin.last_login,
        "created_at": admin.created_at
    }


@router.put("/profile")
def update_profile(
    body: ProfileUpdate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新管理员信息"""
    admin = db.query(AdminUser).filter(AdminUser.id == current_admin.id).first()

    if body.email:
        existing = db.query(AdminUser).filter(AdminUser.email == body.email, AdminUser.id != admin.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
    apply_update(admin, body)

    admin.updated_at = datetime.now()
    db.commit()

    return {"message": "更新成功"}


@router.post("/change-password")
def change_password(
    body: PasswordChange,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """修改密码"""
    admin = db.query(AdminUser).filter(AdminUser.id == current_admin.id).first()

    if not bcrypt.checkpw(body.old_password.encode('utf-8'), admin.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="原密码错误")

    admin.hashed_password = bcrypt.hashpw(body.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin.updated_at = datetime.now()
    db.commit()

    return {"message": "密码修改成功"}
