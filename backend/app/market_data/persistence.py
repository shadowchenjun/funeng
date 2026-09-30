"""Idempotent observation storage. Caller controls the database transaction."""
from sqlalchemy import select

from app.models.market_price import MarketPriceObservation


FIELDS = ("source_id", "source_url", "market_name", "province", "category", "commodity",
          "specification", "origin", "observed_date", "period_start", "period_end",
          "quote_type", "source_unit", "price_min", "price_avg", "price_max",
          "price_min_yuan_per_kg", "price_avg_yuan_per_kg", "price_max_yuan_per_kg",
          "quality_flag", "source_row_key")


def upsert_observations(session, observations):
    inserted = updated = 0
    for observation in observations:
        values = {field: getattr(observation, field) for field in FIELDS}
        saved = session.scalar(select(MarketPriceObservation).where(
            MarketPriceObservation.external_key == observation.external_key))
        if saved is None:
            session.add(MarketPriceObservation(external_key=observation.external_key, **values))
            inserted += 1
        elif any(getattr(saved, field) != value for field, value in values.items()):
            for field, value in values.items():
                setattr(saved, field, value)
            updated += 1
    session.commit()
    return inserted, updated
