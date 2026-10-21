#!/usr/bin/env python3
"""The replay loop figure's ruler: the BLAS solve against a pure-Python one (#2270).

``loop_cpu_ratio`` was the coordinator cycle's loop-thread CPU over
``tests/stress.py``'s ``reference_solve``, a BLAS-bound solve. The measure is
interpreter-bound, so over the nightly series the figure tracked the runner
CLASS, not the code: ``corr(loop_cpu_ratio, ref_ms) = -0.94``, and it read
0.244-0.405 (1.66x). #2270's fix normalises it by a fixed pure-Python workload
(``tests/replay.py``'s ``reference_loop``) instead. This harness reports both
halves of the evidence:

  --series   fetch the tests.yml slow lane's clean cost lines from GitHub and
             print the old figure's spread, its correlation with ``ref_ms``,
             and the slow/fast class split, with the interpreter and BLAS
             class factors. This re-derives the finding's baseline.
  (default)  run ``tests/replay.py --one`` N times on THIS box and print, per
             run, the loop CPU, both references and the old and new figures.

The old figure moves with the runner (--series shows the class factor it
imposed); the new figure should not (the local runs show its spread on one
box). Run from a worktree root:

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_loopnorm.py [N]
    python3 dev/audit/harnesses/r10_replay_loopnorm.py --series
"""
from __future__ import annotations

import json
import re
import statistics
import subprocess
import sys
from pathlib import Path


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
FIXTURE = ROOT / "tests" / "replay" / "synthetic-dhw-only.json"
MARK = "<<<replay-json>>>"
REPO = "tvofi/heatpump_optimizer"
COST_RE = re.compile(r"cost (\{.*\})")


# --- the nightly series (the finding's baseline) ----------------------------

def _gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True,
                          check=True).stdout


def nightly_rows() -> list[tuple[str, float, float]]:
    """(run id, ref_ms, clean loop_cpu_ratio) per timed tests.yml slow lane."""
    rows, fails, no_job = [], 0, 0
    for ev in ("schedule", "workflow_dispatch"):
        ids = _gh("run", "list", "--repo", REPO, "--workflow", "tests.yml",
                  "--event", ev, "--limit", "60", "--json", "databaseId,createdAt",
                  "--jq", '.[]|select(.createdAt>="2026-10-01")|.databaseId').split()
        for run in ids:
            try:
                job = _gh("api", f"repos/{REPO}/actions/runs/{run}/jobs?per_page=100",
                          "-q", '.jobs[]|select(.name=="slow")|.id').strip()
                if not job:      # a run with no slow lane: not a read failure
                    no_job += 1
                    continue
                log = _gh("api", "--allow-escape-sequences",
                          f"repos/{REPO}/actions/jobs/{job}/logs")
            except subprocess.CalledProcessError:
                fails += 1
                continue
            line = next((ln for ln in log.splitlines()
                         if "'cpu_ratio'" in ln and "doubled" not in ln), None)
            m = COST_RE.search(line) if line else None
            if not m:
                continue
            c = json.loads(m.group(1).replace("'", '"'))
            rows.append((run, c["ref_ms"], c["loop_cpu_ratio"]))
    print(f"RESULT series_rows={len(rows)} api_failures={fails} no_slow_lane={no_job}")
    return rows


def series_report() -> int:
    rows = nightly_rows()
    if len(rows) < 4:
        print("RESULT series spread=too-few-rows")
        return 1
    ref = [r for _, r, _ in rows]
    old = [o for _, _, o in rows]
    n = len(rows)
    mr, mo = statistics.mean(ref), statistics.mean(old)
    cov = sum((r - mr) * (o - mo) for r, o in zip(ref, old)) / n
    corr = cov / (statistics.pstdev(ref) * statistics.pstdev(old))
    print(f"RESULT old_spread=min{min(old):.4f}_max{max(old):.4f}_factor{max(old)/min(old):.3f}"
          f" corr_ref_ms={corr:.3f}")
    slow = [(r, o) for r, o in zip(ref, old) if r > 45]
    fast = [(r, o) for r, o in zip(ref, old) if r <= 45]

    def cls(rows_):
        rs = [r for r, _ in rows_]
        lc = [o * r for r, o in rows_]     # loop_cpu ms = old ratio x ref_ms
        return len(rows_), statistics.mean(rs), statistics.mean(lc), min(o for _, o in rows_), max(o for _, o in rows_)

    a, b = cls(slow), cls(fast)
    print(f"RESULT slow_class n={a[0]} ref_mean={a[1]:.2f} loop_cpu_mean={a[2]:.2f} "
          f"old={a[3]:.4f}..{a[4]:.4f}")
    print(f"RESULT fast_class n={b[0]} ref_mean={b[1]:.2f} loop_cpu_mean={b[2]:.2f} "
          f"old={b[3]:.4f}..{b[4]:.4f}")
    print(f"RESULT class_factors blas={a[1]/b[1]:.3f}x interpreter={a[2]/b[2]:.3f}x "
          f"old_figure_shift={(a[2]/a[1])/(b[2]/b[1]):.3f}x")
    return 0


# --- the local measurement (the new figure) ---------------------------------

def run(arm: str | None) -> dict:
    cmd = [sys.executable, str(ROOT / "tests" / "replay.py"), "--one", str(FIXTURE)]
    if arm:
        cmd += ["--inject-cost", arm]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith(MARK)), None)
    if line is None:
        raise SystemExit(f"arm {arm}: rc={proc.returncode}: {proc.stderr[-800:]}")
    return json.loads(line[len(MARK):])["cost"]


def local_report(n: int) -> int:
    old, new = [], []
    for i in range(n):
        c = run(None)
        loop_cpu = c["loop_cpu_ratio"] * c["loop_ref_ms"]     # ms, either ruler
        o = loop_cpu / c["ref_ms"]
        old.append(o)
        new.append(c["loop_cpu_ratio"])
        print(f"run[{i}] loop_cpu={loop_cpu:.2f}ms ref_ms={c['ref_ms']:.1f} "
              f"loop_ref_ms={c['loop_ref_ms']:.1f} old={o:.4f} new={c['loop_cpu_ratio']:.4f}")
    print(f"RESULT local new=min{min(new):.4f}_max{max(new):.4f}_factor{max(new)/min(new):.3f} "
          f"median{statistics.median(new):.4f}")
    print(f"RESULT local old=min{min(old):.4f}_max{max(old):.4f}_factor{max(old)/min(old):.3f} "
          f"median{statistics.median(old):.4f}")
    return 0


def main() -> int:
    if "--series" in sys.argv:
        return series_report()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    return local_report(n)


if __name__ == "__main__":
    sys.exit(main())
