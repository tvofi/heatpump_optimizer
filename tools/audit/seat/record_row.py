#!/usr/bin/env python3
"""The record-autofix generator: rows for merges no branch rowed (R9-FR-10).

    python3 tools/audit/seat/record_row.py --enumerate --repo O/R --since v6.7.6
    python3 tools/audit/seat/record_row.py --plan --merges-file F \
        [--roster-ref GITREF | --roster-file PATH]
    python3 tools/audit/seat/record_row.py --apply --plan-file F [--root DIR]
    python3 tools/audit/seat/record_row.py --row-numbers --plan-file F
    python3 tools/audit/seat/record_row.py --write-self-row --pr N [--root DIR]
    python3 tools/audit/seat/record_row.py --self-test

The `record-autofix` job (.github/workflows/tests.yml) drives the three modes
in order: `--enumerate` reads the window's merges off the REST API (the
commit-to-pull-request map `policy_lint --record` reads, then `/pulls/{n}` for
title, state and head branch), `--plan` computes the rows the checked-out tree
still lacks, and `--apply` writes them behind a guarded write set. Stateless
like the other seat tools: every input is a flag, the roster through
`--roster-ref` (a git ref whose `.claude/workflows/wave-r9-groups.json` is
read with `git show`) or `--roster-file`, nothing about a session hardcoded.

WHAT STAYS MANUAL, by design (issue #1952, owner-approved 2026-10-04): the
approving labelled review on the record pull request, and the
`docs/HANDOVER.md` `updated-for:` line -- tied to merges that change owed
work, not every beat, which a job would over-write. This module's write set
cannot express either: `write_rows` refuses every path that is not
`dev/programme/delivery/<N>.md`, so a row can never be appended to the plan's
Delivery-status table (a row at the table's end conflicts every open branch,
and past the freeze `policy_lint` refuses it) nor to the handover.

The generated body closes nothing. GitHub closes issues from a pull request's
body prose, so the generated prose carries no closing keyword before an issue
number anywhere; the record pull request disposes itself as record-class.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_lib  # noqa: E402  the branch-to-group lookup (#1948's product)

_TESTS = Path(__file__).resolve().parents[3] / "tests"
if str(_TESTS) not in sys.path:
    sys.path.insert(0, str(_TESTS))
import delivery_status  # noqa: E402  anchored, mentions, merge_parents

SELF = "tools/audit/seat/record_row.py"
DEFAULT_REPO = "tvofi/heatpump_optimizer"

#: Where a row lives, and the WHOLE write surface. The digits are load-bearing:
#: `dev/programme/delivery/<N>.md` rows <N> through a line anchoring <N> itself, as
#: `tests/delivery_status.py`'s `ROW_ANCHOR` and `policy_lint.mjs`'s
#: `rowAnchor` read it, so a misnamed file rows nobody.
ROW_PATH = re.compile(r"^dev/programme/delivery/(\d+)\.md$")
#: The pre-merge row's title. It names no other pull request. `mentions`
#: reads the whole anchored line, so a second number on it would row a merge
#: this file does not anchor, while `has_row` would still plan that merge.
OPEN_ROW_TITLE = "record: delivery rows (autofix)"

#: The plan of record and the living handover are dispositions a seat writes,
#: never this generator: a row appended to the plan's table sits at the
#: table's end, conflicts every open branch, and past the freeze policy_lint
#: refuses it (delivery-status-tracking.md). They are named here so the guard's
#: refusal can name what it refused.
PLAN_FILE = "dev/programme/plan-2026-09-open-issues.md"
HANDOVER_FILE = "dev/programme/HANDOVER.md"

#: The programme's tracking issue; the beat posts its coordination comment
#: there (delivery-status-tracking.md item 3).
TRACKING_ISSUE = 201

#: GitHub's own closing-keyword families. The generated prose must carry none
#: of them before an issue number, because GitHub closes an issue from a pull
#: request's body prose -- a generated `Closes #N` would close an issue the
#: beat never meant to touch.
CLOSING_KEYWORD = re.compile(
    r"(?i)\b(closes?|closed|fixes?|fixed|resolves?|resolved)\s+#\d+")


class Refuse(Exception):
    """A guard refusal with its reason; the caller prints it, fail-closed."""


# ----------------------------------------------------------------- row facts

def row_line(number: int, title: str, merge_sha: str,
             group: str | None) -> str:
    """The one-line row, in `dev/programme/delivery/<N>.md`'s established shape.

    `- [#N](url) — **merged `sha7`**, <title> (<GROUP>).` The title is a
    GitHub API fact and may carry pipes or newlines: a `|` would read as a
    table cell wherever the line is quoted, and a newline would break the
    one-line rule, so both are flattened -- pipes to `/`, which
    `roster_lib.one_line_brief` does for the same reason.
    """
    safe = " ".join(str(title).split()).replace("|", "/")
    tail = f" ({group})" if group else ""
    return (f"- [#{number}](https://github.com/{DEFAULT_REPO}/pull/{number})"
            f" — **merged `{str(merge_sha)[:7]}`**, {safe}{tail}.")


def row_path(number: int) -> str:
    return f"dev/programme/delivery/{number}.md"


def open_row_line(number: int, title: str) -> str:
    """The row written before the pull request merges.

    ``row_line`` embeds the merge SHA. That SHA does not exist until the
    merge, so this line does not carry one. It anchors ``number`` and says
    the pull request is open. A title that names another pull request is
    refused: ``mentions`` would read it as that pull request's row.
    """
    safe = " ".join(str(title).split()).replace("|", "/")
    if re.search(r"#\d+", safe):
        raise Refuse(
            "a pre-merge row title names a pull request; mentions() would "
            "read that as a row and has_row would not")
    return (f"- [#{int(number)}](https://github.com/{DEFAULT_REPO}/pull/"
            f"{int(number)}) — **open**, {safe}")


def self_row(number: int) -> dict:
    """The record pull request's own row. No merge SHA."""
    line = open_row_line(number, OPEN_ROW_TITLE)
    return {"number": int(number), "path": row_path(int(number)),
            "line": line, "title": OPEN_ROW_TITLE, "merge_sha": "",
            "group": None}


