#!/usr/bin/env python3
"""The #201 record comment of a merge: from a fixed template, read back.

    python3 tools/audit/seat/record_beat.py [--repo O/R] [--state-dir D] [--dry-run] <PR>...
    python3 tools/audit/seat/record_beat.py --self-test

For each merged pull request it resolves the FULL merge sha from git (the oid
GitHub names, then `git rev-parse --verify <oid>^{commit}`; a sha is never
typed), renders one line from `TEMPLATE`, writes it to a body file under the
state directory (`gh_comment.py` refuses a shared root) and posts it with
`tools/pr/gh_comment.py post`, which exits non-zero unless the comment read
back off the API is byte-identical. The orchestrator tick finds a merge's
record by searching #201's comments for the 40-character sha
(`orchestrator_tick.py`'s `unrecorded`), so the template carries it whole: ten
merges once read unrecorded because their comments cited a short sha.

`resolve_group` is the one place a merge's roster group is named, for this
comment and for `postmerge.py`'s `set-stage owed` line: the group whose
`resume.branch` or id equals the head branch (`roster_lib.group_for_branch`,
equality and never a prefix), else the group whose `resume.pr` is the merged
number, else `no-group`. It never guesses a near match.

A failure here is the caller's to print as OWED; it never undoes the merge.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SEAT = Path(__file__).resolve().parent
ROOT = SEAT.parents[2]
sys.path.insert(0, str(SEAT))
import roster_lib  # noqa: E402

DEFAULT_REPO = "tvofi/heatpump_optimizer"
RECORD_ISSUE = 201
NO_GROUP = "no-group"
SHA = re.compile(r"^[0-9a-f]{40}$")
TEMPLATE = "Merged #{pr} {sha} ({group}). Closed issues: {issues}. Leaves #201 open."


class Owed(Exception):
    """A step that could not finish: the caller prints it OWED."""


def sh(argv, stdin=None, cwd=None):
    p = subprocess.run(argv, input=stdin, capture_output=True, text=True, cwd=cwd or ROOT)
    return p.returncode, (p.stdout + p.stderr)


def resolve_group(roster: "dict | None", branch: str, pr: int) -> str:
    """The roster group a merged pull request answers for, else `no-group`."""
    if not roster:
        return NO_GROUP
    g = roster_lib.group_for_branch(roster, branch)
    if g:
        return g
    for grp in roster.get("groups", []):
        if (grp.get("resume") or {}).get("pr") == pr:
            return grp.get("group") or NO_GROUP
    return NO_GROUP


def load_roster(run=sh) -> "dict | None":
    """The round's roster: `roster_lib.round_ref` if that ref is readable, else
    main's. None when neither is: the caller names no group, not a guess."""
    git = lambda argv: run(["git", *argv])
    ref = roster_lib.round_ref(git)
    for cand in ([ref] if ref else []) + [roster_lib.MAIN_REF]:
        if run(["git", "rev-parse", "--verify", "--quiet", cand + "^{commit}"])[0] == 0:
            try:
                return roster_lib.show_roster(str(ROOT), cand)
            except (roster_lib.RosterNotFound, ValueError):
                continue
    return None


def facts(pr: int, repo: str, run=sh) -> dict:
    """{sha, branch, issues} of a MERGED pull request, the sha full and from git."""
    code, o = run(["gh", "pr", "view", str(pr), "--repo", repo, "--json",
                   "state,mergeCommit,headRefName,closingIssuesReferences"])
    try:
        d = json.loads(o) if code == 0 else None
    except ValueError:
        d = None
    if not isinstance(d, dict):
        raise Owed(f"#{pr} could not be read ({o.strip()[-120:] or 'no output'})")
    if d.get("state") != "MERGED" or not (d.get("mergeCommit") or {}).get("oid"):
        raise Owed(f"#{pr} is {d.get('state')}, not merged")
    oid = d["mergeCommit"]["oid"]
    code, full = run(["git", "rev-parse", "--verify", "--quiet", oid + "^{commit}"])
    full = full.strip()
    if code != 0 or not SHA.match(full):
        run(["git", "fetch", "-q", "origin", "main"])
        code, full = run(["git", "rev-parse", "--verify", "--quiet", oid + "^{commit}"])
        full = full.strip()
    if code != 0 or not SHA.match(full):
        raise Owed(f"#{pr}'s merge commit {oid[:12]} does not resolve to a full sha in git")
    issues = sorted(n["number"] for n in d.get("closingIssuesReferences") or ())
    return {"sha": full, "branch": d.get("headRefName") or "", "issues": issues}


def render(pr: int, sha: str, group: str, issues: list) -> str:
    return TEMPLATE.format(pr=pr, sha=sha, group=group,
                           issues=" ".join(f"#{n}" for n in issues) or "none") + "\n"


def body_path(state_dir: Path, pr: int) -> Path:
    d = state_dir / "postmerge"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"record-{pr}.md"


