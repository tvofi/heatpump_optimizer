#!/usr/bin/env python3
"""carry_audit.py -- every finding a pull request records names its destination.

    python3 -I tools/audit/carry_audit.py check --body FILE [--comments FILE]
    python3 -I tools/audit/carry_audit.py pr N
    python3 -I tools/audit/carry_audit.py sweep (--prs N,N | --last N) [--from-dir DIR] [--issues]
                                         [--ledger FILE]
    python3 -I tools/audit/carry_audit.py owners REGEX [REGEX ...] [--ledger FILE]
    python3 -I tools/audit/carry_audit.py --self-test
  (before the subcommand: --repo O/R, --briefs-dir DIR, --roster-ref REF, repeatable)

WHY. `dev/governance/rules/finding-propagation.md` requires every finding to
reach an owner, and nothing enforced it: a sweep of round 10 found 39 of 95
findings with none, recorded in a body's `## Friction` or `## Forward-carry`,
in a `Fix review:` verdict's non-blocking notes, in the orchestrator's ledger,
or as an auto-filed issue no group lists. That rule now states the marker:

    Carry: <GROUP> | #<issue> | O<n>[-name] | dismissed: <reason>

AN ITEM (`items()`): fenced code and HTML comments dropped; a section is the
text under one heading; an item is one bullet with its continuation, one
paragraph, or one table row; in `## Friction` a line shaped `<id>: <word>:`
starts an item without a bullet. A FINDING item:
  body     anything under `## Forward-carry` or `## Friction` but `none` or
           `n/a: <reason>`; elsewhere, an item whose heading or first words
           match LEAD (out of scope, residual, distinct finding, follow-up ...);
  verdict  a comment whose first line is `Fix review: <word> <sha>`: an item
           saying NONBLOCK (non-blocking, not a block, minor, deferred ...)
           anywhere; else, outside a section holding the block (a heading
           naming a block, or any heading of a `blocked` verdict), one under a
           NOTE_HEADING (residual, owed, instrument findings ...) or led by LEAD.
  both     a paragraph that is finding-shaped and ends in `:` is a lead: its
           bullets are the items, it is not one. The bus trailer, `RESULT`
           lines and the attribution line never are.

A DESTINATION (`Dests.check`):
  GROUP      a group of the newest roster (`roster_lib`), not done;
  #N         owned: a live group lists it in `issues`/`fixes`, it has a
             `dev/programme/carries/carry-N.json`, or an O-brief's file name
             carries N; with `gh` reads (`pr`, `sweep`) it must also be open;
  O<n>       a brief `O<n>-*.md` (or exactly `O<n>-name.md`) in --briefs-dir
             or $HPO_BRIEFS_DIR; with neither (CI) it passes, printed UNVERIFIED;
  dismissed: a reason of two words or more.
An item is also routed by a `Carry:` elsewhere in the body or a later verdict
that names its id -- `Carry: R10-X (item 1a2b3c4d)`; every refusal prints it.
The id counts only inside that marker's own segment, so a quoted refusal
(`UNROUTED body item <id>`) beside a marker routes nothing. A `Carry:` inside
a code span is a quoted example, never a marker.

`sweep` adds three reads: `--issues`, every open issue nothing owns; given
two `--roster-ref`, every carry or brief text the first holds and the second
lacks (a roster PR cut from the second reverts it without a conflict); and
`--ledger`, every orchestrator-ledger line saying `FINDING:` or `LESSON:`
with no `Carry:` (the ledger's work-queue OWED lines are tasks, not read).
`owners` is the sweep's owner-corpus search. EXIT 0 when every finding item
is routed to a valid destination; `CARRY-AUDIT:` is the summary line;
`--self-test` prints `carry_audit self-test: N checks, 0 failed`. Reads only:
`gh api` GETs, `git show`/`ls-tree`; nothing is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent / "seat"))
import roster_lib  # noqa: E402  (the one reader of which roster, and of done)

CARRIES_DIR = "dev/programme/carries"
REPO = "tvofi/heatpump_optimizer"

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
BULLET = re.compile(r"^( {0,1})(?:[-*+]|\d+[.)])\s+")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}")
FRICTION_ENTRY = re.compile(r"^\s*(?:[-*+]\s+)?`?[A-Za-z0-9_./#-]+`?\s*:\s*`?[a-z-]+`?\s*:")
VERDICT = re.compile(r"^Fix review:\s+\w+\s+[0-9a-f]{7,40}\b")

CARRY_SECTIONS = ("forward-carry", "friction")
# An explicit none: the template's `none` or `n/a: <reason>`. A `none` that goes
# on to record something is not one (#2341's "recorded rather than propagated").
NONE_ITEM = re.compile(r"^\W*(?:none|n/a)\W*$|^\W*n/a\s*:", re.I)
# Not a finding wherever it sits: attribution, the bus trailer, raw RESULT lines.
TRAILER = re.compile(r"^\W*(?:\U0001f916|Co-Authored-By|bus:|Evidence:|RESULT\b)", re.I)
# The words a seat uses for "this is not done here". LEAD keys an item's first
# words (or, in a body, its section heading); NONBLOCK flags a verdict item
# wherever it says so, and is what a blocking section still lets through.
NONBLOCK = re.compile(r"non-?blocking|not blocking|not a block|neither blocks?|does not block"
                      r"|not owed here|owed to the record|\bminor\b|advisory|secondary note|\bdeferred\b", re.I)
LEAD = re.compile(r"(?:(?:a|an|one|two|three)\s+)?(?:out of scope|residuals?\b|distinct finding"
                  r"|not fixed here|known[- ]open|follow-?up|non-?blocking|not blocking"
                  r"|caveat|observation|deferred|advisory|minor\b)|(?:[\w-]+\s+){1,3}residuals?\s*:", re.I)
# A verdict section heading that makes every item under it a note.
NOTE_HEADING = re.compile(NONBLOCK.pattern + r"|residual|\bowed\b|instrument findings"
                          r"|out of scope|follow-?up|^carry\b", re.I)
BLOCK_HEADING = re.compile(r"\bblock", re.I)

CARRY = re.compile(r"(?<![\w-])Carry:")
ITEM_REF = re.compile(r"\(item\s+([0-9a-f]{8})\)")
CODE_SPAN = re.compile(r"(`+)[^\n]*?\1")
GROUP_TOK = re.compile(r"\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\Z")
ISSUE_TOK = re.compile(r"\A#(\d+)\Z")
BRIEF_TOK = re.compile(r"\AO(\d+)(?:-[a-z0-9][a-z0-9-]*)?\Z")


# ------------------------------------------------------------------ parsing
def items(text: str, verdict: bool) -> list[dict]:
    """The finding-shaped items of one markdown text, in order:
    {"id", "section", "text", "flagged"} (every item; `flagged` marks the
    finding-shaped ones)."""
    lines, fenced = [], False
    for ln in text.replace("\r\n", "\n").split("\n"):
        if ln.lstrip().startswith(("```", "~~~")):  # a fence, as tests/doc_claims.py reads one
            fenced = not fenced
            continue
        if not fenced and not ln.lstrip().startswith("<!--"):
            lines.append(ln)
    out: list[dict] = []
    section, cur, kind = "", [], None

    def flush():
        nonlocal cur, kind
        body = "\n".join(cur).strip()
        if body and not TABLE_SEP.match(body):
            out.append({"section": section, "text": body, "kind": kind})
        cur, kind = [], None

    for ln in lines:
        h = HEADING.match(ln)
        if h:
            flush()
            section = h.group(2)
            continue
        if not ln.strip():
            if kind == "table" or kind == "para":
                flush()
            elif kind == "bullet":
                cur.append(ln)
            continue
        if ln.lstrip().startswith("|"):
            flush()
            kind = "table"
            cur = [ln]
            flush()
            continue
        starts = bool(BULLET.match(ln)) or (
            section.strip().lower() == "friction" and FRICTION_ENTRY.match(ln) and not ln.startswith("  "))
        if starts:
            flush()
            kind, cur = "bullet", [ln]
        elif kind == "bullet" and cur and not cur[-1].strip() and not ln.startswith((" ", "\t")):
            flush()
            kind, cur = "para", [ln]
        else:
            if kind is None:
                kind = "para"
            cur.append(ln)
    flush()

    lead_flag = False
    blocked_verdict = verdict and text.lstrip().split(None, 3)[2:3] == ["blocked"]
    for it in out:
        sec = it["section"].strip()
        t = it["text"]
        first = re.sub(r"^[\s>*_`-]*(?:\d+[.)]\s*)?[*_`]*", "", t)
        if it["kind"] != "bullet":
            lead_flag = False
        inherited = lead_flag and it["kind"] == "bullet"
        why = ""
        if TRAILER.match(first) or VERDICT.match(first):
            pass
        elif verdict:
            # The block is owed in this pull request, so a section that holds it
            # -- a block heading, or any heading of a `blocked` verdict -- makes
            # nothing a note unless it says it is not the block.
            block_sec = BLOCK_HEADING.search(sec) and not NONBLOCK.search(sec)
            note_sec = NONBLOCK.search(sec) if blocked_verdict else NOTE_HEADING.search(sec)
            why = ("non-blocking" if NONBLOCK.search(t) else "" if block_sec
                   else "section" if note_sec else "lead" if LEAD.match(first)
                   else "under lead" if inherited else "")
        elif sec.lower() in CARRY_SECTIONS:
            why = "" if NONE_ITEM.match(t) else "section"
        else:
            why = ("section" if LEAD.search(sec) else "lead" if LEAD.match(first)
                   else "under lead" if inherited else "")
        flagged = bool(why)
        it["why"] = why
        it["lead"] = False
        if it["kind"] == "para" and t.rstrip().endswith(":") and flagged:
            lead_flag, it["lead"] = True, True  # a lead: its bullets carry
            flagged = False
        it["flagged"] = flagged
        it["id"] = hashlib.sha1(re.sub(r"\s+", " ", t).encode()).hexdigest()[:8]
    return out


def carry_segments(text: str) -> list[str]:
    """The text of every `Carry:` marker in <text>, each cut at the next `Carry:`
    or the line end; a `Carry:` inside a code span is a quoted example, not one."""
    spans = [m.span() for m in CODE_SPAN.finditer(text)]
    starts = [m.start() for m in CARRY.finditer(text)]
    segs = []
    for i, at in enumerate(starts):
        if any(a <= at < b for a, b in spans):
            continue
        # each `Carry:` up to the next one: a quoted marker earlier on the line
        # must not swallow the real one after it
        segs.append(text[at:starts[i + 1] if i + 1 < len(starts) else len(text)].split("\n", 1)[0])
    return segs


def carry_refs(text: str) -> "tuple[list[str], dict[str, list[str]]]":
    """The destinations of <text>'s markers, and each item id a marker names
    with that marker's destinations: an id counts only as `(item <id>)` inside
    the segment of a marker that names a destination."""
    found, refs = [], {}
    for seg in carry_segments(text):
        ds = seg_dests(seg)
        found += ds
        for ref in ITEM_REF.findall(seg) if ds else []:
            refs.setdefault(ref, ds)
    return found, refs


def carry_dests(text: str) -> list[str]:
    """The destination tokens of every `Carry:` in <text>; [] when none."""
    return carry_refs(text)[0]


def seg_dests(seg: str) -> list[str]:
    """The destination tokens of one marker segment (`Carry: ...`)."""
    rest = seg.split(":", 1)[1].strip().strip("`*_")
    dm = re.match(r"dismissed\s*:\s*(.*)", rest, re.I)
    if dm:
        return ["dismissed:" + dm.group(1).strip().rstrip("`*_ ")]
    found = []
    for tok in re.split(r"[,;|/]\s*|\s+and\s+|\s+", rest):
        tok = tok.strip("`*_().:")
        if not tok or tok.lower() == "item" or re.fullmatch(r"[0-9a-f]{8}", tok):
            continue
        if GROUP_TOK.match(tok) or ISSUE_TOK.match(tok) or BRIEF_TOK.match(tok):
            found.append(tok)
            continue
        break  # prose after the destinations
    return found


# ------------------------------------------------------------ destinations
class Dests:
    """What a destination may name: the roster's groups, the owned issues,
    the out-of-tree briefs, and (with `gh`) each issue's state."""

    def __init__(self, roster: dict, carry_issues: set[int], briefs_dir: str | None = None,
                 issue_state=None) -> None:
        self.groups = roster_lib.groups_of(roster)
        self.owned: dict[int, str] = {n: f"{CARRIES_DIR}/carry-{n}.json" for n in carry_issues}
        for name, g in self.groups.items():
            if roster_lib.is_open(g):
                for n in list(g.get("issues") or []) + list(g.get("fixes") or []):
                    if isinstance(n, int):
                        self.owned.setdefault(n, name)
        self.briefs_dir = briefs_dir
        for f in sorted(Path(briefs_dir).glob("O*-*.md")) if briefs_dir else []:
            for n in re.findall(r"-(\d{3,})(?=[-.])", f.name):  # an O-brief owns the issues its name carries
                self.owned.setdefault(int(n), f.name)
        self.issue_state = issue_state  # callable n -> "open" | "closed" | None

    def check(self, tok: str) -> tuple[bool, str]:
        """(valid, note) for one destination token."""
        if tok.startswith("dismissed:"):
            reason = tok.split(":", 1)[1].strip()
            if len(re.findall(r"[A-Za-z0-9]{2,}", reason)) < 2:
                return False, "`dismissed:` needs a reason of two words or more"
            return True, ""
        if m := ISSUE_TOK.match(tok):
            n = int(m.group(1))
            if n not in self.owned:
                return False, (f"#{n} has no owner: no live roster group lists it and there is no "
                               f"{CARRIES_DIR}/carry-{n}.json")
            if self.issue_state and (st := self.issue_state(n)) not in (None, "open"):
                return False, f"#{n} is {st}"
            return True, ""
        if m := BRIEF_TOK.match(tok):
            if not self.briefs_dir:
                return True, f"{tok} UNVERIFIED (no --briefs-dir / $HPO_BRIEFS_DIR)"
            d = Path(self.briefs_dir)
            hits = [d / f"{tok}.md"] if "-" in tok else sorted(d.glob(f"{tok}-*.md"))
            if not any(h.is_file() for h in hits):
                return False, f"no brief {tok}{'' if '-' in tok else '-*'}.md in {self.briefs_dir}"
            return True, ""
        g = self.groups.get(tok)
        if g is None:
            return False, f"{tok} is not a group of the roster"
        if not roster_lib.is_open(g):
            return False, f"{tok} is done (resume.stage {(g.get('resume') or {}).get('stage')})"
        return True, ""