def rowed_line(number: int, text: str) -> bool:
    """Whether `text` anchors <N>. ``delivery_status.anchored``, not a copy."""
    return delivery_status.anchored(number, text)


def has_row(number: int, root: Path) -> bool:
    """Whether <N> carries a row in `root`: its own anchored row file, or a
    mention in the plan of record or the handover. The file half is
    ``anchored``; the prose half is ``mentions``. A number in some other
    row file's title is neither."""
    path = root / row_path(number)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if rowed_line(number, line):
                return True
    texts = []
    for name in (PLAN_FILE, HANDOVER_FILE):
        p = root / name
        if p.exists():
            texts.append(p.read_text(encoding="utf-8"))
    return bool(texts) and delivery_status.mentions(number, texts)


def plan_merges(merges: list[dict], root: Path,
                roster: dict | None = None) -> list[dict]:
    """The rows `merges` still owe in `root`, oldest number first.

    Each merge carries the API facts `--enumerate` printed: `number`, `title`,
    `state`, `head_ref`, `merge_sha`. A merge whose row exists -- because it
    landed on main between enumeration and this call, or because a seat wrote
    it -- is dropped, so a plan is recomputed against the tree it is applied
    to and a main that moved re-derives rather than conflicts. A branch no
    roster group claims rows in the neutral phrasing (no group suffix); a
    seat edits it at approval.
    """
    rows = []
    for m in sorted(merges, key=lambda x: int(x["number"])):
        n = int(m["number"])
        if has_row(n, root):
            continue
        group = roster_lib.group_for_branch(roster, m.get("head_ref") or "") \
            if roster else None
        rows.append({
            "number": n,
            "path": row_path(n),
            "line": row_line(n, m.get("title") or "", m.get("merge_sha") or "",
                             group),
            "title": m.get("title") or "",
            "merge_sha": m.get("merge_sha") or "",
            "group": group,
        })
    return rows


