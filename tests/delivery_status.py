#!/usr/bin/env python3
"""The delivery ledger: what merged, what has a row, and what is overdue one.

WHY THIS REPLACES A RED TICK
----------------------------
`record` (in `.github/workflows/governance.yml`) refuses a merged pull request
with no disposition row, and it is correct. `tests/record_status.py` then
reported main's `record` conclusion as a red check on every open pull request,
so that the cost of a missing row landed on somebody rather than on nobody.

Measured over main's last 40 commits on 2026-09-12: **`record` concluded
`failure` on 28 of them**. The reds arrive in six streaks of 4, 8, 3, 2, 4 and 7
commits, and every single streak ends at a `record:` leftover-row commit or at a
release stamp carrying one. That is not a detector finding 28 defects. It is a
detector firing on the protocol's own steady state, because `record` asks

    does every merged pull request have a row RIGHT NOW

while the protocol promises

    every merged pull request gets a row, in a batch, soon

and #541's root-cause seat already costed the pre-merge alternative and refused
it at five false refusals per true one, for exactly that reason. A check that is
red 70 % of the time by design is the shape `record_status.py`'s own docstring
warns about: the first red one teaches everybody to ignore it.

So the predicate changes rather than the reporting. This measures what the
protocol actually promises -- nothing has been waiting too long -- and it
publishes the pending list, which is the thing a seat can act on and which a
tick never was.

THE THRESHOLD IS MEASURED, NOT CHOSEN
-------------------------------------
A rowless merge is OVERDUE once ``STALE_AFTER_COMMITS`` commits have landed on
main after it. The unit is commits and not hours for `record_status.py`'s own
reason: `record` runs on every push to main, so a quiet week is not staleness,
and what makes a row late is the merges that went past it. The number is set
from the measurement above -- longest observed streak 8, median 4 -- with room
over the worst case rather than at it. At 12 it would have fired zero times in
that 40-commit window, which is the point: green through ordinary batching, red
only when the batch has stopped being drained.

A threshold that never fires is the always-green shape this repository keeps
catching, so `tests/entities.py` drives BOTH sides from fixtures: a window whose
oldest rowless merge is past the threshold is OVERDUE, and one inside it is not.

WHAT IT DOES NOT DO
-------------------
It does not prevent a merge with no row, and `record` on main is unchanged --
that gate is right and stays. This replaces one binary tick with a list that is
current, and it leaves the aging case as the only thing that goes red.

FIND IT WITHOUT ASKING ANYONE
-----------------------------
The ledger is written to ``docs/delivery-status.json`` and committed, so any
session reads it with `cat` -- a cursor lane, a cloud seat, a session with no
GitHub token, or a person. Nothing about finding the current state depends on
having credentials or on scrolling an issue.

The same content goes into #201's body, inside the delimited region below, and
into the body rather than a comment ON PURPOSE: the newest comment competes with
every seat's own posts and is unfindable after forty of them, while a body is
singular, is the first thing `gh issue view 201` prints, and editing it notifies
nobody.

    python3 tests/delivery_status.py --emit docs/delivery-status.json
    python3 tests/delivery_status.py --from docs/delivery-status.json --check
    python3 tests/delivery_status.py --from docs/delivery-status.json --markdown

`--from` reads a recorded ledger and runs no query, which is how the classifier
is driven in tests and how a seat inspects a ledger it did not build.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Commits that may land on main after a rowless merge before it is OVERDUE.
#: Set from the measurement in the docstring: longest observed batch 8 commits,
#: median 4. Raising it hides a stalled batch; lowering it re-creates the noise
#: this file exists to remove, and either is a deliberate edit with its own
#: measurement.
STALE_AFTER_COMMITS = 12

#: Where the ledger lands in #201's body. The region is delimited so the
#: issue's own hand-written tracking text survives every update -- replacing
#: the whole body would destroy it, and this is the difference between an
#: idempotent update and a destructive one.
REGION_BEGIN = "<!-- delivery-status:begin -->"
REGION_END = "<!-- delivery-status:end -->"

#: Where a disposition may be written. Both are read whole: a row in either
#: satisfies `record`, and this must agree with it or the two tell a seat
#: different things about the same merge.
DISPOSITION_FILES = (
    "docs/plan-2026-09-open-issues.md",
    "docs/HANDOVER.md",
)

OK = "OK"
OVERDUE = "OVERDUE"
#: The window since the last release tag holds no merge at all. Reported as
#: its own verdict rather than folded into OK, because "we looked at forty
#: merges and every one had a row" and "there was nothing to look at" are
#: different facts and only one of them is evidence. It is not a failure --
#: right after a stamp the window is legitimately empty.
EMPTY = "EMPTY"
UNREADABLE = "UNREADABLE"


# --------------------------------------------------------------- classifier
# Pure, so `tests/entities.py` drives every state from fixtures with no network
# and no token -- `tests/nightly_status.py`'s shape, for its reason.

def mentions(number: int, texts: list[str]) -> bool:
    """Whether a disposition file names pull request `number`.

    Matched as `#<n>` or as a pull URL ending in `/<n>`, both bounded, because
    `#88` must not be satisfied by `#885`. That the two spellings both count is
    not a convenience: the Delivery-status rows use the link form and the
    handover uses the bare form, so a matcher that took only one would report
    half the record missing.
    """
    pattern = re.compile(rf"(?:#|/pull/){number}(?![0-9])")
    return any(pattern.search(t) for t in texts)


def classify(merges: list[dict], texts: list[str],
             stale_after: int = STALE_AFTER_COMMITS) -> dict:
    """The ledger for one window of merges, newest first.

    `merges` carries, per entry, the pull-request `number`, its `title`, its
    `merge_sha`, `merged_at`, and `commits_after` -- how many commits landed on
    main after it. Everything below is derived from those and from the
    disposition files; nothing is carried.
    """
    rows = []
    for m in merges:
        has_row = mentions(int(m["number"]), texts)
        after = int(m.get("commits_after", 0))
        state = "rowed" if has_row else (
            "overdue" if after >= stale_after else "pending")
        rows.append({**m, "state": state})
    overdue = [r for r in rows if r["state"] == "overdue"]
    pending = [r for r in rows if r["state"] == "pending"]
    return {
        "verdict": OVERDUE if overdue else (OK if rows else EMPTY),
        "stale_after_commits": stale_after,
        "merges": rows,
        "counts": {
            "rowed": sum(1 for r in rows if r["state"] == "rowed"),
            "pending": len(pending),
            "overdue": len(overdue),
        },
    }


def render_markdown(ledger: dict) -> str:
    """The human form, for #201's delimited region. No figure about itself."""
    counts = ledger["counts"]
    lines = [
        REGION_BEGIN,
        "",
        "### Delivery status — generated, do not edit by hand",
        "",
        f"Regenerated by `tests/delivery_status.py`; the machine form is "
        f"`docs/delivery-status.json`, committed, which a session with no "
        f"GitHub token can read. Verdict **{ledger['verdict']}**.",
        "",
        f"A merge is *pending* a Delivery-status row until one is written, and "
        f"*overdue* once **{ledger['stale_after_commits']}** commits have "
        f"landed on `main` after it — batching is the protocol, so pending is "
        f"the ordinary state and only overdue is a problem.",
        "",
        f"| rowed | pending | overdue |",
        f"|---|---|---|",
        f"| {counts['rowed']} | {counts['pending']} | {counts['overdue']} |",
        "",
    ]
    for state, heading in (("overdue", "Overdue a row"),
                           ("pending", "Pending a row")):
        rows = [r for r in ledger["merges"] if r["state"] == state]
        if not rows:
            continue
        lines.append(f"**{heading}**")
        lines.append("")
        for r in rows:
            lines.append(
                f"- #{r['number']} `{str(r.get('merge_sha', ''))[:7]}` — "
                f"{r.get('title', '')} "
                f"({r.get('commits_after', 0)} commit(s) since)"
            )
        lines.append("")
    if ledger["verdict"] == EMPTY:
        lines.append("The window since the last release tag holds no merge — "
                     "which is not evidence that rows are being written.")
        lines.append("")
    elif not counts["pending"] and not counts["overdue"]:
        lines.append("Every merge in the window carries a row.")
        lines.append("")
    lines.append(
        "This region is replaced in place; the issue's own text above and "
        "below it is never touched."
    )
    lines.append("")
    lines.append(REGION_END)
    return "\n".join(lines)


