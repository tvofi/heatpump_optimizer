#!/usr/bin/env python3
"""R10-LIVE-BUNDLE-READS (#3120): the D15 reads a live bundle answers, as numbers.

Reads one diagnostics download (HA's ``data`` and ``debug`` wrappers are
unwrapped; a bare bundle works) and prints derived numbers and reason words
only: no entity id, text or value of the bundle is ever printed. A bundle is a
user's private data and is never committed.

Arms (each prints RESULT lines):

  health   D15 lead L9. Per weekly learner snapshot in the ``snapshots`` store:
           ``healthy``, and whether the snapshot carries ``unhealthy_input``
           (written since #2261; an older snapshot carries no key and is
           unattributable, not healthy). A name is printed only when it is a
           reason word the tree emits (``external_heat_source``, ``defrosting``,
           ``ventilation``, ``boost``, or ``<problem>:<configuration key>``).
           Controls, driven through ``SnapshotRing``: every heartbeat
           reporting names none; one input silent names that input.
  age      D15 lead L6. The freshness rule for a quiet power meter, driven
           through ``inputs.age_limit_for`` and ``inputs.state_age`` on stand-in
           states, each 240 min since the last write: a meter reporting on
           change, a polling meter re-reporting an unchanged value, a polling
           meter that went silent. ``--mutant last_changed`` makes the stamp
           chain read ``last_changed`` first.
  samples  L-a and L-b. Rows against the accuracy tracker's samples: distinct
           sample stamps, the longest run of rows repeating one sample, the
           longest gap between distinct samples, how far a row's stamp stands
           past its own sample's (a stalled tracker), and the rows lacking the
           action keys. ``--plant-stall`` repeats the middle row's sample to
           the end, the tracker stopping while cycle rows continue.

Metric (one line): the arm's RESULT lines for the bundle given.
Command (repository root):
    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/d15_bundle_reads.py --bundle B [--mutant last_changed] [--plant-stall]
Expected (the arms that need no bundle, ``--bundle`` omitted):
    EXPECTED RESULT control_all_reporting_unhealthy_input=None
    EXPECTED RESULT control_one_silent_unhealthy_input=stale:outdoor_temp_entity
    EXPECTED RESULT age_on_change_flagged=False
    EXPECTED RESULT age_polling_reporting_flagged=False
    EXPECTED RESULT age_polling_silent_flagged=True
Baseline SHA: c3a279e32. Machine: macOS arm64, CI venv 3.14; no solve.
Perturbation: --mutant last_changed -- age_polling_reporting_flagged turns True;
    --plant-stall -- samples_max_row_lag_h and samples_longest_repeat_rows rise.
Null control: the unplanted run; the all-reporting week names none.
Instrumented symbols: snapshots:SnapshotRing, inputs:age_limit_for,
    inputs:state_age, inputs:state_stamp.
"""
import argparse
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "custom_components")

from heatpump_optimizer import boost, inputs  # noqa: E402
from heatpump_optimizer.const import CONF_HOUSE_POWER_ENTITY  # noqa: E402
from heatpump_optimizer.snapshots import SnapshotRing  # noqa: E402

NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
SILENT = "stale:outdoor_temp_entity"
WORDS = {"external_heat_source", "defrosting", "ventilation", boost.FREEZE_REASON}


def load(path):
    doc = json.load(open(path))
    doc = doc.get("data", doc) if isinstance(doc.get("data"), dict) else doc
    return doc["debug"] if isinstance(doc.get("debug"), dict) else doc


def reason_word(reason):
    """The reason when the tree emits it, else a class name; never a bundle string."""
    if reason is None:
        return "None"
    if reason in WORDS:
        return reason
    problem, _, key = str(reason).partition(":")
    from heatpump_optimizer import const
    keys = {v for k, v in vars(const).items() if k.startswith("CONF_") and isinstance(v, str)}
    return f"{problem}:{key}" if problem.isidentifier() and key in keys else "unlisted"


