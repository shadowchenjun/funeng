"""文件上传 API"""
from fastapi import APIRouter
router = APIRouter()

@router.post("/image")
def upload_image():
    return {"url": "", "filename": ""}