# ---------------------------------------------------------------- write side

def write_rows(rows: list[dict], root: Path) -> list[str]:
    """Write row files behind the guarded write set; returns what was written.

    Every path must match `dev/programme/delivery/<N>.md` -- the plan table, the
    handover, and any other path are refused, not skipped -- and a row file
    that already exists is left alone (the plan was stale, the tree won).
    Each file is exactly one line and a trailing newline: one line can
    neither split a table nor trail one.
    """
    written = []
    for r in rows:
        path = str(r.get("path") or "")
        if not ROW_PATH.match(path):
            raise Refuse(
                f"outside the row writer's grant: {path!r} -- the write set "
                f"is {ROW_PATH.pattern} only ({PLAN_FILE} and {HANDOVER_FILE} "
                "are a seat's dispositions, never this generator's)")
        if not rowed_line(int(r.get("number") or 0), str(r.get("line") or "")):
            raise Refuse(
                f"row for #{r.get('number')} does not anchor its own number: "
                f"{str(r.get('line'))[:60]!r}")
        target = root / path
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(r["line"]) + "\n", encoding="utf-8")
        written.append(path)
    return written


# ------------------------------------------------------------------ the body

def sections(body: str) -> dict:
    """`## Heading` -> text, the same split `checkPrBody` applies.

    The h2 heading grammar's canonical form lives in `policy_lint.mjs`
    (`sections()` there); this reader reads ONLY the headings `pr_body`
    emits, so it parses them with plain string ops and holds no second copy
    of that grammar -- the agreement lane (decision 0003 discovery) refuses
    a governance grammar written twice, and registering a copy beside the
    canonical one would be the weaker repair.
    """
    out: dict = {}
    cur = None
    for line in body.split("\n"):
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = []
            continue
        if cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def _no_closing_where(label: str, text: str) -> None:
    if CLOSING_KEYWORD.search(text):
        raise Refuse(
            f"generated {label} carries a closing keyword before an issue "
            "number; GitHub closes issues from a pull request's body prose, "
            "and the record pull request closes nothing")


def pr_body(head_sha: str, base_sha: str, rows: list[dict]) -> str:
    """The record pull request's body, in the shape `pr-contract` grades.

    Every required heading is content or an explicit `n/a: <reason>`; the
    figures name instruments, never numbers; the Red checks section names the
    red `record` this beat answers; ## Approval keeps the review manual and
    points at the standing round-9 mandate. The head SHA is load-bearing:
    `checkPrBody` refuses a body whose `## Head` does not name the head CI
    runs on, so the caller passes the SHA the row commit was pushed at.
    """
    nums = ", ".join(f"#{r['number']} (`{str(r['merge_sha'])[:7]}`)"
                     for r in rows) or "(none listed)"
    lines = [
        "_Requested by **tvofi**_",
        "",
        "The mechanical record beat (R9-FR-10): delivery rows for the merges "
        "that landed without one, generated from REST API facts by "
        f"`tools/audit/seat/row` automation and written behind a guarded "
        "write set. Rows for merged pull requests " + nums + ". This pull "
        "request disposes itself as record-class (only row files change); a "
        "row whose subject no roster group claimed carries the neutral "
        "phrasing, and a seat edits it at approval. The handover's "
        "updated-for line and the approving review stay manual by design.",
        "",
        "## Head",
        "",
        f"`{head_sha}` (the row commit this pull request opens at, computed "
        f"against main at `{str(base_sha)[:7]}`; a main that moved under the "
        "push is re-derived by the fetch/reset loop, never merged or forced)",
        "",
        "## Figures",
        "",
        "- delivery-status ledger at this head: "
        "`python3 tests/delivery_status.py` -- the instrument; re-derive at "
        "the head.",
        "- each row file is exactly one line anchoring its own pull request "
        "number, never a table row: read back through the same anchor "
        "`policy_lint --record` applies.",
        "",
        "## Mutation proof",
        "",
        "n/a: record-only diff -- every file in this pull request is a "
        "`dev/programme/delivery/<N>.md` row file; there is no production, test or "
        "check code here to mutate.",
        "",
        "## Null control",
        "",
        "n/a: no quantified production claim; the one figure names its "
        "instrument and re-derives at the head.",
        "",
        "## Red checks",
        "",
        "`record` is red on main at the base this beat was computed against: "
        "a rowless merge is the batch interval the record protocol promises, "
        "and this pull request is that batch, which is the answer the "
        "check's own refusal text names. No cheaper detector exists than the "
        "check that already fired; its standing cost is one beat per batch.",
        "",
        "## Forward-carry",
        "",
        "none",
        "",
        "## Friction",
        "",
        "none",
        "",
        "## Approval",
        "",
        "Opened by the hpo-author App; the approving labelled review on this "
        "pull request stays manual (rows on wave branches read into "
        "reviewed work), as does the HANDOVER updated-for line, which this "
        "automation deliberately never writes.",
    ]
    body = "\n".join(lines) + "\n"
    _no_closing_where("body", body)
    return body


