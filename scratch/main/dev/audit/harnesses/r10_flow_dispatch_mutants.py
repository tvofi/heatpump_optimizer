#!/usr/bin/env python3
"""R10-FLOW-DISPATCH: each predicate of cloud_dispatch.py's group path dies alone.

Written by the R10-FLOW-DISPATCH fixer, round 2, after the round-1 review found
two survivors (head-ignored, privacy-off) that 42 green checks hid; round 3
added the four the round-2 review found (explicit-roster-ref-ignored,
cli-head-dropped, cli-roster-ref-dropped, fetch-skipped); round 4 added
the three the round-3 review found (cli-role-fixed, cli-pr-dropped,
cli-nonce-dropped) and the rest of the --group call's inputs (cli-group-fixed,
cli-model-fixed, cli-overlay-dropped); round 5 added the flag table's arms
(group-refusal-off, env-id-forwarded-as-none, flag-unlisted) and cli-pr-truncated. Each
mutant is a one-occurrence replacement in tools/audit/seat/cloud_dispatch.py;
it is applied alone, `cloud_dispatch.py --self-test` run, and the file
restored byte for byte. The drive refuses a dirty file and aborts on a
pattern that is not found exactly once. Metric, one line per mutant:

  RESULT mutant=<name> failed=<n> verdict=killed|SURVIVED|CRASHED
  RESULT mutants=<n> survived=<n>

failed=-1 is a self-test that died before its summary line (CRASHED: it is
killed, but no check names what broke). Expected at the fixing head:
survived=0. Null control: M0, the file unmutated, must print failed=0.

    python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py [NAME ...]
"""
from __future__ import annotations

import re
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
REL = "tools/audit/seat/cloud_dispatch.py"
F = ROOT / REL

MUTANTS = [
    ("M0", None, None),
    ("tree-skip", "    if tip and _git(repo_dir, \"rev-parse\"", "    if False and _git(repo_dir, \"rev-parse\""),
    ("brief-drop", 'brief=group.get("brief") or ""', 'brief=""'),
    ("parent-drop", '*(["-p", tip[0]] if tip else [])', "*[]"),
    ("nonce-altered", "pr=pr, topic=topic, nonce=nonce,", "pr=pr, topic=topic, nonce=nonce + \"0\","),
    ("topic-to-id", 'ref = f"{DISPATCH_NS}/{role}-{topic}"', 'ref = f"{DISPATCH_NS}/{role}-{group_id}"'),
    ("render-host-off", "    m = HOME.search(json.dumps(payload))", "    m = None"),
    ("privacy-off", "    if why:\n        raise Refusal(f\"the dispatch ref", "    if False:\n        raise Refusal(f\"the dispatch ref"),
    ("head-ignored", 'head or _git(repo_dir, "rev-parse", f"{HEAD_REF}', '_git(repo_dir, "rev-parse", f"{HEAD_REF}'),
    ("prompt-wrong", '"PROMPT.md": payload["job_config"]', '"PROMPT.md": "" and payload["job_config"]'),
    ("roster-repo-ignored", 'repo=roster.get("repo") or known["repo"]', 'repo=known["repo"]'),
    ("roster-ref-main", "roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)",
     "roster_ref = roster_ref or roster_lib.MAIN_REF"),
    ("head-from-roster-ref", 'f"{HEAD_REF}^{{commit}}"', 'f"{roster_ref}^{{commit}}"'),
    ("reviewer-head-off", 'if role == "reviewer" and not head:', "if False:"),
    ("explicit-roster-ref-ignored", "roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)",
     "roster_ref = roster_lib.reader_ref(repo_dir, None)"),
    ("cli-head-dropped", 'head=args.head or ""', 'head=""'),
    ("cli-roster-ref-dropped", "roster_ref=args.roster_ref,", "roster_ref=None,"),
    ("fetch-skipped", '        _git(repo_dir, "fetch", "-q", "origin", f"refs/heads/{ref}")', "        pass"),
    ("cli-role-fixed", "print(dispatch_group(args.role,", 'print(dispatch_group("fixer",'),
    ("cli-pr-dropped", 'head=args.head or "", pr=args.pr,', 'head=args.head or "", pr="",'),
    ("cli-nonce-dropped", "nonce=args.nonce, overlay=args.overlay))", 'nonce="", overlay=args.overlay))'),
    ("cli-group-fixed", "print(dispatch_group(args.role, args.group,", 'print(dispatch_group(args.role, "R10-X",'),
    ("cli-model-fixed", "args.group, args.model, roster_ref", 'args.group, "m-1", roster_ref'),
    ("cli-overlay-dropped", "nonce=args.nonce, overlay=args.overlay))", "nonce=args.nonce, overlay=None))"),
    ("group-refusal-off", "if why and getattr(args, dest)", "if False and getattr(args, dest)"),
    ("env-id-forwarded-as-none", '"env_id": "the environment id', '"env_id": None and "the environment id'),
    ("flag-unlisted", '    ap.add_argument("--out")\n    return ap', '    ap.add_argument("--out")\n    ap.add_argument("--extra")\n    return ap'),
    ("cli-pr-truncated", 'head=args.head or "", pr=args.pr,', "head=args.head or \"\", pr=(args.pr or '')[:1],"),
]
SUMMARY = re.compile(r"cloud_dispatch self-test: (\d+) checks, (\d+) failed")


def run() -> tuple[int, list[str]]:
    r = subprocess.run([sys.executable, "-I", str(F), "--self-test"], capture_output=True, text=True, cwd=ROOT)
    m = SUMMARY.search(r.stdout)
    return (int(m.group(2)) if m else -1), [ln.strip() for ln in r.stdout.splitlines() if "FAIL" in ln]


def main(names: list[str]) -> int:
    if subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", REL]).returncode:
        print(f"refused: {REL} has uncommitted changes")
        return 2
    orig = F.read_text()
    survived = 0
    picked = [m for m in MUTANTS if not names or m[0] in names]
    try:
        for name, old, new in picked:
            if old is not None:
                if orig.count(old) != 1:
                    print(f"abort: {name}'s pattern occurs {orig.count(old)} times")
                    return 2
                F.write_text(orig.replace(old, new))
            failed, fails = run()
            F.write_text(orig)
            if name == "M0":
                verdict = "null-ok" if failed == 0 else "NULL-FAILED"
            else:
                verdict = "killed" if failed > 0 else "CRASHED" if failed < 0 else "SURVIVED"
                survived += verdict == "SURVIVED"
            print(f"RESULT mutant={name} failed={failed} verdict={verdict}")
            for ln in fails:
                print(f"    {ln}")
    finally:
        F.write_text(orig)
    print(f"RESULT mutants={sum(1 for m in picked if m[1] is not None)} survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
