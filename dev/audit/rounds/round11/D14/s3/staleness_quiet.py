#!/usr/bin/env python3
"""D14-s3 (round 11, nightly-replay axis): N-staleness on a QUIET NIGHT, replayed.

The synthetic fixture's room and tank probes re-report every 5-10 min, so it
never holds a quiet gap (round 10's C5). This harness builds the quiet night
from it in memory: the report-on-change sources -- the room probe
(``sensor.indoor_temp``) and the tank probe (``sensor.dhw_temp``) -- send no
row from 00:00 to 00:00+GAP local and never re-report an unchanged value
(``last_reported`` absent), which is what a Zigbee/1-wire probe with a
reporting threshold does in a calm room.

Metric (count key: the production entity's ``available`` as
``tests/replay.py:sweep`` reads it): (cycle, entity) pairs published
UNAVAILABLE in the quiet arm that the polling control arm (the same values,
re-reported every 10 min) publishes available, over the replayed window.

Arms: quiet5  -- a 5 h gap, inside the R9 field gap (4 h 15) plus margin;
      poll5   -- null control: the same 5 h, the probes re-report -> 0;
      quiet7  -- a 7 h gap, past QUIET_STORE_MAX_AGE_MINUTES (360): the bound
                 working as designed (a dead probe stops in 6 h);
      mode5   -- the mode select goes ``unavailable`` for 5 h (C5's second
                 half): cycles whose source is past MODE_LAST_GOOD (180 min)
                 and whose plan buys space heat the hot-water-only pump
                 cannot serve.
Perturbation (``--perturb``): ``const.INPUT_ON_CHANGE_MAX_AGE_MINUTES`` and
``INPUT_MAX_AGE_MINUTES`` for the room and tank keys set to 60 (the pre-R9
limit) -> quiet5's count goes up.
Pre-fix re-find (``--tree`` an export of 3e9f1878bd^, before R9 F4.1): quiet5 > 0.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s3/staleness_quiet.py
Expected at 92d38ecb6: quiet5 0, poll5 0, quiet7 > 0 (designed); exact counts.
Machine: box B7, 4 vCPU.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replaykit  # noqa: E402  (pins BLAS threads first)

import argparse  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

QUIET = ("sensor.indoor_temp", "sensor.dhw_temp")
ARMS = {"quiet5": ("quiet", 5), "poll5": ("poll", 5), "quiet7": ("quiet", 7), "mode5": ("mode", 5)}
HOURS = 9.0  # 00:00 .. 09:00 local, 30-min cycles


def _iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat()


def doc_for(tree: Path, kind: str, gap_h: float) -> dict:
    doc = json.loads((tree / "tests" / "replay" / "synthetic-dhw-only.json").read_text())
    start = datetime.fromisoformat(doc["window"]["start"])
    doc["window"]["end"] = (start + timedelta(hours=HOURS)).isoformat()
    q0, q1 = start, start + timedelta(hours=gap_h)
    if kind == "mode":
        mode_id = next(e for e in doc["states"] if e.startswith("select."))
        rows = doc["states"][mode_id]
        attrs = rows[0][2]
        rows.append([_iso(q0 + timedelta(minutes=1)), "unavailable", attrs, None])
        rows.append([_iso(q1), rows[0][1], attrs, None])
        rows.sort(key=lambda r: r[0])
        return doc
    cfg = {**doc["entry"]["data"], **doc["entry"]["options"]}
    quiet = [cfg.get(k) for k in ("indoor_temp_entity", "dhw_temp_entity")] if cfg.get(
        "indoor_temp_entity") else list(QUIET)
    for eid in quiet:
        rows = doc["states"][eid]
        before = [r for r in rows if datetime.fromisoformat(r[0]) < q0]
        inside = [r for r in rows if q0 <= datetime.fromisoformat(r[0]) < q1]
        after = [r for r in rows if datetime.fromisoformat(r[0]) >= q1]
        held = before[-1]
        if kind == "quiet":
            # On change only: no re-report anywhere, and no row in the gap.
            new = [[r[0], r[1], r[2], None] for r in before + after]
        else:
            # Polling: the held value re-reported through the gap. Recording.at
            # caps ``last_reported`` at each cycle's instant, so one row whose
            # re-report stamp is the gap's end reads as re-reported "now".
            new = before[:-1] + [[held[0], held[1], held[2], _iso(q1)]] + after
        doc["states"][eid] = sorted(new, key=lambda r: r[0])
    return doc


def child(tree: Path, arm: str, perturb: bool) -> dict:
    kind, gap = ARMS[arm]

    def setup(ctx):
        if perturb:
            from heatpump_optimizer import const
            for table in ("INPUT_MAX_AGE_MINUTES", "INPUT_ON_CHANGE_MAX_AGE_MINUTES"):
                tab = getattr(const, table, None)
                if tab is not None:
                    tab[const.CONF_INDOOR_TEMP_ENTITY] = 60.0
                    tab[const.CONF_DHW_TEMP_ENTITY] = 60.0
    out = replaykit.run(tree, doc_for(tree, kind, gap), 30, setup)
    unavailable = {}
    for recs in out["records"]:
        for r in recs:
            if not r["available"]:
                unavailable.setdefault(r["entity_id"], []).append(r["t"][11:16])
    away = out["run"].get("away") or []
    space = [(o["t"][11:16], o["space_kwh"]) for o in away]
    return {"arm": arm, "cycles": out["run"]["cycles"], "unavailable": unavailable,
            "space": space, "cycle_offenders": (out["run"]["counts"] or {}).get("cycle")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, default=replaykit.ROOT)
    ap.add_argument("--arm", choices=tuple(ARMS))
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--child", action="store_true")
    a = ap.parse_args()
    tree = a.tree.resolve()
    if a.child:
        replaykit.emit(child(tree, a.arm, a.perturb))
        return 0
    t0 = time.monotonic()
    import concurrent.futures as cf
    arms = [a.arm] if a.arm else list(ARMS)
    extra = ["--perturb"] if a.perturb else []
    with cf.ThreadPoolExecutor(len(arms)) as ex:
        res = dict(zip(arms, ex.map(lambda arm: replaykit.child(
            Path(__file__).resolve(), tree, ["--arm", arm, *extra]), arms)))
    base = res.get("poll5")
    base_unav = {(e, t) for e, ts in (base or {}).get("unavailable", {}).items() for t in ts}
    for arm, d in res.items():
        if d is None:
            print(f"RESULT {arm}_ran=0 count")
            continue
        pairs = {(e, t) for e, ts in d["unavailable"].items() for t in ts}
        extra_pairs = pairs - base_unav if arm != "poll5" else pairs
        print(f"arm {arm}: cycles={d['cycles']} cycle_offenders={d['cycle_offenders']}")
        for e, ts in sorted(d["unavailable"].items()):
            print(f"  unavailable {e}: {len(ts)} cycle(s) {ts[:4]}..{ts[-2:]}")
        if arm == "mode5":
            print(f"  space kWh per cycle: {d['space']}")
            print(f"RESULT mode5_space_cycles={sum(1 for _, k in d['space'] if k and k > 0)} count")
        print(f"RESULT {arm}_unavailable_pairs={len(extra_pairs)} count")
    print(f"RESULT wall_s={time.monotonic() - t0:.1f} s (provisional)")
    replaykit.tail_results()
    return 0


if __name__ == "__main__":
    sys.exit(main())