def load_dests(repo: Path = ROOT, ref: str | None = None, briefs_dir: str | None = None,
               issue_state=None) -> Dests:
    # A carry file's destination issue is its own `issue` field (brief_lint.mjs
    # owns the file-name grammar and refuses a name that disagrees with it).
    if ref:
        roster = roster_lib.show_roster(str(repo), ref)
        r = subprocess.run(["git", "-C", str(repo), "ls-tree", "--name-only", ref, CARRIES_DIR + "/"],
                           capture_output=True, text=True)
        texts = [subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{n}"], capture_output=True,
                                text=True).stdout for n in r.stdout.split() if n.endswith(".json")]
    else:
        roster = roster_lib.load_roster_file(str(repo / roster_lib.roster_path(str(repo))))
        texts = [p.read_text() for p in sorted((repo / CARRIES_DIR).glob("*.json"))]
    carry = set()
    for t in texts:
        try:
            n = json.loads(t).get("issue")
        except (ValueError, AttributeError):
            continue
        if isinstance(n, int):
            carry.add(n)
    return Dests(roster, carry, briefs_dir or os.environ.get("HPO_BRIEFS_DIR"), issue_state)


# ---------------------------------------------------------------- the audit
def finding_rows(body: str, comments: list[dict]) -> "tuple[list[dict], dict]":
    """The finding items of a body and its verdict comments, each with the
    destinations its own `Carry:` names, and the item ids routed by reference."""
    texts = [("body", body or "", False)]
    for c in comments:
        b = c.get("body") or ""
        if VERDICT.match(b.lstrip()):
            texts.append((f"review {c.get('id')}", b, True))
    rows, refs = [], {}
    for where, text, verdict in texts:
        for it in items(text, verdict):
            ds, named = carry_refs(it["text"])
            for ref, rds in named.items():
                refs.setdefault(ref, rds)
            if it["flagged"]:
                rows.append({"where": where, **it, "dests": ds})
    return rows, refs


