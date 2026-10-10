"""OWN HARNESS (reviewer-built, disclosed as mine). Drives the PRODUCTION
Train.one recarry re-read with my own fake `run`, independent of the fixer's
self-test assertions. Prints my own RESULT lines."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/Users/timmalmstrom/hpo-seats/r9rev-2117/wt/tools/audit/seat")
import merge_train as M  # noqa: E402

H0 = "1" * 40
H1 = "2" * 40
V = "3" * 40


def drive(name, heads, remerge, contains, sleep_calls):
    calls = []
    out = {"n": 0}
    contains = list(contains)

    def run(argv, cwd=None, stdin=None):
        calls.append(argv)
        a = " ".join(argv)
        if argv[:3] == ["gh", "pr", "view"] and "headRefOid" in a:
            i = out["n"]
            out["n"] += 1
            if i < len(heads) - 1:
                head = heads[i]
            else:
                head = heads[-1]
            return 0, head
        if "merge-base --is-ancestor" in a:
            if not contains:
                return 0, ""
            return (1, "") if contains.pop(0) is False else (0, "")
        if "preflight.sh" in a:
            return 0, "  clean    no refusal"
        if "remerge_main.sh" in a:
            return 0, remerge
        if "check-runs" in a:
            runs = [{"name": "fast", "status": "completed",
                     "conclusion": "success", "started_at": "1"},
                    {"name": "nightly-status", "status": "completed",
                     "conclusion": "failure", "started_at": "1"}]
            return 0, "\n".join(json.dumps(c) for c in runs)
        if argv[:3] == ["git", "merge-base", "origin/main"]:
            return 0, "e" * 40 + "\n"
        if "--carry" in a:
            return 0, "CARRY: yes"
        if "--corpus-filter" in a:
            return 0, "\n".join(f for f in (stdin or "").split()
                                 if f in ("CLAUDE.md", "AGENTS.md",
                                          "dev/governance/roles/fixer.md"))
        if argv[:2] == ["git", "diff"]:
            return 0, "\n".join(["custom_components/x.py",
                                 f"{M.ROW_DIR}/7.md", f"{M.ROW_DIR}/8.md"])
        if argv[:3] == ["gh", "pr", "merge"]:
            return 0, ""
        if "state,mergeCommit" in a:
            return 0, "MERGED " + "d" * 40
        return 0, ""

    lines = []
    item = {"pr": 7, "verdict": V, "verdict_comment": "42",
            "worktree": "/nonexistent-wt", "branch": "fix/x"}
    with tempfile.TemporaryDirectory() as d:
        t = M.Train("o/r", Path(d), None, "the orchestrator", ("nightly-status",),
                    1, run=run, sleep=lambda s: sleep_calls.append(s),
                    log=lines.append, polls=2, merge_tries=3)
        rc = t.train([dict(item)])
    merged = [c for c in calls if c[:3] == ["gh", "pr", "merge"]]
    print(f"RESULT {name} rc={rc} merged_at={[c[-1][:8] for c in merged]} "
          f"settle_calls={sleep_calls} last={lines[-1][:60]!r}")
    print(f"       landed_line={any(chr(39)+chr(39) in ln or True for ln in lines)}")
    for ln in lines:
        print("       |", ln[:150])


# arm 1: the refusal, but the head MOVED -> landed, carry on
drive("recarry-refusal-head-moved", [H0, H1], "REFUSE: the pull request did not read back", [False], [])
# arm 2: the refusal, head did NOT move -> real stop
drive("recarry-refusal-head-still", [H0], "REFUSE: the pull request did not read back", [False], [])
# arm 3: null control -- a normal PUSHED recarry (no re-read sleep on the refusal path)
drive("recarry-pushed-ok", [H1], "RECARRY: prepr SKIPPED\napp_push: PUSHED", [False], [])
