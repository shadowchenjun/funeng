"""
阿里云 OSS 文件上传模块
支持本地存储和阿里云 OSS 存储切换
"""
import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()

# ============== 阿里云 OSS 配置 ==============
# 环境变量配置
OSS_ENABLED = os.getenv("OSS_ENABLED", "false").lower() == "true"
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "")  # 如: https://oss-cn-beijing.aliyuncs.com
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET", "")
OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME", "")
OSS_PUBLIC_URL = os.getenv("OSS_PUBLIC_URL", "")  # OSS 公共访问地址

# 本地存储配置
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的图片类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    file_extension = get_file_extension(original_filename)
    return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"

# 阿里云 OSS 客户端（延迟导入）
oss2 = None
bucket = None

if OSS_ENABLED:
    try:
        import oss2
        auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)
        print("✅ 阿里云 OSS 已启用")
    except ImportError:
        print("⚠️ 阿里云 OSS SDK 未安装，将使用本地存储")
        OSS_ENABLED = False
    except Exception as e:
        print(f"⚠️ 阿里云 OSS 配置错误: {e}，将使用本地存储")
        OSS_ENABLED = False

def upload_to_oss(file_content: bytes, filename: str) -> str:
    """上传文件到阿里云 OSS"""
    if bucket is None:
        raise Exception("OSS not initialized")
    result = bucket.put_object(filename, file_content)
    if result.status == 200:
        return f"{OSS_PUBLIC_URL}/{filename}"
    raise Exception("OSS upload failed")

def delete_from_oss(filename: str) -> bool:
    """从阿里云 OSS 删除文件"""
    if bucket is None:
        return False
    try:
        bucket.delete_object(filename)
        return True
    except:
        return False

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
    unique_filename = generate_unique_filename(file.filename)
    
    # 读取文件内容
    content = await file.read()
    
    if OSS_ENABLED and bucket:
        # 上传到阿里云 OSS
        try:
            file_url = upload_to_oss(content, unique_filename)
        except Exception as e:
            # OSS 上传失败，回退到本地存储
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            with open(file_path, "wb") as f:
                f.write(content)
            file_url = f"/api/upload/files/{unique_filename}"
    else:
        # 本地存储
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as f:
            f.write(content)
        file_url = f"/api/upload/files/{unique_filename}"
    
    return {
        "filename": unique_filename,
        "url": file_url,
        "size": len(content)
    }

@router.get("/files/{filename}")
async def get_file(filename: str):
    """获取上传的文件"""
    if OSS_ENABLED and bucket:
        # 从 OSS 获取签名 URL
        try:
            signed_url = bucket.sign_url('GET', filename, 3600)
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=signed_url)
        except:
            pass
    
    # 本地文件
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
    if OSS_ENABLED:
        if delete_from_oss(filename):
            return {"message": "文件删除成功"}
    
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    os.remove(file_path)
    return {"message": "文件删除成功"}
