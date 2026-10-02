"""Vercel system callbacks: server secret required, never user JWTs."""
import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.market_data.cron import beijing_today, run_collection
from app.market_data.fetch import COLLECTORS

router = APIRouter()


def require_cron_secret(authorization: str | None = Header(default=None)):
    secret = os.getenv('CRON_SECRET', '')
    if len(secret) < 32:
        raise HTTPException(status_code=503, detail='Cron is not configured')
    if not hmac.compare_digest((authorization or '').encode(), f'Bearer {secret}'.encode()):
        raise HTTPException(status_code=401, detail='Unauthorized')


@router.get('/market-prices/{source}', dependencies=[Depends(require_cron_secret)])
def collect_market_prices(source: str, response: Response, db: Session = Depends(get_db)):
    """Collect an allowlisted publisher, reconcile three days and persist audit."""
    response.headers['Cache-Control'] = 'no-store'
    if source not in COLLECTORS:
        raise HTTPException(status_code=404, detail='Unknown market source')
    result = run_collection(db, source, beijing_today())
    if result['status'] in {'failed', 'partial', 'lease_lost'}:
        response.status_code = 502
    return result