def audit(body: str, comments: list[dict], dests: Dests) -> dict:
    """Every finding item of a body and its verdict comments, each with its
    disposition: routed (with its destinations), unrouted, or bad."""
    rows, refs = finding_rows(body, comments)
    for r in rows:
        if not r["dests"] and r["id"] in refs:
            r["dests"], r["via"] = refs[r["id"]], "item ref"
        bad, notes = [], []
        for tok in r["dests"]:
            ok, note = dests.check(tok)
            (notes if ok else bad).append(f"{tok}: {note}" if note else tok)
        r["bad"], r["notes"] = bad, notes
        r["status"] = "unrouted" if not r["dests"] else ("bad" if bad else "routed")
    return {"rows": rows}


def report(res: dict, label: str = "") -> int:
    rows = res["rows"]
    for r in rows:
        snip = re.sub(r"\s+", " ", r["text"])[:110]
        sec = f" (## {r['section']})" if r["section"] else ""
        if r["status"] == "unrouted":
            print(f"UNROUTED {label}{r['where']} item {r['id']}{sec} [{r['why']}]: {snip!r}")
        elif r["status"] == "bad":
            print(f"BAD-DEST {label}{r['where']} item {r['id']}: {'; '.join(r['bad'])}")
        for n in r["notes"]:
            if "UNVERIFIED" in n:
                print(f"NOTE {label}{r['where']} item {r['id']}: {n}")
    u = sum(r["status"] == "unrouted" for r in rows)
    b = sum(r["status"] == "bad" for r in rows)
    print(f"CARRY-AUDIT{(' ' + label.strip()) if label else ''}: {len(rows)} finding item(s): "
          f"{len(rows) - u - b} routed, {u} unrouted, {b} bad destination(s)")
    return 1 if (u or b) else 0


