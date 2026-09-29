"""Persistent status for CSV exports."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.models.base import Base


class ExportTaskRecord(Base):
    __tablename__ = "export_tasks"

    id = Column(String(36), primary_key=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    export_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    progress = Column(Integer, nullable=False, default=0)
    storage_key = Column(String(100), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
