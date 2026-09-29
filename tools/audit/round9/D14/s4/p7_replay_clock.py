#!/usr/bin/env python3
"""P7 instrument probe: can the nightly replay lane see a DST wall-clock seam at all?

METRIC (one line): `replay_wrong_sites` = distinct production file:line sites at
which datetime arithmetic returned a duration different from the UTC truth,
while tests/replay.py:run_fixture itself replays a DST-transition day.

COUNT KEY: the timedelta production computes against `b.timestamp()-a.timestamp()`
(p7_dst_seams.py's tracer, imported unchanged), on the clock `run_fixture`
freezes -- `dt_util.freeze(t)` with `t = _ts(window.start) + k*step`, a
`datetime.fromisoformat` value whose tzinfo is a FIXED offset. Home Assistant's
`dt_util.now()` carries the configured ZoneInfo instead.

ARMS:
  default       run_fixture as committed, on the spring and autumn days
                (tools/audit/round9/D14/s4/dst_fixture.py writes them to a temp dir)
  --zone-clock  perturbation, in memory: replay._ts returns the instant in the
                fixture's ZoneInfo (`.astimezone(dt_util.DEFAULT_TIME_ZONE)`),
                i.e. the clock Home Assistant hands the integration.
Null control: the plain day (no transition) under both arms.

COMMAND (repository root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    /home/claude/venv314/bin/python tools/audit/round9/D14/s4/p7_replay_clock.py [--zone-clock]
EXPECTED at 1936d5ca: default replay_wrong_sites=0 on spring and autumn;
  --zone-clock >0 on both; plain day 0 under both. Exact integers.
Machine: Linux container, 4 cores, python 3.14 (box B9).
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ["HASTUB_TZ"] = "Europe/Stockholm"

import json  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

ZONE_CLOCK = "--zone-clock" in sys.argv
sys.argv = [sys.argv[0]]  # p7_dst_seams parses argv at import: give it defaults
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(Path("tests/hastub").resolve()), str(Path("tests").resolve()),
                str(Path("custom_components").resolve()), str(HERE)]

import p7_dst_seams as tr  # noqa: E402  (installs the tracer on dt_util)
import dst_fixture  # noqa: E402
import replay  # noqa: E402  (tests/replay.py, the instrument under test)
from homeassistant.util import dt as dt_util  # noqa: E402

if ZONE_CLOCK:
    replay._ts = lambda raw: (datetime.fromisoformat(raw).astimezone(dt_util.DEFAULT_TIME_ZONE)
                              if raw else None)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="p7replay-"))
    began_cpu, began = time.process_time(), time.monotonic()
    total = set()
    for day in ("spring", "autumn", "plain"):
        path = tmp / f"dst-{day}.json"
        path.write_text(json.dumps(dst_fixture.build(day, HERE.parents[4])))
        before = {k: v["wrong"] for k, v in tr.REC.items()}
        out = replay.run_fixture(path, None)
        wrong = {k[:2] for k, v in tr.REC.items() if v["wrong"] > before.get(k, 0)}
        total |= wrong
        print(f"RESULT {day}_cycles={out['cycles']} count")
        print(f"RESULT {day}_cycle_failures={out['counts']['cycle']} count")
        print(f"RESULT {day}_replay_wrong_sites={len(wrong)} count")
        for k in sorted(wrong):
            print(f"#   {day}: {k[0]}:{k[1]}")
    print(f"RESULT zone_clock={int(ZONE_CLOCK)}")
    print(f"RESULT replay_wrong_sites={len(total)} count")
    pc, tc = time.process_time() - began_cpu, time.thread_time()
    print(f"RESULT wall_s={time.monotonic() - began:.1f} s provisional")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + str(sum(int(l.split()[1]) for l in open("/proc/vmstat")
                                      if l.startswith("pswpin"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
