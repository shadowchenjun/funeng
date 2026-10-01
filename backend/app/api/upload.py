"""
文件上传API
"""
import os
import uuid
import mimetypes
import re
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.config import IS_PRODUCTION, STORAGE_IMAGE_BUCKET
from app.database import get_db
from app.models.uploaded_file import UploadedFile
from app.models.user import User
from app.api.auth import get_current_user
from app import storage

router = APIRouter()

# 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")

# 允许的图片类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
SAFE_FILENAME = re.compile(r"^[0-9]{14}_[0-9a-f]{8}\.(jpg|jpeg|png|gif|webp)$")

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

def _validate_filename(filename: str) -> None:
    if not SAFE_FILENAME.fullmatch(filename):
        raise HTTPException(status_code=400, detail="无效的文件名")

def _is_image_content(extension: str, content: bytes) -> bool:
    if extension in (".jpg", ".jpeg"):
        return content.startswith(b"\xff\xd8\xff")
    if extension == ".png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if extension == ".gif":
        return content.startswith((b"GIF87a", b"GIF89a"))
    if extension == ".webp":
        return content.startswith(b"RIFF") and content[8:12] == b"WEBP"
    return False

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传图片"""
    # 验证文件类型
    if not is_allowed_file(file.filename or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型，仅支持 jpg, jpeg, png, gif, webp"
        )
    
    # 生成唯一文件名
    file_extension = get_file_extension(file.filename or "")
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"

    content = await file.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="图片大小不能超过 10 MB")
    if not content:
        raise HTTPException(status_code=400, detail="图片内容不能为空")
    if not _is_image_content(file_extension, content):
        raise HTTPException(status_code=400, detail="图片内容与文件类型不符")
    content_type = mimetypes.guess_type(unique_filename)[0] or "application/octet-stream"

    if storage.is_configured():
        try:
            storage.upload(STORAGE_IMAGE_BUCKET, unique_filename, content, content_type)
        except storage.StorageError as exc:
            raise HTTPException(status_code=503, detail="图片存储暂不可用") from exc
    elif not IS_PRODUCTION:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(os.path.join(UPLOAD_DIR, unique_filename), "wb") as destination:
            destination.write(content)
    else:
        raise HTTPException(status_code=503, detail="图片存储未配置")

    db.add(UploadedFile(
        filename=unique_filename,
        owner_id=current_user.id,
        content_type=content_type,
        size=len(content),
    ))
    try:
        db.commit()
    except Exception:
        db.rollback()
        if storage.is_configured():
            storage.remove(STORAGE_IMAGE_BUCKET, unique_filename)
        else:
            os.remove(os.path.join(UPLOAD_DIR, unique_filename))
        raise
    
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
    _validate_filename(filename)
    if storage.is_configured():
        try:
            content = storage.download(STORAGE_IMAGE_BUCKET, filename)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="文件不存在") from exc
        except storage.StorageError as exc:
            raise HTTPException(status_code=503, detail="图片存储暂不可用") from exc
    elif not IS_PRODUCTION:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        with open(file_path, "rb") as source:
            content = source.read()
    else:
        raise HTTPException(status_code=503, detail="图片存储未配置")
    return Response(content, media_type=mimetypes.guess_type(filename)[0] or "application/octet-stream")

@router.delete("/files/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除上传的文件"""
    _validate_filename(filename)
    record = db.get(UploadedFile, filename)
    if record is None and not current_user.is_admin:
        raise HTTPException(status_code=404, detail="文件不存在")
    if record is not None and record.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权删除此文件")

    if storage.is_configured():
        try:
            storage.remove(STORAGE_IMAGE_BUCKET, filename)
        except storage.StorageError as exc:
            raise HTTPException(status_code=503, detail="图片存储暂不可用") from exc
    elif not IS_PRODUCTION:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        os.remove(file_path)
    else:
        raise HTTPException(status_code=503, detail="图片存储未配置")
    if record is not None:
        db.delete(record)
        db.commit()

    return {"message": "文件删除成功"}
