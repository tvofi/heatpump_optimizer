#!/usr/bin/env python3
"""The obligations ledger: one schema, two stores, one fold (R10-ORCH-LEDGER).

    python3 -I tools/audit/seat/ledger.py [--log FILE] dispose <ref> <sha40> [how]
    python3 -I tools/audit/seat/ledger.py [--log FILE] disposed <ref> <sha40>
    python3 -I tools/audit/seat/ledger.py [--log FILE] open <kind> <subject> <sha40|-> [why...]
    python3 -I tools/audit/seat/ledger.py [--log FILE] close <kind> <subject> <sha40|-> [how]
    python3 -I tools/audit/seat/ledger.py [--log FILE] attempt <ref> <sha40> <outcome>
    python3 -I tools/audit/seat/ledger.py [--log FILE] level <hrefs-file> <topics-file>
    python3 -I tools/audit/seat/ledger.py [--log FILE] board
    python3 -I tools/audit/seat/ledger.py landed [--no-ancestry] [--no-content] <main> [<head>...] < tips
    python3 -I tools/audit/seat/ledger.py --self-test

WHY. An obligation was a level read out of append-only history: the relay
appended OWED rows, the tick replayed them, and a closer could only match on a
PR number (the design at handoff/orch-machinery, section 6.3; the round-10
orphaned-handoff RCA, dev/audit/rca/N-orphaned-handoff.md). Here every
obligation has a KIND from one table, a SUBJECT and a SHA, and a closer.

HOME. Beside the relay's log (--log, default $HPO_STATE_DIR/cloud-relay.log),
where its rewritten level `<log>.level` already lives:
  dispositions.tsv  `<ref> <sha> <utc> <how>`, one line per act, the last per
                    ref wins; written only by `dispose`. A missing file is
                    first run: the relay's `cloud-disposed` beside it, if any,
                    is imported once (its last disposition per ref, each ref
                    classified; one matching no arm is refused and reported).
  events.tsv        `<op> <utc> <kind> <subject> <sha|-> <text>`, op `open`,
                    `close` or `attempt`, append-only. A missing file is first
                    run: the log's still-open OWED events (b38c6431a's rule: an
                    OWED stands until a later POSTED for its PR) are its first
                    rows, each keeping its journal line as its text, so the
                    board reads the same across the migration. A reader
                    (`board`, the tick) folds that import in memory and writes
                    nothing; the first writer persists it.
  An unreadable store, or one holding a row of the wrong shape or of no ledger
  kind, is UNREADABLE (rc 2): never a clean board.

KINDS. DERIVED kinds are recomputed every pass from the live world and never
accumulate: the relay rewrites them into `<log>.level` (`handoff-no-pr` through
`level` here), the tick computes `design-build` and `review-owed`. EVENT kinds
cannot be recomputed and live in events.tsv: an `open` at a new sha supersedes
the subject's open entry (a moved subject closes the old one and opens one); a
`close` at its sha, or at `-`, is the producer's disposal. The PR-keyed events
also close, in the fold, on what the tick reads: the PR's head moved off the
sha (superseded), the PR is no longer open (subject-absent), or a read-back --
an approver `Fix review:` comment whose first line is the relayed verdict
(`verdict-unposted`, comment-readback.md) or names the sha (the others). A
relayed claim that a verdict was posted (the relay's POSTED) closes nothing.
An obligation of no kind in KINDS is refused, never stored.

LEVEL (`level`): the relay's handoff level for one pass. Each `handoff/<t>`
and `handoff-body/<t>` ref listed is owed (`handoff-no-pr`) unless: a state
ref by name (`audit-r<N>-plan`, `audit-r<N>-roster`); <t> has an open pull
request (the topics file's bare lines); a pull request of <t> merged at or
after the tip's commit time (its `<t> merged=<utc>` lines: a squash or an App
push rewrote the commits, and the merge's own record moved the files on, so
no content test can see it; a re-handoff committed later stays owed); the ref
is disposed at its sha; or main already
carries the change, by `landed`: the code tip is inside main or a live `fix/*`
head, or outside them only by clean merges; its patch applies to main reversed
and not forward; or `covered` finds every file it touches on main (a hunk
re-applied by another pull request into a file main has since changed, which
a byte-identical test cannot see). A body ref follows its code ref: one line
per topic, the code ref's, naming the body as `body=<sha>`; only a body ref
with no code ref is a line of its own. Each owed line carries `ct=<epoch>`
(the tip's commit time) and the topic's last opener attempt at that tip.

LANDED (`landed`): the same classifier for bus.sh orphans, one owner. Main
and the live heads are arguments, the tips stdin; one `<tip> <why>` line each,
`-` when nothing carries it. --no-ancestry and --no-content drop an arm.

AGING. `escalate` turns those lines into a queue: DISPATCH at the first
threshold, oldest first, naming the roster group and the repair; an OWNER FLAG
at the second. The thresholds are policy (tvofi's); the switch is
HPO_LEDGER_AGING = `<dispatch_h>,<owner_h>` or `off`, defaulting to the
owner's ruling of 2026-10-21 (4 h, 12 h). A tip stamped ahead of the clock has
no age (fixer.md step 16): it escalates nothing.

EXIT CODES (`board`, `level`, `disposed`). 0: nothing owed (not disposed).
1: obligations exist (disposed), the finding, with `board`'s summary line.
2: refused or UNREADABLE. A finding is never an instrument failure, nor an
unreadable read a clean zero (the RCA's section 5.6: 143 passes once read a
finding's rc 1 as "unavailable").
"""
from __future__ import annotations

import collections
import datetime
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_train import is_sha  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
KINDS = {
    "handoff-no-pr": "derived", "handoff-update": "derived", "probe-ref": "derived",
    "handoff-hold-malformed": "derived", "handoff-held": "derived",
    "design-build": "derived", "review-owed": "derived",
    "probe-refused": "derived", "confirm-owed": "derived", "push-stuck": "derived",
    "reviewer-fire": "event", "verdict-unposted": "event", "approve-held-runs": "event",
    "dispatch": "event", "train-stop": "event", "postmerge-owed": "event",
}
PR_KEYED = ("reviewer-fire", "verdict-unposted", "approve-held-runs", "dispatch")
ARMS = (("refs/heads/probe/", "probe-ref"), ("refs/heads/handoff-body/", "handoff-no-pr"),
        ("refs/heads/handoff/", "handoff-no-pr"), ("refs/heads/design-verdict/", "design-build"),
        ("refs/heads/review/", "confirm-owed"))
STATE_REF = re.compile(r"^audit-r\d+-(?:plan|roster)$")
RELAY_WRITE = re.compile(r"\b(ledger_open|level_line) ([a-z-]+) ")
VERDICT = re.compile(r"^Fix review: (?:merge|blocked) ([0-9a-f]{40})(?: |$)")
APPROVE = re.compile(r"^Design review: approve ([0-9a-f]{40})\s*$")
NOT_DISPATCHED = (None, "", "not-started")
DISP, EVENTS, LEGACY_DISP = "dispositions.tsv", "events.tsv", "cloud-disposed"
OPS = ("open", "close", "attempt")
AGING_ENV, AGING_DEFAULT = "HPO_LEDGER_AGING", (4.0, 12.0)
NS = "refs/hpo-ledger"


class Refused(Exception):
    """An input the ledger will not take: a ref of no arm, a kind of no table."""


class Unreadable(Exception):
    """A store or world read that failed: never a clean board."""


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_log() -> str:
    return os.path.join(os.environ.get("HPO_STATE_DIR") or os.path.expanduser("~/.local/state/hpo"),
                        "cloud-relay.log")


