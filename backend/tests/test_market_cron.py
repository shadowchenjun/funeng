"""Cron auth, leases, failure audit and historical preservation."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.market_data.types import MarketObservation


def observation(day, price='4.2'):
    return MarketObservation(source_id='mofcom', source_url='https://cif.mofcom.gov.cn/test',
                             market_name='测试市场', category='蔬菜', commodity='西红柿',
                             observed_date=day, quote_type='market', source_unit='元/公斤',
                             price_avg=Decimal(price))


@pytest.fixture
def session():
    from app.models.market_price import MarketPriceObservation
    from app.models.collection_run import AgriCollectionRun
    engine = create_engine('sqlite:///:memory:')
    MarketPriceObservation.__table__.create(engine)
    AgriCollectionRun.__table__.create(engine)
    with Session(engine) as db:
        yield db


def test_cron_fails_closed_without_secret(client, monkeypatch):
    monkeypatch.delenv('CRON_SECRET', raising=False)
    assert client.get('/api/cron/market-prices/mofcom').status_code == 503


@pytest.mark.parametrize('header', ['', 'Bearer wrong', 'Bearer undefined'])
def test_cron_rejects_bad_secret(client, monkeypatch, header):
    monkeypatch.setenv('CRON_SECRET', 'test-cron-secret-that-is-long-enough')
    assert client.get('/api/cron/market-prices/mofcom', headers={'Authorization': header}).status_code == 401


def test_unknown_source_is_rejected_before_collection(client, monkeypatch):
    monkeypatch.setenv('CRON_SECRET', 'test-cron-secret-that-is-long-enough')
    response = client.get('/api/cron/market-prices/arbitrary',
                          headers={'Authorization': 'Bearer test-cron-secret-that-is-long-enough'})
    assert response.status_code == 404


def test_beijing_date_crosses_utc_midnight():
    from app.market_data.cron import beijing_today
    assert beijing_today(datetime(2026, 10, 1, 17, tzinfo=timezone.utc)) == date(2026, 10, 2)


def test_no_data_is_recorded_without_deleting_history(session):
    from app.market_data.cron import run_collection
    from app.market_data.persistence import upsert_observations
    from app.models.market_price import MarketPriceObservation
    upsert_observations(session, [observation(date(2026, 9, 30))])
    result = run_collection(session, 'mofcom', date(2026, 10, 2), collector=lambda day: [])
    assert result['status'] == 'no_data'
    assert session.query(MarketPriceObservation).count() == 1


def test_repeat_execution_is_idempotent_and_records_runs(session):
    from app.market_data.cron import run_collection
    from app.models.market_price import MarketPriceObservation
    from app.models.collection_run import AgriCollectionRun
    collect = lambda day: [observation(day)]
    first = run_collection(session, 'mofcom', date(2026, 10, 2), collector=collect)
    second = run_collection(session, 'mofcom', date(2026, 10, 2), collector=collect)
    assert first['inserted'] == 3
    assert second['inserted'] == second['updated'] == 0
    assert session.query(MarketPriceObservation).count() == 3
    assert session.query(AgriCollectionRun).count() == 2


def test_failure_is_sanitized_and_partial_rows_survive(session):
    from app.market_data.cron import run_collection
    def collect(day):
        if day.day == 1:
            raise RuntimeError('postgres://user:supersecret@example.invalid')
        return [observation(day)]
    result = run_collection(session, 'mofcom', date(2026, 10, 2), collector=collect)
    assert result['status'] == 'partial'
    assert result['inserted'] == 2
    assert 'supersecret' not in str(result)
    assert result['errors'] == [{'date': '2026-10-01', 'error': 'RuntimeError'}]


def test_active_lease_blocks_overlapping_run(session):
    from app.market_data.cron import claim_run, run_collection
    row = claim_run(session, 'mofcom', date(2026, 10, 2))
    assert row
    result = run_collection(session, 'mofcom', date(2026, 10, 2), collector=lambda _: pytest.fail('must not fetch'))
    assert result['status'] == 'skipped_running'


def test_expired_lease_cannot_write_after_replacement(session):
    from app.market_data.cron import claim_run, finish_run
    from app.models.collection_run import AgriCollectionRun
    old = claim_run(session, 'mofcom', date(2026, 10, 2))
    session.execute(AgriCollectionRun.__table__.update().where(AgriCollectionRun.run_id == old.run_id)
                    .values(lease_until=datetime.now(timezone.utc) - timedelta(seconds=1)))
    session.commit()
    new = claim_run(session, 'mofcom', date(2026, 10, 2))
    assert new
    result = finish_run(session, old.run_id, [observation(date(2026, 10, 2))], [])
    assert result['status'] == 'lease_lost'


def test_duplicate_rows_in_one_batch_and_corrections(session):
    from app.market_data.persistence import upsert_observations
    day = date(2026, 10, 2)
    assert upsert_observations(session, [observation(day), observation(day)]) == (1, 0)
    assert upsert_observations(session, [observation(day, '4.3')]) == (0, 1)


def test_mofcom_ignoring_requested_date_is_not_new_data(monkeypatch):
    from app.market_data import fetch
    from types import SimpleNamespace
    body=b'<input name="searchDate" value="2026-09-30"><table id="goaler"><tr><td>A</td></tr></table>'
    monkeypatch.setattr(fetch.subprocess, 'run', lambda *a, **kw: SimpleNamespace(stdout=body))
    assert fetch.collect_mofcom(date(2026, 10, 1)) == []


def test_budget_expires_before_request(monkeypatch):
    from app.market_data import fetch
    with fetch.collection_budget(-1):
        with pytest.raises(TimeoutError):
            fetch._get('https://example.com')


def test_retry_transient_errors_but_not_access_denial(monkeypatch):
    from app.market_data import fetch
    import requests
    calls=[]
    def transient(*args, **kwargs):
        calls.append(1)
        raise requests.Timeout('private diagnostic')
    monkeypatch.setattr(fetch.SESSION, 'request', transient)
    with pytest.raises(requests.Timeout):
        fetch._get('https://example.com')
    assert len(calls)==2
    calls.clear()
    def denied(*args, **kwargs):
        calls.append(1)
        response=requests.Response()
        response.status_code=403
        raise requests.HTTPError(response=response)
    monkeypatch.setattr(fetch.SESSION, 'request', denied)
    with pytest.raises(requests.HTTPError):
        fetch._get('https://example.com')
    assert len(calls)==1
