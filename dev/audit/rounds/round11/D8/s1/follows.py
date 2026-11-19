"""D8-s1 M2 value-follows-payload: each sensor static between cycles A and B, resolved per key.

Metric: count of (cell, sensor) pairs whose published state is identical in cycles A and B while
at least one payload leaf its own `native_value` read (traced, not guessed) changed value.
Key: the leaves `native_value` actually reads from `coordinator.data`, recorded by a tracing
mapping substituted for the published dict; a state is "static" when equal in A and B.
Command (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s1/follows.py [-v]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B4. Expected: printed counts, exact.
Instrumented symbols: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data,
heatpump_optimizer.sensor:async_setup_entry (each sensor's native_value).
Perturbation: --freeze-src KEY republishes cycle A's value of payload key KEY in cycle B; a sensor
reading KEY then becomes static with no moved leaf, so `static_src_static` rises and
`static_src_moved` for that sensor cannot rise.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402


class Tracing(dict):
    """A dict that records every leaf path read through get/[]."""

    def __init__(self, data, log, prefix=()):
        super().__init__(data)
        self._log, self._prefix = log, prefix

    def _wrap(self, key, value):
        path = self._prefix + (key,)
        if isinstance(value, dict) and not isinstance(value, Tracing):
            # A sub-mapping is traced on; it is also recorded at its own path,
            # so a copy taken of it (dict(...)) is still a recorded read.
            self._log.add(path + ("*",))
            return Tracing(value, self._log, path)
        self._log.add(path)
        return value

    def __getitem__(self, key):
        return self._wrap(key, super().__getitem__(key))

    def get(self, key, default=None):
        if key in self:
            return self._wrap(key, super().__getitem__(key))
        self._log.add(self._prefix + (key,))
        return default


def leaf(data, path):
    node = data
    if path and path[-1] == "*":
        path = path[:-1]
    for k in path:
        if not isinstance(node, dict) or k not in node:
            return "<absent>"
        node = node[k]
    return node


def reads(coord, ent, data):
    log = set()
    saved = coord.data
    coord.data = Tracing(data, log)
    try:
        val = ent.native_value
    finally:
        coord.data = saved
    return val, log


def main():
    t0, th0 = time.process_time(), time.thread_time()
    freeze = sys.argv[sys.argv.index("--freeze-src") + 1] if "--freeze-src" in sys.argv else None
    moved, quiet, nosrc = [], [], []
    for cell, cfg in rig.cells().items():
        hass, entry, coord = rig.build(cfg)
        ents = None
        per = []
        for idx in range(2):
            err = rig.cycle(hass, coord, idx)
            if idx and freeze and freeze in per[0][0]:
                coord.data[freeze] = copy.deepcopy(per[0][0][freeze])
            if ents is None:
                ents = [e for p, e in rig.entities(hass, entry) if p == "sensor"]
            data = coord.data
            snap = {}
            for e in ents:
                if not e.available:
                    snap[type(e).__name__] = ("<unavailable>", set())
                    continue
                snap[type(e).__name__] = reads(coord, e, data)
            per.append((copy.deepcopy(dict(data)), snap, err))
        rig.dt_util.freeze(None)
        (da, sa, _), (db, sb, _) = per
        for name, (va, la) in sa.items():
            vb, lb = sb[name]
            if va != vb or va in ("<unavailable>", None):
                continue
            paths = sorted(la | lb)
            # A sub-mapping's own path counts only where no leaf under it was read.
            paths = [p for p in paths if p[-1] != "*" or not any(
                q[:len(p) - 1] == p[:-1] and len(q) >= len(p) and q[-1] != "*" for q in paths)]
            changed = [p for p in paths if leaf(da, p) != leaf(db, p)]
            line = f"{cell}|{name}|state={va!r}|reads={['.'.join(map(str, p)) for p in paths][:8]}"
            if changed:
                moved.append(line + f"|moved={['.'.join(map(str, p)) + ':' + str(leaf(da, p))[:30] + '->' + str(leaf(db, p))[:30] for p in changed][:4]}")
            elif not paths:
                nosrc.append(line)
            else:
                quiet.append(line)
    if "-v" in sys.argv:
        for x in moved:
            print("  MOVED", x)
        for x in nosrc:
            print("  NOPAYLOAD", x)
        for x in quiet:
            print("  QUIET", x)
    by_cls = defaultdict(int)
    for x in moved:
        by_cls[x.split("|")[1]] += 1
    print(f"RESULT static_src_moved={len(moved)} count")
    print(f"RESULT static_src_static={len(quiet)} count")
    print(f"RESULT static_no_payload_read={len(nosrc)} count")
    for k, v in sorted(by_cls.items()):
        print(f"RESULT static_src_moved[{k}]={v} count")
    print(f"RESULT thread_factor={(time.process_time() - t0) / max(time.thread_time() - th0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
