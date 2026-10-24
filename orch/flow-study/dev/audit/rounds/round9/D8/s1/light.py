#!/usr/bin/env python3
"""D8-s1 (audit round 9), D8.M1/M2: the setup-time light refresh, entity by entity.

METRIC: per violation class (matrix.py's judge), the count of entities of the
  sensor/binary_sensor platforms that break it after the first refresh Home
  Assistant runs at setup (``_skip_solve_once``: inputs, prices, weather, no
  solve), over every matrix cell; plus the full state listing with --list.
RUN:   PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/s1/light.py [--list CELL]
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1: see REPORT.md (exact counts).
MACHINE: B6 cloud container, 4 CPU, CPython 3.14.0rc2.
"""
from __future__ import annotations
import os, sys, asyncio, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matrix as M  # thread pin + TZ happen there, before numpy
from homeassistant.util import dt as dt_util


def main() -> int:
    lst = sys.argv[sys.argv.index("--list") + 1] if "--list" in sys.argv else None
    table = M.units_table()
    counts: dict[str, int] = {}
    t_cpu, t_thr = time.process_time(), time.thread_time()
    for tname, tcfg in M.topologies().items():
        for fname, fcfg in M.FEATURES.items():
            cell = f"{tname}+{fname}"
            if lst and cell != lst:
                continue
            cfg = {**tcfg, **fcfg}
            if tname == "coord_minimal_bare":
                cfg = {k: v for k, v in cfg.items() if not k.endswith("_entity") or k in ("heat_pump_mode_entity", "weather_entity")}
            hass, coord, ents, _ = M.build(cfg)
            dt_util.freeze(M.T0)
            M.set_inputs(hass, M.INPUTS[0], M.T0)
            coord._skip_solve_once = True
            coord.data = asyncio.run(coord._async_update_data())
            for e in ents:
                r = M.read(e)
                for cls, line in M.judge(r, table):
                    counts[cls] = counts.get(cls, 0) + 1
                    if lst or cls != "available_unknown":
                        print(f"  {cell} {cls} {line}")
                if lst:
                    print(f"    {r['entity_id']:70s} avail={r['available']!s:5} state={r['state']!r}"[:160])
            dt_util.freeze(None)
    for cls in sorted(counts):
        print(f"RESULT light_{cls}={counts[cls]} count")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
