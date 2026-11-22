"""Box D3-u1a: re-drive one full-net TIMEOUT with a longer limit, one script, alone.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/redrive_timeout.py <key> <script> <timeout_s>

Applies the mutant of state/results/complete/<key>.json on a fresh worker tree
(w9), runs <script> once with <timeout_s>, judges it with mutation_table.killed
against this box's traced baseline, restores the file, and writes
state/results/redrive/<key>.json. Prints RESULT lines.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prescreen as ps  # noqa: E402

mt = ps.mt


def main() -> int:
    key, script, limit = sys.argv[1], sys.argv[2], int(sys.argv[3])
    r = json.loads((ps.RESULTS / "complete" / f"{key}.json").read_text())
    m = r["mutant"]
    base = ps.load_base()
    t = ps.recycle(9)
    path = t / m["file"]
    original = path.read_text()
    lines = original.splitlines(True)
    assert lines[m["line"] - 1].rstrip("\n") == m["old"]
    lines[m["line"] - 1] = m["new"] + "\n"
    t0 = time.time()
    try:
        path.write_text("".join(lines))
        a, e = ps.spec(script)
        run = mt.run_script(script, t, limit, a, e)
    finally:
        path.write_text(original)
    k = mt.killed(script, run, ps.from_json(base[script]["run"]))
    out = {"key": key, "mutant": m, "script": script, "limit_s": limit,
           "run": ps.to_json(run), "killed": k, "wall": round(time.time() - t0, 1),
           "baseline_seconds": base[script]["run"]["seconds"]}
    (ps.RESULTS / "redrive").mkdir(parents=True, exist_ok=True)
    (ps.RESULTS / "redrive" / f"{key}.json").write_text(json.dumps(out))
    print(f"RESULT redrive_killed={k} rc={run.rc} failed={run.failed} timed_out={run.timed_out} "
          f"seconds={run.seconds:.1f} baseline_seconds={base[script]['run']['seconds']}")
    print("RESULT provisional=true (wall under this box's own load; nproc 4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
