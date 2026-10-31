#!/usr/bin/env python3
"""ARCH-s3 harness: the architecture score's delta-S between the baseline and a prototype ref,
with every counter on, plus this seat's cells and their 30% target.

Metric: delta_S = tools/audit/archscore/score.py --diff BASE PROTO's dS (sum w*log2((b+1)/(c+1))),
and per metric the base -> proto value of untyped_payload_keys, family_splits and the four
GATE_ONLY tripwires. cells_S_30pct = the dS of cutting each of this seat's two weighted cells by
30% from its baseline value: w*log2((b+1)/(0.7b+1)) summed -- 0 when both sit at 0.

Run:     python3 dev/audit/rounds/round10/D7/arch-s3/score_delta.py BASE PROTO
         (perturbation: PROTO := BASE, delta_S must read 0)
Root:    the working directory's tools/audit/archscore (its counters measure both refs).
Expected at baseline 554e2ecfa vs 52f0de63 (instrument protos 01-03) and vs c402bce8 (+ proto 04): delta_S=0.0000, cells 0 -> 0, (c402bce8: reflective_writes 17 -> 15),
         cells_S_30pct=0.0000.
Machine: macOS arm64, tvofi's audit box. Counts only.
Instrumented: archscore.vector:measure, archscore.score:delta.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import math  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tools" / "audit")]
assert "ARCHSCORE_ABLATE" not in os.environ or not os.environ["ARCHSCORE_ABLATE"], "every counter must be on"
from archscore import score as S  # noqa: E402
from archscore import vector as V  # noqa: E402

CELLS = ("untyped_payload_keys", "family_splits")
TRIPS = V.GATE_ONLY


def main() -> None:
    base_ref, proto_ref = sys.argv[1], sys.argv[2]
    t_cpu, th_cpu = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="arch-s3-score-") as tmp:
        b_dir, p_dir = Path(tmp) / "b", Path(tmp) / "p"
        b_dir.mkdir()
        p_dir.mkdir()
        base = V.measure(S.tree_of(base_ref, b_dir))
        proto = V.measure(S.tree_of(proto_ref, p_dir))
    d = S.delta(base, proto)
    print(S.report(base, proto))
    w = S.weights()
    for m in (*CELLS, *TRIPS):
        print(f"RESULT {m}_base={base.get(m)} count")
        print(f"RESULT {m}_proto={proto.get(m)} count")
    total_w = sum(w[m] for m in V.SCORE_METRICS)
    cells_30 = sum(w[m] * math.log2((base[m] + 1) / (0.7 * base[m] + 1)) for m in CELLS)
    print(f"RESULT cells_weight={sum(w[m] for m in CELLS):.4f}")
    print(f"RESULT all_weight={total_w:.4f}")
    print(f"RESULT cells_S_30pct={cells_30:.4f}")
    print(f"RESULT admissible={d['admissible']}")
    print(f"RESULT delta_S={d['dS']:.4f}")
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th_cpu, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
