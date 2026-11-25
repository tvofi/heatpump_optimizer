"""D14-s3 round 11: shared driver for the nightly-replay-axis detectors.

Not a harness on its own (no RESULT lines): it runs one replay fixture --
mutated in memory -- through a tree's own ``tests/replay.py:run_fixture`` (the
real coordinator cycle, one interpreter per arm) and hands back what the lane
itself throws away: every entity record of every cycle (``replay.sweep``'s
output) and every service call the coordinator made
(``harness.FakeServices.async_call``).

Used by p8_currency.py, staleness_quiet.py, registry_reload.py.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import contextlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
MARK = "<<<replaykit>>>"


def tree_paths(tree: Path) -> None:
    for p in (tree / "tests" / "hastub", tree / "tests", tree / "custom_components",
              tree / "tools" / "replay"):
        sys.path.insert(0, str(p))


def run(tree: Path, doc: dict, step_minutes: int | None, setup=None) -> dict:
    """Replay ``doc`` in THIS interpreter (call from a child), capturing records."""
    tree_paths(tree)
    import replay
    import harness

    per_cycle: list[list[dict]] = []
    calls: list[tuple] = []
    real_sweep = replay.sweep

    def sweep(entities, action, errors, t):
        recs = real_sweep(entities, action, errors, t)
        per_cycle.append([{**r, "t": t.isoformat()} for r in recs])
        return recs

    replay.sweep = sweep
    real_call = harness.FakeServices.async_call

    async def call(self, domain, service, data=None, **kw):
        from homeassistant.util import dt as dt_util
        calls.append((dt_util.now().isoformat(), domain, service, dict(data or {})))
        return await real_call(self, domain, service, data, **kw)

    harness.FakeServices.async_call = call
    ctx = {}
    if setup is not None:
        setup(ctx)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "day.json"
        path.write_text(json.dumps(doc))
        with contextlib.redirect_stdout(io.StringIO()):
            out = replay.run_fixture(path, step_minutes)
    return {"run": {k: out.get(k) for k in ("cycles", "entities", "results", "counts", "away")},
            "records": per_cycle, "calls": calls, "ctx": ctx}


def child(script: Path, tree: Path, args: list[str], tz: str = "Europe/Stockholm") -> dict | None:
    env = {**os.environ, "HASTUB_TZ": tz, "PYTHONPATH": str(tree / "tests" / "hastub")}
    p = subprocess.run([sys.executable, str(script), "--child", "--tree", str(tree), *args],
                       capture_output=True, text=True, env=env, cwd=tree)
    line = next((ln for ln in p.stdout.splitlines() if ln.startswith(MARK)), None)
    if line is None:
        sys.stderr.write(f"child {args} rc={p.returncode}\n{p.stderr[-2500:]}\n")
        return None
    return json.loads(line[len(MARK):])


def emit(obj) -> None:
    print(MARK + json.dumps(obj, default=str))


def tail_results(load_before: float | None = None) -> None:
    import time
    pc, tc = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(pc / tc) if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
