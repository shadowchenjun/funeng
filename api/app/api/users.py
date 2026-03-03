"""
用户管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()

# 用户管理Schema
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserListResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# 获取所有用户（仅管理员）
@router.get("/", response_model=List[UserListResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可访问"
        )
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.username.contains(search)) | 
            (User.email.contains(search)) |
            (User.full_name.contains(search))
        )
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users

# 获取用户统计
@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户统计信息"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可访问"
        )
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "admin_users": admin_users
    }

# 更新用户
@router.put("/{user_id}", response_model=UserListResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户信息（仅管理员或本人）"""
    # 只有管理员可以修改其他用户，普通用户只能修改自己的信息
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 权限检查：管理员可以修改任何用户，普通用户只能修改自己
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此用户"
        )
    
    # 管理员才能修改 is_admin 和 is_active
    if current_user.is_admin:
        if user_data.is_active is not None:
            target_user.is_active = user_data.is_active
    
    # 更新其他字段
    if user_data.email is not None:
        target_user.email = user_data.email
    if user_data.full_name is not None:
        target_user.full_name = user_data.full_name
    
    db.commit()
    db.refresh(target_user)
    
    return target_user

# 禁用/启用用户
@router.patch("/{user_id}/status")
def toggle_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """禁用/启用用户（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可执行此操作"
        )
    
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能禁用自己
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己的账户")
    
    target_user.is_active = is_active
    db.commit()
    
    status_text = "启用" if is_active else "禁用"
    return {"message": f"用户 {status_text} 成功"}