def classify(ref: str) -> str:
    for prefix, kind in ARMS:
        if ref.startswith(prefix) and len(ref) > len(prefix):
            return kind
    raise Refused(f"'{ref}' matches no ledger arm ({', '.join(p for p, _ in ARMS)})")


def topic_of(ref: str) -> str:
    return next(ref[len(p):] for p, _ in ARMS if ref.startswith(p))


def kind_of(kind: str) -> str:
    if kind not in KINDS:
        raise Refused(f"'{kind}' is no ledger kind: an obligation nothing reads is refused, never stored")
    return KINDS[kind]


def relay_writers(text: str) -> "list[tuple[int, str, str]]":
    """(line, kind, sink) for every `ledger_open <kind>` (event) and `level_line
    <kind>` (level) call in cloud_relay.sh before `self_test()`: the one census of
    the relay's writers, read by the self-test and r10_ledger_class_reach.py."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("self_test()"):
            break
        if line.lstrip().startswith(("#", "ledger_open()", "level_line()", "level_set()")):
            continue
        out += [(n, m.group(2), "event" if m.group(1) == "ledger_open" else "level")
                for m in RELAY_WRITE.finditer(line)]
    return out


def _rows(path: Path, width: int) -> "list[list[str]] | None":
    """The store's rows; None when it is missing (first run)."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable(f"{path.name}: {e}") from e
    rows = [l.split("\t") for l in text.splitlines() if l and not l.startswith("#")]
    bad = next((r for r in rows if len(r) != width), None)
    if bad is not None:
        raise Unreadable(f"{path.name}: a row of {len(bad)} fields, not {width}")
    return rows


def _clean(s: str) -> str:
    return re.sub(r"[\t\r\n]+", " ", s).strip() or "-"


def _write(path: Path, header: str, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}")
    tmp.write_text(header + "".join("\t".join(r) + "\n" for r in rows), encoding="utf-8")
    tmp.replace(path)