def pr_title(rows: list[dict]) -> str:
    nums = ", ".join(f"#{r['number']}" for r in rows)
    return f"record: delivery rows for {nums} (autofix)"


def coord_comment(pr_number: int, rows: list[dict]) -> str:
    """The beat's #201 coordination comment (delivery-status-tracking item 3).

    States what landed and what stayed manual; carries no closing keyword.
    """
    nums = ", ".join(f"#{r['number']} (`{str(r['merge_sha'])[:7]}`)"
                     for r in rows) or "none"
    text = (
        f"record-autofix beat: opened #{pr_number} with delivery rows for "
        f"{nums}, generated from REST API facts "
        "(`tools/audit/seat/record_row.py`). The approving labelled review "
        "on that pull request and the HANDOVER updated-for line stay manual "
        "by design; rows whose branch no roster group claimed carry the "
        "neutral phrasing and need a seat's edit at approval.")
    _no_closing_where("#201 comment", text)
    return text


# --------------------------------------------------------------- enumeration

def _api(repo: str, path: str, token: str) -> object:
    url = f"https://api.github.com/repos/{repo}{path}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "hpo-record-autofix",
    })
    with urllib.request.urlopen(req) as resp:  # nosec - fixed https host
        return json.load(resp)


def enumerate_merges(repo: str, since: str, token: str) -> list[dict]:
    """The window's merged pull requests, from the REST API, oldest first.

    The window is `<since>..HEAD` over the FIRST-PARENT log -- the same window
    `record` reads -- and each first-parent merge commit is attributed through
    `/commits/<sha>/pulls`, the commit-to-pull-request map, then `/pulls/<n>`
    for the title, state and head branch the rows carry. A commit the map
    cannot attribute is REFUSED, not skipped: a collection that cannot read
    the window must fail this run, never report an empty one.
    """
    span = f"{since}..HEAD" if since else "HEAD"
    log = subprocess.run(
        ["git", "log", "--first-parent", "--format=%H%x1f%P", span],
        check=True, capture_output=True, text=True).stdout.splitlines()
    # A single-parent first-parent commit is a direct push and owes no row.
    # `merge_parents` is `collect`'s predicate: a two-parent commit is a
    # merged pull request and is never skipped, the record beat included.
    # Skipping that beat here while `collect` still ages it is the loop.
    # The beat's own row is `self_row`, written once its number exists.
    merges = []
    for line in log:
        sha, _, parents = line.partition("\x1f")
        if not delivery_status.merge_parents(len(parents.split())):
            continue
        pulls = _api(repo, f"/commits/{sha}/pulls", token) or []
        # The endpoint answers `merged: null` on this surface, so the merge
        # that landed on main is matched by its OWN merge_commit_sha -- the
        # commit-to-pull-request map's authoritative join, true for both the
        # merge-commit and the squash shape.
        matched = [p for p in pulls
                   if (p.get("merge_commit_sha") or "") == sha]
        if not matched:
            raise Refuse(
                f"merge commit {sha[:7]} attributes to no pull request via "
                "the REST API; the window is UNCHECKED this run, not "
                "confirmed empty")
        pr = _api(repo, f"/pulls/{matched[0]['number']}", token)
        merges.append({
            "number": int(pr["number"]),
            "title": pr.get("title") or "",
            "state": pr.get("state") or "",
            "head_ref": (pr.get("head") or {}).get("ref") or "",
            "merge_sha": pr.get("merge_commit_sha") or sha,
        })
    merges.sort(key=lambda m: m["number"])
    return merges


