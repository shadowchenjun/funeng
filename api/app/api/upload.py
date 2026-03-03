"""文件上传 API - 使用阿里云 OSS"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends
from app import supabase_client
from app.api.auth import get_current_user

router = APIRouter()

# 阿里云 OSS 配置
OSS_ENABLED = os.getenv("OSS_ENABLED", "false").lower() == "true"
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "https://oss-cn-beijing.aliyuncs.com")
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET", "")
OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME", "benlai-openclaw")
OSS_PUBLIC_URL = os.getenv("OSS_PUBLIC_URL", "https://benlai-openclaw.oss-cn-beijing.aliyuncs.com")

# OSS 客户端
oss_client = None
if OSS_ENABLED and OSS_ACCESS_KEY_ID:
    try:
        import oss2
        auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
        oss_client = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)
        print(f"✅ 阿里云 OSS 已启用: {OSS_BUCKET_NAME}")
    except Exception as e:
        print(f"❌ OSS 初始化失败: {e}")

def generate_filename(filename: str) -> str:
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """上传图片到阿里云 OSS"""
    if not oss_client:
        return {"error": "OSS未配置", "url": ""}
    
    # 读取文件内容
    content = await file.read()
    
    # 生成唯一文件名
    filename = generate_filename(file.filename or "image.jpg")
    
    # 上传到 OSS
    try:
        result = oss_client.put_object(filename, content)
        if result.status == 200:
            url = f"{OSS_PUBLIC_URL}/{filename}"
            return {"url": url, "filename": filename}
    except Exception as e:
        return {"error": str(e), "url": ""}
    
    return {"error": "上传失败", "url": ""}
