"""Backend-only collection audit and cross-instance source lease."""
from sqlalchemy import Column, Date, DateTime, Index, Integer, JSON, String, Text, text

from .base import Base


class AgriCollectionRun(Base):
    __tablename__ = 'agri_collection_runs'

    run_id = Column(String(36), primary_key=True)
    source_id = Column(Text, nullable=False)
    target_date = Column(Date, nullable=False)
    status = Column(Text, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    lease_until = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    inserted = Column(Integer, nullable=False, default=0)
    updated = Column(Integer, nullable=False, default=0)
    observed = Column(Integer, nullable=False, default=0)
    errors = Column(JSON, nullable=False, default=list)

    __table_args__ = (
        Index('agri_collection_one_running_source', 'source_id', unique=True,
              postgresql_where=text("status = 'running'"), sqlite_where=text("status = 'running'")),
        Index('agri_collection_recent', 'started_at'),
    )
