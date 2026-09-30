"""Source-attributed public market observations. Migrated explicitly in production."""
from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, Text, func

from .base import Base


class MarketPriceObservation(Base):
    __tablename__ = "market_price_observations"

    id = Column(Integer, primary_key=True)
    external_key = Column(String(64), nullable=False, unique=True, index=True)
    source_id = Column(String(40), nullable=False)
    source_url = Column(Text, nullable=False)
    market_name = Column(String(180), nullable=False)
    province = Column(String(80), nullable=False, default="")
    category = Column(String(40), nullable=False)
    commodity = Column(String(180), nullable=False)
    specification = Column(String(180), nullable=False, default="")
    origin = Column(String(180), nullable=False, default="")
    observed_date = Column(Date, nullable=False)
    period_start = Column(Date)
    period_end = Column(Date)
    quote_type = Column(String(60), nullable=False)
    source_unit = Column(String(40), nullable=False)
    price_min = Column(Numeric(12, 4))
    price_avg = Column(Numeric(12, 4))
    price_max = Column(Numeric(12, 4))
    price_min_yuan_per_kg = Column(Numeric(12, 4))
    price_avg_yuan_per_kg = Column(Numeric(12, 4))
    price_max_yuan_per_kg = Column(Numeric(12, 4))
    quality_flag = Column(String(40), nullable=False)
    source_row_key = Column(String(100), nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