# ------------------------------------------------------------------- reads
def gh_json(path: str, paginate: bool = False):
    argv = ["gh", "api", *(["--paginate", "--slurp"] if paginate else []), path]
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"carry_audit: REFUSED gh api {path}: {(r.stderr or r.stdout).strip()[:200]}")
    data = json.loads(r.stdout)
    if paginate:
        data = [x for page in data for x in page]
    return data


def gh_issue_state(repo: str):
    cache: dict[int, str | None] = {}

    def state(n: int) -> str | None:
        if n not in cache:
            cache[n] = gh_json(f"repos/{repo}/issues/{n}").get("state")
        return cache[n]
    return state


def read_pr(n: int, repo: str, from_dir: str | None) -> tuple[str, list[dict]]:
    if from_dir:
        b = Path(from_dir, "bodies", f"{n}.md")
        c = Path(from_dir, "comments", f"{n}.json")
        body = b.read_text() if b.is_file() else ""
        comments = json.loads(c.read_text()) if c.is_file() and c.stat().st_size else []
        if comments and isinstance(comments[0], list):
            comments = [x for page in comments for x in page]
        return body, comments
    body = gh_json(f"repos/{repo}/pulls/{n}").get("body") or ""
    return body, gh_json(f"repos/{repo}/issues/{n}/comments?per_page=100", paginate=True)


