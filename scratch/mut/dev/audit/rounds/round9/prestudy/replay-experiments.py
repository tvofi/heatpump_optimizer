#!/usr/bin/env python3
"""Falsifying experiments for the replay-speed pre-study (READ-ONLY on r9-main).

Runs the channel_boost arm of tests/boost_drift_replay.py under four
conditions, timing each and reporting every R.check verdict, WITHOUT editing
the r9-main checkout: the module source is copied here and edited in-memory.

Conditions:
  base     -- the module verbatim (the timing control)
  warm     -- hands each cycle's solve the previous shipped plan, exactly as
              production's coordinator does (optimizer._prev_shipped_plan,
              coordinator.py:_hand_prev_plan), which the replay never does
  maxiter60-- _multi_start_minimize capped at maxiter=60 (harness-only knob)
  h12      -- horizon_hours 24 -> 12 (n_steps 48 -> 24)

Each condition prints WALL <seconds> and the check outcomes. Usage:
  python3 experiments.py <base|warm|maxiter60|h12>
"""
import sys
import time
from pathlib import Path

REPO = Path("/private/tmp/r9-main")
SCRATCH = Path("/private/tmp/r9-prestudy-replay")
SRC = (REPO / "tests" / "boost_drift_replay.py").read_text()

which = sys.argv[1]

src = SRC
if which == "warm":
    src = src.replace(
        '    result = st["optimizer"].optimize(inputs=solve_inputs(',
        '    _pp = st.pop("prev_plan", None)\n'
        '    if _pp is not None:\n'
        '        st["optimizer"]._prev_shipped_plan = _pp\n'
        '    result = st["optimizer"].optimize(inputs=solve_inputs(',
    )
    src = src.replace(
        '    coord._optimization_result = result\n',
        '    coord._optimization_result = result\n'
        '    st["prev_plan"] = np.asarray(result.power_schedule, dtype=float).copy()\n',
    )
    assert src != SRC
elif which == "maxiter60":
    src = src.replace(
        "R = Results(",
        'import heatpump_optimizer.optimizer as _opt_mod\n'
        "_orig_ms = _opt_mod._multi_start_minimize\n"
        "def _capped_ms(objective, candidates, bounds, **kw):\n"
        "    kw['maxiter'] = min(kw.get('maxiter', 300), 60)\n"
        "    return _orig_ms(objective, candidates, bounds, **kw)\n"
        "_opt_mod._multi_start_minimize = _capped_ms\n"
        "R = Results(",
    )
    assert src != SRC
elif which == "h12":
    src = src.replace("horizon_hours=24.0,", "horizon_hours=12.0,")
    assert src != SRC
elif which != "base":
    raise SystemExit(f"unknown condition {which}")

mod_name = f"bdr_{which}"
out_file = SCRATCH / f"{mod_name}.py"
out_file.write_text(src)
sys.path.insert(0, str(REPO / "tests"))
sys.path.insert(0, str(REPO / "tests" / "hastub"))
sys.path.insert(0, str(REPO / "custom_components"))
sys.path.insert(0, str(SCRATCH))

import importlib

b = importlib.import_module(mod_name)

t0 = time.time()
outs = b.replay({"channel_boost": "channel"})
wall = time.time() - t0
out = outs["channel_boost"]
b.check_arm(out, boosted=True)
b.check_record(out)
rc = b.R.close(f"EXPERIMENT {which}")
print(f"### {which}: WALL {wall:.1f}s rc={rc}")
print(f"### daily={out['daily']}")
print(f"### folds frozen={out['folds_frozen']} outside={out['folds_outside']} "
      f"after={out['folds_after']} tagged={len(out['tagged'])} "
      f"untagged={len(out['untagged'])} hh_final={out['hh_final']}")
