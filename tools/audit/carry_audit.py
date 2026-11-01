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
  verdict  a comment whose first line is `Fix review: <word> <sha>`. In a
           FINDINGS SECTION (a heading opening with FINDINGS_HEADING's words:
           Findings, Friction, Block, Residuals, Follow-ups ...), and in every
           section of a `blocked` verdict but `## Evidence`: an item saying
           NONBLOCK (non-blocking, not a block, minor, deferred ...) outside an
           owner-approval merge condition and a negated deferral ("nothing is
           deferred"); else, outside a section holding the block, one under a
           NOTE_HEADING (residual, owed ...) or led by LEAD.
  structural  `## Evidence` of any verdict, and every other section of a merge
           verdict (P308, P314): only an item led by LEAD, under a lead, or
           carrying a `Carry:` marker; no word inside it is read.
  both     a paragraph that is finding-shaped and ends in `:` is a lead: its
           bullets are the items, it is not one. The bus trailer, `RESULT`
           lines and the attribution line never are.

A DESTINATION (`Dests.check`):
  GROUP      a group of the newest roster (`roster_lib`), not done; with no
             --roster-ref, also one open on the round's roster branch
             (`roster_lib.round_ref`), printed NOTE ... resolved on <ref>;
             a checkout lacking origin/main reads the roster there instead of
             its tree, printed NOTE stale tree: <HEAD> lacks origin/main <sha>
             (a shallow clone, or one with no origin/main, keeps its tree);
  #N         owned: a live group lists it in `issues`/`fixes`, it has a
             `dev/programme/carries/carry-N.json`, or an O-brief's file name
             carries N; with `gh` reads (`pr`, `sweep`) it must also be open;
  O<n>       a brief `O<n>-*.md` (or exactly `O<n>-name.md`) in --briefs-dir
             or $HPO_BRIEFS_DIR; with neither (CI) it passes, printed UNVERIFIED;
  dismissed: a reason of two words or more.
An item is also routed by a `Carry:` elsewhere in the body or a later verdict
that names its id -- `Carry: R10-X (item 1a2b3c4d)`; every refusal prints it.
Every marker naming an item adds its destinations, and each must hold.
The id counts only inside that marker's own segment, so a quoted refusal
(`UNROUTED body item <id>`) beside a marker routes nothing. A `Carry:` inside
a code span is a quoted example, never a marker.

`sweep` reads the round's live roster ref when no `--roster-ref` is given
(`roster_lib.reader_ref`; main's copy lags it), and adds three reads:
`--issues`, every open issue nothing owns (`Dests.owns`, the test
`orphaned` asks at a group's done transition in roster_sync.py and
roster_edit.py); given
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
import contextlib
import hashlib
import io
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
# A verdict's `## Evidence` section, and every section of a merge verdict but a
# findings section, is read by its structure alone (P308, P314): a check's
# state or a measurement there says "not blocking" or "deferred" as often as a
# finding does, and the word tuning that freed one shape at a time (P293, P306)
# parked the train on the next. An item there is a finding only when it opens
# with LEAD, sits under a lead, or carries a `Carry:` marker.
EVIDENCE_HEADING = re.compile(r"evidence\b", re.I)
# A findings section: its heading OPENS with one of these words (a declared
# grammar, CARRY 5: `## Body (steps 7, 10, non-blocking note 1)` holds check
# results, not findings, though a NONBLOCK word sits in it). A block heading
# (BLOCK_HEADING, not NONBLOCK) is one too.
FINDINGS_HEADING = re.compile(r"^\W*(?:findings?\b|friction\b|residuals?\b|non-?blocking|not blocking"
                              r"|follow-?ups?\b|out of scope|deferred\b|owed\b|notes?\b|caveats?\b"
                              r"|observations?\b|instrument findings|carry\b)", re.I)
# An owner-approval merge condition (P329): the sentence naming an approving
# review at (or before) the merge, and the one bare sentence after it saying it
# does not block on that, are a merge condition, not a non-blocking note.
APPROVAL = re.compile(r"\bapproving review\b.*\b(?:at|before) (?:the )?merge\b", re.I)
APPROVAL_BARE = re.compile(r"\s*(?:this (?:review|verdict) |this is |it )?(?:flag(?:s|ged)(?: that)?,? (?:and )?)?"
                           r"(?:does not block(?: on it)?|not a block)\s*[.;]?\s*$", re.I)
# A negated deferral, "nothing is deferred or owed", defers nothing (#2955 2471d3e6).
NOTHING = re.compile(r"\bnothing (?:is|was|remains)\b[^.;]*", re.I)
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

# A roster carry index stated as not done, outside the carry sections (R10-RCA-JIDOKA-YIELD,
# M1; #3010 r1: "Carry 1: **not done in this pull request.**" under no heading
# `LEAD` reads). Matched on the item with its code spans and double-quoted text
# removed (`owed_carry`): unstripped, a body quoting the phrase as an example is read.
OWED_CARRY = re.compile(r"\bcarry\s*\[?\d+\]?\W{0,6}[^.\n]{0,80}?\b(?:not done|not (?:built|answered|implemented)"
                        r"|not in this (?:part|diff|pull request|change)|still (?:not met|open|owed)"
                        r"|owed (?:by|to|in))", re.I)
QUOTED = re.compile(r'"[^"\n]*"|\u201c[^\u201d\n]*\u201d')

CARRY = re.compile(r"(?<![\w-])Carry:")
ITEM_REF = re.compile(r"\(item\s+([0-9a-f]{8})\)")
# `Carry: <dest> (item <id>, supersedes <old>)` (P296): retires <old> for that item alone.
SUPERSEDES = re.compile(r"\(item\s+([0-9a-f]{8}),\s*supersedes\s+([^\s),]+)\)")
# a code span as CommonMark closes one: a backtick run closes only on a run of
# exactly its own length, on its line or a later one of the same item
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)")
GROUP_TOK = re.compile(r"\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\Z")
ISSUE_TOK = re.compile(r"\A#(\d+)\Z")
BRIEF_TOK = re.compile(r"\AO(\d+)(?:-[a-z0-9][a-z0-9-]*)?\Z")


# ------------------------------------------------------------------ parsing
def freed(t: str) -> str:
    """<t> less what reads NONBLOCK without being a note: each APPROVAL sentence
    (split on `.` and `;`) with the APPROVAL_BARE sentence right after it, and
    each NOTHING clause."""
    out, after = [], False
    for part in re.split(r"(?<=[.;])", t):
        if APPROVAL.search(part):
            after = True
            continue
        if after and APPROVAL_BARE.match(part):  # only the one sentence after it
            after = False
            continue
        after = False
        out.append(part)
    return NOTHING.sub(" ", "".join(out))


def items(text: str, verdict: bool) -> list[dict]:
    """The finding-shaped items of one markdown text, in order:
    {"id", "section", "text", "flagged"} (every item; `flagged` marks the
    finding-shaped ones)."""
    lines, fenced = [], False
    for ln in text.split("\n"):
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
            if kind == "para":
                flush()
            elif kind == "bullet":
                cur.append("")
            continue
        if ln.lstrip().startswith("|"):
            flush()
            kind = "table"
            cur = [ln]
            flush()
            continue
        starts = bool(BULLET.match(ln)) or (
            section.lower() == "friction" and FRICTION_ENTRY.match(ln) and not ln.startswith("  "))
        if starts:
            flush()
            kind, cur = "bullet", [ln]
        elif cur[-1:] == [""] and not ln.startswith((" ", "\t")):  # a bullet's blank, then no indent
            flush()
            kind, cur = "para", [ln]
        else:
            if kind is None:
                kind = "para"
            cur.append(ln)
    flush()

    lead_flag, lead_sec = False, None
    blocked_verdict = text.split(None, 3)[2:3] == ["blocked"]  # read only for a verdict
    for it in out:
        sec = it["section"]
        t = it["text"]
        first = re.sub(r"^[\s>*_`-]*(?:\d+[.)]\s*)?[*_`]*", "", t)
        # a lead's bullets end at a non-bullet, and at its section's end (CARRY 3, #2645)
        if it["kind"] != "bullet" or sec != lead_sec:
            lead_flag = False
        inherited = lead_flag  # a non-bullet has just reset it
        why = ""
        # The block is owed in this pull request, so a section that holds it
        # -- a block heading, or any heading of a `blocked` verdict -- makes
        # nothing a note unless it says it is not the block.
        block_sec = BLOCK_HEADING.search(sec) and not NONBLOCK.search(sec)
        if TRAILER.match(first) or VERDICT.match(first):
            pass
        elif verdict and (EVIDENCE_HEADING.match(sec)
                          or not (blocked_verdict or block_sec or FINDINGS_HEADING.match(sec))):
            why = ("lead" if LEAD.match(first) else "under lead" if inherited
                   else "carry" if carry_segments(t) else "")
        elif verdict:
            note_sec = NONBLOCK.search(sec) if blocked_verdict else NOTE_HEADING.search(sec)
            why = ("non-blocking" if NONBLOCK.search(freed(t)) else "" if block_sec
                   else "section" if note_sec else "lead" if LEAD.match(first)
                   else "under lead" if inherited else "")
        elif sec.lower() in CARRY_SECTIONS:
            why = "" if NONE_ITEM.match(t) else "section"
        else:
            why = ("section" if LEAD.search(sec) else "lead" if LEAD.match(first)
                   else "under lead" if inherited else "owed carry" if owed_carry(t) else "")
        flagged = bool(why)
        it["why"] = why
        it["lead"] = False
        if it["kind"] == "para" and t.endswith(":") and flagged:
            lead_flag, lead_sec, it["lead"] = True, sec, True  # a lead: its bullets carry
            flagged = False
        it["flagged"] = flagged
        it["id"] = hashlib.sha1(re.sub(r"\s+", " ", t).encode()).hexdigest()[:8]
    return out


def owed_carry(text: str) -> bool:
    """Whether an item states a roster carry as not done, outside code and quotes."""
    bare = CODE_SPAN.sub(" ", text)
    return bool(OWED_CARRY.search(QUOTED.sub(" ", bare)))


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


def carry_refs(text: str) -> "tuple[list[str], dict[str, list[str]], dict[str, list]]":
    """The destinations of <text>'s markers; each item id a marker names, with
    every destination the markers naming it name (an id counts only as
    `(item <id>)` or `(item <id>, supersedes <old>)` inside a marker's own
    segment); and each superseded token, `(old, its marker's destinations)`."""
    found, refs, sups = [], {}, {}
    for seg in carry_segments(text):
        ds = seg_dests(seg)
        found += ds
        for ref in ITEM_REF.findall(seg):
            refs.setdefault(ref, []).extend(ds)
        for ref, old in SUPERSEDES.findall(seg):
            refs.setdefault(ref, []).extend(ds)
            sups.setdefault(ref, []).append((old.strip("`*_.:"), ds))
    return found, refs, sups


def carry_dests(text: str) -> list[str]:
    """The destination tokens of every `Carry:` in <text>; [] when none."""
    return carry_refs(text)[0]


def seg_dests(seg: str) -> list[str]:
    """The destination tokens of one marker segment (`Carry: ...`)."""
    rest = seg.split(":", 1)[1].strip().strip("`*_")
    dm = re.match(r"dismissed\s*:\s*(.*)", rest, re.I)
    if dm:
        return ["dismissed:" + dm.group(1)]
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
    the out-of-tree briefs, and (with `gh`) each issue's state. `round_roster`,
    `(ref, roster)`, is the round's roster branch: finding-propagation.md counts
    a carry to a group open there as in the tree before the group reaches main."""

    def __init__(self, roster: dict, carry_issues: set[int], briefs_dir: str | None = None,
                 issue_state=None, round_roster: tuple[str, dict] | None = None) -> None:
        self.groups = roster_lib.groups_of(roster)
        self.round_ref, self.round_groups = ((round_roster[0], roster_lib.groups_of(round_roster[1]))
                                             if round_roster else (None, {}))
        self.owned: dict[int, str] = {n: f"{CARRIES_DIR}/carry-{n}.json" for n in carry_issues}
        for name, g in self.groups.items():
            if roster_lib.is_open(g):
                for n in issue_numbers(g):
                    self.owned.setdefault(n, name)
        self.briefs_dir = briefs_dir
        for f in sorted(Path(briefs_dir).glob("O*-*.md")) if briefs_dir else []:
            for n in re.findall(r"-(\d{3,})(?=[-.])", f.name):  # an O-brief owns the issues its name carries
                self.owned.setdefault(int(n), f.name)
        self.issue_state = issue_state  # callable n -> "open" | "closed" | None

    def owns(self, n: int) -> bool:
        """THE owned-issue test: a live group lists #n, a carry file is its
        destination, or an O-brief names it. `sweep --issues` reports an open
        issue failing it; a done transition asks it first (`orphaned`)."""
        return n in self.owned

    def check(self, tok: str) -> tuple[bool, str]:
        """(valid, note) for one destination token."""
        if tok.startswith("dismissed:"):
            reason = tok.split(":", 1)[1].strip()
            if len(re.findall(r"[A-Za-z0-9]{2,}", reason)) < 2:
                return False, "`dismissed:` needs a reason of two words or more"
            return True, ""
        if m := ISSUE_TOK.match(tok):
            n = int(m.group(1))
            if not self.owns(n):
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
        g, r = self.groups.get(tok), self.round_groups.get(tok)
        if g is None and r is None:
            return False, f"{tok} is not a group of the roster{f' or of {self.round_ref}' if self.round_ref else ''}"
        if g is not None and roster_lib.is_open(g):
            return True, ""
        if r is not None and roster_lib.is_open(r):
            return True, f"{tok} resolved on {self.round_ref}"
        return False, f"{tok} is done (resume.stage {((g or r).get('resume') or {}).get('stage')})"


def issue_numbers(group: dict) -> list[int]:
    """The issues a group owns: the integers of its `issues` and `fixes`."""
    return [n for n in list(group.get("issues") or []) + list(group.get("fixes") or [])
            if isinstance(n, int)]


def orphaned(dests: Dests, group: dict) -> list[int]:
    """The open issues `group` lists that nothing would own once it is done.

    `sweep --issues`' own test (ISSUE-UNOWNED), asked of one group's issues
    at its done transition instead of after it: `dests` is built from the
    roster as that write will leave it, so the closing group owns nothing
    there and only another live owner keeps an issue. A state the reader
    cannot give counts as open: a group held open is visible on the roster,
    an orphan is visible only to a sweep someone remembers to run."""
    return [n for n in issue_numbers(group)
            if not dests.owns(n)
            and (dests.issue_state(n) if dests.issue_state else None) in (None, "open")]


def carry_issues(repo, ref: str | None = None) -> set[int]:
    """The issues the carry files at `ref` (else the working tree) are the
    destination of: each file's own `issue` field (brief_lint.mjs owns the
    file-name grammar and refuses a name that disagrees with it)."""
    if ref:
        r = subprocess.run(["git", "-C", str(repo), "ls-tree", "--name-only", ref, CARRIES_DIR + "/"],
                           capture_output=True, text=True)
        texts = [subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{n}"], capture_output=True,
                                text=True).stdout for n in r.stdout.split() if n.endswith(".json")]
    else:
        texts = [p.read_text() for p in sorted((Path(repo) / CARRIES_DIR).glob("*.json"))]
    carry = set()
    for t in texts:
        try:
            n = json.loads(t).get("issue")
        except (ValueError, AttributeError):
            continue
        if isinstance(n, int):
            carry.add(n)
    return carry


def load_dests(repo: Path = ROOT, ref: str | None = None, briefs_dir: str | None = None,
               issue_state=None, extra_ref: str | None = None) -> Dests:
    round_roster = None
    git = roster_lib.git_in(str(repo))
    if ref:
        roster = roster_lib.show_roster(str(repo), ref)
    else:
        # A checkout behind origin/main reads main's roster, not its own stale
        # one (P98: a detached checkout 387 commits behind refused groups open
        # on main). One containing it keeps its tree, so a pull request's own
        # new group still counts. Only rc 1 ("not an ancestor") is stale: a
        # clone without origin/main answers 128 and keeps its tree. A shallow
        # clone also keeps it: its walk stops at the graft and answers 1 for an
        # ancestor it cannot reach, so ancestry there is unknowable.
        shallow = git(["rev-parse", "--is-shallow-repository"])[1].strip() == "true"
        if not shallow and git(["merge-base", "--is-ancestor", roster_lib.MAIN_REF, "HEAD"])[0] == 1:
            roster = roster_lib.show_roster(str(repo), roster_lib.MAIN_REF)
            print(f"NOTE stale tree: {git(['rev-parse', 'HEAD'])[1].strip()} lacks {roster_lib.MAIN_REF} "
                  f"{git(['rev-parse', roster_lib.MAIN_REF])[1].strip()}; roster read at {roster_lib.MAIN_REF}")
        else:
            roster = roster_lib.load_roster_file(str(repo / roster_lib.roster_path(str(repo))))
    # The roster at main, or at an explicit ref, lags the round's branch
    # (finding-propagation.md counts a carry landed there), on either path
    # (P319: the pre-flight's explicit origin/main parked two carries the round
    # branch held); a branch this clone lacks is skipped, which only narrows
    # what passes, and a ref that is the round's own is not read twice.
    rref = roster_lib.round_ref(git)
    if rref and rref != ref and not git(["rev-parse", "--verify", "--quiet", rref + "^{commit}"])[0]:
        round_roster = (rref, roster_lib.show_roster(str(repo), rref))
    carry = carry_issues(repo, ref)
    # A pull request that adds its own carry file routes to it (P43): the issues of <extra_ref>'s
    # carry files join the set, read with one local ls-tree; an unreadable ref adds nothing.
    if extra_ref:
        carry |= carry_issues(repo, extra_ref)  # mut:extra
    return Dests(roster, carry, briefs_dir or os.environ.get("HPO_BRIEFS_DIR"), issue_state, round_roster)


# ---------------------------------------------------------------- the audit
def finding_rows(body: str, comments: list[dict]) -> "tuple[list[dict], dict]":
    """The finding items of a body and its verdict comments, each with the
    destinations its own `Carry:` names, and the item ids routed by reference."""
    texts = [("body", body or "", False)]
    for c in comments:
        b = c.get("body") or ""
        if VERDICT.match(b.lstrip()):
            texts.append((f"review {c.get('id')}", b, True))
    rows, refs, sups = [], {}, {}
    for where, text, verdict in texts:
        for it in items(text, verdict):
            ds, named, sup = carry_refs(it["text"])
            for ref, rds in named.items():
                refs.setdefault(ref, []).extend(rds)
            for ref, olds in sup.items():
                sups.setdefault(ref, []).extend(olds)
            if it["flagged"]:
                rows.append({"where": where, **it, "dests": ds})
    return rows, refs, sups


def audit(body: str, comments: list[dict], dests: Dests) -> dict:
    """Every finding item of a body and its verdict comments, each with its
    disposition: routed (with its destinations), unrouted, or bad."""
    rows, refs, sups = finding_rows(body, comments)
    for r in rows:
        r["dests"] = r["dests"] + refs.get(r["id"], [])
        bad, notes = [], []
        # A supersede retires a bad token of this item only, printed, never dropped silently; one
        # naming a valid destination is refused, so a live routing cannot be undone by it (P296).
        for old, new in sups.get(r["id"], []):
            if dests.check(old)[0]:
                bad.append(f"{old}: a supersede names a valid destination (item {r['id']}); only a bad one retires")
            elif old in r["dests"]:
                r["dests"] = [t for t in r["dests"] if t != old]
                notes.append(f"{old} superseded by {', '.join(new) or '-'} (item {r['id']})")
        for tok in r["dests"]:
            ok, note = dests.check(tok)
            (notes if ok else bad).append(f"{tok}: {note}" if note else tok)
        r["bad"], r["notes"] = bad, notes
        r["status"] = "bad" if bad else "unrouted" if not r["dests"] else "routed"
    return {"rows": rows}


# ------------------------------------------------------------ the landing
def group_text(dests: Dests, group: str) -> str:
    """A group's brief and carries, on main's roster and on the round's branch."""
    out = []
    for g in (dests.groups.get(group), dests.round_groups.get(group)):
        if g:
            out += [str(g.get("brief") or "")] + [str(c) for c in (g.get("carry") or [])]
    return "\n".join(out)


