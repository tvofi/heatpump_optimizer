#!/usr/bin/env python3
"""The fix reviewer's gather share, from local seat transcripts (R10-ORCH-REVIEW-PACKET).

Written by the R10-ORCH-REVIEW-PACKET fixer. Reads Cursor agent transcripts
(`*.jsonl`, one per seat; the corpus is out of the tree), keeps those whose first
record names a reviewer brief, and counts tool calls. A call is GATHER when it
fetches what `review_packet.py` now renders: a `Read`, a `gh api|pr` read, a
check-run read, a git read (show, diff, log, fetch, ls-remote, merge-base,
cat-file), or a `carry_audit` / `figure_lint` / `policy_lint --pr-body` run.
Transcripts record no tool-result sizes, so the share is of calls, not tokens,
and is an upper bound: a `Read` that judges code is counted as gather.
A seat whose transcript appears twice (top level and as a subagent) counts once.

    python3 dev/audit/harnesses/r10_review_gather_share.py <transcript dir>
    python3 dev/audit/harnesses/r10_review_gather_share.py --self-test
"""
import json
import re
import sys
from pathlib import Path

REVIEWER = re.compile(r"brief-rev|fix reviewer|Role: reviewer", re.I)
GATHER = re.compile(r"\bgh (api|pr)\b|check-runs|\bgit (show|diff|log|fetch|ls-remote|merge-base|cat-file)\b"
                    r"|carry_audit|figure_lint|policy_lint\.mjs --pr-body")


def seat_calls(rows: list) -> tuple[int, int] | None:
    if not rows or not REVIEWER.search(json.dumps(rows[0])[:3000]):
        return None
    calls = gather = 0
    for d in rows:
        content = d.get("message", {}).get("content")
        for c in content if isinstance(content, list) else []:
            if c.get("type") == "tool_use":
                calls += 1
                gather += c.get("name") == "Read" or bool(GATHER.search(json.dumps(c.get("input", {}))))
    return calls, gather


def self_test() -> int:
    use = lambda name, **i: {"type": "tool_use", "name": name, "input": i}  # noqa: E731
    head = {"role": "user", "message": {"content": [{"type": "text", "text": "Read brief-rev-1.txt"}]}}
    tools = {"role": "assistant", "message": {"content": [use("Shell", command="gh api repos/o/r/pulls/1"),
                                                          use("Read", path="x"), use("Shell", command="python3 m.py")]}}
    ok = seat_calls([head, tools]) == (3, 2)
    fixer = {"role": "user", "message": {"content": [{"type": "text", "text": "Role: fixer"}]}}
    null = seat_calls([fixer, tools]) is None
    print(f"  {'ok  ' if ok else 'FAIL'} two of three calls are gather")
    print(f"  {'ok  ' if null else 'FAIL'} null control: a fixer's transcript is not a reviewer's")
    return 0 if ok and null else 1


def main(argv: list) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    seen, calls, gather, seats = set(), 0, 0, 0
    for f in sorted(Path(argv[0]).rglob("*.jsonl")):
        if f.name in seen:
            continue
        r = seat_calls([json.loads(x) for x in f.read_text().splitlines() if x.strip()])
        if r is None:
            continue
        seen.add(f.name)
        seats, calls, gather = seats + 1, calls + r[0], gather + r[1]
        print(f"SEAT {f.stem[:8]} calls={r[0]} gather={r[1]}")
    print(f"RESULT seats={seats} calls={calls} gather={gather} share={100 * gather / max(calls, 1):.0f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
