"""Exact observations and provenance for annual and quarterly industry statistics."""
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from hashlib import sha256


@dataclass(frozen=True)
class IndustryObservation:
    """One published measurement; overlapping metrics must never be summed."""

    source_id: str
    source_url: str
    metric: str
    metric_name: str
    region: str
    category: str
    period_start: date
    period_end: date
    frequency: str
    value: Decimal
    unit: str
    measure_type: str
    evidence: str
    qualifier: str = "exact"
    yoy_percent: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.value.is_finite() or self.value < 0:
            raise ValueError("Industry measurement must be finite and non-negative")
        if self.period_end < self.period_start:
            raise ValueError("Invalid observation period")
        if self.qualifier not in {"exact", "gt", "ge", "approx"}:
            raise ValueError("Invalid measurement qualifier")

    @property
    def external_key(self) -> str:
        """Stable identity excluding values, allowing source revisions."""
        identity = (self.source_id, self.metric, self.region, self.category,
                    str(self.period_start), str(self.period_end), self.unit)
        return sha256("|".join(identity).encode()).hexdigest()

    def to_dict(self) -> dict:
        result = asdict(self)
        for key in ("period_start", "period_end"):
            result[key] = result[key].isoformat()
        for key in ("value", "yoy_percent"):
            result[key] = str(result[key]) if result[key] is not None else None
        result["external_key"] = self.external_key
        return result