def arm_health(bundle):
    ring = SnapshotRing()
    ring.observe_health(None)
    ring.take(NOW, {}, {}, ring.day_unhealthy is None)
    print(f"RESULT control_all_reporting_unhealthy_input={ring.snapshots[-1]['unhealthy_input']}")
    ring = SnapshotRing()
    for reason in (None, SILENT, None):
        ring.observe_health(reason)
    ring.take(NOW, {}, {}, ring.day_unhealthy is None)
    print(f"RESULT control_one_silent_unhealthy_input={ring.snapshots[-1]['unhealthy_input']}")
    if bundle is None:
        return
    store = next(v for k, v in bundle["stores"].items() if k.endswith("_snapshots"))
    ring_rows = store["snapshots"]
    print(f"RESULT ring_snapshots={len(ring_rows)}")
    print(f"RESULT ring_unhealthy={sum(1 for s in ring_rows if not s.get('healthy'))}")
    print(f"RESULT ring_with_field={sum(1 for s in ring_rows if 'unhealthy_input' in s)}")
    for i, snap in enumerate(ring_rows):
        word = reason_word(snap["unhealthy_input"]) if "unhealthy_input" in snap else "no-field"
        print(f"RESULT snapshot_{i}_healthy={snap.get('healthy')} reason={word}")
    print(f"RESULT ring_naming_outdoor="
          f"{sum(1 for s in ring_rows if 'outdoor' in str(s.get('unhealthy_input')))}")


class _State:
    def __init__(self, updated, reported=None):
        self.last_updated = updated
        self.last_changed = updated
        self.last_reported = reported if reported is not None else updated


class _Hass:
    """A weakref-able owner for the polling-source side table."""


def arm_age(mutant):
    if mutant == "last_changed":
        inputs.state_stamp = lambda s: getattr(s, "last_changed", None)
    hass = _Hass()
    quiet = NOW - timedelta(minutes=240)

    def flagged(entity, state):
        limit = inputs.age_limit_for(hass, CONF_HOUSE_POWER_ENTITY, entity, state)
        age = inputs.state_age(state, NOW)
        minutes = None if age is None else age.total_seconds() / 60.0
        return limit is not None and minutes is not None and minutes > limit
    print(f"RESULT age_on_change_flagged={flagged('sensor.a', _State(quiet))}")
    polled = _State(quiet, reported=NOW - timedelta(minutes=1))
    print(f"RESULT age_polling_reporting_flagged={flagged('sensor.b', polled)}")
    inputs.age_limit_for(hass, CONF_HOUSE_POWER_ENTITY, "sensor.c", _State(
        quiet - timedelta(minutes=1), reported=quiet))
    silent = _State(quiet - timedelta(minutes=1), reported=quiet)
    print(f"RESULT age_polling_silent_flagged={flagged('sensor.c', silent)}")


def arm_samples(bundle, plant):
    rows = [dict(r) for r in bundle["cycle_rows"]]
    if plant:
        mid = len(rows) // 2
        for r in rows[mid:]:
            r["accuracy_sample"] = rows[mid]["accuracy_sample"]
    stamps = [r["accuracy_sample"]["t"] for r in rows if r.get("accuracy_sample")]
    run = best = 1
    for a, b in zip(stamps, stamps[1:]):
        run = run + 1 if a == b else 1
        best = max(best, run)
    distinct = sorted(datetime.fromisoformat(t) for t in set(stamps))
    gaps = [(b - a).total_seconds() / 3600.0 for a, b in zip(distinct, distinct[1:])]
    print(f"RESULT samples_rows={len(rows)}")
    print(f"RESULT samples_distinct={len(distinct)}")
    print(f"RESULT samples_longest_repeat_rows={best}")
    print(f"RESULT samples_max_gap_h={max(gaps):.2f}")
    print(f"RESULT samples_median_gap_h={statistics.median(gaps):.3f}")
    lag = [(datetime.fromisoformat(r["t"]) - datetime.fromisoformat(r["accuracy_sample"]["t"]))
           .total_seconds() / 3600.0 for r in rows if r.get("accuracy_sample")]
    print(f"RESULT samples_max_row_lag_h={max(lag):.2f}")
    keys = ("action_mode", "action_kw", "heat_pump_on")
    lacking = [i for i, r in enumerate(rows) if not all(k in r for k in keys)]
    print(f"RESULT rows_lacking_action_keys={len(lacking)}")
    stamps_t = [datetime.fromisoformat(r["t"]) for r in rows]
    for i in lacking:
        before = (stamps_t[i] - stamps_t[i - 1]).total_seconds() / 60.0 if i else 0.0
        after = (stamps_t[i + 1] - stamps_t[i]).total_seconds() / 60.0 if i + 1 < len(rows) else 0.0
        print(f"RESULT lacking_row={i} gap_before_min={before:.1f} gap_after_min={after:.1f} "
              f"version_changed={i > 0 and rows[i].get('version') != rows[i - 1].get('version')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=None)
    ap.add_argument("--mutant", choices=["", "last_changed"], default="")
    ap.add_argument("--plant-stall", action="store_true")
    a = ap.parse_args()
    bundle = load(a.bundle) if a.bundle else None
    arm_health(bundle)
    arm_age(a.mutant)
    if bundle is not None:
        arm_samples(bundle, a.plant_stall)


if __name__ == "__main__":
    main()
