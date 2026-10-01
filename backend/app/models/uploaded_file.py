"""Persistent metadata for uploaded images."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.models.base import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    filename = Column(String(100), primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
