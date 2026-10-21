#!/usr/bin/env python3
"""The replay loop figure's ruler: the BLAS solve against a pure-Python one (#2270).

``loop_cpu_ratio`` was the coordinator cycle's loop-thread CPU over
``tests/stress.py``'s ``reference_solve``, a BLAS-bound solve. The measure is
interpreter-bound, so over the nightly series the figure tracked the runner
CLASS, not the code: ``corr(loop_cpu_ratio, ref_ms) = -0.94``, and it read
0.244-0.405 (1.66x). #2270's fix normalises it by a fixed pure-Python workload
(``tests/replay.py``'s ``reference_loop``) instead. This harness reports both
halves of the evidence:

  --series   fetch the tests.yml slow lane's clean cost lines from GitHub (the
             scheduled runs, and dispatches on main -- a feature branch's
             dispatch is not the series a cap gates) and
             print, split by ruler era: the BLAS-ruler figure's spread on the
             rows before #2339 changed the ruler, the pure-Python figure's
             spread on the rows after it, the same rows' BLAS figure derived
             for comparison, and each era's slow/fast class split. The pre era
             re-derives the finding's baseline; the post era is the series the
             recorded cap has to hold.
  (default)  run ``tests/replay.py --one`` N times on THIS box and print, per
             run, the loop CPU, both references and the old and new figures.

The old figure moves with the runner (--series shows the class factor it
imposed). The new figure cancels most of that, not all of it: its numerator is
not all interpreter work, and the post era carries the residual. Run from a
worktree root:

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_loopnorm.py [N]
    python3 dev/audit/harnesses/r10_replay_loopnorm.py --series
    python3 dev/audit/harnesses/r10_replay_loopnorm.py --self-test
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


def nightly_rows() -> list[dict]:
    """One row per timed tests.yml slow lane's clean cost line, on main.

    ``loop_ref_ms`` is what separates the two ruler eras: #2339 changed the
    figure normalised into ``loop_cpu_ratio`` from the BLAS solve to this
    pure-Python reference, and added the ruler's own time beside it under the
    same field name. Before it the field is the old figure; after it the field
    is the new one. The key is the printed field, never a date.

    Scope is the default branch: a scheduled run is main by construction, and
    a dispatch on a ``fix/`` branch measures code that has not merged, so it
    is not the series a recorded cap has to hold.
    """
    rows, fails, no_job, no_logs, off_main = [], 0, 0, 0, 0
    first_fail = ""
    for ev in ("schedule", "workflow_dispatch"):
        ids = _gh("run", "list", "--repo", REPO, "--workflow", "tests.yml",
                  "--event", ev, "--limit", "60",
                  "--json", "databaseId,createdAt,headBranch",
                  "--jq", r'.[]|select(.createdAt>="2026-10-01")|'
                          r'"\(.databaseId) \(.headBranch)"').splitlines()
        for entry in ids:
            run, _, branch = entry.partition(" ")
            if branch != "main":
                off_main += 1
                continue
            try:
                job = _gh("api", f"repos/{REPO}/actions/runs/{run}/jobs?per_page=100",
                          "-q", '.jobs[]|select(.name=="slow")|.id').strip()
                if not job:      # a run with no slow lane: not a read failure
                    no_job += 1
                    continue
                log = _gh("api", "--allow-escape-sequences",
                          f"repos/{REPO}/actions/jobs/{job}/logs")
            except subprocess.CalledProcessError as err:
                # A cancelled or superseded job has no log: the API answers
                # 404. That is a run with no reading, not a failed read.
                if "HTTP 404" in (err.stderr or ""):
                    no_logs += 1
                else:
                    fails += 1
                    first_fail = first_fail or (err.stderr or "").strip()[:200]
                continue
            line = next((ln for ln in log.splitlines()
                         if "'cpu_ratio'" in ln and "doubled" not in ln), None)
            m = COST_RE.search(line) if line else None
            if not m:
                continue
            c = json.loads(m.group(1).replace("'", '"'))
            rows.append({"run": run, "ref_ms": c["ref_ms"],
                         "loop_ref_ms": c.get("loop_ref_ms"),
                         "loop_cpu_ratio": c["loop_cpu_ratio"]})
    print(f"RESULT series_rows={len(rows)} api_failures={fails} no_slow_lane={no_job} "
          f"no_logs={no_logs} off_main={off_main}"
          + (f" first_failure={first_fail!r}" if first_fail else ""))
    return rows


def figures(row: dict) -> tuple[float | None, float | None, float]:
    """(old, new, loop_cpu_ms) for one slow-lane row.

    ``old`` is the loop-thread CPU over the BLAS solve's ``ref_ms``; ``new`` is
    over the pure-Python ruler's own time. ``loop_cpu_ms`` is the cycle's loop
    CPU either way: the field itself times ``ref_ms`` before #2339 and
    ``loop_ref_ms`` after it.
    """
    if row["loop_ref_ms"] is None:        # before #2339: the field is ``old``
        return row["loop_cpu_ratio"], None, row["loop_cpu_ratio"] * row["ref_ms"]
    loop_cpu_ms = row["loop_cpu_ratio"] * row["loop_ref_ms"]
    return loop_cpu_ms / row["ref_ms"], row["loop_cpu_ratio"], loop_cpu_ms


def _spread(values: list[float]) -> str:
    return (f"min{min(values):.4f}_max{max(values):.4f}_"
            f"factor{max(values) / min(values):.3f}")


def _corr(a: list[float], b: list[float]) -> float:
    if len(a) < 2 or not statistics.pstdev(a) or not statistics.pstdev(b):
        return float("nan")
    ma, mb = statistics.mean(a), statistics.mean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)
    return cov / (statistics.pstdev(a) * statistics.pstdev(b))


def _class_line(name: str, rows: list[dict], key: str) -> None:
    """One era's slow/fast split of ``key`` (``old`` or ``new``), with the
    runner's own factors: the BLAS solve's time and the loop CPU's."""
    for cls, keep in (("slow", lambda r: r["ref_ms"] > 45),
                      ("fast", lambda r: r["ref_ms"] <= 45)):
        got = [r for r in rows if keep(r)]
        if not got:
            print(f"RESULT {name}_era_{key}_{cls}_class n=0")
            continue
        old, new, loop_cpu = zip(*(figures(r) for r in got))
        vals = [v for v in (old if key == "old" else new) if v is not None]
        print(f"RESULT {name}_era_{key}_{cls}_class n={len(got)} "
              f"ref_mean={statistics.mean(r['ref_ms'] for r in got):.2f} "
              f"loop_cpu_mean={statistics.mean(loop_cpu):.2f} "
              f"{key}={min(vals):.4f}..{max(vals):.4f}")


