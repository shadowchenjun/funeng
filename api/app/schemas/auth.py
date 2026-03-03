"""
认证相关的Schema
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 用户注册
class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    full_name: Optional[str] = None

# 用户登录
class UserLogin(BaseModel):
    username: str
    password: str

# 用户信息
class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
