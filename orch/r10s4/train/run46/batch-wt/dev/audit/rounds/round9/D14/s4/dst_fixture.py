"""Shift the committed replay day onto a DST transition day (P7 detector input).

Metric: none -- a fixture builder imported by p7_dst_seams.py. Every ISO
timestamp in tests/replay/synthetic-dhw-only.json is moved by one ABSOLUTE
delta (UTC), then re-emitted in its original style: a "+00:00" stamp stays
UTC, any other offset is re-rendered in Europe/Stockholm local time, so a
post-transition hour carries +02:00 (spring) / +01:00 (autumn) as a real
recorder export would. The day keeps 24 true hours of rows (a DST local day
has 23 or 25), which is recorded, not hidden.
Command: imported only; `build(day)` returns the fixture dict.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, Linux container (B9).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Stockholm")
SRC_START = datetime(2026, 1, 15, tzinfo=TZ)  # the committed day's local midnight
DAYS = {
    # local midnight of the transition day; spring 02:00 -> 03:00, autumn 03:00 -> 02:00
    "spring": datetime(2026, 3, 29, tzinfo=TZ),
    "autumn": datetime(2026, 10, 25, tzinfo=TZ),
    # null control: an ordinary day in the same season band, no transition
    "plain": datetime(2026, 3, 22, tzinfo=TZ),
    # leave-one-out cells: the neighbouring years' transitions
    "spring2025": datetime(2025, 3, 30, tzinfo=TZ),
    "autumn2025": datetime(2025, 10, 26, tzinfo=TZ),
    "spring2027": datetime(2027, 3, 28, tzinfo=TZ),
    "autumn2027": datetime(2027, 10, 31, tzinfo=TZ),
    "plain_autumn": datetime(2026, 10, 18, tzinfo=TZ),
}
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}$")


def _shift(s: str, delta: timedelta) -> str:
    t = datetime.fromisoformat(s)
    moved = t + delta  # fixed-offset tz: absolute arithmetic
    if t.utcoffset() == timedelta(0):
        return moved.astimezone(timezone.utc).isoformat()
    return moved.astimezone(TZ).isoformat()


def _walk(node, delta):
    if isinstance(node, str) and ISO.match(node):
        return _shift(node, delta)
    if isinstance(node, list):
        return [_walk(x, delta) for x in node]
    if isinstance(node, dict):
        return {k: _walk(v, delta) for k, v in node.items()}
    return node


def build(day: str, root: Path | None = None) -> dict:
    root = root or Path(".")
    src = json.loads((root / "tests/replay/synthetic-dhw-only.json").read_text())
    delta = DAYS[day].astimezone(timezone.utc) - SRC_START.astimezone(timezone.utc)
    out = _walk(src, delta)
    out["time_zone"] = "Europe/Stockholm"
    return out
