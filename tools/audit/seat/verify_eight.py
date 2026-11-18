#!/usr/bin/env python3
"""Measure, per early_cutoff.py inventory site, whether tests/features.py kills
the mutant -- the local stand-in for `mutation_table.py --pin-killed` when
features.py's baseline is red on the seat (the macOS BLAS float R9-F2.1 P3, so
the tool returns MUTATION TABLE INCONCLUSIVE here). For each target site it
applies that one site's mutation in a private git worktree (so the run uses the
tree's own features.py), runs tests/features.py, and diffs the FAIL set against
the clean baseline {R9-F2.1 P3}: a new deterministic early-cutoff FAIL == KILLED,
an unchanged set == SURVIVES (an equivalent or a genuine coverage gap).

    python3 tools/audit/seat/verify_eight.py [HEAD] [site ...]

With no sites, the eight the round-4 drive found features.py left unkilled are
driven (early_cutoff.py:201/215/259/266/275/293 GUARD_OFF|CMP_BOUND|RETURN_DEL
and :284 BOOLOP|CMP_BOUND). ROOT is the current directory; HEAD defaults to the
working tree's HEAD. Prints one line per (site, kind) and a summary; writes
nothing to the tree.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

PY = Path(sys.executable)
BASELINE = "R9-F2.1 P3"
DEFAULT_TARGETS = [(201, "GUARD_OFF"), (215, "GUARD_OFF"), (259, "GUARD_OFF"),
                   (266, "CMP_BOUND"), (275, "CMP_BOUND"), (275, "RETURN_DEL"),
                   (284, "BOOLOP"), (284, "CMP_BOUND"), (293, "GUARD_OFF")]
EC = "custom_components/heatpump_optimizer/early_cutoff.py"


def main(argv: list[str]) -> int:
    head = argv[0] if argv and not argv[0].isdigit() else "HEAD"
    targets = []
    for a in argv:
        if " " in a:
            ln, kind = a.split()
            targets.append((int(ln), kind))
    if not targets:
        targets = DEFAULT_TARGETS

    sites = [s for s in mt.inventory([ROOT / EC])
             if (s["line"], s["kind"]) in set(targets) and s["file"].endswith("early_cutoff.py")]
    if not sites:
        print("no matching inventory sites (pass HEAD then 'LINE KIND' args)")
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="verify_eight."))
    trees = []
    for i in range(3):
        t = tmp / f"wt{i}"
        r = subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "-f", "--detach", str(t), head],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("worktree add failed:", r.stderr.strip()[:200])
            return 1
        trees.append(t)

    free: queue.Queue = queue.Queue()
    for t in trees:
        free.put(t)
    res: dict = {}
    lock = threading.Lock()
    q: queue.Queue = queue.Queue()
    for s in sites:
        q.put(s)

    def worker() -> None:
        while True:
            try:
                s = q.get_nowait()
            except queue.Empty:
                return
            tree = free.get()
            ec = Path(tree) / EC
            lines = ec.read_text().splitlines(keepends=True)
            idx = s["line"] - 1
            assert lines[idx].rstrip("\n") == s["old"], (s["line"], s["kind"], repr(lines[idx]))
            lines[idx] = s["new"] + "\n"
            ec.write_text("".join(lines))
            try:
                p = subprocess.run([str(PY), "tests/features.py"], cwd=str(tree),
                                   capture_output=True, text=True,
                                   env={**os.environ, "PYTHONPATH": "tests/hastub"}, timeout=2400)
                real = [ln.strip() for ln in p.stdout.splitlines()
                        if ln.strip().startswith("FAIL ") and BASELINE not in ln]
            except Exception as exc:  # noqa: BLE001
                real = [f"RUNERROR {exc}"]
            finally:
                subprocess.run(["git", "-C", str(tree), "checkout", "--", EC],
                               capture_output=True)
                free.put(tree)
            res[(s["line"], s["kind"], s["new"])] = (
                "KILLED -- " + "; ".join(real)) if real else "SURVIVES"
            print(f"[{s['line']}/{s['kind']}] new_real_fails={len(real)} :: "
                  f"{res[(s['line'], s['kind'], s['new'])][:110]}", flush=True)
            q.task_done()

    th = [threading.Thread(target=worker, daemon=True) for _ in trees]
    for t in th:
        t.start()
    q.join()
    for t in th:
        t.join()
    for t in trees:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(t)],
                       capture_output=True)
    surv = [k for k, v in res.items() if v == "SURVIVES"]
    print(f"\ntotal {len(res)} killed {len(res) - len(surv)} survivors {len(surv)}")
    for k in surv:
        print("  SURVIVES:", k[0], k[1])
    print(json.dumps({f"{k[0]} {k[1]}": v for k, v in res.items()}))
    return 0 if not surv else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