def series_report() -> int:
    rows = nightly_rows()
    pre = [r for r in rows if r["loop_ref_ms"] is None]
    post = [r for r in rows if r["loop_ref_ms"] is not None]
    print(f"RESULT era_rows pre={len(pre)} post={len(post)}")
    if len(pre) < 2 or len(post) < 2:
        print("RESULT series spread=too-few-rows")
        return 1
    old_pre = [figures(r)[0] for r in pre]
    new_post = [r["loop_cpu_ratio"] for r in post]
    old_post = [figures(r)[0] for r in post]
    print(f"RESULT old_pre_spread={_spread(old_pre)} (BLAS ruler, the field)")
    print(f"RESULT new_post_spread={_spread(new_post)} "
          f"median={statistics.median(new_post):.4f} (pure-Python ruler, the field)")
    print(f"RESULT old_post_spread={_spread(old_post)} (BLAS figure on the same rows)")
    print(f"RESULT corr_new_post_ref_ms={_corr([r['ref_ms'] for r in post], new_post):.3f} "
          f"n={len(post)}")
    _class_line("pre", pre, "old")
    for key in ("old", "new"):
        _class_line("post", post, key)
    worst = max(post, key=lambda r: r["loop_cpu_ratio"])
    _, _, loop_cpu_ms = figures(worst)
    print(f"RESULT worst_post run={worst['run']} new={worst['loop_cpu_ratio']:.4f} "
          f"loop_cpu_ms={loop_cpu_ms:.2f} loop_ref_ms={worst['loop_ref_ms']:.2f} "
          f"ref_ms={worst['ref_ms']:.2f}")
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


def self_test() -> int:
    """The era key and the derivation, on rows shaped exactly as the lane prints.

    A row before #2339 prints the BLAS-normalised figure and no ruler time; a
    row after it prints the pure-Python figure and ``loop_ref_ms``. The check
    pins both readings of ``figures()``: the old figure is the field before
    the change and the loop CPU over ``ref_ms`` after it.
    """
    pre = {"run": "0", "ref_ms": 50.0, "loop_ref_ms": None, "loop_cpu_ratio": 0.30}
    post = {"run": "1", "ref_ms": 20.0, "loop_ref_ms": 100.0, "loop_cpu_ratio": 0.09}
    o_pre, n_pre, c_pre = figures(pre)
    o_post, n_post, c_post = figures(post)
    checks = [
        ("pre: the field is the old figure", (o_pre, n_pre) == (0.30, None)),
        ("pre: loop CPU is the field times ref_ms", abs(c_pre - 15.0) < 1e-9),
        ("post: the field is the new figure", n_post == 0.09),
        ("post: loop CPU is the new field times loop_ref_ms", abs(c_post - 9.0) < 1e-9),
        ("post: the old figure is derived", abs(o_post - 0.45) < 1e-9),
        ("the era key is the ruler time, not a date", pre["loop_ref_ms"] is None
         and post["loop_ref_ms"] is not None),
        ("the spreads separate", _spread([0.30]) == "min0.3000_max0.3000_factor1.000"),
    ]
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"  {'ok' if ok else 'FAIL'}: {name}")
    print(f"RESULT self_test checks={len(checks)} failed={len(failed)}")
    return 1 if failed else 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    if "--series" in sys.argv:
        return series_report()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    return local_report(n)


if __name__ == "__main__":
    sys.exit(main())