def unowned_issues(repo: str, dests: Dests) -> list[tuple[int, str]]:
    issues = gh_json(f"repos/{repo}/issues?state=open&per_page=100", paginate=True)
    return [(i["number"], i.get("title") or "") for i in issues
            if "pull_request" not in i and i["number"] not in dests.owned]


def roster_drift(repo: Path, refs: list[str]) -> list[str]:
    """A carry or brief the first roster ref holds that a later one lacks:
    a roster pull request cut from the later ref reverts it with no conflict."""
    out = []
    rosters = [(ref, roster_lib.groups_of(roster_lib.show_roster(str(repo), ref))) for ref in refs]
    (ref0, g0), rest = rosters[0], rosters[1:]
    for ref, gs in rest:
        for name, g in g0.items():
            other = gs.get(name, {})
            for c in g.get("carry") or []:
                if c not in (other.get("carry") or []):
                    out.append(f"ROSTER-DRIFT {name}: a carry on {ref0} is missing on {ref}: {c[:90]!r}")
            if g.get("brief") and other.get("brief") is not None and g["brief"] not in other["brief"]:
                out.append(f"ROSTER-DRIFT {name}: {ref} lacks part of the brief {ref0} holds")
    return out


# A ledger line that records a finding, as the orchestrator writes one: the
# work queue's OWED/QUEUED lines are tasks, not findings, and are not read (a
# key on OWED printed 31 lines over round 10's SEATS.md, one a finding).
LEDGER_FINDING = re.compile(r"\b(?:FINDING|LESSON):")


def ledger_unrouted(text: str) -> list[str]:
    """Each ledger line saying FINDING: or LESSON: with no `Carry:` on it."""
    return [f"LEDGER-UNROUTED l{k}: {ln.strip()[:110]!r}"
            for k, ln in enumerate(text.splitlines(), 1)
            if LEDGER_FINDING.search(ln) and not carry_dests(ln)]


# ---------------------------------------------------------------- the owners
def owner_corpus(repo: Path = ROOT, ref: str | None = None, briefs_dir: str | None = None,
                 ledger: str | None = None) -> list[tuple[str, str]]:
    """Where an owner can hold a finding: every roster group's brief, carry,
    architect note, resume, findings and files; each O-brief; the ledger;
    each carry file (the sweep's own.py)."""
    roster = (roster_lib.show_roster(str(repo), ref) if ref else
              roster_lib.load_roster_file(str(repo / roster_lib.roster_path(str(repo)))))
    out = []
    for g in roster.get("groups", []):
        for k in ("brief", "carry", "architect_note", "resume", "findings", "files", "rca"):
            v = g.get(k)
            if v is not None:
                out.append((f"roster:{g['group']}.{k}", v if isinstance(v, str) else json.dumps(v)))
    bd = briefs_dir or os.environ.get("HPO_BRIEFS_DIR")
    for f in sorted(Path(bd).glob("*.md")) if bd else []:
        out.append(("brief:" + f.name, f.read_text()))
    if ledger:
        out.append(("ledger", Path(ledger).read_text()))
    for f in sorted((repo / CARRIES_DIR).glob("carry-*.json")):
        out.append(("carryfile:" + f.name, f.read_text()))
    return out


