"""Synchronous, bounded market collection with durable database leases."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from app.models.collection_run import AgriCollectionRun
from .fetch import COLLECTORS, collection_budget, collect_guangzhou, collect_moa_milk
from .persistence import upsert_observations


def beijing_today(now=None):
    return (now or datetime.now(timezone.utc)).astimezone(ZoneInfo('Asia/Shanghai')).date()


def _db_now(session):
    now = session.scalar(select(func.current_timestamp()))
    return now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now


def claim_run(session, source, day):
    now = _db_now(session)
    session.execute(update(AgriCollectionRun).where(
        AgriCollectionRun.source_id == source, AgriCollectionRun.status == 'running',
        AgriCollectionRun.lease_until <= now).values(
            status='failed', finished_at=now, errors=[{'error': 'lease_expired'}]))
    run = AgriCollectionRun(run_id=str(uuid4()), source_id=source, target_date=day,
                            status='running', started_at=now, lease_until=now + timedelta(minutes=6))
    session.add(run)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        return None
    return run


def finish_run(session, run_id, rows, errors):
    # The lock and observation writes stay in ONE transaction. A worker whose
    # lease was replaced can never commit over its replacement's result.
    run = session.scalar(select(AgriCollectionRun).where(
        AgriCollectionRun.run_id == run_id).with_for_update().execution_options(populate_existing=True))
    now = _db_now(session)
    lease = run.lease_until.replace(tzinfo=timezone.utc) if run and run.lease_until.tzinfo is None else (run.lease_until if run else None)
    if run is None or run.status != 'running' or lease <= now:
        session.rollback()
        return {'run_id': run_id, 'status': 'lease_lost'}
    inserted, updated = upsert_observations(session, rows, commit=False)
    status = ('partial' if rows else 'failed') if errors else ('completed' if rows else 'no_data')
    run.status, run.finished_at = status, now
    run.inserted, run.updated, run.observed, run.errors = inserted, updated, len(rows), errors
    result = {'run_id': run_id, 'source': run.source_id, 'status': status,
              'inserted': inserted, 'updated': updated, 'observed': len(rows), 'errors': errors}
    session.commit()
    return result


def run_collection(session, source, day, *, collector=None):
    run = claim_run(session, source, day)
    if run is None:
        return {'source': source, 'status': 'skipped_running'}
    run_id = run.run_id
    # Release the pooled connection during all upstream requests.
    session.rollback()
    rows, errors = [], []
    selected = collector or COLLECTORS[source]
    weekly = collector is None and source in {'guangzhou', 'moa_milk'}
    days = [day] if weekly else [day - timedelta(days=offset) for offset in range(3)]
    with collection_budget(200):
        for target in days:
            try:
                if weekly:
                    selected = collect_guangzhou if source == 'guangzhou' else collect_moa_milk
                    batch = selected(target, latest=True)
                else:
                    batch = selected(target)
                if any(row.observed_date > day or not row.commodity for row in batch):
                    raise ValueError('Invalid observation date or commodity')
                rows.extend(batch)
            except Exception as exc:
                # Messages may contain connection strings. Store only class.
                errors.append({'date': target.isoformat(), 'error': type(exc).__name__})
                if isinstance(exc, TimeoutError):
                    break
    try:
        return finish_run(session, run_id, rows, errors)
    except Exception as exc:
        session.rollback()
        return finish_run(session, run_id, [], [{'error': type(exc).__name__}])
