"""Count recorded runner-conditional instances on issue #996's thread.

Issue #996's recorded decision (2026-09-13, re-affirmed by the owner on
2026-09-14) priced the runner-conditional chaos dilemma at two instances
and declined a claim-grammar extension; the owner's fail-fast ruling then
replaced the passive tripwire with an executable one, in three parts:

  * `tests/env_drift.py` names the signature at the moment of failure
    (RUNNER-CONDITIONAL CANDIDATE) and hands the seat a pre-agreed
    decision tree whose step 2 is to post the instance on #996;
  * a post records ONE instance when it carries a line starting at column
    0 with the marker `env_drift.RUNNER_CONDITIONAL_INSTANCE_MARKER` --
    quoted replies, indented pastes and mid-line mentions are discussion,
    not records, so nothing a seat quotes re-tallies;
  * THIS script counts those lines and says when the third instance has
    landed, which re-opens the declined grammar decision.

The thread is the ledger. The two instances the decision already priced
(v5.1.7's search-path chaos, #992's valve_storage_small_tank) were seeded
into the thread as marker lines when this mechanism landed, so the count
starts at two and this script holds no state of its own -- no baked-in
history, nothing to go stale if the decision is re-baselined.

Hand-run by the record seat; the gate never runs it (NOT_A_TEST in
`tests/closure.py` -- `tests/entities.py` imports it and pins its
counting rule, its threshold and its CLI instead):

    python3 tests/issue996_count.py                  # the live thread, via gh
    python3 tests/issue996_count.py --from F.json    # offline: comment bodies

`--from` takes a JSON list of comment bodies or of `{"body": ...}` objects
(the shape the GitHub API returns), which is how the fixture-thread pin in
entities.py drives the exact CLI a seat runs. Exit 0 below the threshold,
2 at it and beyond (the crossing is machine-visible), 1 when the thread
cannot be read.

Why a hand-run script and not a CI post (the claims-autofix pattern):
`ci-autofix.md` caps that family at the two jobs it already has, a CI job
with write permissions is a larger standing surface than the repo needs,
and an automated post has nothing honest to add -- an instance is real
only once a seat has verified BOTH captures' numbers, which is the seat's
step 2, not the runner's.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import env_drift

REPO = "tvofi/heatpump_optimizer"
ISSUE = 996


def count_instances(bodies: list[str]) -> int:
    """Recorded instances in a comment thread: marker lines at column 0.

    One marker line is one instance, wherever it sits -- a single comment
    reporting two instances writes two lines. The line must START with the
    marker, so a quoted report (`> 996-instance: ...`), an indented paste
    of the decision tree and a mid-line mention all record nothing.
    """
    marker = env_drift.RUNNER_CONDITIONAL_INSTANCE_MARKER
    return sum(
        1
        for body in bodies
        for line in body.splitlines()
        if line.startswith(marker)
    )


def reopen_verdict(count: int) -> str | None:
    """The re-open message at and beyond the threshold, None below it."""
    threshold = env_drift.RUNNER_CONDITIONAL_REOPEN_AT
    if count < threshold:
        return None
    return (
        "THIRD INSTANCE — grammar decision reopens: "
        f"{count} runner-conditional instance(s) now recorded on "
        f"{REPO}#{ISSUE} (threshold {threshold}). The 2026-09-13 decision "
        "declined the grammar extension at two; the owner's tripwire "
        "re-opens it at three, and this is that crossing."
    )


def fetch_bodies(repo: str = REPO, issue: int = ISSUE) -> list[str]:
    """Comment bodies off the GitHub API, oldest first, via `gh`.

    Paged by hand: `--paginate` concatenates pages into a stream this
    script would have to re-split, and the counter's honesty lives in its
    inputs, not in a client convenience.
    """
    bodies: list[str] = []
    page = 1
    while True:
        proc = subprocess.run(
            ["gh", "api", f"repos/{repo}/issues/{issue}/comments",
             "--method", "GET", "-f", "per_page=100", "-f", f"page={page}"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise SystemExit(
                f"cannot read {repo}#{issue} (page {page}): "
                f"{proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else 'no message'}"
            )
        comments = json.loads(proc.stdout)
        if not isinstance(comments, list):
            raise SystemExit(f"{repo}#{issue} page {page} is not a comment list")
        if not comments:
            break
        bodies += [c.get("body") or "" for c in comments]
        if len(comments) < 100:
            break
        page += 1
    return bodies


def usage() -> "SystemExit":
    return SystemExit(
        "usage: python3 tests/issue996_count.py [--from F.json]\n"
        "  --from F.json   count a fixture thread (JSON list of bodies or\n"
        "                  of {\"body\": ...} objects) instead of the live one"
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    from_file = ""
    while args:
        if args[0] == "--from" and len(args) > 1:
            from_file = args[1]
            args = args[2:]
        else:
            raise usage()
    if from_file:
        data = json.loads(Path(from_file).read_text())
        if not isinstance(data, list):
            raise SystemExit(f"{from_file} is not a JSON list")
        bodies = [item["body"] if isinstance(item, dict) else item for item in data]
    else:
        bodies = fetch_bodies()
    count = count_instances(bodies)
    print(f"recorded runner-conditional instance(s) on {REPO}#{ISSUE}: {count}")
    verdict = reopen_verdict(count)
    if verdict:
        print(verdict)
        return 2
    print(
        f"below the re-open threshold "
        f"({env_drift.RUNNER_CONDITIONAL_REOPEN_AT}); the recorded "
        "decision stands"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
