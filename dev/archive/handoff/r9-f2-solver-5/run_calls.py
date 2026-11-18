"""Run the round-9 RCA prototype's production-call capture against a tree root.

Self-contained: the driver text (CALLS_PROBE_DRIVER) is taken from
tests/stress.py at handoff/r9-rca-avoidable-interpreter-bound-recomputation
(ab04e39b) via git and imported from a temp file, so nothing on a seat-local
scratch path is load-bearing.

  python3 tools/audit/handoff/r9-f2-solver-5/run_calls.py <tree-root> <out.json> '["winter/tariff"]'

Needs CPython 3.12+ (sys.monitoring); the PR's captures ran in the hpo-ci
Linux container (3.14.7).
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def driver_text() -> str:
    src = subprocess.run(
        ["git", "-C", REPO, "show", "ab04e39b:tests/stress.py"],
        capture_output=True, text=True, check=True,
    ).stdout
    sys.path[:0] = [
        os.path.join(REPO, "tests"), os.path.join(REPO, "tests", "hastub"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        mod = os.path.join(tmp, "stress_rca_ab04e39b.py")
        with open(mod, "w") as fh:
            fh.write(src.split("if __name__")[0])
        spec = importlib.util.spec_from_file_location("stress_rca_ab04e39b", mod)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)  # type: ignore[union-attr]
        return str(loaded.CALLS_PROBE_DRIVER)


def main() -> int:
    root, out, labels = sys.argv[1], sys.argv[2], sys.argv[3]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.join(root, "tests", "hastub")
    p = subprocess.run(
        [sys.executable, "-c", driver_text(), root, out, labels],
        capture_output=True, text=True, env=env,
    )
    sys.stderr.write(p.stderr[-2000:])
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