# ------------------------------------------------------------------- the CLI
def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    p = argparse.ArgumentParser(prog="carry_audit.py")
    p.add_argument("--repo", default=REPO)
    p.add_argument("--briefs-dir")
    p.add_argument("--roster-ref", action="append", default=[])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--body", required=True)
    c.add_argument("--comments")
    r = sub.add_parser("pr")
    r.add_argument("n", type=int)
    s = sub.add_parser("sweep")
    s.add_argument("--prs")
    s.add_argument("--last", type=int)
    s.add_argument("--from-dir")
    s.add_argument("--issues", action="store_true")
    s.add_argument("--ledger", help="the orchestrator's ledger: FINDING:/LESSON: lines need a Carry:")
    o = sub.add_parser("owners")
    o.add_argument("pattern", nargs="+")
    o.add_argument("--ledger")
    a = p.parse_args(argv)
    ref = a.roster_ref[0] if a.roster_ref else None
    try:
        if a.cmd == "check":
            dests = load_dests(ROOT, ref, a.briefs_dir)
            comments = json.loads(Path(a.comments).read_text()) if a.comments else []
            return report(audit(Path(a.body).read_text(), comments, dests))
        if a.cmd == "pr":
            dests = load_dests(ROOT, ref, a.briefs_dir, gh_issue_state(a.repo))
            body, comments = read_pr(a.n, a.repo, None)
            return report(audit(body, comments, dests), f"#{a.n} ")
        if a.cmd == "owners":
            corpus = owner_corpus(ROOT, ref, a.briefs_dir, a.ledger)
            for pat in a.pattern:
                print("##", pat)
                for name, s_ in corpus:
                    if m := re.search(pat, s_, re.I):
                        print("  ", name, "::", s_[max(0, m.start() - 80):m.end() + 120].replace("\n", " "))
            return 0
        # sweep
        online = not a.from_dir
        dests = load_dests(ROOT, ref, a.briefs_dir, gh_issue_state(a.repo) if online else None)
        if a.prs:
            prs = [int(x) for x in a.prs.split(",") if x.strip()]
        elif a.last:
            pulls = gh_json(f"repos/{a.repo}/pulls?state=closed&per_page=100", paginate=True)
            prs = [x["number"] for x in sorted(
                (x for x in pulls if x.get("merged_at")), key=lambda x: x["merged_at"], reverse=True)][:a.last]
        else:
            prs = []
        rc, total = 0, {"rows": []}
        for n in prs:
            body, comments = read_pr(n, a.repo, a.from_dir)
            res = audit(body, comments, dests)
            for row in res["rows"]:
                row["where"] = f"#{n} {row['where']}"
            total["rows"] += res["rows"]
        rc |= report(total)
        extra = []
        if a.issues:
            extra += [f"ISSUE-UNOWNED #{n} {t[:90]!r}" for n, t in unowned_issues(a.repo, dests)]
        if len(a.roster_ref) > 1:
            extra += roster_drift(ROOT, a.roster_ref)
        if a.ledger:
            extra += ledger_unrouted(Path(a.ledger).read_text())
        for line in extra:
            print(line)
        print(f"CARRY-SWEEP: {len(prs)} pull request(s), {len(extra)} other unowned finding(s)")
        return 1 if (rc or extra) else 0
    except roster_lib.RosterNotFound as e:
        print(f"carry_audit: REFUSED {e}")
        return 2


