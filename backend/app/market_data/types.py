"""Typed, source-preserving market observations."""
from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json


def decimal_or_none(value):
    if value is None or str(value).strip() in {"", "-", "--", "—"}:
        return None
    try:
        number = Decimal(str(value).replace(",", "").strip())
        return number if number >= 0 and number.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def normalize_price(value: Decimal | None, unit: str):
    if value is None:
        return None
    unit = unit.strip().replace(" ", "")
    if unit in {"元/公斤", "元/千克", "元/kg", "公斤", "千克", "kg"}:
        return value
    if unit in {"元/市斤", "元/斤", "市斤", "斤"}:
        return value * 2
    return None


@dataclass
class MarketObservation:
    source_id: str
    source_url: str
    market_name: str
    category: str
    commodity: str
    observed_date: date
    quote_type: str
    source_unit: str
    province: str = ""
    specification: str = ""
    origin: str = ""
    period_start: date | None = None
    period_end: date | None = None
    price_min: Decimal | None = None
    price_avg: Decimal | None = None
    price_max: Decimal | None = None
    quality_flag: str = "ok"
    source_row_key: str = ""
    external_key: str = field(init=False)

    def __post_init__(self):
        identity = [self.source_id, self.market_name, self.category, self.commodity,
                    self.observed_date.isoformat(), self.quote_type, self.specification,
                    self.origin, self.source_row_key]
        self.external_key = sha256(json.dumps(identity, ensure_ascii=False).encode()).hexdigest()
        if not self.source_unit or all(normalize_price(v, self.source_unit) is None
                                       for v in (self.price_min, self.price_avg, self.price_max)):
            self.quality_flag = "missing_unit" if not self.source_unit else "unknown_unit"

    @property
    def price_min_yuan_per_kg(self):
        return normalize_price(self.price_min, self.source_unit)

    @property
    def price_avg_yuan_per_kg(self):
        return normalize_price(self.price_avg, self.source_unit)

    @property
    def price_max_yuan_per_kg(self):
        return normalize_price(self.price_max, self.source_unit)

    def to_dict(self):
        result = asdict(self)
        for name in ("price_min_yuan_per_kg", "price_avg_yuan_per_kg", "price_max_yuan_per_kg"):
            result[name] = getattr(self, name)
        return {key: str(value) if isinstance(value, Decimal) else value.isoformat()
                if isinstance(value, date) else value for key, value in result.items()}
