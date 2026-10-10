#!/usr/bin/env python3
"""Mutate-then-revert through miniec.py: the round-5 kill claims, re-taken.

For each target site: apply the canonical mutant (mutation_table.py's own
inventory) in MY private worktree, run the early-cut-off block (miniec.py),
record the FAIL set; restore the file, run the clean block again, and diff.
new != {} is KILLED; the revert arm is the clean run that must NOT name the
check. Nothing here is the fixer's harness.

usage: mm.py ROOT OUTFILE line:kind [line:kind ...]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUTFILE = Path(sys.argv[2])
EC = "custom_components/heatpump_optimizer/early_cutoff.py"
MINIEC = str(OUTFILE.parent / "miniec.py")
PY = sys.executable
TARGETS = []
for a in sys.argv[3:]:
    ln, kind = a.split(":")
    TARGETS.append((int(ln), kind))

sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402


def fails(stdout: str) -> set[str]:
    return {ln.strip()[5:].strip() for ln in stdout.splitlines() if ln.strip().startswith("FAIL ")}


def run(tree: Path) -> tuple[set[str], str]:
    p = subprocess.run([str(PY), MINIEC, "tests/features.py"], cwd=str(tree),
                       capture_output=True, text=True,
                       env={**os.environ, "PYTHONPATH": "tests/hastub"}, timeout=900)
    return fails(p.stdout), p.stdout


def main() -> int:
    inv = [s for s in mt.inventory([ROOT / EC]) if s["file"].endswith("early_cutoff.py")]
    seen, sites = set(), []
    for s in inv:
        if (s["line"], s["kind"]) in set(TARGETS) and (s["line"], s["kind"], s["new"]) not in seen:
            seen.add((s["line"], s["kind"], s["new"]))
            sites.append(s)

    tmp = OUTFILE.parent / "mmtree"
    subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(tmp)],
                   capture_output=True)
    r = subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "-f", "--detach", str(tmp),
                        "HEAD"], capture_output=True, text=True)
    if r.returncode != 0:
        print("worktree:", r.stderr[:300])
        return 1
    ec = tmp / EC
    res = {}
    clean_fails, clean_out = run(tmp)
    print(f"clean block: {len(clean_fails)} FAIL -> {sorted(clean_fails)}", flush=True)
    (OUTFILE.parent / "miniec_clean.out").write_text(clean_out)

    for s in sites:
        key = f"{s['line']} {s['kind']} {s['new'][-22:]}"
        src = ec.read_text().splitlines(keepends=True)
        idx = s["line"] - 1
        assert src[idx].rstrip("\n") == s["old"], (s["line"], repr(src[idx]))
        src[idx] = s["new"] + "\n"
        t0 = time.time()
        ec.write_text("".join(src))
        mut, mut_out = run(tmp)
        subprocess.run(["git", "-C", str(tmp), "checkout", "--", EC], capture_output=True)
        back, back_out = run(tmp)  # the revert-to-green arm
        new = sorted(mut - back)
        res[key] = {"line": s["line"], "kind": s["kind"], "new": s["new"],
                    "mutant_fails": sorted(mut), "revert_fails": sorted(back),
                    "new_fails": new, "verdict": "KILLED" if new else "SURVIVES",
                    "secs": round(time.time() - t0, 1)}
        print(f"[{s['line']}/{s['kind']}] {res[key]['verdict']} new={new} "
              f"(revert {len(back)} FAIL) ({res[key]['secs']}s)", flush=True)
        (OUTFILE.parent / f"mm_{s['line']}_{s['kind']}_{abs(hash(s['new']))%9999}.out").write_text(mut_out)

    OUTFILE.write_text(json.dumps({"head": "HEAD", "clean": sorted(clean_fails), "results": res}, indent=2))
    k = sum(1 for v in res.values() if v["verdict"] == "KILLED")
    surv = [x for x, v in res.items() if v["verdict"] != "KILLED"]
    print(f"\ntotal {len(res)} killed {k} not-killed {len(surv)}", flush=True)
    for x in surv:
        print("  NOT KILLED:", x, flush=True)
    subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(tmp)],
                   capture_output=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
