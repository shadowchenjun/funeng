"""Authenticated, read-only snapshot for the six-page industry dashboard."""
from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.industry_data import (
    AgriDataImportRun, AgriDataSource, ColdChainReferenceNode, IndustryObservation,
)
from app.models.market_price import MarketPriceObservation

router = APIRouter()
MARKET_LIMIT = 10000


def serialize_value(value: object) -> object:
    """Preserve decimal values; distinguish UTC ingestion time from observation dates."""
    if isinstance(value, Decimal):
        number = format(value, 'f')
        return number.rstrip('0').rstrip('.') if '.' in number else number
    if isinstance(value, datetime):
        return (value if value.tzinfo else value.replace(tzinfo=timezone.utc)).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def observation(row: object) -> dict:
    """Serialize mapped columns without SQLAlchemy internals or credentials."""
    return {c.name: serialize_value(getattr(row, c.name)) for c in row.__table__.columns}


@router.get('/snapshot')
def get_snapshot(response: Response, db: Session = Depends(get_db)) -> dict:
    """Read imported observations; never scrape, mutate data, or substitute demo data."""
    response.headers['Cache-Control'] = 'private, no-store'
    statistics = db.query(IndustryObservation).order_by(
        IndustryObservation.period_end.desc(), IndustryObservation.updated_at.desc(),
        IndustryObservation.external_key,
    ).all()
    # Latest release for each metric/population; overlapping loan types remain separate.
    latest = {}
    for row in statistics:
        key = (row.metric, row.region, row.category, row.unit, row.measure_type)
        if key not in latest:
            latest[key] = observation(row)
    rows = list(latest.values())
    prices = [observation(r) for r in db.query(MarketPriceObservation).order_by(
        MarketPriceObservation.observed_date.desc(), MarketPriceObservation.external_key,
    ).limit(MARKET_LIMIT).all()]
    sources = [{
        'source_id': s.source_id, 'name': s.name, 'domain': s.domain,
        'url': s.source_url, 'status': s.status, 'scope': s.coverage,
    } for s in db.query(AgriDataSource).order_by(AgriDataSource.source_id).all()]
    nodes = [dict(observation(n), region=n.province)
             for n in db.query(ColdChainReferenceNode).order_by(ColdChainReferenceNode.name).all()]
    run = db.query(AgriDataImportRun).filter(AgriDataImportRun.status == 'completed').order_by(
        AgriDataImportRun.created_at.desc()).first()
    dates = [r['observed_date'] for r in prices]
    market_total = db.query(MarketPriceObservation).count()
    return {
        'meta': {
            'last_import_at': serialize_value(run.verified_at or run.created_at) if run else None,
            'automatic_collection': False, 'industry_total': len(statistics),
            'market_total': market_total, 'market_returned': len(prices),
            'market_truncated': market_total > MARKET_LIMIT,
            'price_from': min(dates) if dates else None,
            'price_to': max(dates) if dates else None,
            'generated_at': datetime.now(timezone.utc).isoformat(),
        },
        'industry': {
            'observations': [r for r in rows if r['review_status'] == 'collected'],
            'manual_observations': [r for r in rows if r['review_status'] == 'manual_reviewed'],
            'sources': [s for s in sources if s['domain'] == 'industry'],
            'reference_sources': [], 'cold_nodes': nodes, 'market_record_count': len(prices),
        },
        'market': {'rows': prices, 'history': [r for r in prices if r['quote_type'] == 'national_wholesale_mean'],
                   'sources': [s for s in sources if s['domain'] == 'market']},
    }
