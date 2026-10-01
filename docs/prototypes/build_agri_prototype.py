"""Build the self-contained prototype from its reviewed local snapshot."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
snapshot = json.loads((ROOT / 'agri-market-dashboard.snapshot.json').read_text())
template = (ROOT / 'agri-market-dashboard.template.html').read_text()
values = {'__MAP_PATHS__': snapshot['map_paths'],
          '__ROWS__': json.dumps(snapshot['rows'], ensure_ascii=False, separators=(',', ':')),
          '__HISTORY__': json.dumps(snapshot['history'], ensure_ascii=False, separators=(',', ':')),
          '__CENTERS__': json.dumps(snapshot['centers'], ensure_ascii=False)}
for key, value in values.items():
    template = template.replace(key, value)
(ROOT / 'agri-market-dashboard.html').write_text(template)
print(f"Built {len(snapshot['rows'])} snapshot rows and {len(snapshot['history'])} trend points")
