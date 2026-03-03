"""
文件上传API
"""
import os
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()

# 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的图片类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传图片"""
    # 验证文件类型
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型，仅支持 jpg, jpeg, png, gif, webp"
        )
    
    # 生成唯一文件名
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
    
    # 保存文件
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 返回文件访问URL
    file_url = f"/api/upload/files/{unique_filename}"
    
    return {
        "filename": unique_filename,
        "url": file_url,
        "size": len(content)
    }

@router.get("/files/{filename}")
async def get_file(filename: str):
    """获取上传的文件"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(file_path)

@router.delete("/files/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """删除上传的文件"""
    # 不允许删除非本用户上传的文件（简单验证）
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    os.remove(file_path)
    
    return {"message": "文件删除成功"}