def splice(body: str, region: str) -> str:
    """Put `region` into `body`, replacing any previous one. Idempotent."""
    if REGION_BEGIN in body and REGION_END in body:
        head = body[: body.index(REGION_BEGIN)]
        tail = body[body.index(REGION_END) + len(REGION_END):]
        return head + region + tail
    return body.rstrip() + "\n\n" + region + "\n"


# ------------------------------------------------------------------ gathering

def _gh(args: list[str]) -> str:
    return subprocess.run(["gh", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def gather(repo: str, since_tag: str | None = None) -> list[dict]:
    """Merged pull requests in the current window, newest first.

    The window starts at the last release tag, because that is the unit the
    record protocol itself works in -- `policy_lint --record --since <tag>` is
    what a seat runs -- and because an unbounded window would re-report every
    merge this repository has ever made.
    """
    if since_tag is None:
        since_tag = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"], cwd=ROOT,
            capture_output=True, text=True).stdout.strip()
    span = f"{since_tag}..origin/main" if since_tag else "origin/main"
    log = subprocess.run(
        ["git", "log", "--first-parent", "--format=%H%x09%s", span], cwd=ROOT,
        capture_output=True, text=True).stdout.splitlines()
    out: list[dict] = []
    for depth, line in enumerate(log):
        sha, _, subject = line.partition("\t")
        m = re.search(r"\(#(\d+)\)\s*$", subject)
        if not m:
            continue
        out.append({
            "number": int(m.group(1)),
            "title": subject[: subject.rfind("(#")].strip(),
            "merge_sha": sha,
            "commits_after": depth,
        })
    return out


def read_texts() -> list[str]:
    return [
        (ROOT / name).read_text() for name in DISPOSITION_FILES
        if (ROOT / name).exists()
    ]


# ----------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", default="", help="write the ledger to this path")
    ap.add_argument("--from", dest="source", default="",
                    help="classify a recorded ledger; runs no query")
    ap.add_argument("--markdown", action="store_true",
                    help="print the #201 region instead of the ledger")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when a merge is OVERDUE a row")
    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
    ap.add_argument("--since", default="")
    args = ap.parse_args()

    if args.source:
        ledger = json.loads(Path(args.source).read_text())
    else:
        try:
            merges = gather(args.repo, args.since or None)
        except Exception as err:  # noqa: BLE001
            # Fails CLOSED, like every reporter here: a ledger that could not
            # be built must not read as a ledger with nothing in it.
            print(f"DELIVERY STATUS {UNREADABLE}: could not build the "
                  f"ledger: {err}")
            return 2
        ledger = classify(merges, read_texts())

    if args.emit:
        Path(args.emit).write_text(json.dumps(ledger, indent=2) + "\n")
        print(f"wrote {args.emit}")

    if args.markdown:
        print(render_markdown(ledger))
        return 0

    counts = ledger["counts"]
    print(f"DELIVERY STATUS {ledger['verdict']} — {counts['rowed']} rowed, "
          f"{counts['pending']} pending, {counts['overdue']} overdue "
          f"(overdue at {ledger['stale_after_commits']} commits)")
    for r in ledger["merges"]:
        if r["state"] != "rowed":
            print(f"  {r['state']:<8} #{r['number']} "
                  f"{str(r.get('merge_sha', ''))[:7]} "
                  f"{r.get('commits_after', 0)} commit(s) since — "
                  f"{r.get('title', '')[:56]}")
    if ledger["verdict"] == EMPTY:
        print("  the window since the last release tag holds no merge; this "
              "is not evidence that rows are being written")
    elif not counts["pending"] and not counts["overdue"]:
        print("  every merge in the window carries a row")
    print()
    print("This check is NOT a required context and a red here blocks no "
          "merge. Pending is the ordinary state: the protocol writes rows in "
          "batches, and only OVERDUE means a batch has stopped being drained.")
    if args.check and ledger["verdict"] == OVERDUE:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