def record(pr: int, repo: str, state_dir: Path, f: dict, group: str, dry: bool, run=sh,
           out=print) -> str:
    """Post (or, dry, print) the comment; the body text. Owed on a refused post."""
    text = render(pr, f["sha"], group, f["issues"])
    path = body_path(state_dir, pr)
    path.write_text(text)
    cmd = [sys.executable, "-I", str(ROOT / "tools/pr/gh_comment.py"), "post", "--repo", repo,
           "--issue", str(RECORD_ISSUE), "--body-file", str(path)]
    if dry:
        out("DRY-RUN comment: " + text.rstrip("\n"))
        out("DRY-RUN command: " + " ".join(cmd))
        return text
    code, o = run(cmd)
    if code != 0:
        raise Owed(f"the #201 comment was refused ({o.strip()[-160:] or 'no output'})")
    return text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("prs", nargs="*", type=int)
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--state-dir", default=os.environ.get("HPO_STATE_DIR")
                    or str(Path.home() / ".local/state/hpo"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.prs:
        ap.error("give at least one <PR>")
    roster, rc = load_roster(), 0
    for pr in a.prs:
        try:
            f = facts(pr, a.repo)
            record(pr, a.repo, Path(a.state_dir), f, resolve_group(roster, f["branch"], pr), a.dry_run)
            print(f"recorded #{pr} {f['sha']}")
        except Owed as e:
            print(f"OWED record #{pr}: {e}")
            rc = 1
    return rc


def self_test() -> int:
    fails, n = [], [0]

    def check(name, ok, got=""):
        n[0] += 1
        if not ok:
            fails.append(f"{name} (got: {got})")
            print("FAIL", fails[-1], flush=True)

    full = "a1b2c3d4" * 5
    roster = {"groups": [
        {"group": "R9-FR-1", "resume": {"branch": "fix/r9-fr-1", "pr": 11}},
        {"group": "R9-FR-10", "resume": {"branch": "fix/r9-fr-10", "pr": 12}},
        {"group": "R10-PRN", "resume": {"pr": 77}}]}
    check("a branch matching a group's resume.branch names that group",
          resolve_group(roster, "fix/r9-fr-10", 5) == "R9-FR-10")
    check("a triage/* branch names no group (null control)",
          resolve_group(roster, "triage/s9-batch92", 5) == NO_GROUP)
    check("a record/autofix branch names no group",
          resolve_group(roster, "record/autofix-3", 5) == NO_GROUP)
    check("a guessed-name branch with no group is no-group, not a near match",
          resolve_group(roster, "fix/r9-fr", 5) == NO_GROUP
          and resolve_group(roster, "fix/r9-fr-100", 5) == NO_GROUP)
    check("no branch match, but a group's resume.pr is the merged number: that group",
          resolve_group(roster, "weird/branch", 77) == "R10-PRN")
    check("no roster readable names no group", resolve_group(None, "fix/r9-fr-1", 11) == NO_GROUP)

    def fake(rc_comment=0, state="MERGED", oid=full, resolves=True):
        log = []

        def run(argv, stdin=None, cwd=None):
            log.append(argv)
            j = " ".join(map(str, argv))
            if argv[:3] == ["gh", "pr", "view"]:
                return 0, json.dumps({"state": state, "mergeCommit": {"oid": oid},
                                      "headRefName": "fix/r9-fr-1",
                                      "closingIssuesReferences": [{"number": 9}, {"number": 3}]})
            if "rev-parse" in j:
                return (0, full + "\n") if resolves else (1, "")
            if "gh_comment.py" in j:
                return rc_comment, "refused: read-back differs" if rc_comment else "ok"
            return 0, ""
        return run, log

    with tempfile.TemporaryDirectory() as td:
        run, log = fake()
        f = facts(7, DEFAULT_REPO, run)
        check("the merge sha is the full 40 characters, resolved by git", f["sha"] == full, f)
        check("issues closed by the merge are sorted", f["issues"] == [3, 9], f)
        lines = []
        text = record(7, DEFAULT_REPO, Path(td), f, "R9-FR-1", True, run, lines.append)
        check("the dry run prints the exact comment", lines[0] == "DRY-RUN comment: " + text.rstrip("\n")
              and text == f"Merged #7 {full} (R9-FR-1). Closed issues: #3 #9. Leaves #201 open.\n", lines)
        check("the dry run prints the exact command and posts nothing",
              "gh_comment.py post --repo " + DEFAULT_REPO + " --issue 201 --body-file " in lines[1]
              and not any("gh_comment.py" in " ".join(a) for a in log), lines)
        check("the body file lives under the state directory",
              (Path(td) / "postmerge/record-7.md").read_text() == text)
        record(7, DEFAULT_REPO, Path(td), f, "R9-FR-1", False, run)
        check("a real run posts through gh_comment.py", any("gh_comment.py" in " ".join(a) for a in log))
        # the tick's finder searches the comment text for the full sha
        short = f"Merged #7 {full[:7]} (R9-FR-1). Leaves #201 open."
        check("the tick's finder (full sha in the comment) matches the new comment, not a short-sha one",
              full in text and full not in short)
        bad, _ = fake(rc_comment=1)
        try:
            record(7, DEFAULT_REPO, Path(td), f, "R9-FR-1", False, bad)
            check("a refused comment is owed", False)
        except Owed as e:
            check("a refused comment (read-back mismatch) is owed", "refused" in str(e), e)
        for kw, why in ((dict(state="OPEN"), "not merged"), (dict(resolves=False), "full sha")):
            r2, _ = fake(**kw)
            try:
                facts(7, DEFAULT_REPO, r2)
                check(f"owed: {why}", False)
            except Owed as e:
                check(f"owed: {why}", why in str(e), e)
    print(f"record_beat self-test: {n[0]} checks, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