# ----------------------------------------------------------------- entry CLI

def _load_roster(args) -> dict | None:
    if getattr(args, "roster_file", None):
        return roster_lib.load_roster_file(args.roster_file)
    if getattr(args, "roster_ref", None):
        return roster_lib.show_roster(".", args.roster_ref)
    return None


def self_test() -> int:
    """Offline: every trap the issue names, driven from fixtures."""
    fails: list[str] = []

    def ok(name: str, cond: bool) -> None:
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # the row: shape, pipe safety, one line
        line = row_line(2052, "fix: a | piped title", "3f7ed8161234",
                        "R9-FR-4")
        ok("row shape", rowed_line(2052, line) and "|" not in line
           and "\n" not in line and line.endswith("(R9-FR-4)."))
        neutral = row_line(2053, "policy: hotfix", "451a078f9876", None)
        ok("neutral row", rowed_line(2053, neutral)
           and neutral.endswith("hotfix."))
        # the write set: row files only. Each bad path carries a well-formed
        # anchored line, so only the path guard can refuse it -- a line-shape
        # refusal here would read exactly like a passing path guard.
        _good_line = row_line(2052, "fix: one", "a" * 40, None)
        (root / "docs/delivery").mkdir(parents=True)
        for _bad in (PLAN_FILE, HANDOVER_FILE, "dev/programme/delivery/1.md.bak"):
            try:
                write_rows([{"number": 2052, "path": _bad,
                             "line": _good_line}], root)
                ok(f"{_bad} refused", False)
            except Refuse:
                pass
        try:
            write_rows([{"number": 1, "path": "dev/programme/delivery/1.md",
                         "line": "not anchored"}], root)
            ok("unanchored line refused", False)
        except Refuse:
            pass
        # plan/apply: idempotent, re-derives, numbers only its own
        merges = [
            {"number": 2052, "title": "fix: one", "state": "merged",
             "head_ref": "fix/r9-fr-4", "merge_sha": "a" * 40},
            {"number": 2053, "title": "fix: two", "state": "merged",
             "head_ref": "claude/x", "merge_sha": "b" * 40},
        ]
        plan1 = plan_merges(merges, root, roster=None)
        ok("plan both", [r["number"] for r in plan1] == [2052, 2053])
        ok("plan paths", all(ROW_PATH.match(r["path"]) for r in plan1))
        wrote = write_rows(plan1, root)
        ok("wrote both", wrote == ["dev/programme/delivery/2052.md",
                                   "dev/programme/delivery/2053.md"])
        ok("re-plan empty", plan_merges(merges, root, roster=None) == [])
        ok("re-apply empty", write_rows(plan1, root) == [])
        # a row file the anchor does not read is not a disposition
        (root / "dev/programme/delivery/2060.md").write_text(
            "| [#2060](https://github.com/o/r/pull/2060) | merged |\n")
        ok("table shape not a row",
           [r["number"] for r in plan_merges(
               [{"number": 2060, "title": "t", "state": "merged",
                 "head_ref": "", "merge_sha": "c" * 40}], root,
               roster=None)] == [2060])
        # the roster lookup rides roster_lib, one derivation only
        roster = {"groups": [
            {"group": "R9-FR-4", "resume": {"branch": "handoff/r9-fr-4"}},
            {"group": "R9-FR-10", "resume": {}},
        ]}
        ok("lookup exact",
           roster_lib.group_for_branch(roster, "handoff/r9-fr-4") == "R9-FR-4")
        ok("lookup tail",
           roster_lib.group_for_branch(roster, "fix/r9-fr-10") == "R9-FR-10")
        ok("lookup prefix is not a match",
           roster_lib.group_for_branch(roster, "fix/r9-fr-1") is None)
        ok("lookup unknown is neutral",
           roster_lib.group_for_branch(roster, "claude/x") is None)
        grouped = plan_merges(merges[:1], root, roster=roster)
        ok("row already there", grouped == [])  # 2052 rowed above
        fresh = plan_merges([dict(merges[0], number=2061,
                                  head_ref="fix/r9-fr-4")],
                            root, roster=roster)
        ok("group suffix", len(fresh) == 1 and fresh[0]["group"] == "R9-FR-4"
           and fresh[0]["line"].endswith("(R9-FR-4)."))
        fresh2 = plan_merges([dict(merges[0], number=2062,
                                   head_ref="claude/x")],
                             root, roster=roster)
        ok("neutral suffix", len(fresh2) == 1 and fresh2[0]["group"] is None
           and not fresh2[0]["line"].rstrip(".").endswith(")"))
        # the body: sections, closing keywords, table rows, head named
        rows = plan1
        body = pr_body("a" * 40, "0b9c8d7", rows)
        comment = coord_comment(1953, rows)
        secs = sections(body)
        for h in ("Head", "Mutation proof", "Null control", "Figures",
                  "Red checks", "Forward-carry", "Friction", "Approval"):
            ok(f"section {h}", bool(secs.get(h)))
        ok("bare na refused-shape", secs["Mutation proof"].startswith("n/a:"))
        ok("head named", "a" * 40 in secs["Head"])
        ok("red named", "record" in secs["Red checks"])
        ok("approval manual", "hpo-author" in secs["Approval"]
           and HANDOVER_FILE not in body)
        ok("forward-carry none", secs["Forward-carry"] == "none")
        ok("friction none", secs["Friction"] == "none")
        _no_closing_where("self-test body", body)
        ok("no closing keyword", True)
        ok("no table row in body",
           not re.search(r"(?m)^\s*\|", body))
        _no_closing_where("self-test comment", comment)
        ok("comment no closing keyword", True)
        ok("title", pr_title(rows) == "record: delivery rows for #2052, "
                                     "#2053 (autofix)")
        # The record pull request's own row, written before it merges.
        # No merge SHA. Both readers see the anchor. A real unrowed merge,
        # including one this beat will itself be, still plans a row.
        try:
            open_row_line(2002, "record: delivery rows for #2001 (autofix)")
            ok("other number refused", False)
        except Refuse:
            pass
        opened = open_row_line(2002, OPEN_ROW_TITLE)
        ok("open row anchors and carries no merge sha",
           rowed_line(2002, opened) and "**open**" in opened
           and "**merged `" not in opened
           and re.findall(r"#(\d+)", opened) == ["2002"])
        try:
            _self_wrote = write_rows([self_row(2002)], root)
            _self_again = write_rows([self_row(2002)], root)
        except Refuse:
            _self_wrote = _self_again = None
        ok("self row written",
           _self_wrote == ["dev/programme/delivery/2002.md"])
        ok("self row already there", _self_again == [])
        saved_root = delivery_status.ROOT
        delivery_status.ROOT = root
        try:
            texts = delivery_status.read_texts()
        finally:
            delivery_status.ROOT = saved_root
        ok("readers agree the open row is a row",
           has_row(2002, root) and delivery_status.mentions(2002, texts))
        beat = {"number": 2001,
                "title": pr_title([{"number": 2000}]),
                "state": "merged", "head_ref": "record/autofix",
                "merge_sha": "d" * 40}
        ok("an unrowed record merge still plans a row",
           [r["number"] for r in plan_merges([beat], root, roster=None)]
           == [2001])
        ok("readers agree that merge is not rowed by the self-row",
           not has_row(2001, root)
           and not delivery_status.mentions(2001, texts))
        real = {"number": 1887, "title": "fix: a real change",
                "state": "merged", "head_ref": "fix/r9-x",
                "merge_sha": "e" * 40}
        ok("a real unrowed merge still plans a row",
           [r["number"] for r in plan_merges([real], root, roster=None)]
           == [1887])
        ok("one parent is not a merge",
           not delivery_status.merge_parents(1))
        ok("two parents is a merge", delivery_status.merge_parents(2))
        import inspect
        ok("enumerate and collect share the parent predicate",
           "delivery_status.merge_parents" in inspect.getsource(
               enumerate_merges)
           and "merge_parents(" in inspect.getsource(delivery_status.collect))
        led = delivery_status.classify(
            delivery_status.collect([{
                "sha": "a" * 40, "parents": 2,
                "subject": "Merge pull request #2001 from "
                           "tvofi/record/autofix",
                "body": pr_title([{"number": 2000}]),
            }])[0], [])
        ok("ledger still pending a record merge with no row",
           led["merges"][0]["state"] == "pending"
           and led["counts"]["overdue"] == 0)

    if fails:
        print(f"{len(fails)} self-test check(s) failed: "
              + ", ".join(fails))
        return 1
    print("record_row self-test: all checks passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--enumerate", dest="enumerate_", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--row-numbers", action="store_true",
                    help="print the plan's numbers, space-separated")
    ap.add_argument("--print-body", action="store_true",
                    help="print the record pull request body for --plan-file")
    ap.add_argument("--print-title", action="store_true",
                    help="print the record pull request title for --plan-file")
    ap.add_argument("--print-comment", action="store_true",
                    help="print the #201 comment for --plan-file and --pr")
    ap.add_argument("--write-self-row", action="store_true",
                    help="write dev/programme/delivery/<--pr>.md for the open record "
                         "pull request, anchoring its number and carrying no "
                         "merge SHA")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--since", default="")
    ap.add_argument("--merges-file", default="")
    ap.add_argument("--plan-file", default="")
    ap.add_argument("--roster-ref", default="")
    ap.add_argument("--roster-file", default="")
    ap.add_argument("--root", default=".")
    ap.add_argument("--head", default="", help="the pushed head SHA")
    ap.add_argument("--base", default="", help="the main SHA the beat ran on")
    ap.add_argument("--pr", type=int, default=0,
                    help="the record pull request number, for --print-comment")
    ap.add_argument("--token-env", default="GH_TOKEN",
                    help="env var carrying the read token for --enumerate")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.write_self_row:
        if args.pr <= 0:
            print("::error::--write-self-row needs --pr", file=sys.stderr)
            return 2
        written = write_rows([self_row(args.pr)], Path(args.root))
        print("wrote: " + (" ".join(written) if written else "(nothing)"))
        return 0
    if args.enumerate_:
        token = __import__("os").environ.get(args.token_env, "")
        if not token:
            print(f"::error::${args.token_env} is not set; --enumerate "
                  "refuses (fail-closed: an unread window is not an empty "
                  "one)", file=sys.stderr)
            return 2
        merges = enumerate_merges(args.repo, args.since, token)
        print(json.dumps(merges, indent=2))
        return 0
    if args.plan:
        merges = json.loads(Path(args.merges_file).read_text())
        roster = _load_roster(args)
        plan = plan_merges(merges, Path(args.root), roster=roster)
        print(json.dumps(plan, indent=2))
        return 0
    if args.apply:
        plan = json.loads(Path(args.plan_file).read_text())
        written = write_rows(plan, Path(args.root))
        print("wrote: " + (" ".join(written) if written else "(nothing)"))
        return 0
    if args.print_body:
        plan = json.loads(Path(args.plan_file).read_text())
        sys.stdout.write(pr_body(args.head, args.base, plan))
        return 0
    if args.print_title:
        plan = json.loads(Path(args.plan_file).read_text())
        print(pr_title(plan))
        return 0
    if args.print_comment:
        plan = json.loads(Path(args.plan_file).read_text())
        print(coord_comment(args.pr, plan))
        return 0
    if args.row_numbers:
        plan = json.loads(Path(args.plan_file).read_text())
        print(" ".join(str(r["number"]) for r in plan))
        return 0
    ap.print_usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
