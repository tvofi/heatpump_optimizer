#!/usr/bin/env python3
"""R10-ROSTER-OPS: the roster sync's base-vs-head control (state_docs.py beat --apply).

    python3 dev/audit/harnesses/r10_roster_sync_base.py [--base DIR] [--head DIR]

The defect: `resume.stage` is a human claim nothing compared with the refs,
so a group whose pull request merged stayed `in-progress`. This runs the
same fixture, offline, against two trees:

  base  the merge base with origin/main. `beat --apply` does not exist there
        (argparse refuses the flag, rc 2) and the plain beat has no
        derivation, so the merged group stays `in-progress`: the property
        "after a sync the merged group is done" FAILS at the base.
  head  this worktree. `beat --once --apply` derives `done` at the merge
        commit; the deferred group's merged pull request does not move it,
        and a plain beat without --apply still derives nothing (the null
        control that `--apply` is the switch).

The fixture is built twice in throwaway repositories (`tests/throwaway_git.py`),
so the two runs share no state. `--base` names an already-exported tree; the
default exports the merge base with `git archive`. No network, no gh: the
pull-request read is a recorded fixture.

Printed:
  RESULT base_apply_rc=2 head_apply_rc=0
  RESULT base_stage=in-progress head_stage=done
  RESULT head_noapply_stage=in-progress
  RESULT base_deferred=deferred head_deferred=deferred
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
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
sys.path.insert(0, str(ROOT / "tests"))
from throwaway_git import (throwaway_git_clone, throwaway_git_environ,  # noqa: E402
                           throwaway_git_init)

ROSTER = "dev/programme/rosters/wave-r9-groups.json"
BRANCH = "handoff/audit-r9-roster"
STATE_REF = "handoff/audit-r9-plan"
MERGED_SHA = "f" * 40


def g(*args, cwd=None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"git {' '.join(args)}: {(r.stderr or r.stdout)[:300]}")
    return r.stdout.strip()


def export_base(dest: Path) -> None:
    mb = g("-C", str(ROOT), "merge-base", "origin/main", "HEAD")
    dest.mkdir(parents=True)
    ar = subprocess.Popen(["git", "-C", str(ROOT), "archive", mb],
                          stdout=subprocess.PIPE)
    tar = subprocess.Popen(["tar", "-x", "-C", str(dest)], stdin=ar.stdout)
    ar.stdout.close()
    if tar.wait() or ar.wait():
        raise SystemExit("exporting the merge base failed")


def fixture(root: Path) -> tuple[Path, Path, Path, Path]:
    """(bare origin, driver clone, roster branch, pr fixture) for one run."""
    seed = root / "seed"
    seed.mkdir(parents=True)
    (seed / "tools" / "policy").mkdir(parents=True)
    (seed / "tools/policy/brief_lint.mjs").write_text(
        "console.log('TOTAL: 0 error(s) across 1 file(s)');\n", encoding="utf-8")
    roster = {"repo": "fixture/state", "session": "r9-sync", "groups": [
        {"group": "R9-MERGED", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "fixture merged.",
         "resume": {"stage": "in-progress", "branch": "handoff/r9-merged"}},
        {"group": "R9-DEFER", "lane": "L1", "issues": [], "fixes": [],
         "after": [], "brief": "fixture deferred.",
         "resume": {"stage": "deferred", "branch": "handoff/r9-defer"}}]}
    (seed / ROSTER).parent.mkdir(parents=True, exist_ok=True)
    (seed / ROSTER).write_text(json.dumps(roster, indent=1), encoding="utf-8")
    throwaway_git_init(seed, "-q", "-b", "main")
    g("-C", str(seed), "add", "-A")
    g("-C", str(seed), "commit", "-q", "-m", "fixture roster")
    g("-C", str(seed), "branch", BRANCH)
    bare = root / "origin.git"
    throwaway_git_clone(seed, bare, "-q", "--bare")
    drv = root / "drv"
    throwaway_git_clone(bare, drv, "-q")
    prs = root / "prs.json"
    prs.write_text(json.dumps([
        {"number": 41, "state": "MERGED", "head": "handoff/r9-merged",
         "mergeCommit": {"oid": MERGED_SHA}, "body": "## Friction\n\n- none\n"},
        {"number": 42, "state": "MERGED", "head": "handoff/r9-defer",
         "mergeCommit": {"oid": "0" * 40}, "body": "## Friction\n\n- none\n"}],
    ), encoding="utf-8")
    return bare, drv, prs, root / "out"


def run(tree: Path, bare: Path, drv: Path, prs: Path, *extra) -> tuple[int, str]:
    out = Path(drv).parent / "out" / "log.txt"
    out.parent.mkdir(exist_ok=True)
    r = subprocess.run(
        [sys.executable, str(tree / "tools/audit/seat/state_docs.py"), "beat",
         "--checkout", str(drv), "--repo", "fixture/state",
         "--roster-ref", f"origin/{BRANCH}", "--state-ref", STATE_REF,
         "--pr-state", str(prs), "--mirror", str(out.parent / "mirror"),
         "--tip-file", str(out.parent / "tip"), "--once", *extra],
        capture_output=True, text=True, timeout=600)
    out.write_text((r.stdout + r.stderr)[-4000:], encoding="utf-8")
    return r.returncode, out.read_text(encoding="utf-8")


def stages(bare: Path) -> dict:
    shown = g("-C", str(bare), "show", f"refs/heads/{BRANCH}:{ROSTER}")
    return {x["group"]: (x.get("resume") or {}).get("stage")
            for x in json.loads(shown)["groups"]}


def main() -> int:
    args = sys.argv[1:]
    base = Path(args[args.index("--base") + 1]) if "--base" in args else None
    head = Path(args[args.index("--head") + 1]) if "--head" in args else ROOT
    with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        if base is None:
            base = tmp / "base"
            export_base(base)
        out = {}
        for label, tree, extra in (("base", base, ("--apply",)),
                                   ("head", head, ("--apply",)),
                                   ("head_noapply", head, ())):
            bare, drv, prs, _ = fixture(tmp / label)
            rc, log = run(tree, bare, drv, prs, *extra)
            out[f"{label}_rc"] = rc
            out[f"{label}_stage"] = stages(bare)["R9-MERGED"]
            out[f"{label}_deferred"] = stages(bare)["R9-DEFER"]
            out[f"{label}_log"] = log
        print(f"RESULT base_apply_rc={out['base_rc']} "
              f"head_apply_rc={out['head_rc']}")
        print(f"RESULT base_stage={out['base_stage']} "
              f"head_stage={out['head_stage']}")
        print(f"RESULT head_noapply_stage={out['head_noapply_stage']}")
        print(f"RESULT base_deferred={out['base_deferred']} "
              f"head_deferred={out['head_deferred']}")
        ok = (out["base_stage"] == "in-progress" and out["head_stage"] == "done"
              and out["head_noapply_stage"] == "in-progress"
              and out["head_deferred"] == "deferred"
              and out["base_deferred"] == "deferred" and out["head_rc"] == 0)
        print("RESULT control=" + ("PASS" if ok else "FAIL"))
        if not ok:
            for k in ("base_log", "head_log", "head_noapply_log"):
                print(f"--- {k} ---")
                print(out[k][-1200:])
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