def landed(body: str, dests: Dests, source: str = "") -> list[dict]:
    """Each (finding item, GROUP destination) of a body whose group's brief or
    carries hold neither the item id nor the source (`#<pr>` or the handoff
    topic: P310, an id re-minted by a reword still lands by its source), or
    whose group is no valid destination. A `dismissed:` item, a `#N` and an
    O-brief need no landing. Each: {"group", "id", "text", "why"}."""
    out = []
    srcs = [x for x in re.split(r"[\s,]+", source) if x]
    for r in audit(body, [], dests)["rows"]:
        for tok in r["dests"]:
            if not GROUP_TOK.match(tok):
                continue
            ok, note = dests.check(tok)
            if not ok:
                out.append({"group": tok, "id": r["id"], "text": r["text"], "why": f"bad destination: {note}"})
                continue
            words = set(re.split(r"[^\w#-]+", group_text(dests, tok)))  # whole tokens: #25581 is not #2558
            keys = [r["id"]] + srcs
            if not any(k in words for k in keys):  # mut:landed
                out.append({"group": tok, "id": r["id"], "text": r["text"], "why": "not in its brief or carries"})
    return out


def land_ops(missing: list[dict], pr: str = "", topic: str = "") -> list[str]:
    """roster_edit.py's append-carry op for each missing landing a carry can
    make (never a bad destination), tagged `(items <id>)`, one per tag."""
    ops, seen = [], set()
    src = f"From {pr} ({topic})" if pr and topic else f"From {pr or topic or 'this pull request'}"
    for m in missing:
        if m["why"].startswith("bad destination") or (m["group"], m["id"]) in seen:
            continue
        seen.add((m["group"], m["id"]))
        one = re.sub(r"^[-*+]\s+", "", re.sub(r"\s+", " ", m["text"]).strip())
        text = f"{src}, body item {m['id']}: {one} (items {m['id']})"
        ops.append("append-carry " + m["group"] + " '" + text.replace("'", "'\\''") + "'")
    return ops


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


