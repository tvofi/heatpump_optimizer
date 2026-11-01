#!/usr/bin/env python3
"""R10-FLY-RAISE-REVIEWABLE (P345): the real-head control for `classify --pr`.

Runs <checkout>/tools/audit/seat/merge_train.py's `classify` CLI against live
GitHub with one TRANSPORT shim and nothing else changed: a proxy that refuses
`gh api --paginate`'s numeric-id follow-up links (a cloud seat's) is answered
by reading `gh api --paginate --slurp P` as the single page `gh api P`, wrapped
in a list; every read the classifier makes for one pull request is < 100 items.
Without the shim such a seat's raise_hold Stops and approval_owed fails closed
(RED, rc 1), which is the designed answer to an unread mandate thread.

    python3 dev/audit/harnesses/r10_fly_raise_reviewable.py <checkout> classify <sha> --repo R [--pr N]

Point <checkout> at a merge-base worktree (no `--pr` there) and at the head.
Control: #3045 at 9ef51b82, RED rc 1 at the base, APPROVAL-OWED rc 4 at the head.
Null: #3055 at 6a988a23, RED rc 1 at both ends.
"""
import importlib.util
import json
import sys

root = sys.argv[1]
spec = importlib.util.spec_from_file_location("mt", f"{root}/tools/audit/seat/merge_train.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
orig = mt.Train._run


def run(argv, cwd=mt.ROOT, stdin=None):
    if argv[:4] == ["gh", "api", "--paginate", "--slurp"]:
        code, o = orig(["gh", "api", *argv[4:]], cwd=cwd, stdin=stdin)
        return (code, json.dumps([json.loads(o)])) if code == 0 else (code, o)
    return orig(argv, cwd=cwd, stdin=stdin)


mt.Train._run = staticmethod(run)
rc = mt.main(sys.argv[2:])
print(f"rc={rc}")
sys.exit(0)
