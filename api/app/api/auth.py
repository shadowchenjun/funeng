"""
认证 API - 使用 Supabase
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import Optional
import bcrypt

from app import supabase_client

router = APIRouter()

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT 配置
SECRET_KEY = "funeng-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def verify_password(plain_password: str, stored_password: str) -> bool:
    """验证密码，兼容明文和哈希密码"""
    if not stored_password:
        return False
    # 如果是明文密码（导入的数据），直接比较
    if stored_password == plain_password:
        return True
    # 如果是哈希密码，用 bcrypt 验证
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), stored_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = supabase_client.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

# 注册
@router.post("/register")
def register(user_data: dict):
    username = user_data.get("username")
    password = user_data.get("password")
    email = user_data.get("email", "")
    full_name = user_data.get("full_name", "")
    
    # 检查用户名是否已存在
    existing_user = supabase_client.get_user_by_username(username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建用户
    hashed_password = get_password_hash(password)
    new_user = supabase_client.create_user({
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_admin": False
    })
    
    return new_user

# 登录
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = supabase_client.get_user_by_username(form_data.username)
    
    # 兼容 hashed_password 和 password 字段
    stored_password = user.get('hashed_password') or user.get('password', '') if user else ''
    
    if not user or not verify_password(form_data.password, stored_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    # 创建 token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# 获取当前用户信息
@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
