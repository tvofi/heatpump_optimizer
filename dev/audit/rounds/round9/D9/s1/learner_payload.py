"""D9-s1 H9: bytes the defrost and flow-lift learners contribute to the
coordinator payload and store per cycle, and the loop-thread CPU of producing
them; fully populated vs empty.

Metric: len(json.dumps(x)) of defrost.DefrostDerate.summary() (published in
the data dict every cycle as defrost_buckets), DefrostDerate.as_dict() (the
store) and flow_lift.FlowCurveBias.as_dict(); and thread CPU per summary()
call (mean of 200).
Count key: the objects the production methods RETURN.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python \
      tools/audit/round9/D9/s1/learner_payload.py [--observations N]
Perturbation: --observations 0 (empty learner): bytes must go DOWN; more
observations spread over the grid: bytes UP until every bucket is populated,
then flat (the grid is bounded).
Bytes final; CPU provisional. Baseline SHA 1936d5ca72a0.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

import argparse
import json
import time

import numpy as np

from heatpump_optimizer.defrost import DefrostDerate
from heatpump_optimizer.flow_lift import FlowCurveBias


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--observations", type=int, default=5000)
    args = ap.parse_args()
    rng = np.random.default_rng(0)
    d = DefrostDerate()
    f = FlowCurveBias()
    for _ in range(args.observations):
        t = float(rng.uniform(-25, 15))
        h = float(rng.uniform(30, 100))
        d.observe(t, h, float(rng.uniform(0.6, 1.0)))
        f.observe(float(rng.uniform(25, 55)), float(rng.uniform(25, 55)))
    summ = d.summary()
    C.result("defrost_summary_json_bytes", len(json.dumps(summ)), "bytes")
    C.result("defrost_summary_rows", len(summ), "count")
    C.result("defrost_store_json_bytes", len(json.dumps(d.as_dict())), "bytes")
    C.result("flow_bias_store_json_bytes", len(json.dumps(f.as_dict())), "bytes")
    t0 = time.thread_time()
    for _ in range(200):
        d.summary()
    C.result("defrost_summary_cpu_us_per_call", round((time.thread_time() - t0) / 200 * 1e6, 1), "us (provisional)")
    C.trailer(1.0)


if __name__ == "__main__":
    main()
