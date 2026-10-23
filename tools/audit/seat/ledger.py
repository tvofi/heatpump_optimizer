#!/usr/bin/env python3
"""The obligations ledger: one schema, two stores, one fold (R10-ORCH-LEDGER).

    python3 -I tools/audit/seat/ledger.py [--log FILE] dispose <ref> <sha40> [how]
    python3 -I tools/audit/seat/ledger.py [--log FILE] disposed <ref> <sha40>
    python3 -I tools/audit/seat/ledger.py [--log FILE] open <kind> <subject> <sha40|-> [why...]
    python3 -I tools/audit/seat/ledger.py [--log FILE] close <kind> <subject> <sha40|-> [how]
    python3 -I tools/audit/seat/ledger.py [--log FILE] attempt <ref> <sha40> <outcome>
    python3 -I tools/audit/seat/ledger.py [--log FILE] level <hrefs-file> <topics-file>
    python3 -I tools/audit/seat/ledger.py [--log FILE] board
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
request (the topics file); the ref is disposed at its sha; or main already
carries the change -- the code tip is inside main or a live `fix/*` head, or
every line its uncovered commits add is on main's copy of that file and every
line they remove is gone (`covered`: a hunk re-applied by another pull request
into a file main has since changed, which a byte-identical test cannot see).
A body ref follows its code ref there. Each owed line carries `ct=<epoch>`
(the tip's commit time) and the topic's last opener attempt at that tip.

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

ROOT = Path(__file__).resolve().parents[3]
KINDS = {
    "handoff-no-pr": "derived", "handoff-update": "derived", "probe-ref": "derived",
    "handoff-hold-malformed": "derived", "design-build": "derived", "review-owed": "derived",
    "reviewer-fire": "event", "verdict-unposted": "event", "approve-held-runs": "event",
    "dispatch": "event", "train-stop": "event", "postmerge-owed": "event",
}
PR_KEYED = ("reviewer-fire", "verdict-unposted", "approve-held-runs", "dispatch")
ARMS = (("refs/heads/probe/", "probe-ref"), ("refs/heads/handoff-body/", "handoff-no-pr"),
        ("refs/heads/handoff/", "handoff-no-pr"), ("refs/heads/design-verdict/", "design-build"))
STATE_REF = re.compile(r"^audit-r\d+-(?:plan|roster)$")
SHA = re.compile(r"^[0-9a-f]{40}$")
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
            if len(f) != 2 or not SHA.match(f[1]):
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
        if not SHA.match(sha):
            raise Unreadable(f"{DISP}: '{sha}' is not a sha")
        out[ref] = (sha, when, how)
    return out


def dispose(home: Path, ref: str, sha: str, how: str = "disposed") -> None:
    classify(ref)
    if not SHA.match(sha):
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
                sha = f[4] if len(f) > 4 and SHA.match(f[4]) else "-"
            elif f[2] == "handoff-update":
                continue  # derived now: the relay's level from cloud-handoff-failed
            elif f[2] == pr and len(f) > 3 and (f[3] == "-" or SHA.match(f[3])):
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
                or not (sha == "-" or SHA.match(sha)):
            raise Unreadable(f"{EVENTS}: a row '{op} {kind} {sha}' of no ledger shape")
    return rows


def record(home: Path, log: str, op: str, kind: str, subject: str, sha: str, text: str) -> None:
    if op == "attempt":
        if classify(subject) != "handoff-no-pr":
            raise Refused("an attempt is recorded on a handoff ref")
    elif kind_of(kind) != "event":
        raise Refused(f"'{kind}' is derived: it is recomputed each pass, never opened or closed")
    if not (sha == "-" or SHA.match(sha)):
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
    """Every line tip's uncovered commits add is on main's copy of its file,
    and every line they remove is gone from it: main carries the change."""
    rc, mb = git(["merge-base", main, tip])
    if rc:
        return False
    rc, diff = git(["diff", "--no-color", "--no-renames", "-U0", mb.strip(), tip])
    if rc or not diff.strip():
        return False
    files: dict[str, tuple[set, set]] = {}
    path = None
    for l in diff.splitlines():
        if l.startswith("Binary files "):
            return False
        if l.startswith("+++ "):
            path = l[6:] if l.startswith("+++ b/") else None
            if path is None:
                return False  # a deletion: covered only by a byte-identical arm, not this one
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
    return bool(files)


def handoff_level(hrefs: list, topics: set, git, disp: dict, att: dict, now: str):
    """(level lines, Counter of why each listed ref is or is not owed)."""
    rc, main = git(["rev-parse", "--verify", f"{NS}/main"])
    if rc:
        raise Unreadable("no main in the ledger's fetched namespace")
    main = main.strip()
    code = {topic_of(r): s for s, r in hrefs if r.startswith("refs/heads/handoff/")}
    carried: dict[str, bool] = {}

    def is_carried(t: str) -> bool:
        if t not in carried:
            sha = code.get(t)
            rc, out = git(["for-each-ref", "--contains", sha, "--format=%(refname)", f"{NS}/main", f"{NS}/fix/"]) \
                if sha else (1, "")
            carried[t] = bool(sha) and ((rc == 0 and bool(out.strip())) or covered(git, main, sha))
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
        elif t in topics:
            why["open-pr"] += 1
        elif disp.get(ref, ("",))[0] == sha:
            why["disposed"] += 1
        elif is_carried(t):
            why["carried"] += 1
        else:
            why["owed"] += 1
            a = att.get(f"refs/heads/handoff/{t}")
            tail = f" attempt={a[1]},{a[2].replace(' ', '_')}" if a and a[0] == code.get(t) else ""
            lines.append(f"OWED {now} handoff-no-pr {ref} {sha} ct={ct.get(sha, '?')}{tail}")
    return lines, why


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
        repair = "opener" if len(refs) == 2 else "no code ref" if "code" not in refs else "no body ref"
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


def review_owed(prs: list, readback: dict, dispatched: set) -> list[str]:
    """`REVIEW OWED: #N <head12>` per open non-draft PR whose comments were
    read, no verdict names its head, and no dispatch record is at that head."""
    out = []
    for pr in sorted(prs, key=lambda p: p["number"]):
        n, head = pr["number"], pr.get("headRefOid") or ""
        if pr.get("isDraft") or str(n) not in readback or not head:
            continue
        if any(verdict_head(l) == head for l in readback[str(n)]) or (str(n), head) in dispatched:
            continue
        out.append(f"REVIEW OWED: #{n} {head[:12]}")
    return out


# --------------------------------------------------------------------- CLI
def _git_cwd(argv: list) -> "tuple[int, str]":
    r = subprocess.run(["git", *argv], capture_output=True, text=True)
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
            topics = {l.strip() for l in Path(args[1]).read_text().splitlines() if l.strip()}
            fetch_world(_git_cwd)
            lines, why = handoff_level(hrefs, topics, _git_cwd, dispositions(home),
                                       attempts(events(home, log)), utc())
            print("".join(l + "\n" for l in lines), end="")
            print("ledger: level " + " ".join(f"{k}={v}" for k, v in sorted(why.items())), file=sys.stderr)
            return 1 if lines else 0
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
        check("each of the four arms classifies", [classify(f"refs/heads/{p}/x") for p in
              ("probe", "handoff", "handoff-body", "design-verdict")]
              == ["probe-ref", "handoff-no-pr", "handoff-no-pr", "design-build"])
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
        gw = lambda argv: (lambda r: (r.returncode, r.stdout + (r.stderr if r.returncode else "")))(
            subprocess.run(["git", "-C", str(w), *argv], capture_output=True, text=True, env=env))
        fetch_world(gw)
        mn = g("rev-parse", "main")
        check("covered: a hunk main carries beside a later change (the ecaf178c shape)", covered(gw, mn, cov))
        check("null control: a hunk adding a line main lacks is not covered", not covered(gw, mn, unc))
        hr = [tuple(l.split()) for l in g("ls-remote", "origin", "refs/heads/handoff/*",
                                           "refs/heads/handoff-body/*").splitlines()]
        att = {"refs/heads/handoff/unc": (unc, "2026-10-20T11:50:33Z", "rc=143")}
        lines, why = handoff_level(hr, {"open"}, gw, {"refs/heads/handoff/disp": (unc, "t", "h")}, att, "NOW")
        owed = sorted(l.split()[3] for l in lines)
        check("the level owes exactly the uncovered topic's two refs and the body-only ref",
              owed == ["refs/heads/handoff-body/bodyonly", "refs/heads/handoff-body/unc", "refs/heads/handoff/unc"])
        check("and names each close: state ref, open PR, disposed, carried (ancestry and content)",
              dict(why) == {"owed": 3, "state-ref": 1, "open-pr": 1, "disposed": 1, "carried": 2})
        check("every owed line, an orphan body ref's included, carries its tip's commit time",
              all(" ct=" in l and not l.split("ct=")[1].startswith("?") for l in lines))
        check("the code ref's topic carries the opener attempt at that tip",
              sum("attempt=2026-10-20T11:50:33Z,rc=143" in l for l in lines) == 2)
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
              r.returncode == 1 and r.stdout.count("handoff-no-pr") == 4 and "owed=4" in r.stderr)
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
                for _ in range(200):
                    if (st / EVENTS).exists() and "started" in (st / EVENTS).read_text().splitlines()[-1]:
                        break
                    subprocess.run(["sleep", "0.05"])
                p.terminate()
            p.wait(timeout=30)
            return [r[5] for r in events(st, str(st / "cloud-relay.log")) if r[0] == "attempt"]
        killed = run_opener("sleep 30 & wait $!\nPR_ATTEMPT=opened,PR=9", term=True)
        clean = run_opener("sleep 0.1 & wait $!\nPR_ATTEMPT=opened,PR=9", term=False)
        check("open_pr.sh carries both attempt lines", len(wired) == 2)
        check("a TERMed opener records started then unopened on its handoff ref", killed == ["started", "unopened"])
        check("null control: an opener that ends records opened,PR=<n>", clean[2:] == ["started", "opened,PR=9"])
        # ---- the relay's level writers each have a ledger kind
        relay = (ROOT / "tools/audit/seat/cloud_relay.sh").read_text()
        body = relay.split("\nself_test()")[0]
        used = set(re.findall(r"\blevel_line ([a-z-]+) ", body)) | set(re.findall(r"\bledger_open ([a-z-]+) ", body))
        check("every kind cloud_relay.sh writes is a ledger kind (census of level_line and ledger_open)",
              used and all(k in KINDS for k in used))
    print(f"ledger self-test: {ok + bad} checks, {bad} failed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
