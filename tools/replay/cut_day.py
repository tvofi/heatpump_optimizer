#!/usr/bin/env python3
"""Cut one replay fixture out of a sealed multi-day ``hpo-replay/1`` export.

The export (``export.py --days 7``) is the owner's recorded week, and at over
10 MB it is never committed. The replay lane reads a fixture in only three
ways (``tests/replay.py:run_fixture``): each mapped input's state in force at
a cycle instant, the weather entity's rows from that instant on (its
forecast) and the price series' state in force at each quarter. All three
instants lie on the quarter-hour grid that starts at the window's local
midnight, so this keeps, of every input, only the rows in force at a grid
instant -- what the lane reads, unchanged -- and drops the rest (a
thermometer reporting every 30 s keeps 96 rows a day, not 3000). The price
series and the weather, read ahead of the cycle, keep their grid rows to the
export's end. ``--span`` cuts part of a day: the lane's cost scales with its
cycles.

The entities the integration publishes are left out, because the lane never
reads them and they are what the build that recorded the day did -- often
the defect itself. The one exception is the away override the owner set from
the integration's own away switch and return-time entity: the user's
command, not the integration's output. ``controls.away`` carries it as
events ``[time, active, return_time]``; the lane replays each through
``coordinator.async_set_away``, the call the switch and the datetime entity
make. Both entities are masked to hashes, so they are found by what they
did: the one published ``datetime`` entity is the return time, and the away
switch is the one published switch that turned on within a few seconds of
that return time being set. Anything else is refused.

    python3 tools/replay/cut_day.py EXPORT.json --day 2026-10-30 --out tests/replay/F.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import export  # noqa: E402

GRID = timedelta(minutes=15)
#: How close the away switch's turn-on and the return time's setting are.
PAIRED = timedelta(seconds=10)


def _ts(text: str) -> datetime:
    return datetime.fromisoformat(text)


def grid(start: datetime, end: datetime) -> list[datetime]:
    """The quarter-hour instants of ``[start, end)``, stepped in UTC."""
    out, t = [], start.astimezone(ZoneInfo("UTC"))
    while t < end:
        out.append(t)
        t += GRID
    return out


def thinned(rows: list[list], instants: list[datetime]) -> list[list]:
    """The rows in force at some instant of ``instants``, each carrying its full
    attributes, then compacted as ``replay_doc.state_rows`` writes them."""
    full, attrs = [], None
    for updated, state, maybe, reported in rows:
        attrs = maybe if maybe is not None else attrs
        full.append((updated, state, attrs, reported))
    keep, i = [], -1
    for t in instants:
        while i + 1 < len(full) and _ts(full[i + 1][0]) <= t:
            i += 1
        if i >= 0 and (not keep or keep[-1] is not full[i]):
            keep.append(full[i])
    return export._doc.state_rows(keep)


def _changes(series: list[tuple[datetime, object]]) -> list[tuple[datetime, object]]:
    """The points where a value changes, a restart's ``unavailable`` skipped: a
    restart writes every entity again, which is no command."""
    out, last = [], object()
    for t, v in series:
        if v != "unavailable" and v != last:
            out.append((t, v))
            last = v
    return out


def away_events(doc: dict, start: datetime, end: datetime) -> list[list]:
    """The owner's away commands in ``[start, end)``, and the one in force at
    ``start``, from the published away switch and return-time entity."""
    states, published = doc["states"], doc["published"]
    dates = [e for e in published if e.startswith("datetime.")]
    if len(dates) != 1:
        raise SystemExit(f"{len(dates)} published datetime entities; the away return "
                         "time is the only one this integration publishes")
    returns = [(_ts(r[0]), r[1]) for r in states.get(dates[0], [])]
    set_at = [t for t, v in _changes(returns) if v not in ("unknown", None)]
    switches = [e for e in published if e.startswith("switch.") and any(
        v == "on" and any(abs(t - s) <= PAIRED for s in set_at)
        for t, v in _changes([(_ts(r[0]), r[1]) for r in states.get(e, [])]))]
    if len(switches) > 1 or (set_at and not switches):
        raise SystemExit(f"{len(switches)} published switches turned on as the away "
                         "return time was set; expected exactly one")
    if not switches:
        return []
    events, last = [], None
    for updated, state, _attrs, _rep in states[switches[0]]:
        if state not in ("on", "off"):
            continue  # a restart's ``unavailable``, not a command
        t = _ts(updated)
        ret = next((v for when, v in reversed(returns) if when <= t + PAIRED
                    and v not in ("unknown", "unavailable")), None)
        event = [t.isoformat(), state == "on", ret if state == "on" else None]
        if event[1:] == (last or [None, None, None])[1:]:
            continue
        if t < start:
            events = [[start.isoformat(), *event[1:]]] if event[1] else []
        elif t < end:
            events.append(event)
        last = event
    return events


def _read_ahead(doc: dict, entity_id: str) -> bool:
    return entity_id == doc.get("price_series_entity") or entity_id.startswith("weather.")


def cut(doc: dict, day: str, warmup_days: int = 0,
        span: tuple[time, time] | None = None) -> dict:
    """``day``, local midnight to midnight -- or the local ``span`` of it --
    after ``warmup_days`` whole days before it that the lane replays too."""
    tz = ZoneInfo(doc["time_zone"])
    first = datetime.fromisoformat(day).date()
    begin, until = span or (time(0), None)
    start = datetime.combine(first - timedelta(days=warmup_days), begin, tz)
    end = (datetime.combine(first, until, tz) if until
           else datetime.combine(first + timedelta(days=1), time(0), tz))
    if not _ts(doc["window"]["start"]) <= start < end <= _ts(doc["window"]["end"]):
        raise SystemExit(f"{day} is not inside the export's window {doc['window']}")
    instants = grid(start, end)
    # The price series and the weather are read ahead -- the day's quarters and
    # the forecast's hours -- so they keep their rows to the export's end.
    ahead = grid(start, _ts(doc["window"]["end"]))
    out = {k: v for k, v in doc.items() if k not in ("states", "published")}
    out["window"] = {"start": start.isoformat(), "end": end.isoformat()}
    out["published"] = []
    out["states"] = {eid: thinned(rows, ahead if _read_ahead(doc, eid) else instants)
                     for eid, rows in doc["states"].items() if eid in doc["inputs"]}
    out["controls"] = {"away": away_events(doc, start, end)}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("export", type=Path)
    ap.add_argument("--day", required=True, help="the local date to cut, YYYY-MM-DD")
    ap.add_argument("--warmup-days", type=int, default=0,
                    help="whole days before --day the fixture starts at")
    ap.add_argument("--span", help="local HH:MM-HH:MM of --day only, not the whole day")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    found = export.check_file(args.export)
    if found:
        raise SystemExit(f"{args.export} fails the export's check: " + "; ".join(found[:3]))
    span = tuple(time.fromisoformat(x) for x in args.span.split("-")) if args.span else None
    fixture = cut(json.loads(args.export.read_text()), args.day, args.warmup_days, span)
    args.out.write_text(json.dumps(fixture, sort_keys=True, indent=1) + "\n")
    found = export.check_file(args.out)
    if found:
        args.out.unlink()
        raise SystemExit("the cut fails the export's check: " + "; ".join(found[:3]))
    rows = sum(len(v) for v in fixture["states"].values())
    print(f"wrote {args.out}: {len(fixture['states'])} inputs, {rows} rows, "
          f"{len(fixture['controls']['away'])} away event(s), {args.out.stat().st_size} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