def issue_reader(repo: str, path: str | None = None):
    """n -> "open" | "closed" | None: the recorded states in `path`
    (`{"<n>": "open" | "closed"}`, a ValueError when it does not read; an
    issue it does not name is None), else one cached `gh api` read per issue."""
    if not path:
        return gh_issue_state(repo)
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"--issue-state {path}: {e}")
    if not isinstance(data, dict):
        raise ValueError(f"--issue-state {path}: not an object")
    return lambda n: data.get(str(n))


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
            if "pull_request" not in i and not dests.owns(i["number"])]


def sweep_ref(repo: Path, ref: str | None) -> str:
    """The roster a sweep reads: `--roster-ref` when given, else the round's
    live roster ref (`roster_lib.reader_ref`, its note on stderr), never main's
    copy: main lags the round's edits, so a group done on the live ref but open
    on main would still own its issues there (#2492's and #2731's miss)."""
    return roster_lib.reader_ref(str(repo), ref)


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
    p.add_argument("--git-dir", default=str(ROOT), help="the checkout whose refs the roster is read at")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--body", required=True)
    c.add_argument("--comments")
    for name in ("landed", "land-ops"):
        x = sub.add_parser(name)
        x.add_argument("--body", required=True)
        x.add_argument("--pr", default="", help="the source pull request, #<N>")
        x.add_argument("--topic", default="", help="the source handoff topic")
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
            body = Path(a.body).read_text()
            comments = json.loads(Path(a.comments).read_text()) if a.comments else []
            if not finding_rows(body, comments)[0]:
                return report({"rows": []})  # nothing to route: the roster is not read
            dests = load_dests(Path(a.git_dir), ref, a.briefs_dir)
            return report(audit(body, comments, dests))
        if a.cmd in ("landed", "land-ops"):
            # rc 0 every carry landed, 1 one is missing (CARRY-MISSING lines), 3 the roster unreadable
            try:
                dests = load_dests(Path(a.git_dir), ref, a.briefs_dir)
            except (roster_lib.RosterNotFound, ValueError, OSError) as e:
                print(f"carry_audit: UNREAD the roster: {e}")
                return 3
            missing = landed(Path(a.body).read_text(), dests, f"{a.pr} {a.topic}")
            if a.cmd == "land-ops":
                for op in land_ops(missing, a.pr, a.topic):
                    print(op)
                return 1 if missing else 0
            for m in missing:
                one = re.sub(r"\s+", " ", m["text"])[:100]
                print(f"CARRY-MISSING {m['group']} body item {m['id']}: {m['why']}: {one!r}")
            print(f"CARRY-LANDED: {len(missing)} missing")
            return 1 if missing else 0
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
        online = not a.from_dir
        dests = load_dests(ROOT, sweep_ref(ROOT, ref), a.briefs_dir,
                           gh_issue_state(a.repo) if online else None)
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
        {"group": "R10-STALE", "issues": [400], "fixes": [], "resume": {"stage": "in-progress"}},
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

    def first_id(res: dict) -> str:  # a mutant that reads no row fails checks, never crashes them
        return res["rows"][0]["id"] if res["rows"] else "-"

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
          and any("UNVERIFIED" in n for x in r["rows"] for n in x["notes"]))
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
    # THE DONE TRANSITION (R10-RCA-ROSTER-SYNC-ORPHANS): `orphaned` is the
    # `--issues` test asked of a closing group, on the roster the write leaves.
    def closed(gid: str, extra=()) -> dict:
        return {"groups": [dict(g, resume={"stage": "done"}) if g["group"] == gid else g
                           for g in roster["groups"]] + list(extra)}
    live_g = next(g for g in roster["groups"] if g["group"] == "R10-LIVE")
    co = {"group": "R10-CO", "issues": [101], "resume": {"stage": "carries-open"}}
    check("a group closing with an open issue nothing else owns orphans it; one a live group "
          "also lists does not",
          orphaned(Dests(closed("R10-LIVE", [co]), {300}, None, lambda n: "open"), live_g) == [100])
    check("... a closed issue is no orphan (null control)",
          orphaned(Dests(closed("R10-LIVE", [co]), {300}, None, lambda n: "closed"), live_g) == [])
    check("... an unreadable state counts as open, and with no other owner both are orphans",
          orphaned(Dests(closed("R10-LIVE"), set(), None, lambda n: None), live_g) == [100, 101])
    check("... a carry file is another live owner",
          orphaned(Dests(closed("R10-LIVE"), {100, 101}, None, lambda n: "open"), live_g) == [])
    check("... and an O-brief is too",
          orphaned(Dests(closed("R10-LIVE"), set(), tmp.name, lambda n: "open"),
                   {"issues": [2353, 7]}) == [7])
    rnd = ("origin/handoff/audit-r10-roster", {"groups": [
        dict(g, resume={"stage": "done"}) if g["group"] == "R10-STALE" else g for g in roster["groups"]] + [
        {"group": "R10-BRANCH", "resume": {"stage": "not-started"}},
        {"group": "R10-BRDONE", "resume": {"stage": "done"}}]})
    Drr = Dests(roster, {300}, tmp.name, round_roster=rnd)
    r = run(plant.rstrip() + " Carry: R10-BRANCH\n", d=Drr)
    check("a group only on the round's roster ref is a destination, and the note names that ref",
          r["u"] == 0 and r["b"] == 0 and any(rnd[0] in n for x in r["rows"] for n in x["notes"]))
    r = run(plant.rstrip() + " Carry: R10-BRANCH\n")
    check("... and without the round ref it is not (null control)", r["b"] == 1)
    # load_dests itself reads the round ref, in a scratch clone whose tree and
    # origin/main hold `roster` and whose round branch adds R10-BRANCH.
    gtmp = tempfile.TemporaryDirectory()
    rp = Path(gtmp.name, roster_lib.ROSTERS_DIR, "wave-r10-groups.json")
    rp.parent.mkdir(parents=True)

    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_init  # noqa: E402  (the one way to build a scratch repo)
    genv = throwaway_git_init(gtmp.name, "-q")

    def git(*argv: str) -> None:
        subprocess.run(["git", "-C", gtmp.name, "-c", "commit.gpgsign=false", *argv], env=genv,
                       capture_output=True, check=True)
    for refname, data in (("refs/remotes/" + rnd[0], rnd[1]), ("refs/remotes/origin/main", roster)):
        rp.write_text(json.dumps(data))
        git("add", "-A")
        git("commit", "-qm", refname)
        git("update-ref", refname, "HEAD")
    r = run(plant.rstrip() + " Carry: R10-BRANCH\n", d=load_dests(Path(gtmp.name)))
    check("load_dests reads the round ref: a group only there passes, the note naming it",
          r["b"] == 0 and any(rnd[0] in n for x in r["rows"] for n in x["notes"]))
    # P43: a pull request's own new carry file routes its `#N` at the pre-flight (extra_ref, its head).
    git("checkout", "-q", "-b", "pr-carry")
    Path(gtmp.name, CARRIES_DIR).mkdir(parents=True, exist_ok=True)
    Path(gtmp.name, CARRIES_DIR, "carry-777.json").write_text('{"issue": 777}')
    git("add", "-A")
    git("commit", "-qm", "the pull request adds carry-777.json")
    git("checkout", "-q", "-")
    r = run(plant.rstrip() + " Carry: #777\n", d=load_dests(Path(gtmp.name), "origin/main"))
    check("P43: a #N whose carry file only the pull request's head adds is bad at origin/main (before)", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: #777\n", d=load_dests(Path(gtmp.name), "origin/main", extra_ref="pr-carry"))
    check("P43: ... and routes once the head is the extra ref (after)", r["b"] == 0)
    r = run(plant.rstrip() + " Carry: #778\n", d=load_dests(Path(gtmp.name), "origin/main", extra_ref="pr-carry"))
    check("P43: a #N with a carry file in neither main nor the head still refuses (null control)", r["b"] == 1)
    # P319: an explicit ref (the pre-flight's origin/main) reads the round ref too.
    r = run(plant.rstrip() + " Carry: R10-BRANCH\n", d=load_dests(Path(gtmp.name), "origin/main"))
    check("load_dests at an explicit origin/main routes a group only on the round ref (P319)", r["b"] == 0)
    r = run(plant.rstrip() + " Carry: R10-NEITHER\n", d=load_dests(Path(gtmp.name), "origin/main"))
    check("... a group on neither is still BAD-DEST at an explicit ref (null control)", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: R10-BRDONE\n", d=load_dests(Path(gtmp.name), "origin/main"))
    check("... and a group done on the round ref is still refused at an explicit ref", r["b"] == 1)
    with contextlib.redirect_stderr(io.StringIO()):
        sref = sweep_ref(Path(gtmp.name), None)
    check("a sweep with no --roster-ref reads the round's live roster ref", sref == rnd[0])
    check("... and a given --roster-ref wins (null control)",
          sweep_ref(Path(gtmp.name), "origin/main") == "origin/main")
    check("at the live ref a group done there owns nothing; main's stale copy still credits it "
          "(#2492's miss)",
          not load_dests(Path(gtmp.name), sref).owns(400)
          and load_dests(Path(gtmp.name), "origin/main").owns(400))
    git("update-ref", "-d", "refs/remotes/" + rnd[0])
    r = run(plant.rstrip() + " Carry: R10-BRANCH\n", d=load_dests(Path(gtmp.name)))
    check("... and a clone without that ref refuses it (null control)", r["b"] == 1)
    # P98 arm (b2): a tree behind origin/main reads the roster at origin/main.
    main_only = {"groups": roster["groups"] + [{"group": "R10-MAINONLY", "resume": {"stage": "not-started"}}]}
    rp.write_text(json.dumps(main_only))
    git("commit", "-qam", "main gains R10-MAINONLY")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    git("reset", "-q", "--hard", "HEAD~1")

    def dests_out(at: str = gtmp.name) -> "tuple[Dests | None, str]":
        # A refusal (RosterNotFound, SystemExit) is a None the checks fail on,
        # never a crash: a crash names no check (the mutant harness's rule).
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                d_ = load_dests(Path(at))
            except (Exception, SystemExit) as e:  # noqa: BLE001
                return None, f"REFUSED {e}"
        return d_, buf.getvalue()
    d_, out = dests_out()
    r = run(plant.rstrip() + " Carry: R10-MAINONLY\n", d=d_)
    check("a tree behind origin/main reads the roster there: a group only on main passes", r["b"] == 0)
    check("... and says so: NOTE stale tree names HEAD and origin/main",
          out.startswith("NOTE stale tree: ") and "lacks origin/main" in out)
    r = run(plant.rstrip() + " Carry: R10-NEITHER\n", d=d_)
    check("... and a group on neither is still a bad destination (null control)", r["b"] == 1)
    git("reset", "-q", "--hard", "origin/main")
    rp.write_text(json.dumps({"groups": main_only["groups"] + [
        {"group": "R10-PRONLY", "resume": {"stage": "not-started"}}]}))
    git("commit", "-qam", "the pull request adds R10-PRONLY")
    d_, out = dests_out()
    r = run(plant.rstrip() + " Carry: R10-PRONLY\n", d=d_)
    check("a tree containing origin/main keeps its own roster: the PR's own new group passes", r["b"] == 0)
    check("... and prints no stale-tree NOTE (null control)", "stale tree" not in out)
    # A shallow clone answers rc 1 for an ancestor it cannot walk to: HEAD (the
    # PR commit) at depth 1, origin/main (its parent) fetched at depth 1.
    from throwaway_git import throwaway_git_clone  # noqa: E402
    git("branch", "-f", "mainline", "refs/remotes/origin/main")
    branch = subprocess.run(["git", "-C", gtmp.name, "symbolic-ref", "--short", "HEAD"], env=genv,
                            capture_output=True, text=True, check=True).stdout.strip()
    shal = Path(gtmp.name, "shallow")
    senv = throwaway_git_clone(Path(gtmp.name).as_uri(), shal, "-q", "--depth", "1", "--single-branch",
                               "--branch", branch)
    subprocess.run(["git", "-C", str(shal), "fetch", "-q", "--depth", "1", "origin",
                    "+refs/heads/mainline:refs/remotes/origin/main"], env=senv, capture_output=True, check=True)
    d_, out = dests_out(str(shal))
    r = run(plant.rstrip() + " Carry: R10-PRONLY\n", d=d_) if d_ else {"b": -1}
    check("a shallow clone whose HEAD contains origin/main keeps its tree: the PR's own group passes",
          r["b"] == 0)
    check("... and prints no stale-tree NOTE", d_ is not None and "stale tree" not in out)
    subprocess.run(["git", "-C", str(shal), "fetch", "-q", "--unshallow", "origin",
                    "+refs/heads/mainline:refs/remotes/origin/main"], env=senv, capture_output=True, check=True)
    d_, out = dests_out(str(shal))
    r = run(plant.rstrip() + " Carry: R10-PRONLY\n", d=d_) if d_ else {"b": -1}
    check("... and once unshallowed the ancestry answers itself: passes, no NOTE (null control)",
          r["b"] == 0 and "stale tree" not in out)
    # A clone with no origin/main at all cannot be judged stale: it keeps its
    # tree, silently (rc 128, not 1; the reviewer's B2-rc).
    git("update-ref", "-d", "refs/remotes/origin/main")
    d_, out = dests_out()
    r = run(plant.rstrip() + " Carry: R10-PRONLY\n", d=d_) if d_ else {"b": -1}
    check("a clone without origin/main keeps its tree: the PR's own group passes", r["b"] == 0)
    check("... and prints no stale-tree NOTE", d_ is not None and "stale tree" not in out)
    gtmp.cleanup()
    r = run(plant.rstrip() + " Carry: R10-INVENTED\n", d=Drr)
    check("a group on neither ref is a bad destination", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: R10-OVER\n", d=Drr)
    check("a group done on main and on the round ref is a bad destination", r["b"] == 1)
    r = run(plant.rstrip() + " Carry: R10-BRDONE\n", d=Drr)
    check("a group done on the round ref alone is a bad destination", r["b"] == 1)
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
    vid = first_id(r)
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
    check("a ledger FINDING: with no Carry: is unrouted", len(ledger_unrouted("== FINDING: x.\n")) == 1)
    fr = head + "## Friction\n\n- carry_audit.py: unenforced: nothing reads the ledger key at merge.\n"
    fid = first_id(run(fr))
    r = run(fr + f"\n## Red checks\n\n- `pr-contract`: it printed `UNROUTED body item {fid} (## Friction)`; "
            "the fold names Carry: R10-LIVE as its example.\n")
    check("a quoted refusal beside an unrelated marker routes nothing (#2404's review)",
          r["u"] == 1 and len(r["rows"]) == 1)
    r = run(fr + f"\n## Red checks\n\n- `pr-contract`: answered. Carry: R10-LIVE (item {fid})\n")
    check("the same id inside the marker, `Carry: R10-LIVE (item <id>)`, routes it (null control)",
          r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
    r = run(fr + f"\n## Red checks\n\n- `pr-contract`: Carry: R10-LIVE, see the quoted UNROUTED line: "
            f"body item {fid} stays owed.\n")
    check("a bare `item <id>` after a marker on its line routes nothing; only `(item <id>)` does",
          r["u"] == 1 and len(r["rows"]) == 1)
    r = run(fr + f"\n## Red checks\n\n- `pr-contract`: Carry: R10-LIVE, see the quoted UNROUTED line: "
            f"(item {fid}) is routed here.\n")
    check("the same line with the paren form routes it (null control)",
          r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
    r = run(fr + f"\n## Red checks\n\n- `pr-contract`: the refusal named (item {fid}) and stays owed;\n"
            "  the repair itself is answered. Carry: R10-LIVE\n")
    check("an `(item <id>)` outside the marker's segment, in the same paragraph, routes nothing",
          r["u"] == 1 and len(r["rows"]) == 1)
    r = run(fr + f"\n## Red checks\n\n- `pr-contract`: the refusal stays owed;\n"
            f"  the repair itself is answered. Carry: R10-LIVE (item {fid})\n")
    check("the same paragraph with the id inside the marker's segment routes it (null control)",
          r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
    r = run(head + "## Friction\n\n- PULL_REQUEST_TEMPLATE.md: unenforced: its example "
            "`Carry: R10-LIVE` names a group a fixer copies unchecked.\n")
    check("a backticked example `Carry:` in a finding's prose does not route it", r["u"] == 1)
    r = run(head + "## Friction\n\n- PULL_REQUEST_TEMPLATE.md: unenforced: its example "
            "`Carry: R10-LIVE` names a group a fixer copies unchecked. Carry: R10-LIVE\n")
    check("the same finding with a plain marker routes (null control)", r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
    # M1 (R10-RCA-JIDOKA-YIELD): a roster carry stated as not done, outside the
    # carry sections, is a finding item needing a marker. #3010 r1's paragraph.
    owed = ("**Roster carry (open, not answered by this change).** Carry 1: **not done in "
            "this pull request.** The group's roster entry folded R10-FLOW-POSTMERGE.\n")
    r = run(head + owed)
    check("an owed roster carry in an untitled paragraph is an unrouted [owed carry] item",
          r["u"] == 1 and [x["why"] for x in r["rows"]] == ["owed carry"])
    r = run(head + owed.rstrip() + " Carry: R10-LIVE\n")
    check("the same paragraph with a Carry: marker routes (null control)",
          r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
    r = run(head + 'The reviewer wrote "Carry 1: not done in this pull request" as an example.\n')
    check("an owed-carry phrase inside double quotes is not read", r["rows"] == [])
    r = run(head + "The probe pattern `Carry 1: not done in this pull request` is an example.\n")
    check("... nor one inside a code span", r["rows"] == [])
    r = run(head + "Carry 1 landed in this change and is answered by the test below.\n")
    check("a carry index with no not-done phrase is no finding (null control)", r["rows"] == [])
    # One row per boundary of the marker grammar, each with the status it must
    # read: dev/audit/harnesses/r10_carry_parser_mutants.py names the mutant
    # each row kills alone, so no predicate is pinned only with another.
    P = plant.rstrip()
    rc = fr + "\n## Red checks\n\n- `pr-contract`: "
    pid = first_id(run(P + " Carry: R10-LIVE\n"))
    grammar = [
        ("a `Carry:` right after a closing backtick is a marker", P + " see `x`Carry: R10-LIVE\n", "routed"),
        ("an unmatched double backtick opens no span", P + " the `` run. Carry: R10-LIVE `z`\n", "routed"),
        ("a longer backtick run does not close a span", P + " `a``Carry: R10-LIVE`\n", "unrouted"),
        ("a double-backtick span closes only on a double run", P + " ``a`Carry: R10-LIVE``\n", "unrouted"),
        ("a code span may cross a line ending", P + " `an example\n  Carry: R10-LIVE` reads.\n", "unrouted"),
        ("a word glued to `Carry:` is not a marker", P + " see PreCarry: R10-LIVE\n", "unrouted"),
        ("a hyphen glued to `Carry:` is not a marker", P + " see pre-Carry: R10-LIVE\n", "unrouted"),
        ("a segment ends at its line: an id on the next line routes nothing",
         rc + f"Carry: R10-LIVE\n  The refusal it printed, (item {fid}), stays owed.\n", "unrouted"),
        ("a segment ends at the next `Carry:`: its id is not the first marker's",
         rc + f"Carry: R10-LIVE; the friction item stays owed, Carry: (item {fid})\n", "unrouted"),
        ("two markers naming one id in one item: each destination must hold",
         rc + f"Carry: R10-LIVE (item {fid}); Carry: R10-INVENTED (item {fid})\n", "bad"),
        ("two items naming one id: each destination must hold",
         rc + f"Carry: R10-LIVE (item {fid})\n- `fast`: Carry: R10-INVENTED (item {fid})\n", "bad"),
        ("an item's own marker and a reference to it: each destination must hold",
         P + f" Carry: R10-LIVE\n\n## Red checks\n\n- Carry: R10-INVENTED (item {pid})\n", "bad"),
        ("a bolded `dismissed:` reads", P + " Carry: **dismissed: host load**\n", "routed"),
        ("`Dismissed:` reads in any case", P + " Carry: Dismissed: host load, not a defect\n", "routed"),
        ("`and` separates destinations", P + " Carry: R10-LIVE and #999\n", "bad"),
        ("a destination ending a sentence reads", P + " Carry: R10-LIVE.\n", "routed"),
        ("a space before the list's comma separates", P + " Carry: R10-LIVE , #999\n", "bad"),
        ("`(item <id>)` inside the destinations does not end them",
         P + " Carry: R10-LIVE (item 0123abcd), #999\n", "bad"),
        ("prose ends the destinations: a token after it is not one",
         P + " Carry: R10-LIVE because it owns #999\n", "routed"),
        ("`item <id>)` without its open paren routes nothing", rc + f"Carry: R10-LIVE, item {fid}) owed.\n",
         "unrouted"),
        ("`(item <id>` without its close paren routes nothing", rc + f"Carry: R10-LIVE, (item {fid} owed.\n",
         "unrouted"),
        ("one capitalised word is not a group", P + " Carry: TODO\n", "unrouted"),
        ("a group token ends at the word", P + " Carry: R10-LIVE's\n", "unrouted"),
        ("an issue token ends at the word", P + " Carry: #100's\n", "unrouted"),
        ("a brief token ends at the word", P + " Carry: O7's\n", "unrouted"),
    ]
    for name, text, want in grammar:
        got = sorted(x["status"] for x in run(text)["rows"])
        check(f"grammar: {name}", got == [want])
    # The same for what an item is and when it is a finding: each row's
    # (why, status) pairs, sorted.
    def verdict_of(word: str, rest: str) -> list:
        return [{"id": 48, "body": f"Fix review: {word} {'d' * 40}\n\n{rest}"}]
    U, R_ = "unrouted", "routed"
    item_grammar = [
        ("a fence indented under a bullet still fences",
         head + "## Figures\n\n  ```\n## Friction\n- a: unclear: fenced\n  ```\n", (), []),
        ("a `~~~` fence fences", head + "## Figures\n\n~~~\n## Friction\n- a: unclear: fenced\n~~~\n", (), []),
        ("a fence line is not an item", head + "## Friction\n\n```\nx\n```\n", (), []),
        ("an HTML comment is not an item", head + "## Friction\n\n<!-- template note -->\n", (), []),
        ("an indented HTML comment is not an item", head + "## Friction\n\n  <!-- note -->\n", (), []),
        ("a thematic break is not an item", head + "## Friction\n\n- a: unclear: x. Carry: R10-LIVE\n\n---\n", (),
         [("section", R_)]),
        ("a whitespace-only line ends a paragraph",
         head + "## Figures\n\nOut of scope: x. Carry: R10-LIVE\n   \nOut of scope: y.\n", (),
         [("lead", R_), ("lead", U)]),
        ("a blank line ends a paragraph",
         head + "## Figures\n\nOut of scope: x. Carry: R10-LIVE\n\nOut of scope: y.\n", (),
         [("lead", R_), ("lead", U)]),
        ("an indented line after a bullet's blank continues it",
         head + "## Friction\n\n- a: unclear: x.\n\n  more of a. Carry: R10-LIVE\n", (), [("section", R_)]),
        ("a tab-indented line after a bullet's blank continues it",
         head + "## Friction\n\n- a: unclear: x.\n\n\tmore of a. Carry: R10-LIVE\n", (), [("section", R_)]),
        ("an unindented line after a bullet's blank is a paragraph",
         head + "## Figures\n\n- a figure.\n\nOut of scope: x.\n", (), [("lead", U)]),
        ("an unindented line right after a bullet continues it",
         head + "## Figures\n\n- Out of scope: x\ncontinued. Carry: R10-LIVE\n", (), [("lead", R_)]),
        ("each table row is an item, its separator none",
         head + "## Friction\n\n  | a: unclear: x | Carry: R10-LIVE |\n  |---|---|\n  | b: unclear: y | - |\n", (),
         [("section", R_), ("section", U)]),
        ("a Friction-shaped line starts an item only under Friction",
         head + "## Figures\n\nOut of scope: a.\nfixer.md: unclear: b. Carry: R10-LIVE\n", (), [("lead", R_)]),
        ("a section name reads in any case",
         head + "## FRICTION\n\nfixer.md: unclear: one.\ngate-scoping.md: cost: two. Carry: R10-LIVE\n", (),
         [("section", R_), ("section", U)]),
        ("under Friction an unshaped unindented line continues the item",
         head + "## Friction\n\n- a: unclear: x\ncontinued. Carry: R10-LIVE\n", (), [("section", R_)]),
        ("an indented Friction-shaped line continues the item",
         head + "## Friction\n\n- a: unclear: x\n  b.md: cost: y. Carry: R10-LIVE\n", (), [("section", R_)]),
        ("an indented `#` line is not a heading",
         head + "## Friction\n\n- a: unclear: x\n  # a quoted shell comment. Carry: R10-LIVE\n", (),
         [("section", R_)]),
        ("a numbered, bolded lead reads", head + "## Figures\n\n1. **Out of scope:** x.\n", (), [("lead", U)]),
        ("a section heading that leads makes each item a finding",
         head + "## Out of scope\n\n- the tracked-file scrub.\n", (), [("section", U)]),
        ("a lead paragraph's bullets inherit it",
         head + "## Figures\n\nOut of scope:\n- a.\n- b. Carry: R10-LIVE\n", (), [("under lead", R_), ("under lead", U)]),
        ("a paragraph ending `:` that is no finding leads nothing",
         head + "## Figures\n\nThe figures:\n- a figure.\n", (), []),
        ("a CRLF body reads as its LF twin",
         (head + "## Friction\n\n- a: unclear: x\n  more.\n\n- b: cost: y. Carry: R10-LIVE\n").replace("\n", "\r\n"),
         (), [("section", R_), ("section", U)]),
        ("a non-bullet ends a verdict's lead", head,
         verdict_of("merge", "Non-blocking notes:\n- (a) x.\n\nThe check passed.\n\n- a later verified bullet.\n"),
         [("under lead", U)]),
        ("a verdict's own first line is not a finding", head,
         [{"id": 48, "body": f"Fix review: merge {'d' * 40} with one minor note\n\n## Verified\n\n- x.\n"}], []),
        ("a heading saying it is not the block is a note section", head,
         verdict_of("merge", "## Non-blocking\n\n- a re-booking.\n"), [("section", U)]),
        ("in a merge verdict a residual heading is a note section", head,
         verdict_of("merge", "## Residuals\n\n- the body over-claims.\n"), [("section", U)]),
        ("in a blocked verdict a lead inside the block is owed, not a note", head,
         verdict_of("blocked", "## Block\n\n- Residual: the census misses one.\n"), []),
        ("in a blocked verdict a non-blocking heading is a note section", head,
         verdict_of("blocked", "## Non-blocking notes\n\n- a re-booking.\n"), [("section", U)]),
        ("a blocked verdict reads with two spaces before its word", head,
         [{"id": 49, "body": v3["body"].replace("Fix review: blocked", "Fix review:  blocked")}],
         [("lead", U), ("non-blocking", U)]),
    ]
    # Each word of the vocabulary regexes, alone: the harness removes one
    # alternative at a time.
    item_grammar += [(f"LEAD reads {w!r}", head + f"## Figures\n\n- {w} x.\n", (), [("lead", U)])
                     for w in ("Residual:", "Distinct finding:", "Not fixed here:", "Known-open:", "Follow-up:",
                               "Non-blocking:", "Not blocking:", "Caveat:", "Observation:", "Deferred:",
                               "Advisory:", "Minor:", "A follow-up:", "An observation:", "One caveat:",
                               "Two follow-ups:", "Three caveats:")]
    item_grammar += [(f"NONBLOCK reads {w!r} mid-sentence in a findings section", head,
                      verdict_of("merge", f"## Findings\n\n- the check is {w} here.\n"), [("non-blocking", U)])
                     for w in ("not blocking", "not a block", "neither blocks", "does not block", "not owed here",
                               "owed to the record", "minor", "advisory", "a secondary note", "deferred")]
    item_grammar += [(f"NOTE_HEADING reads {w!r}", head, verdict_of("merge", f"## {w}\n\n- a re-booking.\n"),
                      [("section", U)])
                     for w in ("Owed", "Instrument findings", "Out of scope", "Follow-up", "Carry forward")]
    item_grammar += [(f"TRAILER reads {w!r}", head + f"## Friction\n\n{w}\n", (), [])
                     for w in ("Co-Authored-By: x", "bus: verdict/1 at abc", "Evidence: ev/x", "RESULT x=1", "n/a")]
    item_grammar += [
        ("`#2404` opening a line is no heading",
         head + "## Friction\n\n- a: unclear: x\n#2404's review found it. Carry: R10-LIVE\n", (), [("section", R_)]),
        ("a heading's closing hashes are not its name", head + "## Friction ##\n\n- a: unclear: x.\n", (),
         [("section", U)]),
        ("under Friction a `word:` line without the kind's colon continues the item",
         head + "## Friction\n\n- a: unclear: x\nNote: this continues it. Carry: R10-LIVE\n", (), [("section", R_)]),
        ("a verdict naming a short SHA is read", head,
         [{"id": 50, "body": "Fix review: merge abc1234\n\n## Findings\n\n- a minor note.\n"}], [("non-blocking", U)]),
    ]
    item_grammar += [("a numbered list item is a bullet",
                      head + "## Friction\n\n1. a: unclear: x.\n2. b: cost: y. Carry: R10-LIVE\n", (),
                      [("section", R_), ("section", U)])]
    # A verdict's `## Evidence` (r10-verdict-item-barrier): what a check does
    # to the merge is no finding there; a defect handed on still is.
    item_grammar += [
        ("under the Evidence heading a check that is not a required context and does not block is no finding",
         head, verdict_of("merge", "## Evidence\n\n- composed-proof is queued, but it is not a required context "
                          "and does not block the PR (tests.yml:2775).\n"), []),
        ("... `not required check` reads too", head,
         verdict_of("merge", "## Evidence\n\n- composed-proof is not required check and does not block.\n"), []),
        ("P308: under the Evidence heading a check that does not block is no finding, unrequired or not", head,
         verdict_of("merge", "## Evidence\n\n- composed-proof is queued and does not block the PR.\n"), []),
        # #2441's and #2465's rows flip (P308): a defect handed on belongs under `## Findings`, or opens
        # with a lead, where it is read; under Evidence only the structure is.
        ("P308: #2441's shape under the Evidence heading passes (a nit belongs under ## Findings)", head,
         verdict_of("merge", "## Evidence\n\n- composed-proof is not a required check and does not block. One nit, "
                    "not blocking: the usage string still lists the arm names by hand.\n"), []),
        ("P308: #2465's shape under the Evidence heading passes (a defect handed on opens with a lead)", head,
         verdict_of("merge", "## Evidence\n\n- A hand-set fractional floor is written 0.27 K low and the check "
                    "re-raises the issue; the selector cannot produce it, so it is not blocking.\n"), []),
        ("... the same #2465 sentence under ## Findings is a finding (null control)", head,
         verdict_of("merge", "## Findings\n\n- A hand-set fractional floor is written 0.27 K low and the check "
                    "re-raises the issue; the selector cannot produce it, so it is not blocking.\n"),
         [("non-blocking", U)]),
        ("the Evidence heading reads in any case and with words after it", head,
         verdict_of("merge", "## EVIDENCE (not findings)\n\n- nightly-status: not a required check, not blocking.\n"),
         []),
        ("a heading that only mentions evidence is not the Evidence heading", head,
         verdict_of("merge", "## Notes on evidence\n\n- nightly-status: not a required check, not blocking.\n"),
         [("non-blocking", U)]),
        ("a heading whose first word only starts `evidence` is not the Evidence heading (a blocked verdict reads it)",
         head, verdict_of("blocked", "## Evidenced claims\n\n- nightly-status: not a required check, not blocking.\n"),
         [("non-blocking", U)]),
        ("P308: a deferral word under the Evidence heading is not read", head,
         verdict_of("merge", "## Evidence\n\n- M4 survives, not blocking, noted for a later tightening.\n"), []),
        ("P308: an Evidence item carrying Carry: <live group> routes", head,
         verdict_of("merge", "## Evidence\n\n- M4 survives, noted for a later tightening. Carry: R10-LIVE\n"),
         [("carry", R_)]),
        ("P308: an Evidence item carrying Carry: <done group> is a bad destination", head,
         verdict_of("merge", "## Evidence\n\n- M4 survives. Carry: R10-OVER\n"), [("carry", "bad")]),
        ("P308: an Evidence item opening `Follow-up:` is a finding (null control)", head,
         verdict_of("merge", "## Evidence\n\n- Follow-up: the census misses one.\n"), [("lead", U)]),
        ("a LEAD opening under the Evidence heading is a finding", head,
         verdict_of("merge", "## Evidence\n\n- Residual: the census misses one.\n"), [("lead", U)]),
        ("a lead's bullets under the Evidence heading are findings", head,
         verdict_of("merge", "## Evidence\n\nNon-blocking notes:\n- a re-booking.\n"), [("under lead", U)]),
        ("the Evidence heading is read only in a verdict: a body's is a plain section",
         head + "## Evidence\n\n- the figure is deferred to round 11.\n", (), []),
        ("a RESULT line under the Evidence heading stays a trailer", head,
         verdict_of("merge", "## Evidence\n\n- RESULT repro: a run 0.2 s later takes the lock; residual 0\n"), []),
        ("a time `later` under the Evidence heading is no deferral", head,
         verdict_of("merge", "## Evidence\n\n- a run 2.5 s later takes the lock.\n"), []),
    ]
    item_grammar += [(f"P308: {w!r} under the Evidence heading is not read", head,
                      verdict_of("merge", f"## Evidence\n\n- the check is {w} here.\n"), [])
                     for w in ("a follow-up", "out of scope", "not fixed here", "known-open",
                               "a distinct finding", "residual", "for later", "moved to a later round",
                               "fixed in the later pass", "left until later", "a caveat", "an observation",
                               "still has to", "still have to", "still needs to", "deferred", "advisory",
                               "minor", "a secondary note", "owed to the record", "not owed here")]
    item_grammar += [("under ## Findings a nit after a not-required check is a finding", head,
                      verdict_of("merge", "## Findings\n\n- composed-proof is not a required check; "
                                 "one nit, not blocking: x.\n"), [("non-blocking", U)])]
    # The carve-out frees the check's own clause, never its sentence: each
    # nit or defect sharing a sentence with it is a finding (round 2's attack).
    item_grammar += [(f"under ## Findings a {k} beside a not-required check is a finding", head,
                      verdict_of("merge", f"## Findings\n\n- {v}\n"), [("non-blocking", U)]) for k, v in (
        ("nit", "nightly-status is not a required check, and one nit is not blocking: the usage string."),
        ("minor defect", "composed-proof is not a required check and a minor defect stays, not blocking."),
        ("defect", "The guard misses a deleted ref, which is not a required check to fix, so not blocking."),
        ("parenthetical defect", "The floor is written 0.27 K low (not a required check) and is not blocking."),
        ("colon-led nit", "composed-proof is not a required check, not blocking: the guard misses a ref."))]
    item_grammar += [("the check's clause frees `, and it is not blocking` (null control)", head,
                      verdict_of("merge", "## Evidence\n\n- nightly-status is not a required check, and it "
                                 "is not blocking.\n"), [])]
    item_grammar += [("... and `, non-blocking`", head,
                      verdict_of("merge", "## Evidence\n\n- composed-proof: not a required check, non-blocking.\n"),
                      [])]
    item_grammar += [("a later-stage compound is no deferral", head,
                      verdict_of("merge", "## Evidence\n\n- I found no later-stage finding.\n"), [])]
    # The field items (dev/audit/harnesses/r10_carry_field_verdicts.json, verbatim): each was flagged at
    # origin/main 7539d1675 and is no finding -- P308's four, P293's class A and C, P329's #3005 and
    # #3013, CARRY 5's #2683 `## Body (steps 7, 10, non-blocking note 1)` four, #2955's "None."
    fx = json.loads((ROOT / "dev/audit/harnesses/r10_carry_field_verdicts.json").read_text())
    item_grammar += [(f"field item {i} (#{x['pr']} {x['verdict']}, ## {x['section']}) is no finding", head,
                      verdict_of(x["verdict"], f"## {x['section']}\n\n{x['text']}\n"), [])
                     for i, x in sorted(fx["items"].items())]
    ap = fx["items"]["fccf8846"]["text"]
    item_grammar += [
        # P314: a merge verdict's every section but a findings section is read by its structure.
        ("P314: #3013's code-owner note under a merge verdict's ## Findings is still read", head,
         verdict_of("merge", "## Findings\n\n- `away.py` is code-owned, and a defect in it does not block.\n"),
         [("non-blocking", U)]),
        ("P314: a merge verdict's Summary item with a NONBLOCK word is no finding", head,
         verdict_of("merge", "## Summary\n\n- the docs-only diff does not block on the nightly lane.\n"), []),
        ("P314: a Summary line opening `Follow-up:` is a finding (null control)", head,
         verdict_of("merge", "## Summary\n\nFollow-up: the census misses one.\n"), [("lead", U)]),
        ("P314: a blocked verdict's Summary item keeps today's reading (null control)", head,
         verdict_of("blocked", "## Summary\n\n- a minor defect stays.\n"), [("non-blocking", U)]),
        ("CARRY 5: a heading that only holds a non-blocking word is no findings section (#2683)", head,
         verdict_of("merge", "## Body (steps 7, 10, non-blocking note 1)\n\n- `figure_lint` printed 0 refused.\n"), []),
        ("CARRY 5: a heading opening with a findings word is one (null control)", head,
         verdict_of("merge", "## Non-blocking notes (steps 7, 10)\n\n- `figure_lint` printed 0 refused.\n"),
         [("section", U)]),
        # P329: an owner-approval merge condition, and its one bare sentence, read no NONBLOCK.
        ("a blocked verdict's own first line is not a finding, whatever it says", head,
         [{"id": 48, "body": f"Fix review: blocked {'d' * 40} harness: a minor note\n\n## Block\n\n- x.\n"}], []),
        ("P314: a block heading in a merge verdict still reads NONBLOCK", head,
         verdict_of("merge", "## Block\n\n- a minor nit stays.\n"), [("non-blocking", U)]),
        ("P329: a bare `does not block` sentence with no approval before it is read (null control)", head,
         verdict_of("merge", "## Findings\n\n- A defect in x stays. It does not block.\n"), [("non-blocking", U)]),
        ("P329: only the one sentence right after the approval is freed", head,
         verdict_of("merge", "## Findings\n\n- x.py needs tvofi's approving review at merge. A defect in y stays. "
                    "It does not block.\n"), [("non-blocking", U)]),
        ("P329: #3013's approval note under ## Findings clears", head,
         verdict_of("merge", f"## Findings\n\n{ap}\n"), []),
        ("P329: the approval note in a blocked verdict clears", head,
         verdict_of("blocked", "## Notes\n\n- x.py is code-owned, so tvofi's approving review is required at merge. "
                    "This review does not block on it.\n"), []),
        ("P329: the approval sentence then a defect left in place stays a finding (null control)", head,
         verdict_of("blocked", "## Notes\n\n- x.py is code-owned, so tvofi's approving review is required at merge. "
                    "A defect in y is left in place, not blocking.\n"), [("non-blocking", U)]),
        ("P329: code-owned with a defect that does not block stays a finding (null control)", head,
         verdict_of("blocked", "## Notes\n\n- x.py is code-owned and a defect in it does not block.\n"),
         [("non-blocking", U)]),
        ("P329: #2281's line under a residual heading stays a finding (null control)", head,
         verdict_of("merge", "## Residuals (not blocking)\n\n- tests.yml line 3908 comment names the removed "
                    "roster_lib.ROSTER_PATH. It is code-owned and routed to TICK-ORCH.\n"), [("section", U)]),
        ("a negated deferral, `nothing is deferred or owed`, is no finding (#2955 2471d3e6)", head,
         verdict_of("merge", "## Findings\n\n- None. Nothing is deferred.\n"), []),
        ("... a deferral is still one (null control)", head,
         verdict_of("merge", "## Findings\n\n- A defect in x is deferred.\n"), [("non-blocking", U)]),
        # CARRY 3: a lead's bullets end at its section's end.
        ("CARRY 3: a lead's bullets in a later section do not inherit it (#2645)", head,
         verdict_of("blocked", "## Notes\n\nTwo more survivors. Neither blocks, but:\n\n- s1.\n\n"
                    "## Brief checklist\n\n- the brief names the file.\n"), [("under lead", U)]),
        ("CARRY 3: a LEAD bullet under a checklist heading still counts (null control)", head,
         verdict_of("blocked", "## Notes\n\nTwo more survivors. Neither blocks, but:\n\n- s1.\n\n"
                    "## Brief checklist\n\n- Residual: the census misses one.\n"), [("under lead", U), ("lead", U)]),
    ]
    item_grammar += [(f"FINDINGS_HEADING reads {w!r}: its NONBLOCK item is a finding", head,
                      verdict_of("merge", f"## {w}\n\n- a minor nit stays.\n"), [("non-blocking", U)])
                     for w in ("Findings", "Friction", "Block", "Residuals", "Non-blocking", "Not blocking (x)",
                               "Follow-ups", "Out of scope", "Deferred", "Owed", "Notes", "Caveats", "Observations",
                               "Instrument findings", "Carry forward", "What blocks the merge")]
    item_grammar += [(f"P329: the bare {w!r} after an approval sentence is freed", head,
                      verdict_of("blocked", f"## Notes\n\n- x.py needs tvofi's approving review {m} merge. {w}\n"), [])
                     for m, w in (("at", "This is not a block."), ("before the", "It does not block on it."),
                                  ("at the", "This verdict flagged that and does not block."))]
    item_grammar += [(f"a negated deferral reads {w!r}", head,
                      verdict_of("merge", f"## Findings\n\n- None. Nothing {w} deferred.\n"), [])
                     for w in ("is", "was", "remains")]
    # P296: `Carry: <dest> (item <id>, supersedes <old>)` retires a bad <old> for that item alone.
    def sup_rows(old_dest: str, marker: str, other: str = "") -> dict:
        vc = verdict_of("merge", f"## Findings\n\n- a minor nit stays. Carry: {old_dest}\n{other}")
        iid = ([x["id"] for x in items(vc[0]["body"], True) if x["flagged"]] + [""])[0]
        res = run(head + "## Forward-carry\n\n- " + marker.replace("<id>", iid) + "\n", vc)
        # a mutant that reads no row fails these checks, never crashes them
        return {r["id"]: r for r in res["rows"] if r["where"].startswith("review")}.get(
            iid, {"id": iid, "status": None, "notes": [], "bad": []})
    r = sup_rows("R10-OVER", "Carry: R10-LIVE (item <id>, supersedes R10-OVER)")
    check("P296: a bad destination superseded for its item routes (the #2925 and #2962 shape)", r["status"] == "routed")
    check("... and the retired token prints as a NOTE, never dropped silently",
          "R10-OVER superseded by R10-LIVE (item " + r["id"] + ")" in r["notes"])
    r = sup_rows("R10-OVER", "Carry: R10-LIVE (item <id>, supersedes `R10-OVER`)")
    check("P296: a backticked superseded token reads as the bare token", r["status"] == "routed")
    r = sup_rows("R10-OVER", "Carry: R10-LIVE (item <id>)")
    check("P296 null control: without `supersedes` the item stays bad", r["status"] == "bad")
    r = sup_rows("R10-LIVE", "Carry: R10-LIVE (item <id>, supersedes R10-LIVE)")
    check("P296: a supersede of a valid destination is refused, naming the item",
          r["status"] == "bad" and any("a supersede names a valid destination (item " + r["id"] in b for b in r["bad"]))
    r = sup_rows("R10-OVER", "Carry: R10-INVENTED (item <id>, supersedes R10-OVER)")
    check("P296: a supersede whose new destination is bad stays bad", r["status"] == "bad")
    r = sup_rows("R10-OVER", "Carry: R10-LIVE (item 0badc0de, supersedes R10-OVER)")
    check("P296: a supersede naming another item's id leaves this item bad", r["status"] == "bad")
    # CARRY 0 / P310: `landed` -- each body item's GROUP carry holds the item id or its source.
    Dl_roster = {"groups": [
        {"group": "R10-A", "resume": {"stage": "not-started"}, "brief": "Build the A arm.", "carry": []},
        {"group": "R10-B", "resume": {"stage": "not-started"}, "brief": "Build the B arm.", "carry": []},
        {"group": "R10-DONE", "resume": {"stage": "done"}, "brief": "", "carry": []}]}

    def dl(a_carry=(), b_carry=()) -> Dests:
        r_ = json.loads(json.dumps(Dl_roster))
        r_["groups"][0]["carry"], r_["groups"][1]["carry"] = list(a_carry), list(b_carry)
        return Dests(r_, {300})
    lb = head + "## Forward-carry\n\n- The census misses the store seam. Carry: R10-A\n"
    lid = ([x["id"] for x in items(lb, False) if x["flagged"]] + [""])[0]  # a mutant flagging none fails, never crashes
    miss = landed(lb, dl())
    check("landed: a carry not in its group's brief or carries is missing (the #2558 pair, before)",
          [(m["group"], m["id"]) for m in miss] == [("R10-A", lid)])
    ops = land_ops(miss, "#2558", "r10-x")
    check("land-ops: one append-carry op, tagged with the item id",
          ops == ["append-carry R10-A 'From #2558 (r10-x), body item " + lid
                  + ": The census misses the store seam. Carry: R10-A (items " + lid + ")'"])
    landed_text = ops[0].split(" ", 2)[2][1:-1] if ops else ""
    check("landed: once the op's text is in the group's carries, nothing is missing (the #2558 pair, after)",
          bool(landed_text) and landed(lb, dl([landed_text])) == [])
    check("land-ops: a group named twice by one item yields one op (deduped on its tag)",
          len(land_ops(landed(lb.replace("Carry: R10-A", "Carry: R10-A, R10-A"), dl()))) == 1)
    check("land-ops: an already landed body yields no op (null control)", land_ops(landed(lb, dl([landed_text]))) == [])
    check("landed: a carry reworded but naming the item id lands (the #2545 paraphrase)",
          landed(lb, dl(["From #2545: the store seam is missed by the census (items " + lid + ")"])) == [])
    check("landed: the id in another group's carries does not land it (the wrong group)",
          len(landed(lb, dl(b_carry=["(items " + lid + ")"]))) == 1)
    check("landed: a carry naming the source pull request lands its items (P310)",
          landed(lb, dl(["From #2558: the census."]), "#2558") == [])
    check("... and another pull request's number does not (null control)",
          len(landed(lb, dl(["From #2558: the census."]), "#25581")) == 1)
    check("landed: a dismissed item and a #N with a carry file need no landing",
          landed(head + "## Forward-carry\n\n- x. Carry: dismissed: no seam remains\n- y. Carry: #300\n", dl()) == [])
    md = landed(head + "## Forward-carry\n\n- x. Carry: R10-DONE\n", dl())
    check("landed: a done destination is missing as a bad destination, and never gets an op",
          len(md) == 1 and md[0]["why"].startswith("bad destination") and land_ops(md) == [])
    flagged_2645 = [x["id"] for x in items(fx["verdict_2645"]["whole"], True) if x["flagged"]]
    check("CARRY 3: #2645's round-1 blocked verdict flags at most one item (8 at 7539d1675)", len(flagged_2645) <= 1)
    for name, text, comments, want in item_grammar:
        got = sorted((x["why"], x["status"]) for x in run(text, comments)["rows"])
        check(f"items: {name}", got == sorted(want))
    check("an item's id is the sha1 of its whitespace-collapsed text, 8 hex (printed and quoted)",
          [x["id"] for x in run(head + "## Friction\n\n- a: unclear:   x\n  more.\n\n- b.\n")["rows"]]
          == ["af08778d", "85fdb5d3"])
    vr = {"id": 46, "body": "\n" + v["body"]}
    check("a verdict after a blank line is still read", len(run(head, [vr])["rows"]) == 2)
    try:
        nulls = run(None, [{"id": 47, "body": None}])["rows"]
    except (AttributeError, TypeError):
        nulls = None
    check("a null body and a null comment (gh's empty body) read as no finding", nulls == [])
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