# --------------------------------------------------------------- self-test
def _self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
        else:
            failed += 1
            print(f"FAIL {name}")

    roster = {"groups": [
        {"group": "R10-LIVE", "issues": [100], "fixes": [101], "resume": {"stage": "not-started"}},
        {"group": "R10-OVER", "issues": [200], "fixes": [], "resume": {"stage": "done"}},
    ]}
    tmp = tempfile.TemporaryDirectory()
    Path(tmp.name, "O7-same-sha.md").write_text("brief\n")
    D = Dests(roster, {300}, tmp.name)
    Dci = Dests(roster, {300}, None)

    def run(body: str, comments=(), d=D) -> dict:
        res = audit(body, list(comments), d)
        res["u"] = sum(r["status"] == "unrouted" for r in res["rows"])
        res["b"] = sum(r["status"] == "bad" for r in res["rows"])
        return res

    head = "## Head\n\nabc\n\n"
    plant = head + "## Friction\n\n- fixer.md: unclear: step 2 offers a disposition that pins nothing.\n"
    r = run(plant)
    check("a planted body with an unrouted Friction finding refuses", r["u"] == 1 and r["b"] == 0)
    r = run(plant.rstrip() + " Carry: R10-LIVE\n")
    check("the same body with a Carry: to a live group passes (null control)", r["u"] == 0 and r["b"] == 0
          and len(r["rows"]) == 1)
    r = run(plant.rstrip() + " Carry: R10-INVENTED\n")
    check("an invented group name is a bad destination", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: R10-OVER\n")
    check("a done group is a bad destination", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: #100\n")
    check("an issue a live group lists is a destination", r["u"] == 0 and r["b"] == 0)
    r = run(plant.rstrip() + " Carry: #300\n")
    check("an issue with a carry file is a destination", r["u"] == 0 and r["b"] == 0)
    r = run(plant.rstrip() + " Carry: #200\n")
    check("an issue only a done group lists has no owner", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: #999\n")
    check("an issue no group lists has no owner (the L20 shape)", r["b"] == 1)
    Dst = Dests(roster, {300}, tmp.name, lambda n: "closed")
    r = run(plant.rstrip() + " Carry: #300\n", d=Dst)
    check("with gh reads, a closed issue is a bad destination", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: O7\n")
    check("an O-brief that exists is a destination", r["u"] == 0 and r["b"] == 0)
    r = run(plant.rstrip() + " Carry: O99\n")
    check("an O-brief that does not exist is a bad destination", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: O99\n", d=Dci)
    check("without a briefs dir an O-brief passes UNVERIFIED", r["b"] == 0
          and any("UNVERIFIED" in n for n in r["rows"][0]["notes"]))
    r = run(plant.rstrip() + " Carry: O7-same-sha\n")
    check("an O-brief named in full is a destination", r["u"] == 0 and r["b"] == 0)
    r = run(plant.rstrip() + " Carry: O7-other\n")
    check("an O-brief named in full that does not exist is a bad destination", r["b"] == 1)
    Path(tmp.name, "O10-rca-friction-2331-2353.md").write_text("brief\n")
    Dob = Dests(roster, set(), tmp.name)
    r = run(plant.rstrip() + " Carry: #2353\n", d=Dob)
    check("an O-brief owns the issues its file name carries", r["b"] == 0 and r["u"] == 0)
    r = run(plant.rstrip() + " Carry: #2354\n", d=Dob)
    check("... and no other issue (null control)", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: dismissed: host load, not a defect\n")
    check("dismissed with a reason is a destination", r["u"] == 0 and r["b"] == 0)
    r = run(plant.rstrip() + " Carry: dismissed:\n")
    check("a bare dismissed is refused", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: R10-LIVE, #999\n")
    check("every destination of a list must hold", r["b"] == 1)
    r = run(head + "## Friction\n\nnone\n\n## Forward-carry\n\n`none`\n")
    check("`none` sections carry no finding", r["rows"] == [])
    r = run(head + "## Friction\n\nfixer.md: unclear: one.\ngate-scoping.md: cost: two. Carry: R10-LIVE\n")
    check("an unbulleted Friction line is its own item (one routed, one not)",
          len(r["rows"]) == 2 and r["u"] == 1)
    r = run(head + "## Forward-carry\n\n`none`. One observation, recorded rather than propagated: x.\n")
    check("a Forward-carry that starts `none` and records an observation is a finding (L05)", r["u"] == 1)
    r = run(head + "## Figures\n\n```\n## Friction\n- a: unclear: fenced\n```\n")
    check("fenced code is not an item", r["rows"] == [])
    r = run(head + "## Figures\n\n- **Out of scope:** the tracked-file scrub.\n- a figure\n")
    check("an out-of-scope lead in another section is a finding; a figure is not",
          len(r["rows"]) == 1 and r["u"] == 1)
    r = run(head + "## Figures\n\nThe residual 2 are documented.\n")
    check("a body word mid-sentence is not a lead (no over-fire)", r["rows"] == [])
    v = {"id": 42, "body": "Fix review: merge " + "a" * 40 + "\n\n## Verified\n\n- M5 is pinned.\n\n"
         "Non-blocking notes, not owed here:\n- (a) a prose duplicate.\n- (b) a re-booking.\n"}
    r = run(head, [v])
    check("a verdict's non-blocking lead flags its bullets, not itself and not ## Verified",
          len(r["rows"]) == 2 and r["u"] == 2)
    vid = r["rows"][0]["id"]
    r = run(head + f"## Forward-carry\n\n- the prose duplicate. Carry: R10-LIVE (item {vid})\n", [v])
    check("an item routed by reference from the body counts as routed", r["u"] == 1 and r["b"] == 0)
    v2 = {"id": 43, "body": "Fix review: blocked " + "b" * 40 + "\n\n## Why blocked\n\n"
          "1. **Blocking**: the arm is untested.\n2. **Minor, not blocking**: sys.path.insert per call.\n"}
    r = run(head, [v2])
    check("in a blocked verdict, only the non-blocking item is a finding", len(r["rows"]) == 1)
    v3 = {"id": 45, "body": "Fix review: blocked " + "c" * 40 + "\n\n## (a) Residual statement: not exact\n\n"
          "- the body's residual text over-claims.\n\n## Other checks\n\n- Stub-selector residual: honestly "
          "stated.\n- A minor point that does not block: x.\n\nbus: verdict/1 at abc, confirmed\n"}
    r = run(head, [v3])
    check("a blocked verdict: a residual heading is the block; a residual lead and a minor note are not",
          sorted(x["why"] for x in r["rows"]) == ["lead", "non-blocking"])
    r = run(head + "## Friction\n\nn/a: roster state, no production code.\n\n"
            "\U0001f916 Generated with [Claude Code](https://claude.com/claude-code)\n")
    check("`n/a: <reason>` and the attribution trailer are not findings", r["rows"] == [])
    nv = {"id": 44, "body": "bus: verdict/1 at abc\n\nNon-blocking notes: x"}
    r = run(head, [nv])
    check("a comment that is not a `Fix review:` verdict is not read", r["rows"] == [])
    led = ("== 03:50Z train PARKED. LESSON: remove the upd wt before training.\n"
           "REVIEWERS OWED: #7 reviewer.\n"
           "== 04:00Z FINDING: the regex rejects a form. Carry: R10-LIVE\n")
    out = ledger_unrouted(led)
    check("a ledger LESSON: with no Carry: is unrouted; a work-queue OWED line and a routed "
          "FINDING: are not", len(out) == 1 and out[0].startswith("LEDGER-UNROUTED l1:"))
    fr = head + "## Friction\n\n- carry_audit.py: unenforced: nothing reads the ledger key at merge.\n"
    fid = run(fr)["rows"][0]["id"]
    r = run(fr + f"\n## Red checks\n\n- `pr-contract`: it printed `UNROUTED body item {fid} (## Friction)`; "
            "the fold names Carry: R10-LIVE as its example.\n")
    check("a quoted refusal beside an unrelated marker routes nothing (#2404's review)",
          r["u"] == 1 and len(r["rows"]) == 1)
    r = run(fr + f"\n## Red checks\n\n- `pr-contract`: answered. Carry: R10-LIVE (item {fid})\n")
    check("the same id inside the marker, `Carry: R10-LIVE (item <id>)`, routes it (null control)",
          r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
    r = run(head + "## Friction\n\n- PULL_REQUEST_TEMPLATE.md: unenforced: its example "
            "`Carry: R10-LIVE` names a group a fixer copies unchecked.\n")
    check("a backticked example `Carry:` in a finding's prose does not route it", r["u"] == 1)
    r = run(head + "## Friction\n\n- PULL_REQUEST_TEMPLATE.md: unenforced: its example "
            "`Carry: R10-LIVE` names a group a fixer copies unchecked. Carry: R10-LIVE\n")
    check("the same finding with a plain marker routes (null control)", r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
    check("a quoted `Carry: ...` earlier on a line does not hide the real one after it (#2404's body)",
          carry_dests("written `FINDING: x Carry: ...`, which the sweep reads. Carry: R10-LIVE")
          == ["R10-LIVE"])
    check("carry_dests stops at prose", carry_dests("Carry: R10-LIVE because it owns x") == ["R10-LIVE"])
    check("carry_dests reads dismissed whole", carry_dests("Carry: dismissed: host load")
          == ["dismissed:host load"])
    print(f"carry_audit self-test: {passed + failed} checks, {failed} failed")
    tmp.cleanup()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
