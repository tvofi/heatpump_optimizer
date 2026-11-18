#!/usr/bin/env python3
"""R10-FLOW-AUTOTRAIN: Train.build_queue over the live tree, for a seat with no gh token.

    python3 dev/audit/harnesses/r10_flow_autotrain_live.py <prs.json> <comments.json>

git runs for real -- `ls-remote` of verdict/*, the fetches and `app_approve.sh
--carry` -- and the two gh reads are answered from files the seat saved from
another reader (the GitHub MCP tools): <prs.json> is `gh pr list --json
number,headRefOid,headRefName`'s shape, <comments.json> maps a pull request
number to its issue comments ({id, created_at, user {login, id}, body}). Any
other gh call is refused, so the run cannot write. Prints the builder's
QUEUE/LEFT lines, then the queue.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools/audit/seat"))
import merge_train as mt  # noqa: E402

prs, comments = (json.loads(Path(p).read_text()) for p in sys.argv[1:3])


def run(argv, cwd=mt.ROOT, stdin=None):
    if argv[:3] == ["gh", "pr", "list"]:
        return 0, json.dumps(prs)
    if argv[:2] == ["gh", "api"] and "/issues/" in argv[-1] and argv[-1].split("?")[0].endswith("/comments"):
        return 0, json.dumps([comments.get(argv[-1].split("/issues/")[1].split("/")[0], [])])
    if argv[0] == "gh":
        return 1, "refused: this harness answers only the two reads"
    return mt.Train._run(argv, cwd=cwd, stdin=stdin)


print(json.dumps(mt.Train("tvofi/heatpump_optimizer", Path("."), None, "", (), 1, run=run).build_queue()))
