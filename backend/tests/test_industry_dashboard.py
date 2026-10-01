"""Read-only industry dashboard: authentication, data provenance and exact values."""
from datetime import date, datetime, timezone
from decimal import Decimal

from app.database import SessionLocal


def test_industry_dashboard_requires_login(client):
    assert client.get('/api/industry-dashboard/snapshot').status_code == 401


def test_industry_dashboard_empty_is_not_demo_data(client, user_headers):
    result = client.get('/api/industry-dashboard/snapshot', headers=user_headers)
    assert result.status_code == 200
    data = result.json()
    assert data['industry']['observations'] == []
    assert data['market']['rows'] == []
    assert data['meta']['last_import_at'] is None
    assert data['meta']['automatic_collection'] is False


def test_industry_dashboard_preserves_precision_sources_and_latest_period(client, user_headers):
    from app.models.industry_data import IndustryObservation, AgriDataSource, AgriDataImportRun
    from app.models.market_price import MarketPriceObservation
    with SessionLocal() as db:
        db.add(AgriDataSource(source_id='dashboard_test', name='Test source', domain='industry',
                             source_url='https://example.com/release', status='collected', coverage='全国'))
        db.add_all([
            IndustryObservation(external_key='a'*64, source_id='dashboard_test', source_url='https://example.com/old',
                                metric='agricultural_related_credit', metric_name='涉农贷款余额', region='全国', category='信贷',
                                period_start=date(2024, 12, 31), period_end=date(2024, 12, 31), frequency='quarterly',
                                value=Decimal('50.00'), unit='万亿元', measure_type='balance', qualifier='exact',
                                evidence='previous release', review_status='collected'),
            IndustryObservation(external_key='b'*64, source_id='dashboard_test', source_url='https://example.com/new',
                                metric='agricultural_related_credit', metric_name='涉农贷款余额', region='全国', category='信贷',
                                period_start=date(2025, 12, 31), period_end=date(2025, 12, 31), frequency='quarterly',
                                value=Decimal('53.570001'), unit='万亿元', measure_type='balance', qualifier='gt',
                                evidence='over this amount', review_status='collected'),
        ])
        db.add(MarketPriceObservation(external_key='c'*64, source_id='moa_daily', source_url='https://example.com/price',
                                     market_name='全国', province='', category='蔬菜', commodity='白菜', observed_date=date(2025, 9, 30),
                                     quote_type='national_wholesale_mean', source_unit='元/公斤', price_avg=Decimal('3.1234'),
                                     price_avg_yuan_per_kg=Decimal('3.1234'), quality_flag='ok'))
        db.add(AgriDataImportRun(snapshot_sha256='d'*64, status='completed', manifest={},
                                verified_at=datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc)))
        db.commit()
    try:
        result = client.get('/api/industry-dashboard/snapshot', headers=user_headers)
        assert result.status_code == 200
        data = result.json()
        rows = data['industry']['observations']
        assert len(rows) == 1
        assert rows[0]['value'] == '53.570001'
        assert rows[0]['qualifier'] == 'gt'
        assert rows[0]['period_end'] == '2025-12-31'
        assert rows[0]['source_url'] == 'https://example.com/new'
        assert data['market']['rows'][0]['price_avg'] == '3.1234'
        assert data['market']['history'][0]['observed_date'] == '2025-09-30'
        assert data['meta']['industry_total'] == 2
        assert data['meta']['market_total'] == 1
        assert data['meta']['last_import_at'].startswith('2026-10-01')
    finally:
        with SessionLocal() as db:
            db.query(IndustryObservation).filter(IndustryObservation.source_id == 'dashboard_test').delete()
            db.query(AgriDataSource).filter(AgriDataSource.source_id == 'dashboard_test').delete()
            db.query(MarketPriceObservation).filter(MarketPriceObservation.external_key == 'c'*64).delete()
            db.query(AgriDataImportRun).filter(AgriDataImportRun.snapshot_sha256 == 'd'*64).delete()
            db.commit()