def _append(path: Path, row: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\t".join(_clean(x) for x in row) + "\n")


# ------------------------------------------------------------ dispositions
def _import_disposed(home: Path) -> "tuple[list, list[str]]":
    """cloud-disposed's `<ref> <sha>` lines as rows, the last per ref; refusals."""
    try:
        lines = (home / LEGACY_DISP).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return [], []
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable(f"{LEGACY_DISP}: {e}") from e
    last: dict[str, str] = {}
    refused = []
    for l in lines:
        f = l.split()
        if not f:
            continue
        try:
            if len(f) != 2 or not is_sha(f[1]):
                raise Refused(f"'{l}' is not `<ref> <sha40>`")
            classify(f[0])
        except Refused as e:
            refused.append(str(e))
            continue
        last.pop(f[0], None)
        last[f[0]] = f[1]
    return [[r, s, "imported", LEGACY_DISP] for r, s in last.items()], refused


def dispositions(home: Path, persist: bool = False) -> dict:
    """{ref: (sha, utc, how)}, the last disposition per ref."""
    rows = _rows(home / DISP, 4)
    if rows is None:
        rows, refused = _import_disposed(home)
        for r in refused:
            print(f"ledger: import refused: {r}", file=sys.stderr)
        if persist and (rows or refused):
            _write(home / DISP, f"# imported from {LEGACY_DISP} at {utc()}: {len(rows)} ref(s), "
                   f"{len(refused)} refused\n", rows)
    out = {}
    for ref, sha, when, how in rows:
        if not is_sha(sha):
            raise Unreadable(f"{DISP}: '{sha}' is not a sha")
        out[ref] = (sha, when, how)
    return out


def dispose(home: Path, ref: str, sha: str, how: str = "disposed") -> None:
    classify(ref)
    if not is_sha(sha):
        raise Refused("sha must be 40 lowercase hex")
    dispositions(home, persist=True)  # the one-time import lands before the first act
    _append(home / DISP, [ref, sha, utc(), how])


# ------------------------------------------------------------------ events
def _import_log(log: str) -> "tuple[list, list[str]]":
    """The log's still-open OWED events as `open` rows, each keeping its line."""
    try:
        lines = Path(log).read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return [], []
    except OSError as e:
        raise Unreadable(f"relay log: {e}") from e
    owed: dict[str, list[list[str]]] = {}
    for l in lines:
        f = l.split()
        pr = next((x for x in f[1:4] if x.isdigit()), None)
        if f[:1] == ["OWED"] and pr is not None:
            owed.setdefault(pr, []).append(f)
        elif f[:1] == ["POSTED"] and pr is not None:
            owed.pop(pr, None)
    rows, refused = [], []
    for pr, fs in owed.items():
        for f in fs:
            line = " ".join(f)
            if f[1] == "reviewer-fire":
                kind, when, sha = "reviewer-fire", f[-1], f[3]
            elif f[2] in ("approve-held-runs", "dispatch"):
                kind, when = f[2], f[1]
                sha = f[4] if len(f) > 4 and is_sha(f[4]) else "-"
            elif f[2] == "handoff-update":
                continue  # derived now: the relay's level from cloud-handoff-failed
            elif f[2] == pr and len(f) > 3 and (f[3] == "-" or is_sha(f[3])):
                kind, when, sha = "verdict-unposted", f[1], "-"
            else:
                refused.append(f"'{line}' is no relay OWED shape")
                continue
            rows.append(["open", when, kind, pr, sha, line])
    return rows, refused


def events(home: Path, log: str, persist: bool = False) -> list:
    rows = _rows(home / EVENTS, 6)
    if rows is None:
        rows, refused = _import_log(log)
        for r in refused:
            print(f"ledger: import refused: {r}", file=sys.stderr)
        if persist:
            _write(home / EVENTS, f"# imported from {Path(log).name} at {utc()}: {len(rows)} open "
                   f"event(s), {len(refused)} refused\n", rows)
    for op, _, kind, _, sha, _ in rows:
        if op not in OPS or (op != "attempt" and KINDS.get(kind) != "event") \
                or not (sha == "-" or is_sha(sha)):
            raise Unreadable(f"{EVENTS}: a row '{op} {kind} {sha}' of no ledger shape")
    return rows


def record(home: Path, log: str, op: str, kind: str, subject: str, sha: str, text: str) -> None:
    if op == "attempt":
        if classify(subject) != "handoff-no-pr":
            raise Refused("an attempt is recorded on a handoff ref")
    elif kind_of(kind) != "event":
        raise Refused(f"'{kind}' is derived: it is recomputed each pass, never opened or closed")
    if not (sha == "-" or is_sha(sha)):
        raise Refused("sha must be 40 lowercase hex or -")
    events(home, log, persist=True)  # the one-time import lands before the first event
    _append(home / EVENTS, [op, utc(), kind, subject, sha, text])


def verdict_head(line: str) -> "str | None":
    m = VERDICT.match(line)
    return m.group(1) if m else None


def fold(rows: list, live: "dict | None" = None, readback: "dict | None" = None):
    """(open [(kind, subject, sha, utc, text)], closed Counter by how). `live`
    is {pr: head} of the open PRs, `readback` {pr: [verdict first lines]} of
    the PRs whose comments were read; either None closes nothing by it."""
    cur: dict = {}
    closed = collections.Counter()
    for op, when, kind, subj, sha, text in rows:
        if op == "open":
            if cur.get((kind, subj), (sha,))[0] != sha:
                closed["superseded"] += 1
            cur[(kind, subj)] = (sha, when, text)
        elif op == "close" and (kind, subj) in cur and sha in ("-", cur[(kind, subj)][0]):
            del cur[(kind, subj)]
            closed["closed"] += 1
    out = []
    for (kind, subj), (sha, when, text) in cur.items():
        how = None
        if kind in PR_KEYED and live is not None:
            how = ("subject-absent" if subj not in live
                   else "superseded" if sha != "-" and live[subj] != sha else None)
        if how is None and kind in PR_KEYED and readback is not None and subj in readback:
            lines = readback[subj]
            if (text in lines if kind == "verdict-unposted"
                    else sha != "-" and any(verdict_head(l) == sha for l in lines)):
                how = "read-back"
        if how:
            closed[how] += 1
        else:
            out.append((kind, subj, sha, when, text))
    return out, closed


def render(ob: tuple) -> str:
    kind, subj, sha, when, text = ob
    return text if text.startswith("OWED ") else f"OWED {when} {kind} {subj} {sha} {text}"


def attempts(rows: list) -> dict:
    """{ref: (sha, utc, outcome)}, the last opener attempt per ref."""
    return {subj: (sha, when, text) for op, when, _, subj, sha, text in rows if op == "attempt"}


# ------------------------------------------------------------------- level
def covered(git, main: str, tip: str) -> bool:
    """Main carries every file tip's uncovered commits touch: the same bytes at
    the path; an added file's bytes elsewhere (a recovery moved it); a deletion
    main already made; or every line they add on main's copy and every line
    they remove gone from it (a hunk re-applied into a file main has changed)."""
    rc, mb = git(["merge-base", main, tip])
    if rc:
        return False
    mb = mb.strip()
    rc, names = git(["diff", "--name-status", "--no-renames", mb, tip])
    if rc or not names.strip():
        return False
    blobs, by_line = None, []
    for row in names.splitlines():
        st, path = row.split("\t", 1)
        rc_t, b_tip = git(["rev-parse", f"{tip}:{path}"])
        rc_m, b_main = git(["rev-parse", f"{main}:{path}"])
        if st == "D":
            if rc_m == 0:
                return False
        elif rc_t:
            return False
        elif rc_m == 0 and b_main == b_tip:
            continue
        elif rc_m:
            if blobs is None:
                rc, out = git(["ls-tree", "-r", main])
                blobs = {l.split()[2] for l in out.splitlines()} if rc == 0 else set()
            if b_tip.strip() not in blobs:
                return False
        else:
            by_line.append(path)
    if not by_line:
        return True
    rc, diff = git(["diff", "--no-color", "--no-renames", "-U0", mb, tip, "--", *by_line])
    if rc:
        return False
    files: dict[str, tuple[set, set]] = {}
    path = None
    for l in diff.splitlines():
        if l.startswith("Binary files "):
            return False
        if l.startswith("+++ "):
            path = l[6:]
            files.setdefault(path, (set(), set()))
        elif path and l.startswith("+") and l[1:].strip():
            files[path][0].add(l[1:].strip())
        elif path and l.startswith("-") and not l.startswith("--- ") and l[1:].strip():
            files[path][1].add(l[1:].strip())
    for path, (add, rem) in files.items():
        rc, text = git(["show", f"{main}:{path}"])
        if rc:
            return False
        have = {l.strip() for l in text.splitlines()}
        if not add <= have or rem & have:
            return False
    return True


def reverse_applies(git, main: str, tip: str) -> bool:
    """Tip's patch from its merge base with main applies to main reversed and
    not forward: main holds the change, context and all (the brief's test),
    checked in a throwaway index, never the work tree."""
    rc, mb = git(["merge-base", main, tip])
    if rc:
        return False
    with tempfile.TemporaryDirectory() as d:
        patch, env = os.path.join(d, "p.diff"), {"GIT_INDEX_FILE": os.path.join(d, "index")}
        rc, diff = git(["diff", "--binary", "--full-index", "--no-renames", mb.strip(), tip])
        if rc or not diff.strip():
            return False
        Path(patch).write_text(diff if diff.endswith("\n") else diff + "\n")
        if git(["read-tree", main], env)[0]:
            return False
        return (git(["apply", "--cached", "--check", "--reverse", patch], env)[0] == 0
                and git(["apply", "--cached", "--check", patch], env)[0] != 0)


ANCESTRY_WHY, CONTENT_WHY = ("ancestor", "merges-only"), ("reverse-apply", "content")


def landed(git, main: str, tip: str, heads=(), ancestry: bool = True, content: bool = True) -> "str | None":
    """Why main, or a live fix/* head, already carries tip; None when nothing
    does. The one classifier of a handoff's landing: `level` folds the relay's
    handoff-no-pr through it and bus.sh orphans asks it (`landed` below).
      ancestor       every commit of tip is inside main or a head
      merges-only    the only commits outside them are merges whose combined
                     diff is empty (no resolution of their own)
      reverse-apply  reverse_applies: the patch is on main, context and all
      content        covered: the change is on main under another commit"""
    if ancestry:
        rc, out = git(["rev-list", "--count", tip, "--not", main, *heads])
        if rc == 0 and out.strip() == "0":
            return "ancestor"
        rc, out = git(["rev-list", "--no-merges", "--count", tip, "--not", main, *heads])
        if rc == 0 and out.strip() == "0":
            rc, merges = git(["rev-list", "--merges", tip, "--not", main, *heads])
            if rc == 0 and all((lambda r: r[0] == 0 and not r[1].strip())(
                    git(["diff-tree", "--cc", "--no-commit-id", "-p", m])) for m in merges.split()):
                return "merges-only"
    if content:
        if reverse_applies(git, main, tip):
            return "reverse-apply"
        if covered(git, main, tip):
            return "content"
    return None


def handoff_level(hrefs: list, topics: set, git, disp: dict, att: dict, now: str, merged: "dict | None" = None):
    """(level lines, Counter of why each listed ref is or is not owed). merged:
    {topic: epoch} of merged pull requests, which close a tip committed by then."""
    merged = merged or {}
    rc, main = git(["rev-parse", "--verify", f"{NS}/main"])
    if rc:
        raise Unreadable("no main in the ledger's fetched namespace")
    main = main.strip()
    rc, out = git(["for-each-ref", "--format=%(objectname)", f"{NS}/fix/"])
    if rc:
        raise Unreadable("the fetched fix/* heads could not be listed")
    heads = sorted(set(out.split()))
    code = {topic_of(r): s for s, r in hrefs if r.startswith("refs/heads/handoff/")}
    body = {topic_of(r): s for s, r in hrefs if r.startswith("refs/heads/handoff-body/")}
    carried: dict[str, bool] = {}

    def is_carried(t: str) -> bool:
        if t not in carried:
            sha = code.get(t)
            carried[t] = bool(sha) and landed(git, main, sha, heads) is not None
        return carried[t]

    ct = {}
    for sha in sorted({s for s, _ in hrefs}):  # one tip's missing object must not blank the rest
        rc, out = git(["log", "-1", "--format=%ct", sha])
        if rc == 0 and out.strip().isdigit():
            ct[sha] = out.strip()
    lines, why = [], collections.Counter()
    for sha, ref in hrefs:
        t = topic_of(ref)
        if STATE_REF.match(t):
            why["state-ref"] += 1
        elif t in code and not ref.startswith("refs/heads/handoff/"):
            why["body-follows-code"] += 1  # one obligation per topic: its code ref's line stands for both
        elif t in topics:
            why["open-pr"] += 1
        elif disp.get(ref, ("",))[0] == sha:
            why["disposed"] += 1
        elif t in merged and ct.get(code.get(t, sha), "").isdigit() and int(ct[code.get(t, sha)]) <= merged[t]:
            why["merged-pr"] += 1  # delivered by that merge; a re-handoff committed after it stays owed
        elif is_carried(t):
            why["carried"] += 1
        else:
            why["owed"] += 1
            a = att.get(f"refs/heads/handoff/{t}")
            tail = f" attempt={a[1]},{a[2].replace(' ', '_')}" if a and a[0] == code.get(t) else ""
            bref = f" body={body[t]}" if ref.startswith("refs/heads/handoff/") and t in body else ""
            lines.append(f"OWED {now} handoff-no-pr {ref} {sha} ct={ct.get(sha, '?')}{bref}{tail}")
    return lines, why


def read_topics(text: str) -> "tuple[set, dict]":
    """The level's topics file: open-PR topics, and {topic: epoch} of each
    topic's latest merged pull request (a reused topic can merge twice)."""
    topics, merged = set(), {}
    for l in text.splitlines():
        f = l.split()
        if len(f) == 2 and f[1].startswith("merged="):
            when = datetime.datetime.fromisoformat(f[1][7:].replace("Z", "+00:00")).timestamp()
            merged[f[0]] = max(merged.get(f[0], 0), int(when))
        elif len(f) == 1:
            topics.add(f[0])
        elif f:
            raise Refused(f"topics: '{l}' is neither '<topic>' nor '<topic> merged=<utc>'")
    return topics, merged


def fetch_world(git) -> None:
    rc, out = git(["fetch", "-q", "--prune", "origin", f"+refs/heads/main:{NS}/main",
                   f"+refs/heads/handoff/*:{NS}/handoff/*", f"+refs/heads/handoff-body/*:{NS}/handoff-body/*",
                   f"+refs/heads/fix/*:{NS}/fix/*"])
    if rc:
        raise Unreadable(f"could not fetch origin's refs ({out.strip()[-100:]}): a shut fetch is not a clean zero")


# ------------------------------------------------------------------- aging
def parse_aging(value: "str | None"):
    """(dispatch_h, owner_h), or None when the switch is off."""
    if value is None or value.strip() == "":
        return AGING_DEFAULT
    if value.strip() == "off":
        return None
    try:
        a, b = (float(x) for x in value.split(","))
    except ValueError:
        raise Refused(f"{AGING_ENV}='{value}' is not '<dispatch_h>,<owner_h>' or 'off'") from None
    if not 0 < a <= b:
        raise Refused(f"{AGING_ENV}='{value}': want 0 < dispatch_h <= owner_h")
    return a, b


def escalate(level_rows: list, now: datetime.datetime, aging, group_of) -> list[str]:
    """DISPATCH lines, oldest first, then OWNER FLAG lines, one per topic."""
    if aging is None:
        return []
    by: dict[str, dict] = {}
    for row in level_rows:
        f = row.split()
        if len(f) < 5 or f[2] != "handoff-no-pr":
            continue
        kv = dict(x.split("=", 1) for x in f[5:] if "=" in x)
        t = by.setdefault(topic_of(f[3]), {})
        t["code" if f[3].startswith("refs/heads/handoff/") else "body"] = (f[3], f[4], kv)
    queue = []
    for t, refs in by.items():
        ref, sha, kv = refs.get("code") or refs["body"]
        if not kv.get("ct", "").isdigit():
            continue
        age = (now.timestamp() - int(kv["ct"])) / 3600  # ahead of the clock: < 0, below any threshold
        repair = ("no code ref" if "code" not in refs
                  else "opener" if "body" in refs or "body" in refs["code"][2] else "no body ref")
        queue.append((age, t, ref, sha, repair, kv.get("attempt")))
    queue.sort(key=lambda q: -q[0])
    out = [f"DISPATCH: {group_of(t) or '?'} {ref} {sha[:12]} {repair} ({age:.1f}h"
           + (f"; last attempt {a}" if a else "") + ")" for age, t, ref, sha, repair, a in queue
           if age >= aging[0]]
    out += [f"OWNER FLAG: {group_of(t) or '?'} {ref} {sha[:12]} stranded {age:.1f}h "
            f"(threshold {aging[1]:g}h)" for age, t, ref, sha, repair, a in queue if age >= aging[1]]
    return out


# ------------------------------------------------------- tick-side derived
def design_builds(verdicts: dict, designs: dict, stage_of, disp: dict) -> list[str]:
    """`design-build` lines: an approved design/<t> owes a build dispatch.
    verdicts {t: (design-verdict sha, verdict.md first line)}, designs {t: sha},
    both keyed lowercased; stage_of(t) -> (group, stage)."""
    out = []
    for t, (vsha, first) in sorted(verdicts.items()):
        m = APPROVE.match(first)
        if not m or designs.get(t) != m.group(1):
            continue  # revise, or approved at a design head that has since moved
        group, stage = stage_of(t)
        if stage not in NOT_DISPATCHED or disp.get(f"refs/heads/design-verdict/{t}", ("",))[0] == vsha:
            continue
        out.append(f"DESIGN-BUILD: {group or '?'} design/{t} {m.group(1)[:12]} approved, no build "
                   f"dispatched (stage {stage or 'none'})")
    return out


def review_owed(prs: list, readback: dict, dispatched: set, carries=None) -> list[str]:
    """`REVIEW OWED: #N <head12>` per open non-draft PR whose comments were
    read, no verdict names its head, no dispatch record is at that head, and
    -- with `carries(verdict_head, head)` -- the newest verdict is not a merge
    that carries to the head (the train's predicate, app_approve_carries)."""
    out = []
    for pr in sorted(prs, key=lambda p: p["number"]):
        n, head = pr["number"], pr.get("headRefOid") or ""
        if pr.get("isDraft") or str(n) not in readback or not head:
            continue
        lines = readback[str(n)]
        if any(verdict_head(l) == head for l in lines) or (str(n), head) in dispatched:
            continue
        last = lines[-1] if lines else ""
        if carries and last.startswith("Fix review: merge ") and carries(verdict_head(last), head):
            continue
        out.append(f"REVIEW OWED: #{n} {head[:12]}")
    return out


def app_approve_carries(cwd: str, main: str, env=None):
    """carries(verdict, head) through `tools/pr/app_approve.sh --carry`, run in `cwd` against
    `main`: True only on its rc 0, so a carry it cannot decide stays owed."""
    def carries(verdict: str, head: str) -> bool:
        return subprocess.run(["bash", str(ROOT / "tools/pr/app_approve.sh"), "--carry", verdict, head, main],
                              cwd=cwd, env=env, capture_output=True).returncode == 0
    return carries


# --------------------------------------------------------------------- CLI
def _git_cwd(argv: list, env: "dict | None" = None) -> "tuple[int, str]":
    r = subprocess.run(["git", *argv], capture_output=True, text=True,
                       env={**os.environ, **env} if env else None)
    return r.returncode, r.stdout + (r.stderr if r.returncode else "")


def main(argv: list) -> int:
    log = default_log()
    if argv[:1] == ["--log"]:
        if len(argv) < 2:
            print("ledger: --log needs a file", file=sys.stderr)
            return 2
        log, argv = argv[1], argv[2:]
    home = Path(log).parent
    cmd, args = (argv[0] if argv else ""), argv[1:]
    try:
        if cmd == "dispose" and len(args) in (2, 3):
            dispose(home, args[0], args[1], args[2] if len(args) == 3 else "disposed")
            print(f"ledger: disposed {args[0]} {args[1]}")
            return 0
        if cmd == "disposed" and len(args) == 2:
            classify(args[0])
            return 0 if dispositions(home).get(args[0], ("",))[0] == args[1] else 1
        if cmd in ("open", "close") and len(args) >= 3:
            record(home, log, cmd, args[0], args[1], args[2], " ".join(args[3:]))
            return 0
        if cmd == "attempt" and len(args) == 3:
            record(home, log, "attempt", "handoff-no-pr", args[0], args[1], args[2])
            return 0
        if cmd == "level" and len(args) == 2:
            hrefs = [tuple(l.split()[:2]) for l in Path(args[0]).read_text().splitlines() if len(l.split()) >= 2]
            topics, merged = read_topics(Path(args[1]).read_text())
            fetch_world(_git_cwd)
            lines, why = handoff_level(hrefs, topics, _git_cwd, dispositions(home),
                                       attempts(events(home, log)), utc(), merged)
            print("".join(l + "\n" for l in lines), end="")
            print("ledger: level " + " ".join(f"{k}={v}" for k, v in sorted(why.items())), file=sys.stderr)
            return 1 if lines else 0
        if cmd == "landed" and args:
            flags = {a for a in args if a in ("--no-ancestry", "--no-content")}
            shas = [a for a in args if a not in flags]
            if not shas or not all(is_sha(a) for a in shas):
                raise Refused("landed takes <main> [<head>...] as 40-hex shas, the tips on stdin")
            for tip in sys.stdin.read().split():
                if not is_sha(tip):
                    raise Refused(f"'{tip}' is no 40-hex tip")
                why = landed(_git_cwd, shas[0], tip, shas[1:], "--no-ancestry" not in flags,
                             "--no-content" not in flags)
                print(f"{tip} {why or '-'}")
            return 0
        if cmd == "board" and not args:
            open_, closed = fold(events(home, log))
            for ob in open_:
                print(render(ob))
            print(f"ledger: {len(open_)} open event obligation(s); closed "
                  + (" ".join(f"{k}={v}" for k, v in sorted(closed.items())) or "none"))
            return 1 if open_ else 0
        if cmd == "--self-test":
            return self_test()
    except Refused as e:
        print(f"ledger: refused: {e}", file=sys.stderr)
        return 2
    except (Unreadable, OSError) as e:
        print(f"ledger: UNREADABLE: {e}", file=sys.stderr)
        return 2
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


# --------------------------------------------------------------- self-test
def self_test() -> int:
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_env, throwaway_git_init
    ok = bad = 0

    def check(name: str, cond: bool) -> None:
        nonlocal ok, bad
        ok, bad = ok + bool(cond), bad + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def refuses(call) -> str:
        try:
            call()
        except Exception as e:  # a crash names its class, so it never reads as the refusal
            return type(e).__name__
        return ""

    A, B, C = "a" * 40, "b" * 40, "c" * 40
    with tempfile.TemporaryDirectory() as d:
        D = Path(d)
        # ---- dispositions: classification, import, last per ref
        check("each of the five arms classifies", [classify(f"refs/heads/{p}/x") for p in
              ("probe", "handoff", "handoff-body", "design-verdict", "review")]
              == ["probe-ref", "handoff-no-pr", "handoff-no-pr", "design-build", "confirm-owed"])
        check("a ref of no arm is refused, not guessed", refuses(lambda: classify("refs/heads/main")) == "Refused")
        h = D / "imp"
        h.mkdir()
        (h / LEGACY_DISP).write_text(
            f"refs/heads/handoff/t1 {A}\nrefs/heads/handoff-body/t1 {A}\nrefs/heads/probe/p {A}\n"
            f"refs/heads/handoff/t1 {B}\nrefs/heads/handoff/t1 {B}\nrefs/heads/wip-sync/x {A}\n")
        got = dispositions(h)
        check("the import takes the last disposition per ref (t1 at its re-disposal)",
              got.get("refs/heads/handoff/t1", ("",))[0] == B and len(got) == 3)
        check("a reader imports in memory and writes nothing", not (h / DISP).exists())
        dispose(h, "refs/heads/probe/q", C, "test")
        check("the first act persists the import, then itself",
              (h / DISP).read_text().count("\n") == 1 + 3 + 1 and dispositions(h)["refs/heads/probe/q"][0] == C)
        check("a ref matching no arm in the import was refused (wip-sync)",
              "refs/heads/wip-sync/x" not in dispositions(h))
        check("dispose refuses a ref of no arm", refuses(lambda: dispose(h, "refs/heads/main", A)) == "Refused")
        check("a missing store with no legacy file is first run: empty", dispositions(D / "none") == {})
        (D / "bad").mkdir()
        (D / "bad" / DISP).write_text("refs/heads/probe/x\tnot-a-sha\tt\th\n")
        check("a store row with no sha is UNREADABLE, never empty",
              refuses(lambda: dispositions(D / "bad")) == "Unreadable")
        (D / "dir").mkdir()
        (D / "dir" / DISP).mkdir()
        check("an unreadable store (a directory) is UNREADABLE", refuses(lambda: dispositions(D / "dir")) == "Unreadable")
        # ---- events: import, keying, supersede, closers
        e = D / "ev"
        e.mkdir()
        log = str(e / "cloud-relay.log")
        Path(log).write_text("\n".join([
            f"OWED 2026-10-18T19:00:00Z 7 {A} bus.sh confirm failed; run it by hand",
            f"POSTED 2026-10-18T19:10:00Z 7 {A}",
            f"OWED 2026-10-18T19:20:00Z 8 - push-verdict printed no 40-hex review commit",
            f"OWED reviewer-fire 9 {B} {'0' * 32} 2026-10-18T19:01:00Z",
            f"OWED 2026-10-18T19:02:00Z handoff-update 9 topic-9 {B}",
            f"OWED 2026-10-18T19:03:00Z dispatch 10 {C} bus.sh dispatch failed; run it by hand",
            f"OWED 2026-10-21T07:00:00Z handoff-no-pr refs/heads/handoff/x {A}",
            f"OWED 2026-10-21T07:00:00Z 11 frobnicate {A}"]) + "\n")
        rows = events(e, log)
        open_, _ = fold(rows)
        check("the import keeps b38c6431a's rule: a POSTED clears its PR, a level copy is skipped",
              sorted((k, s) for k, s, *_ in open_) == [("dispatch", "10"), ("reviewer-fire", "9"),
                                                       ("verdict-unposted", "8")])
        check("an imported event prints its journal line unchanged",
              render(next(o for o in open_ if o[1] == "8")) == "OWED 2026-10-18T19:20:00Z 8 - push-verdict "
              "printed no 40-hex review commit")
        check("an OWED of no relay shape is refused at import, not imported",
              not any(s == "11" for _, s, *_ in open_))
        check("a reader of the events writes nothing", not (e / EVENTS).exists())
        record(e, log, "open", "reviewer-fire", "12", A, "nonce=n")
        check("the first event persists the import", (e / EVENTS).exists() and len(events(e, log)) == 4)
        record(e, log, "open", "reviewer-fire", "12", B, "nonce=m")
        open_, closed = fold(events(e, log))
        check("a moved subject closes the old entry and opens one",
              [o[2] for o in open_ if o[1] == "12"] == [B] and closed["superseded"] == 1)
        record(e, log, "close", "reviewer-fire", "12", A, "stale")
        check("a close at another sha closes nothing", any(o[1] == "12" for o in fold(events(e, log))[0]))
        record(e, log, "close", "reviewer-fire", "12", B, "fired")
        check("a close at its sha is the producer's disposal",
              not any(o[1] == "12" for o in fold(events(e, log))[0]))
        check("an obligation of no kind is refused", refuses(lambda: record(e, log, "open", "frob", "1", A, "")) == "Refused")
        check("a derived kind is never opened", refuses(lambda: record(e, log, "open", "handoff-no-pr", "1", A, "")) == "Refused")
        check("postmerge-owed is an event kind (K17 2)", KINDS["postmerge-owed"] == "event")
        v = f"Fix review: merge {C}"
        rv = [["open", "t", "verdict-unposted", "20", C, v], ["open", "t", "reviewer-fire", "21", C, "n"],
              ["open", "t", "approve-held-runs", "22", C, "b"], ["open", "t", "train-stop", "23", C, "s"]]
        live = {"20": C, "21": C, "22": A, "23": C}
        o0 = {s for _, s, *_ in fold(rv)[0]}
        o1, c1 = fold(rv, live=live, readback={"20": [v], "21": [f"Fix review: blocked {C} x: y"]})
        check("null control: with nothing read, every event stays open", o0 == {"20", "21", "22", "23"})
        check("verdict-unposted closes on a read-back of its first line (4b)", "20" not in {s for _, s, *_ in o1})
        check("reviewer-fire closes on any verdict naming its head", "21" not in {s for _, s, *_ in o1})
        check("a PR head moved off the sha supersedes", "22" not in {s for _, s, *_ in o1} and c1["superseded"] == 1)
        check("train-stop closes only on its close row", "23" in {s for _, s, *_ in o1})
        o2, _ = fold(rv, live=live, readback={"20": [f"Fix review: merge {A}"]})
        check("a relayed claim is no close: a read-back of another verdict leaves it open",
              "20" in {s for _, s, *_ in o2})
        o3, c3 = fold(rv, live={"23": C})
        check("a PR no longer open closes its PR-keyed events (subject-absent)",
              {s for _, s, *_ in o3} == {"23"} and c3["subject-absent"] == 3)
        (D / "badev").mkdir()
        (D / "badev" / EVENTS).write_text(f"open\tt\tfrob\t1\t{A}\tx\n")
        check("an events row of no ledger kind is UNREADABLE", refuses(lambda: events(D / "badev", log)) == "Unreadable")
        # ---- aging, the switch, escalation
        now = datetime.datetime(2026, 10, 23, 12, tzinfo=datetime.timezone.utc)
        ts = lambda h: int(now.timestamp() - h * 3600)
        lv = [f"OWED x handoff-no-pr refs/heads/handoff/old {A} ct={ts(30)}",
              f"OWED x handoff-no-pr refs/heads/handoff-body/old {A} ct={ts(30)}",
              f"OWED x handoff-no-pr refs/heads/handoff/mid {B} ct={ts(5)} attempt=t,rc=143",
              f"OWED x handoff-no-pr refs/heads/handoff/new {C} ct={ts(1)}",
              f"OWED x handoff-no-pr refs/heads/handoff/fut {C} ct={ts(-3)}"]
        es = escalate(lv, now, parse_aging(None), {"old": "R10-OLD"}.get)
        check("the default switch is the owner's 4 h / 12 h", parse_aging(None) == (4.0, 12.0))
        check("DISPATCH oldest first, one per topic, naming group, repair and the attempt",
              [x.split(" (")[0] for x in es if x.startswith("DISPATCH")]
              == [f"DISPATCH: R10-OLD refs/heads/handoff/old {A[:12]} opener",
                  f"DISPATCH: ? refs/heads/handoff/mid {B[:12]} no body ref"]
              and "last attempt t,rc=143" in es[1])
        check("an OWNER FLAG past the second threshold only", [x.split()[2] for x in es if x.startswith("OWNER")]
              == ["R10-OLD"])
        check("null control: a young tip and a tip ahead of the clock escalate nothing",
              not any("/new " in x or "/fut " in x for x in es))
        check("the switch off escalates nothing", escalate(lv, now, parse_aging("off"), dict().get) == [])
        check("a malformed switch is refused", refuses(lambda: parse_aging("4")) == "Refused"
              and refuses(lambda: parse_aging("12,4")) == "Refused")
        check("a moved threshold moves the queue", len([x for x in escalate(lv, now, parse_aging("0.5,40"), dict().get)
                                                         if x.startswith("DISPATCH")]) == 3)
        # ---- design-build and review-owed
        ap = f"Design review: approve {A}"
        vd = {"g1": (B, ap), "g2": (B, ap), "g3": (B, f"Design review: revise {A} class-open"), "g4": (B, ap)}
        st = {"g1": ("R10-G1", "not-started"), "g2": ("R10-G2", "in-progress"), "g4": (None, None)}
        db = design_builds(vd, {"g1": A, "g2": A, "g3": A, "g4": C}, lambda t: st.get(t, (None, None)), {})
        check("an approved design with its group not dispatched owes a build; dispatched, revised and moved do not",
              [x.split()[1] for x in db] == ["R10-G1"])
        check("disposing the verdict ref at its sha closes it",
              design_builds(vd, {"g1": A}, lambda t: st.get(t, (None, None)),
                            {"refs/heads/design-verdict/g1": (B, "t", "h")}) == [])
        prs = [{"number": 1, "headRefOid": A}, {"number": 2, "headRefOid": B}, {"number": 3, "headRefOid": C},
               {"number": 4, "headRefOid": C, "isDraft": True}]
        ro = review_owed(prs, {"1": [f"Fix review: merge {A}"], "2": [], "3": [], "4": []}, {("2", B)})
        check("REVIEW OWED: of reviewed, dispatched and neither, exactly the one with neither",
              ro == [f"REVIEW OWED: #3 {C[:12]}"])
        check("a PR whose comments were not read owes nothing it cannot know",
              review_owed(prs, {}, set()) == [])
        # ---- REVIEW OWED's carry filter, through app_approve.sh --carry itself
        cw = D / "cw"
        cw.mkdir()
        throwaway_git_init(cw, "-q", "-b", "main")
        cg = lambda *a: subprocess.run(["git", "-C", str(cw), *a], capture_output=True, text=True,
                                       env=throwaway_git_env()).stdout.strip()
        cput = lambda p, m: ((cw / p).write_text(m + "\n"), cg("add", "-A"), cg("commit", "-qm", m),
                             cg("rev-parse", "HEAD"))[-1]
        cput("base.txt", "base")
        cg("checkout", "-qb", "fix")
        vh = cput("fix.txt", "the reviewed fix")
        cg("checkout", "-q", "main")
        cput("main.txt", "main moves on")
        cg("checkout", "-q", "fix")
        cg("merge", "-q", "--no-edit", "main")
        carried_head = cg("rev-parse", "HEAD")
        own_head = cput("fix.txt", "a commit of the branch's own after the verdict")
        rb = {"5": [f"Fix review: blocked {vh} harness: x", f"Fix review: merge {vh}"],
              "6": [f"Fix review: merge {vh}"]}
        crs = [{"number": 5, "headRefOid": carried_head}, {"number": 6, "headRefOid": own_head}]
        carrier = app_approve_carries(str(cw), "main", env=throwaway_git_env())
        check("REVIEW OWED skips a head its newest merge verdict carries to (a clean main merge); "
              "a branch-own commit after it is owed (null control)",
              review_owed(crs, rb, set(), carrier) == [f"REVIEW OWED: #6 {own_head[:12]}"])
        rb["5"].append(f"Fix review: blocked {vh} harness: y")
        check("a newest verdict that is blocked carries nothing", [l.split()[2] for l in
              review_owed(crs, rb, set(), carrier)] == ["#5", "#6"])
        # ---- covered, the level, the exit codes, over a throwaway origin
        env = throwaway_git_env()
        o, w = D / "o.git", D / "w"
        throwaway_git_init(o, "-q", "--bare")
        throwaway_git_init(w, "-q", "-b", "main")
        g = lambda *a: subprocess.run(["git", "-C", str(w), *a], capture_output=True, text=True, env=env).stdout.strip()
        put = lambda p, s, m: ((w / p).write_text(s), g("add", "-A"), g("commit", "-qm", m), g("rev-parse", "HEAD"))[-1]
        put("f.py", "a\nb\n", "base")
        g("remote", "add", "origin", str(o))
        g("checkout", "-qb", "work")
        cov = put("f.py", "a\nb\nblock1\nblock2\n", "the handoff adds a block")
        g("checkout", "-q", "main")
        put("f.py", "z\na\nb\nblock1\nblock2\n", "another PR lands it beside a change")
        g("checkout", "-qb", "work2", cov + "~1")
        unc = put("f.py", "a\nb\nnot-on-main\n", "a line main lacks")
        g("checkout", "-q", "main")
        g("checkout", "-qb", "work3", cov + "~1")
        anc = g("rev-parse", "HEAD")
        g("checkout", "-q", "main")
        bo = D / "bo"
        throwaway_git_init(bo, "-q")
        (bo / "BODY.md").write_text("body\n")
        subprocess.run(["git", "-C", str(bo), "add", "-A"], env=env, check=True)
        subprocess.run(["git", "-C", str(bo), "commit", "-qm", "body"], env=env, check=True)
        subprocess.run(["git", "-C", str(bo), "push", "-q", str(o), "HEAD:refs/heads/handoff-body/bodyonly"],
                       env=env, check=True)
        g("push", "-q", "origin", "main", f"{cov}:refs/heads/handoff/cov", f"{unc}:refs/heads/handoff/unc",
          f"{unc}:refs/heads/handoff-body/unc", f"{anc}:refs/heads/handoff/anc",
          f"{unc}:refs/heads/handoff/audit-r10-roster", f"{unc}:refs/heads/handoff/open",
          f"{unc}:refs/heads/handoff/disp")
        gw = lambda argv, extra=None: (lambda r: (r.returncode, r.stdout + (r.stderr if r.returncode else "")))(
            subprocess.run(["git", "-C", str(w), *argv], capture_output=True, text=True, env={**env, **(extra or {})}))
        fetch_world(gw)
        mn = g("rev-parse", "main")
        check("covered: a hunk main carries beside a later change (the ecaf178c shape)", covered(gw, mn, cov))
        check("null control: a hunk adding a line main lacks is not covered", not covered(gw, mn, unc))
        # ---- landed: the one classifier bus.sh orphans shares
        g("checkout", "-qb", "work4", cov + "~1")
        put("g.txt", "x\nfi\ny\nfi\np\nq\nr\ns\nt\n", "g base")
        gb = g("rev-parse", "HEAD")
        rv = put("g.txt", "x\nfi\ny\np\nq\nr\ns\nt\n", "drop the second fi")
        g("checkout", "-qb", "work5", gb)
        put("g.txt", "x\nfi\ny\np\nq\nr\ns\nT\n", "main lands it beside a change")
        rvm = g("rev-parse", "HEAD")
        g("checkout", "-qb", "work6", gb)
        rvn = put("g.txt", "x\ny\nfi\np\nq\nr\ns\nt\n", "drop the first fi")
        check("landed: a patch main holds whose removed line main keeps elsewhere is reverse-apply, not content",
              landed(gw, rvm, rv) == "reverse-apply" and not covered(gw, rvm, rv))
        check("null control: a patch main does not hold lands nowhere", landed(gw, rvm, rvn) is None)
        g("checkout", "-qb", "work13", gb)
        body_ = ["h1", "h2", "h3", "h4", "c1", "c2", "c3", "fi", "c4", "c5", "c6", "t1", "t2", "t3", "t4"]
        put("d.txt", "\n".join(body_) + "\n", "d base")
        db = g("rev-parse", "HEAD")
        dt = put("d.txt", "\n".join(x for x in body_ if x != "fi") + "\n", "drop fi")
        g("checkout", "-qb", "work14", db)
        dm = put("d.txt", "\n".join([x for x in body_ if x != "fi"] + body_[4:11] + ["e1", "e2", "e3"]) + "\n",
                 "main holds the patched region and an unpatched copy")
        check("null control: a patch that applies both ways (an unpatched copy remains) is not landed",
              landed(gw, dm, dt) is None and not reverse_applies(gw, dm, dt))
        check("landed: a tip inside main reads ancestor, not merges-only", landed(gw, mn, anc) == "ancestor")
        check("landed: the re-applied hunk is content (reverse-apply cannot: forward applies too)",
              landed(gw, mn, cov) == "content" and not reverse_applies(gw, mn, cov))
        g("checkout", "-qb", "work7", gb)
        mv = put("moved.txt", "same bytes\n", "add a file")
        g("checkout", "-qb", "work8", gb)
        (w / "sub").mkdir()
        mvm = put("sub/moved.txt", "same bytes\n", "main holds it at another path")
        check("covered: an added file whose bytes main holds at another path is carried (a moved file)",
              covered(gw, mvm, mv))
        check("null control: the same add with other bytes is not", not covered(gw, mvm, put("x.txt", "other\n", "x")))
        g("checkout", "-qb", "work15", gb)
        g("rm", "-q", "g.txt")
        tipd = put("y.txt", "same bytes\n", "delete g.txt, add bytes main holds elsewhere")
        check("null control: a tip deleting a file main still holds is not covered, beside a carried add",
              not covered(gw, mvm, tipd) and landed(gw, mvm, tipd) is None)
        g("checkout", "-qb", "work16", gb)
        g("rm", "-q", "g.txt")
        (w / "sub").mkdir(exist_ok=True)
        mdel = put("sub/moved.txt", "same bytes\n", "main deletes g.txt too and holds the add elsewhere")
        check("covered: a deletion main already made is carried", covered(gw, mdel, tipd))
        g("checkout", "-qb", "work17", gb)
        sbm = put("g.txt", "x\nfi\ny\np\nq\nr\ns\nt\n", "main holds rv's bytes under its own commit")
        check("covered: the same bytes at the path are carried, a removed line kept elsewhere notwithstanding",
              covered(gw, sbm, rv))
        g("checkout", "-qb", "work9", mvm)
        m_a = put("ma.txt", "A\n", "main side")
        g("checkout", "-qb", "work10", mvm)
        f_b = put("fb.txt", "B\n", "fix side")
        g("merge", "-q", "--no-edit", m_a)
        tipm = g("rev-parse", "HEAD")
        g("checkout", "-qb", "work11", f_b)
        fixh = put("fc.txt", "C\n", "the fix head carries both parents' work")
        g("merge", "-q", "--no-edit", m_a)
        fixh = g("rev-parse", "HEAD")
        check("landed: a merge tip whose parents main and a fix head carry is merges-only",
              landed(gw, m_a, tipm, [fixh]) == "merges-only")
        check("null control: without that fix head the same tip is not ancestry-carried",
              landed(gw, m_a, tipm, [], content=False) is None)
        g("checkout", "-qb", "work12", f_b)
        g("merge", "-q", "--no-commit", m_a)
        put("evil.txt", "E\n", "a merge with a resolution of its own")
        check("null control: a merge carrying its own resolution is not merges-only",
              landed(gw, m_a, g("rev-parse", "HEAD"), [fixh], content=False) is None)
        g("checkout", "-q", "main")
        hr = [tuple(l.split()) for l in g("ls-remote", "origin", "refs/heads/handoff/*",
                                           "refs/heads/handoff-body/*").splitlines()]
        att = {"refs/heads/handoff/unc": (unc, "2026-10-20T11:50:33Z", "rc=143")}
        lines, why = handoff_level(hr, {"open"}, gw, {"refs/heads/handoff/disp": (unc, "t", "h")}, att, "NOW")
        owed = sorted(l.split()[3] for l in lines)
        check("the level owes the uncovered topic once, at its code ref, and the body-only ref",
              owed == ["refs/heads/handoff-body/bodyonly", "refs/heads/handoff/unc"])
        check("the code ref's line names its body ref, which is no line of its own (one obligation per topic)",
              any(l.split()[3] == "refs/heads/handoff/unc" and f" body={unc}" in l for l in lines))
        check("and names each close: state ref, open PR, disposed, carried (ancestry and content), body",
              dict(why) == {"owed": 2, "state-ref": 1, "open-pr": 1, "disposed": 1, "carried": 2,
                            "body-follows-code": 1})
        l2, w2 = handoff_level(hr, {"open"}, gw, {}, att, "NOW", {"unc": 4102444800})
        check("a topic whose PR merged after its tip's commit is closed by the merge (RCA 5.1)",
              not any("/unc " in l for l in l2) and w2["merged-pr"] == 1)
        l2, w2 = handoff_level(hr, {"open"}, gw, {}, att, "NOW", {"unc": int(g("log", "-1", "--format=%ct", unc))})
        check("a merge in the tip's own commit second closes it (at or before, not strictly before)",
              not any("/unc " in l for l in l2) and w2["merged-pr"] == 1)
        tp, mg = read_topics("open\nt merged=2026-01-02T00:00:00Z\nt merged=2026-01-01T00:00:00Z\n")
        check("the topics reader keeps a topic's latest merge, whatever the listing order",
              tp == {"open"} and mg == {"t": 1767312000})
        l2, w2 = handoff_level(hr, {"open"}, gw, {}, att, "NOW", {"unc": 1})
        check("null control: a tip committed after its topic's merge stays owed",
              any(" refs/heads/handoff/unc " in l for l in l2) and "merged-pr" not in w2)
        check("every owed line, an orphan body ref's included, carries its tip's commit time",
              all(" ct=" in l and not l.split("ct=")[1].startswith("?") for l in lines))
        check("the code ref's topic carries the opener attempt at that tip",
              sum("attempt=2026-10-20T11:50:33Z,rc=143" in l for l in lines) == 1)
        bo_t = g("ls-remote", "origin", "refs/heads/handoff-body/bodyonly").split()[0]
        check("escalate: a code line naming its body is an opener; a body-only line has no code ref",
              sorted(re.sub(r"^DISPATCH: G (\S+) \S+ (.*) \(.*$", r"\1 \2", q) for q in escalate(
                  [f"OWED x handoff-no-pr refs/heads/handoff/unc {unc} ct=1 body={unc}",
                   f"OWED x handoff-no-pr refs/heads/handoff/nob {unc} ct=1",
                   f"OWED x handoff-no-pr refs/heads/handoff-body/bodyonly {bo_t} ct=1"],
                  datetime.datetime.now(datetime.timezone.utc), (1.0, 1e9), lambda t: "G")
                  if q.startswith("DISPATCH")) == ["refs/heads/handoff-body/bodyonly no code ref",
                                                    "refs/heads/handoff/nob no body ref",
                                                    "refs/heads/handoff/unc opener"])
        r = subprocess.run([sys.executable, "-I", __file__, "--log", str(e / "cloud-relay.log"), "board"],
                           capture_output=True, text=True)
        check("board: obligations exist is rc 1 with its summary line (a finding, not a failure)",
              r.returncode == 1 and "open event obligation(s)" in r.stdout.splitlines()[-1])
        r = subprocess.run([sys.executable, "-I", __file__, "--log", str(D / "empty" / "l"), "board"],
                           capture_output=True, text=True)
        check("board: nothing owed is rc 0 with its summary line", r.returncode == 0 and "0 open" in r.stdout)
        r = subprocess.run([sys.executable, "-I", __file__, "--log", str(D / "badev" / "l"), "board"],
                           capture_output=True, text=True)
        check("board: an unreadable store is rc 2 and UNREADABLE, never a summary",
              r.returncode == 2 and "UNREADABLE" in r.stderr and "open event" not in r.stdout)
        (D / "hr").write_text("\n".join(f"{s}\t{x}" for s, x in hr) + "\n")
        (D / "tp").write_text("open\n")
        r = subprocess.run([sys.executable, "-I", __file__, "--log", str(D / "lv" / "l"), "level",
                            str(D / "hr"), str(D / "tp")], capture_output=True, text=True, cwd=w, env=env)
        check("level CLI: owed lines on stdout, rc 1, the counts on stderr",
              r.returncode == 1 and r.stdout.count("handoff-no-pr") == 3 and "owed=3" in r.stderr)
        g("remote", "set-url", "origin", str(D / "absent.git"))
        r = subprocess.run([sys.executable, "-I", __file__, "--log", str(D / "lv" / "l"), "level",
                            str(D / "hr"), str(D / "tp")], capture_output=True, text=True, cwd=w, env=env)
        check("level CLI: a failed fetch is rc 2 and prints no level (unknown is not 'nothing owed')",
              r.returncode == 2 and r.stdout == "")
        # ---- open_pr.sh's own attempt lines: a TERMed opener records `unopened`, a clean one `opened`
        opener = (ROOT / "tools/audit/seat/open_pr.sh").read_text().splitlines()
        wired = [l for l in opener if l.startswith(('python3 -I "$SEAT/ledger.py" attempt', "pr_exit_trap 'python3"))]
        st = D / "op"

        def run_opener(body: str, term: bool) -> list:
            script = D / "op.sh"
            script.write_text("\n".join([f'. "{ROOT}/tools/audit/seat/pr_args.sh"',
                                         f'SEAT="{ROOT}/tools/audit/seat"; T=t1; PR_HT={A}', *wired, body]) + "\n")
            p = subprocess.Popen(["bash", str(script)], env={**os.environ, "HPO_STATE_DIR": str(st)},
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if term:
                for _ in range(400):  # past both attempt lines: the trap is installed
                    if (D / "op.ready").exists():
                        break
                    subprocess.run(["sleep", "0.05"])
                p.terminate()
            p.wait(timeout=30)
            return [r[5] for r in events(st, str(st / "cloud-relay.log")) if r[0] == "attempt"]
        killed = run_opener(f'touch "{D}/op.ready"; sleep 30 & wait $!\nPR_ATTEMPT=opened,PR=9', term=True)
        clean = run_opener("sleep 0.1 & wait $!\nPR_ATTEMPT=opened,PR=9", term=False)
        check("open_pr.sh carries both attempt lines", len(wired) == 2)
        check("a TERMed opener records started then unopened on its handoff ref", killed == ["started", "unopened"])
        check("null control: an opener that ends records opened,PR=<n>", clean[2:] == ["started", "opened,PR=9"])
        # ---- the relay's level writers each have a ledger kind
        writers = relay_writers((ROOT / "tools/audit/seat/cloud_relay.sh").read_text())
        used = {k for _, k, _ in writers}
        check("the census reads both sinks of the relay (ledger_open events, level_line levels)",
              {s for *_, s in writers} == {"event", "level"})
        check("every kind cloud_relay.sh writes is a ledger kind (census of level_line and ledger_open)",
              used and all(k in KINDS for k in used))
    print(f"ledger self-test: {ok + bad} checks, {bad} failed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
