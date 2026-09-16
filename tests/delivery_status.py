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

A RUN THAT COULD NOT LOOK IS NOT A RUN THAT FOUND NOTHING
---------------------------------------------------------
The window is collected from `git log --first-parent` subjects, and a subject
convention is a PRECONDITION rather than a design choice: this file was written
when every merge arrived squashed as ``<title> (#N)``, the repository moved to
merge commits, and the collector went to zero over a full window while
reporting the same EMPTY it reports right after a stamp. Two things follow, and
both are in the code below rather than in this paragraph.

Both subject shapes are read (`SQUASH_SUBJECT`, `MERGE_SUBJECT`). And a merge
commit the rules cannot attribute is reported, loudly, as ``UNCHECKED`` --
`policy_lint.mjs`'s `enumSkipLine` words for the same defect one file over
(#1050) -- because widening a pattern fixes the instance and only a guard fixes
the class. The guard keys on the PARENT COUNT, not on the subject text, so the
release stamp and the `record:` commits that reach `main` as direct pushes do
not trip it.

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
#: The window holds merge commits this file could not attribute to a pull
#: request. Its own verdict, and the whole point of the distinction: EMPTY
#: claims the window was read and held nothing, and a collection rule that has
#: gone blind produces a byte-identical EMPTY over a window full of merges.
#: That is not a hypothetical -- see `SQUASH_SUBJECT` below for the window it
#: happened over.
UNCHECKED = "UNCHECKED"
UNREADABLE = "UNREADABLE"

#: The two shapes a first-parent subject on `main` carries a pull-request
#: number in, and why there are two rather than one. GitHub writes
#: ``<title> (#N)`` when a pull request is SQUASHED and
#: ``Merge pull request #N from <branch>`` when it is MERGED, and this
#: repository has done both -- but chronologically, not mixed. Derive the split
#: at your own head rather than carrying one; the enumerators are
#:
#:     git log --first-parent --format=%s origin/main | grep -cE '\(#[0-9]+\)$'
#:     git log --first-parent --format=%s origin/main \
#:       | grep -cE '^Merge pull request #[0-9]+'
#:
#: and what matters is not either count but that the newest squash-shaped
#: subject is old: every first-parent commit after it is a merge commit or a
#: release stamp pushed straight to `main`. A rule taking only the squash shape
#: therefore collected the whole of history and nothing since that date, which
#: is exactly what this file did -- ``DELIVERY STATUS EMPTY -- 0 rowed`` over a
#: window whose merges every one named its pull request in the subject.
SQUASH_SUBJECT = re.compile(r"\(#(\d+)\)\s*$")
#: Anchored at the start and bounded after the number, so a subject merely
#: MENTIONING a pull request ("Record #424 W1-G14 merge in delivery-status")
#: is not taken as being that merge. `\b` rather than ` from ` because the
#: oldest merge subjects here are ``Merge pull request #13: Broaden ...``.
MERGE_SUBJECT = re.compile(r"^Merge pull request #(\d+)\b")


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


def subject_number(subject: str) -> int | None:
    """The pull-request number a first-parent subject names, or None.

    The merge shape is tried first: a squash subject cannot also be a merge
    subject, but a merge subject whose branch name happened to end in `(#N)`
    could be read as one, and the number GitHub wrote at the front is the
    authoritative one.
    """
    for pattern in (MERGE_SUBJECT, SQUASH_SUBJECT):
        found = pattern.search(subject)
        if found:
            return int(found.group(1))
    return None


def subject_title(subject: str, body: str) -> str:
    """The human title of a merge, which is not always in its subject.

    A squash subject IS the title with `(#N)` appended. A merge commit's
    subject names a BRANCH and not the work, and GitHub puts the pull
    request's title on the first non-blank line of the commit body -- which is
    what the pending list has to print, because a seat reading
    `pending #1049 fix/d11-publish-concurrency` learns less than nothing about
    what is waiting on it.
    """
    if MERGE_SUBJECT.search(subject):
        for line in body.splitlines():
            if line.strip():
                return line.strip()
        return subject.strip()
    return subject[: subject.rfind("(#")].strip()


def collect(commits: list[dict]) -> tuple[list[dict], list[dict]]:
    """Merges in the window, and the merge commits nothing could attribute.

    `commits` is the first-parent log, newest first, each entry carrying
    `sha`, `parents` (how many), `subject` and `body`.

    THE SECOND RETURN IS THE HONEST HALF, and it is keyed on the PARENT COUNT
    rather than on the subject text. A direct push to `main` -- a release
    stamp, a `record:` leftover-row commit -- has one parent and legitimately
    names no pull request, so a guard asking "does this subject mention a
    number" fires on every stamp and is worthless. A first-parent commit with
    two parents is a pull-request merge by construction: nothing else reaches
    `main` with two parents under the ruleset. So one the subject rules cannot
    attribute is this file going blind, and is not anything else.

    Measure the guard's false-positive surface at your own head rather than
    trusting this sentence; the enumerator is

        git log --first-parent --format='%H%x1f%P%x1f%s' <range>

    filtered to entries whose parent field holds more than one sha, then to
    those `subject_number` returns None for. At the head this was written
    against every such residual predated `v6.2.12` -- hand-written local merge
    subjects from the W1/W2 waves -- so none is reachable from a window a
    release tag opens, and no single-parent commit anywhere in main's history
    was taken by `MERGE_SUBJECT`.
    """
    merges: list[dict] = []
    unattributed: list[dict] = []
    for depth, commit in enumerate(commits):
        number = subject_number(commit["subject"])
        if number is None:
            if int(commit.get("parents", 1)) > 1:
                unattributed.append({"sha": commit["sha"],
                                     "subject": commit["subject"]})
            continue
        merges.append({
            "number": number,
            "title": subject_title(commit["subject"], commit.get("body", "")),
            "merge_sha": commit["sha"],
            "commits_after": depth,
        })
    return merges, unattributed


def unchecked_line(unattributed: list[dict]) -> str:
    """The loud half of the collection guard.

    Deliberately `policy_lint.mjs`'s `enumSkipLine` shape and its words --
    `UNCHECKED this run, not confirmed empty` -- because that guard was landed
    (#1050) for this same defect one file over: an end-anchored `(#N)` falling
    through to a zero that means "no data" and reads as "no merges". A second
    vocabulary for the same fact would cost a reader a translation and buy
    nothing. Pure over its argument so the acceptance drives it with no repo.
    """
    example = unattributed[0] if unattributed else {}
    return (
        f"  skip     merge-collection      "
        f"{len(unattributed)} merge commit(s) in the window name no pull "
        f"request that `subject_number` recognises (e.g. "
        f"{str(example.get('sha', ''))[:7]} "
        f"{example.get('subject', '')!r}); the window's merged pull requests "
        f"are UNCHECKED this run, not confirmed empty -- a merge-subject "
        f"convention that moves out from under these rules reports every "
        f"merge in the window as absent, which is how this file printed "
        f"EMPTY over a window that held nothing but merges"
    )


def classify(merges: list[dict], texts: list[str],
             stale_after: int = STALE_AFTER_COMMITS,
             unattributed: list[dict] | tuple = ()) -> dict:
    """The ledger for one window of merges, newest first.

    `merges` carries, per entry, the pull-request `number`, its `title`, its
    `merge_sha`, `merged_at`, and `commits_after` -- how many commits landed on
    main after it. Everything below is derived from those and from the
    disposition files; nothing is carried.

    `unattributed` is `collect`'s second return. OVERDUE outranks UNCHECKED
    because OVERDUE is the state a seat can act on today and is what `--check`
    exists to raise; the list is emitted and its line printed under EITHER
    verdict, so the stronger one never hides the guard.
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
    blind = list(unattributed)
    return {
        "verdict": OVERDUE if overdue else (
            UNCHECKED if blind else (OK if rows else EMPTY)),
        "stale_after_commits": stale_after,
        "merges": rows,
        "unattributed": blind,
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
    blind = ledger.get("unattributed", [])
    if blind:
        lines.append("**The collection could not read the whole window.**")
        lines.append("")
        lines.append("```")
        lines.append(unchecked_line(blind))
        lines.append("```")
        lines.append("")
        for b in blind:
            lines.append(f"- `{str(b.get('sha', ''))[:7]}` "
                         f"{b.get('subject', '')}")
        lines.append("")
    if ledger["verdict"] == EMPTY:
        lines.append("The window since the last release tag holds no merge — "
                     "which is not evidence that rows are being written, but "
                     "IS evidence that the window was read: a run that could "
                     "not read it reports **UNCHECKED**, above, and never "
                     "this.")
        lines.append("")
    elif not blind and not counts["pending"] and not counts["overdue"]:
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


#: How the window's start is found, as a CONSTANT so the acceptance reads the
#: argv this code runs rather than a copy of it.
#:
#: `--match 'v*'` is not decoration. `git describe --tags --abbrev=0` answers
#: the newest tag of ANY shape, and this repository creates non-release tags:
#: `governance.yml`'s own "Choose the window" step carries this flag and says
#: why in a comment -- `archive-rosters-2026-09` was newer than the release tag
#: and yielded an empty window. That is the SAME failure this file is being
#: repaired for, reached by a different route, and the guard below cannot see
#: it: a wrong tag produces an empty LOG, so there are no merge commits to be
#: unattributable and the run reports a truthful EMPTY about the wrong window.
#: Two lanes reporting on "the window" must also agree on which one it is.
DESCRIBE_ARGV = ("git", "describe", "--tags", "--abbrev=0", "--match", "v*")

#: The first-parent log format. Unit separator between the fields and record
#: separator between commits, because `%b` is multi-line: a line-oriented
#: format silently truncates every title to the branch name it is trying not
#: to print.
LOG_FORMAT = "%H%x1f%P%x1f%s%x1f%b%x1e"


def parse_log(text: str) -> list[dict]:
    """`LOG_FORMAT` output into commit dicts, newest first. Pure."""
    commits: list[dict] = []
    for record in text.split("\x1e"):
        record = record.lstrip("\n")
        if not record.strip():
            continue
        fields = (record.split("\x1f") + ["", "", ""])[:4]
        sha, parents, subject, body = fields
        commits.append({
            "sha": sha.strip(),
            "parents": len(parents.split()),
            "subject": subject,
            "body": body,
        })
    return commits


def gather(repo: str,
           since_tag: str | None = None) -> tuple[list[dict], list[dict]]:
    """Merged pull requests in the current window, newest first, and the
    merge commits in it that could not be attributed to one.

    The window starts at the last release tag, because that is the unit the
    record protocol itself works in -- `policy_lint --record --since <tag>` is
    what a seat runs -- and because an unbounded window would re-report every
    merge this repository has ever made.

    No token and no network: the subject and the parent count are both in the
    log, so this answers the same on a cloud seat, in a cursor lane and behind
    a secondary rate limit, which is the property the original had and the one
    worth keeping. `policy_lint --record`'s API enumerator asks GitHub for the
    commit-to-pull-request map instead and is correct over this same window;
    the two agreeing is a cross-check, and a token-dependent collector here
    would have turned a rate limit into an EMPTY.
    """
    if since_tag is None:
        since_tag = subprocess.run(
            list(DESCRIBE_ARGV), cwd=ROOT,
            capture_output=True, text=True).stdout.strip()
    span = f"{since_tag}..origin/main" if since_tag else "origin/main"
    log = subprocess.run(
        ["git", "log", "--first-parent", f"--format={LOG_FORMAT}", span],
        cwd=ROOT, capture_output=True, text=True).stdout
    return collect(parse_log(log))


#: One file per pull request, `docs/delivery/<N>.md`: a row there is read only
#: through a line anchoring <N> itself, as `policy_lint.mjs`'s `recordRegion`
#: reads it, so a misnamed file rows nobody and the two cannot disagree.
ROW_DIR = "docs/delivery"
ROW_ANCHOR = re.compile(r"^\s*[-*]\s+\[#(\d+)\]\((?:[^()\s]*/pull/)(\d+)\)")


def read_texts() -> list[str]:
    rows = [
        line
        for path in sorted((ROOT / ROW_DIR).glob("*.md")) if path.stem.isdigit()
        for line in path.read_text().splitlines()
        if (m := ROW_ANCHOR.match(line)) and m[1] == m[2] == path.stem
    ]
    return [
        (ROOT / name).read_text() for name in DISPOSITION_FILES
        if (ROOT / name).exists()
    ] + ["\n".join(rows)]


# ----------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", default="", help="write the ledger to this path")
    ap.add_argument("--from", dest="source", default="",
                    help="classify a recorded ledger; runs no query")
    ap.add_argument("--markdown", action="store_true",
                    help="print the #201 region instead of the ledger")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when a merge is OVERDUE a row, or when the "
                         "window could not be read (UNCHECKED)")
    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
    ap.add_argument("--since", default="")
    args = ap.parse_args()

    if args.source:
        ledger = json.loads(Path(args.source).read_text())
    else:
        try:
            merges, unattributed = gather(args.repo, args.since or None)
        except Exception as err:  # noqa: BLE001
            # Fails CLOSED, like every reporter here: a ledger that could not
            # be built must not read as a ledger with nothing in it.
            print(f"DELIVERY STATUS {UNREADABLE}: could not build the "
                  f"ledger: {err}")
            return 2
        ledger = classify(merges, read_texts(), unattributed=unattributed)

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
    blind = ledger.get("unattributed", [])
    if blind:
        print(unchecked_line(blind))
        for b in blind:
            print(f"  unread   {str(b.get('sha', ''))[:7]} "
                  f"{b.get('subject', '')[:64]}")
    if ledger["verdict"] == EMPTY:
        print("  the window since the last release tag holds no merge; this "
              "is not evidence that rows are being written, but it IS "
              "evidence that the window was read -- a run that could not read "
              "it reports UNCHECKED and never EMPTY")
    elif not blind and not counts["pending"] and not counts["overdue"]:
        print("  every merge in the window carries a row")
    print()
    print("This check is NOT a required context and a red here blocks no "
          "merge. Pending is the ordinary state: the protocol writes rows in "
          "batches, and only OVERDUE means a batch has stopped being drained.")
    # `--check` raises UNCHECKED as well as OVERDUE, and that is a DELIBERATE
    # widening of this flag's exit semantics rather than a side effect. The
    # argument: this job's whole subject is noticing that something went dark,
    # and the one state in which it cannot see is the one state it must not
    # report as a pass -- the vacuous green this file's own docstring refuses.
    # It costs nothing that gates: `delivery-status` is not a required
    # context and a red here blocks no merge, which the report says on every
    # run. The `delivery-status-publish` lane passes `--emit` and not
    # `--check`, so it is unaffected either way.
    if args.check and ledger["verdict"] in (OVERDUE, UNCHECKED):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
