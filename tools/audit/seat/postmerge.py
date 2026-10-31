#!/usr/bin/env python3
"""After a merge: the bookkeeping nudge.md step 12 used to hand an agent.

    python3 tools/audit/seat/postmerge.py [--repo O/R] [--state-dir D] [--dry-run] [--retry] <PR>
    python3 tools/audit/seat/postmerge.py --self-test

Both merge paths (`merge_pr.sh`, and `merge_train.py`'s landing) call it once
the merge is confirmed. It runs, in order, and a failure in any is printed as
`OWED <step>: <why>` and never undoes the merge or stops the next step:

  record   `record_beat.py`: one #201 line from the fixed template, posted by
           `tools/pr/gh_comment.py` with a byte-identical read-back.
  stage    `roster_sync.py --apply` derives the group's `done` stage from the
           merged pull request. A refused sync prints `set-stage owed <GROUP>
           <merge sha>`, the group resolved from the roster (`record_beat.
           resolve_group`) or `no-group <merge sha>`, never guessed.
  docs     `state_docs.py --push`.
  main     `merge_train.py classify <merge sha> --main`: main's own suite
           state, the one rule the train and the sweep read (no third). RED or
           unreadable is owed; WAIT (the push's checks still running) is not.

An owed step is opened in the ledger as the event `postmerge-owed`
(`ledger.py open postmerge-owed <pr> <merge-sha40> <why>`); `--retry` after a
fully clean run closes it (`ledger.py close postmerge-owed ... <how>`), the
only closer that kind has. Exit 0 when nothing is owed, else 1, after the
lines. `--dry-run` prints the exact comment and every command and runs none.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

SEAT = Path(__file__).resolve().parent
sys.path.insert(0, str(SEAT))
import record_beat as rb  # noqa: E402

ROOT = rb.ROOT
PY = [sys.executable, "-I"]


def steps(pr: int, repo: str, state_dir: Path, sha: str, group: str) -> "list[tuple[str, list, bool]]":
    """(name, argv, mutating): the commands after the comment, in order."""
    seat = str(SEAT)
    return [
        ("stage", [*PY, f"{seat}/roster_sync.py", "--repo", repo, "--apply"], True),
        ("docs", [*PY, f"{seat}/state_docs.py", "--repo", repo, "--push"], True),
        ("main", [*PY, f"{seat}/merge_train.py", "classify", sha, "--repo", repo, "--main"], False),
    ]


def postmerge(pr: int, repo: str, state_dir: Path, dry: bool, retry: bool = False,
              run=rb.sh, out=print, roster=None) -> int:
    owed: "list[tuple[str, str]]" = []
    try:
        f = rb.facts(pr, repo, run)
    except rb.Owed as e:
        out(f"OWED record: {e}")
        return 1  # no full sha: nothing below can name its subject
    sha = f["sha"]
    group = rb.resolve_group(roster if roster is not None else rb.load_roster(run), f["branch"], pr)
    try:
        rb.record(pr, repo, state_dir, f, group, dry, run, out)
    except rb.Owed as e:
        owed.append(("record", str(e)))
    for name, argv, mutating in steps(pr, repo, state_dir, sha, group):
        if dry:
            out(f"DRY-RUN {name}: " + " ".join(argv))
            continue
        code, o = run(argv)
        last = o.strip().splitlines()[-1][:160] if o.strip() else "no output"
        if name == "main":
            out(f"main {last}")
            if code == 3:  # WAIT: the push's own checks are still running
                continue
        if code != 0:
            owed.append((name, f"rc {code}: {last}"))
            if name == "stage":
                out(f"set-stage owed {group} {sha}" if group != rb.NO_GROUP else f"set-stage owed no-group {sha}")
    for name, why in owed:
        out(f"OWED {name}: {why}")
    ledger = [*PY, f"{SEAT}/ledger.py"]
    if owed and not dry:
        run([*ledger, "open", "postmerge-owed", str(pr), sha, "; ".join(f"{n}: {w}" for n, w in owed)[:300]])
    elif not owed and retry and not dry:
        run([*ledger, "close", "postmerge-owed", str(pr), sha, "a clean postmerge rerun"])
    if not owed:
        out(f"postmerge #{pr} {sha}: nothing owed")
    return 1 if owed else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pr", nargs="?", type=int)
    ap.add_argument("--repo", default=rb.DEFAULT_REPO)
    ap.add_argument("--state-dir", default=os.environ.get("HPO_STATE_DIR")
                    or str(Path.home() / ".local/state/hpo"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retry", action="store_true", help="a rerun of an owed merge: a clean run closes the event")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.pr is None:
        ap.error("give the merged <PR>")
    return postmerge(a.pr, a.repo, Path(a.state_dir), a.dry_run, a.retry)


def self_test() -> int:
    import json
    import tempfile
    fails, n = [], [0]

    def check(name, ok, got=""):
        n[0] += 1
        if not ok:
            fails.append(f"{name} (got: {got})")
            print("FAIL", fails[-1], flush=True)

    full = "c" * 40
    roster = {"groups": [{"group": "R10-X", "resume": {"branch": "fix/r10-x"}}]}

    def fake(rc=None):
        rc = rc or {}
        log = []

        def run(argv, stdin=None, cwd=None):
            log.append(list(argv))
            j = " ".join(map(str, argv))
            if argv[:3] == ["gh", "pr", "view"]:
                return 0, json.dumps({"state": "MERGED", "mergeCommit": {"oid": full},
                                      "headRefName": "fix/r10-x",
                                      "closingIssuesReferences": [{"number": 5}]})
            if "rev-parse" in j:
                return 0, full + "\n"
            for key in ("gh_comment.py", "roster_sync.py", "state_docs.py", "classify", "ledger.py"):
                if key in j:
                    return rc.get(key, 0), f"{key} said" + (" REFUSED" if rc.get(key) else "")
            return 0, ""
        return run, log

    def go(rc=None, dry=False, retry=False):
        run, log = fake(rc)
        lines = []
        with tempfile.TemporaryDirectory() as td:
            code = postmerge(7, rb.DEFAULT_REPO, Path(td), dry, retry, run, lines.append, roster)
        return code, lines, [" ".join(map(str, a)) for a in log]

    code, lines, log = go()
    check("a clean run owes nothing, exits 0 and says so", code == 0 and lines[-1].endswith("nothing owed"), lines)
    check("a clean run runs the comment, the sync, the docs push and the main read, once each",
          [sum(k in c for c in log) for k in ("gh_comment.py post", "roster_sync.py", "state_docs.py",
                                              "merge_train.py classify")] == [1, 1, 1, 1], log)
    code, lines, log = go(dry=True)
    check("the dry run prints the exact comment and every command, runs none, exits 0",
          code == 0 and lines[0] == f"DRY-RUN comment: Merged #7 {full} (R10-X). Closed issues: #5. Leaves #201 open."
          and [l.split(":")[0] for l in lines[1:5]] == ["DRY-RUN command", "DRY-RUN stage", "DRY-RUN docs",
                                                         "DRY-RUN main"]
          and not any(k in c for c in log for k in ("gh_comment", "roster_sync", "state_docs", "classify", "ledger")),
          lines)
    for key, step in (("gh_comment.py", "record"), ("roster_sync.py", "stage"), ("state_docs.py", "docs"),
                      ("classify", "main")):
        code, lines, log = go({key: 1})
        owed = [l for l in lines if l.startswith("OWED ")]
        check(f"a refused {step} step prints OWED {step}, exits non-zero, after the other steps ran",
              code == 1 and len(owed) == 1 and owed[0].startswith(f"OWED {step}:")
              and sum("state_docs.py" in c or "gh_comment" in c for c in log) >= 2, lines)
        check(f"... and opens postmerge-owed for the pull request and the full merge sha ({step})",
              any(f"ledger.py open postmerge-owed 7 {full} " in c for c in log), log)
    code, lines, _ = go({"roster_sync.py": 1})
    check("a refused stage names the resolved group: set-stage owed <GROUP> <merge sha>",
          f"set-stage owed R10-X {full}" in lines, lines)
    code, lines, log = go({"classify": 3})
    check("main WAIT (checks still running) is printed, not owed", code == 0 and
          any(l.startswith("main ") for l in lines) and not any(l.startswith("OWED") for l in lines), lines)
    code, lines, log = go(retry=True)
    check("--retry after a clean run closes the event, the only closer",
          any(f"ledger.py close postmerge-owed 7 {full} " in c for c in log), log)
    code, lines, log = go()
    check("without --retry a clean run closes nothing (null control)",
          not any("ledger.py" in c for c in log), log)
    print(f"postmerge self-test: {n[0]} checks, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
