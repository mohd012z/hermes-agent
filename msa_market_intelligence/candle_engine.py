"""Deterministic closed-candle aggregation; no gap filling or signal generation."""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable

@dataclass(frozen=True)
class Candle:
    symbol: str
    seconds: int
    start: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    complete: bool = True

    def __post_init__(self):
        if self.start.tzinfo is None or self.start.utcoffset() != timezone.utc.utcoffset(self.start):
            raise ValueError("start must be UTC aware")
        if self.seconds <= 0 or int(self.start.timestamp()) % self.seconds:
            raise ValueError("invalid timeframe or unaligned candle")
        if not self.symbol or not all(x.is_finite() and x > 0 for x in (self.open, self.high, self.low, self.close)):
            raise ValueError("invalid symbol or prices")
        if self.high < max(self.open, self.close, self.low) or self.low > min(self.open, self.close, self.high):
            raise ValueError("inconsistent OHLC")

def aggregate(candles: Iterable[Candle], target_seconds: int) -> list[Candle]:
    """Emit only fully contiguous, completed UTC-aligned source groups."""
    rows = list(candles)
    if not rows:
        return []
    base = rows[0].seconds
    if target_seconds < base or target_seconds % base:
        raise ValueError("target must be an integer multiple of source timeframe")
    if any(x.seconds != base or x.symbol != rows[0].symbol or not x.complete for x in rows):
        raise ValueError("mixed symbol/timeframe or incomplete source candle")
    if any(a.start >= b.start for a, b in zip(rows, rows[1:])):
        raise ValueError("unordered or duplicate candles")
    groups: dict[int, list[Candle]] = {}
    for c in rows:
        bucket = int(c.start.timestamp()) // target_seconds * target_seconds
        groups.setdefault(bucket, []).append(c)
    result = []
    for bucket, group in sorted(groups.items()):
        if len(group) != target_seconds // base or any(int(c.start.timestamp()) != bucket + i * base for i, c in enumerate(group)):
            continue
        result.append(Candle(group[0].symbol, target_seconds, datetime.fromtimestamp(bucket, timezone.utc),
                             group[0].open, max(c.high for c in group), min(c.low for c in group), group[-1].close))
    return result
