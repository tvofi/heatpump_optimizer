"""Probe for the D3 seam tools/replay/debug_replay.py:main (round 11, N-silent-zero sweep).

debug_replay seeds store loads only when the bundle carries `stores`
(`run_seeded(replay_doc, stores or None, ...)`); without them the coordinator's load-gated paths
(`if not self._snapshots_loaded: return` in the drift watch) never run, the same mechanism
D15-s2-03 judged in the synthetic generator. This probe runs the real `main` on one bundle with
and without its `stores` section, counts `SnapshotRing.observe_bias` calls, and compares the
RESULT lines the tool prints. A store-less replay whose drift path ran 0 times while its RESULT
lines match the seeded run (and name no loads-off state) is the instance.

Run (repo root): PYTHONPATH=tests/hastub:tests:custom_components python3 replay_unloaded.py FULL.json NOSTORES.json
     --perturb   debug_replay.enable_store_loads forced on for the store-less run too
                 (the generator-side fix shape of D15-s2-03): observe_bias calls rise above 0
"""
import contextlib
import io
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
for p in (ROOT / "tools" / "replay", ROOT / "tests", ROOT / "tests" / "hastub", ROOT / "custom_components"):
    sys.path.insert(0, str(p))

import debug_replay  # noqa: E402
from heatpump_optimizer import snapshots  # noqa: E402

CALLS = {"n": 0}
_orig = snapshots.SnapshotRing.observe_bias


def _counting(self, *a, **k):
    CALLS["n"] += 1
    return _orig(self, *a, **k)


snapshots.SnapshotRing.observe_bias = _counting
PERTURB = "--perturb" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]


def run(bundle):
    CALLS["n"] = 0
    buf = io.StringIO()
    argv = sys.argv
    sys.argv = ["debug_replay.py", "--bundle", bundle]
    original = debug_replay.enable_store_loads() if (PERTURB and "nostores" in bundle.lower().replace("drop_stores", "nostores")) else None
    try:
        with contextlib.redirect_stdout(buf):
            try:
                debug_replay.main()
            except SystemExit:
                pass
    finally:
        sys.argv = argv
        if original is not None:
            debug_replay.restore_store_loads(original)
    lines = [l for l in buf.getvalue().splitlines() if l.startswith("RESULT")]
    return CALLS["n"], lines


full_calls, full_lines = run(args[0])
bare_calls, bare_lines = run(args[1])
print(f"RUN seeded   observe_bias_calls={full_calls} result_lines={len(full_lines)}")
print(f"RUN nostores observe_bias_calls={bare_calls} result_lines={len(bare_lines)}")
same = full_lines == bare_lines
marker = any("load" in l.lower() or "store" in l.lower() for l in bare_lines)
print(f"RESULT nostores_result_lines_identical={int(same)} count")
print(f"RESULT nostores_names_loads_off={int(marker)} count")
print(f"RESULT unloaded_replay_reads_clean={int(bare_calls == 0 and full_calls > 0 and same and not marker)} count")
