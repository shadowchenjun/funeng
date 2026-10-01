"""Build the reviewed industry snapshot without contacting production services."""
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build():
    industry = json.loads((ROOT / 'agri-industry-dashboard.snapshot.json').read_text())
    market = json.loads((ROOT / 'agri-market-dashboard.snapshot.json').read_text())
    rows = industry['observations']
    assert not industry['errors'], 'Resolve source failures before building'
    assert len({r['external_key'] for r in rows}) == len(rows)
    for row in rows + industry['manual_observations']:
        assert Decimal(row['value']).is_finite() and Decimal(row['value']) >= 0
        assert row['qualifier'] in ('exact', 'gt', 'ge', 'approx')
    grain = [r for r in rows if r['metric'] == 'grain_production']
    assert len(grain) == 32 and len({r['region'] for r in grain}) == 32
    assert any(r['metric'] == 'agri_insurance_premium' and r['qualifier'] == 'gt' for r in rows)
    assert len(market['rows']) == 1095, 'Review updated price snapshot before release'
    industry['build_status'] = 'reviewed_local_prototype'
    industry['market_record_count'] = len(market['rows'])
    def js(value):
        return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')
    html = (ROOT / 'agri-industry-dashboard.template.html').read_text()
    html = html.replace('__SNAPSHOT__', js(industry)).replace('__MAP_PATHS__', market['map_paths'])
    assert '__SNAPSHOT__' not in html and '__MAP_PATHS__' not in html
    (ROOT / 'agri-industry-dashboard.html').write_text(html)
    print(f'Built six pages: {len(rows)} collected + {len(industry["manual_observations"])} reviewed observations; {len(industry["cold_nodes"])} cold nodes')


if __name__ == '__main__':
    build()
