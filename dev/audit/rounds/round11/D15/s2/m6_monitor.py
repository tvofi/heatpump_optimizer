#!/usr/bin/env python3
"""D15-s2 harness, D15.M6 (monitor re-run) over a "Download diagnostics" file.

Metrics (one line each):
  anchor_<k>_count_delta: |reconstructed live-deque length - the length the
      install recorded| at an anchor (a snapshot's ``accuracy.samples`` taken
      inside the rows' span, and the self-test's ``live.samples``).
  anchor_<k>_bias_delta / _mae_delta: |AccuracyTracker.temperature_bias (or
      temperature_mae) over the reconstructed deque - the recorded value|, degC.
  window_<day>_n/_bias/_mae: per local calendar day (the replay half's
      time_zone, the day ``SnapshotRing.observe_bias`` counts), the day's own
      samples through AccuracyTracker.
  window_<day>_live_bias: the counting tick's (the day's first cycle row) bias
      over the reconstructed live deque, ``partial=1`` while the deque still
      holds samples from before the collection whose values are unknown.
  latch_match: 1 when ``SnapshotRing.observe_bias`` folded over every fully
      re-derivable counting tick ends in the stored ring's (alarmed,
      bias_days, last_day), else 0.
  restart_flip_days: fully known counting ticks whose in/out-of-band verdict
      differs between the restart-truncated deque (production) and the same
      samples with no restart (deque only capped at HISTORY_LENGTH).
Count key: every number is keyed on what the production seams deliver --
``AccuracySample.from_dict`` over the rows' ``accuracy_sample`` and the
accuracy store's samples, ``AccuracyTracker.temperature_bias``/``_mae``,
``AccuracyTracker.as_dict``'s persisted slice and ``SnapshotRing.observe_bias``.

Reconstruction (time-based): the known samples are the rows' and the accuracy
store's, by their own ``t``. A restart is a row whose ``version`` differs from
the previous row's, or a spacing of three or more optimization intervals
(``d15_restart_gaps.py``'s rule), at that row's time R. The deque after R
is the newest ``as_dict`` slice of the deque at R minus half an interval
(samples stamped before it were recorded before the restart even when the
first row after it is where they show), then every known sample since.

Run (from the export root):
    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round11/D15/s2/m6_monitor.py --bundle B
    ... --enumerate              # the step's universe, one line per item
    ... --perturb no-restart     # control: restarts not modelled -> anchors move
    ... --perturb band=0.1       # control: BIAS_BAND_C patched in memory -> latch_match moves
    ... --bundle SYN --fresh     # null control: tools/replay/dbg_bundle_gen.py's bundle,
                                 # whose tracker starts empty
Expected on the owner's 2026-11-16 download at 92d38ecb: self_test anchor
count_delta 0 and bias_delta <= 0.002; latch_match=1; restart_flip_days=0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: owner's macOS box (B8).
Privacy: prints counts, dates and aggregate degC statistics only; no entity
id, name, location or raw reading.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest import mock  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "custom_components", ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
from heatpump_optimizer import const, snapshots  # noqa: E402
from heatpump_optimizer.accuracy import (  # noqa: E402
    HISTORY_LENGTH, AccuracySample, AccuracyTracker,
)


def persisted_slice() -> int:
    """How many samples ``AccuracyTracker.as_dict`` keeps, read off the method."""
    tracker = AccuracyTracker()
    for i in range(HISTORY_LENGTH):
        tracker.samples.append(AccuracySample(when=datetime.fromtimestamp(i, ZoneInfo("UTC"))))
    return len(tracker.as_dict()["samples"])


def tracker_of(samples) -> AccuracyTracker:
    t = AccuracyTracker()
    t.samples.extend(samples)
    return t


class Model:
    """The live deque at any instant, from the known samples and the restarts."""

    def __init__(self, known, restarts, keep, margin, fresh=False):
        self.known = sorted(known, key=lambda s: s.when)
        self.restarts = sorted(restarts)
        self.keep = keep
        self.margin = margin
        self.fresh = fresh  # a collection that began with an empty tracker

    def at(self, when: datetime):
        """(known samples held, unknown count or None when indeterminate)."""
        before = [r for r in self.restarts if r <= when]
        if not before:
            held = [s for s in self.known if s.when <= when]
            if len(held) >= HISTORY_LENGTH:
                return held[-HISTORY_LENGTH:], 0
            return held, (0 if self.fresh else None)
        r = before[-1]
        held, unknown = self.at(r - self.margin - timedelta(microseconds=1))
        if len(held) >= self.keep:
            held, unknown = held[-self.keep:], 0
        else:
            unknown = self.keep - len(held)  # the install's history assumed long enough
        cut = r - self.margin
        held = held + [s for s in self.known if cut <= s.when <= when]
        total = unknown + len(held)
        if total > HISTORY_LENGTH:
            drop = total - HISTORY_LENGTH
            take = min(unknown, drop)
            unknown -= take
            held = held[drop - take:]
        return held, unknown


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--enumerate", action="store_true")
    ap.add_argument("--perturb", default="")
    ap.add_argument("--fresh", action="store_true",
                    help="the tracker was empty when the collection began (the synthetic bundle)")
    a = ap.parse_args(argv)
    began_cpu, began_thread = time.process_time(), time.thread_time()

    download = debug_ingest.read_download(a.bundle)
    bundle = debug_ingest.unwrap_download(download)
    config = (download.get("data") or {}).get("config") or {}
    named = config.get(const.CONF_OPTIMIZATION_INTERVAL)
    interval_s = float(named if named is not None else const.DEFAULT_OPTIMIZATION_INTERVAL) * 60
    tz = ZoneInfo((bundle.get("replay") or {}).get("time_zone") or "UTC")
    rows = bundle.get("cycle_rows") or []
    stores = bundle.get("stores") or {}
    acc_doc = next((v for k, v in stores.items() if k.endswith("_accuracy")), {})
    store_samples = [s for s in (AccuracySample.from_dict(x) for x in
                     ((acc_doc.get("accuracy") or {}).get("samples") or [])) if s]
    ring_doc = next((v for k, v in stores.items() if k.endswith("_snapshots")), {})

    # A row's sample without its own ``t`` takes the row's (debug_ingest's rule).
    row_samples = [s for s in (AccuracySample.from_dict(
        {**r["accuracy_sample"], "t": r["accuracy_sample"].get("t") or r.get("t")})
        for r in rows if r.get("accuracy_sample")) if s is not None]
    row_whens = {s.when for s in row_samples}
    known: dict = {}
    for s in row_samples + store_samples:
        known.setdefault(s.when, s)
    row_ts = [datetime.fromisoformat(r["t"]) for r in rows]
    restarts = [row_ts[i] for i in range(1, len(rows))
                if rows[i].get("version") != rows[i - 1].get("version")
                or (row_ts[i] - row_ts[i - 1]).total_seconds() >= 3 * interval_s]
    keep = persisted_slice()
    margin = timedelta(seconds=interval_s / 2)
    model = Model(known.values(), restarts if a.perturb != "no-restart" else [], keep, margin, a.fresh)
    free = Model(known.values(), [], keep, margin, a.fresh)

    by_day: dict[str, list] = {}
    for s in sorted(known.values(), key=lambda s: s.when):
        by_day.setdefault(s.when.astimezone(tz).date().isoformat(), []).append(s)
    days = sorted(by_day)
    first_row = {}
    for t in row_ts:
        first_row.setdefault(t.astimezone(tz).date().isoformat(), t)

    anchors = []
    for snap in (ring_doc.get("snapshots") or []):
        when = datetime.fromisoformat(snap["taken_at"])
        if row_ts[0] <= when <= row_ts[-1] and isinstance(snap.get("accuracy"), dict):
            anchors.append(("snapshot_" + when.astimezone(tz).date().isoformat(),
                            when, snap["accuracy"]))
    manifest = bundle.get("manifest") or {}
    st = ((manifest.get("self_tests") or {}).get("accuracy") or {}).get("result") or {}
    if isinstance(st, str):
        st = json.loads(st)
    if st.get("live") and manifest.get("self_tests_at"):
        anchors.append(("self_test", datetime.fromisoformat(manifest["self_tests_at"]),
                        st["live"]))

    if a.enumerate:
        for day in days:
            print(f"window {day}")
        for name, _, _ in anchors:
            print(f"anchor {name}")
        print("latch snapshots-store")
        return 0

    print(f"RESULT known_samples={len(known)} unit=count rows={len(rows)} store={len(store_samples)}")
    print(f"RESULT restarts={len(restarts)} unit=count")
    print(f"RESULT store_only_samples={sum(1 for s in store_samples if s.when not in row_whens)} unit=count")
    for name, when, rec in anchors:
        held, unknown = model.at(when)
        n = len(held) + (unknown or 0)
        partial = unknown is None or unknown > 0
        bias, mae = tracker_of(held).temperature_bias(), tracker_of(held).temperature_mae()
        cdelta = abs(n - int(rec.get("samples") or 0))
        bdelta = (abs(bias - rec["temperature_bias"]) if bias is not None
                  and rec.get("temperature_bias") is not None else None)
        mdelta = (abs(mae - rec["temperature_mae"]) if mae is not None
                  and rec.get("temperature_mae") is not None else None)
        print(f"RESULT anchor_{name}_partial={int(partial)} unit=flag")
        print(f"RESULT anchor_{name}_count_delta={cdelta} unit=count")
        print(f"RESULT anchor_{name}_bias_delta={None if bdelta is None else round(bdelta, 4)} unit=celsius")
        print(f"RESULT anchor_{name}_mae_delta={None if mdelta is None else round(mdelta, 4)} unit=celsius")

    band = snapshots.BIAS_BAND_C
    if a.perturb.startswith("band="):
        band = float(a.perturb.split("=", 1)[1])
    ring = snapshots.SnapshotRing()
    flips = rederived = 0
    first_full = None
    with mock.patch.object(snapshots, "BIAS_BAND_C", band):
        for day in days:
            w = tracker_of(by_day[day])
            print(f"RESULT window_{day}_n={len(by_day[day])} unit=count")
            print(f"RESULT window_{day}_bias={w.temperature_bias()} unit=celsius")
            print(f"RESULT window_{day}_mae={w.temperature_mae()} unit=celsius")
            # the counting tick: the day's first row, else (rows ended) its first sample
            tick = first_row.get(day) or by_day[day][0].when
            held, unknown = model.at(tick)
            held_free, _ = free.at(tick)
            partial = unknown is None or unknown > 0
            live = tracker_of(held).temperature_bias()
            nofix = tracker_of(held_free).temperature_bias()
            print(f"RESULT window_{day}_live_bias={live} unit=celsius partial={int(partial)} "
                  f"deque={len(held) + (unknown or 0) if unknown is not None else 'unknown'}")
            if not partial:
                flips += int((live is not None and abs(live) > band)
                             != (nofix is not None and abs(nofix) > band))
                first_full = first_full or day
                ring.observe_bias(tick.astimezone(tz), live, True)
                rederived += 1
    stored = (bool(ring_doc.get("alarmed")), int(ring_doc.get("bias_days") or 0),
              str(ring_doc.get("last_day") or ""))
    got = (ring.alarmed, ring._bias_days, ring._last_day)
    print(f"RESULT first_fully_known_day={first_full} unit=date")
    print(f"RESULT rederived_ticks={rederived} unit=count")
    print(f"RESULT latch_stored=alarmed:{int(stored[0])},bias_days:{stored[1]},last_day:{stored[2]} unit=state")
    print(f"RESULT latch_rederived=alarmed:{int(got[0])},bias_days:{got[1]},last_day:{got[2]} unit=state")
    print(f"RESULT latch_match={int(stored == got)} unit=flag")
    # The repair issue the latch raises (coordinator._async_watch_learning_drift):
    # present in the download's own issue list exactly while the ring is alarmed.
    issues = [i.get("issue_id") if isinstance(i, dict) else i
              for i in (download.get("issues") or [])]
    raised = any(str(i).startswith("accuracy_drift") for i in issues)
    print(f"RESULT accuracy_drift_issue_present={int(raised)} unit=flag")
    print(f"RESULT issue_agrees_with_latch={int(raised == stored[0])} unit=flag")
    print(f"RESULT restart_flip_days={flips} unit=count")
    print(f"RESULT persisted_slice={keep} unit=count")
    cpu, thr = time.process_time() - began_cpu, time.thread_time() - began_thread
    print(f"RESULT thread_factor={cpu / thr if thr > 0 else float('nan'):.3f} unit=ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    print("RESULT swapins=n/a unit=count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
