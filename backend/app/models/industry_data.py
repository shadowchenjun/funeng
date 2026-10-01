"""Read mappings for the existing, backend-only agriculture data tables."""
from sqlalchemy import Column, Date, DateTime, JSON, Numeric, String, Text, func

from .base import Base


class AgriDataSource(Base):
    __tablename__ = 'agri_data_sources'

    source_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    domain = Column(Text, nullable=False)
    source_url = Column(Text)
    status = Column(Text, nullable=False)
    coverage = Column(Text, nullable=False)
    source_metadata = Column('metadata', JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class IndustryObservation(Base):
    __tablename__ = 'industry_observations'

    external_key = Column(Text, primary_key=True)
    source_id = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)
    metric = Column(Text, nullable=False)
    metric_name = Column(Text, nullable=False)
    region = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    frequency = Column(Text, nullable=False)
    value = Column(Numeric, nullable=False)
    unit = Column(Text, nullable=False)
    measure_type = Column(Text, nullable=False)
    qualifier = Column(Text, nullable=False)
    yoy_percent = Column(Numeric)
    evidence = Column(Text, nullable=False)
    review_status = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ColdChainReferenceNode(Base):
    __tablename__ = 'cold_chain_reference_nodes'

    external_key = Column(Text, primary_key=True)
    source_id = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    province = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    reported = Column(Text, nullable=False)
    scope = Column(Text, nullable=False)
    snapshot_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AgriDataImportRun(Base):
    __tablename__ = 'agri_data_import_runs'

    snapshot_sha256 = Column(String(64), primary_key=True)
    status = Column(Text, nullable=False)
    manifest = Column(JSON, nullable=False)
    verification = Column(JSON)
    verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
