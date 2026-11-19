#!/usr/bin/env python3
"""After a merge: the bookkeeping no contract hands an agent (`standing-merge.md`).

    python3 tools/audit/seat/postmerge.py [--repo O/R] [--state-dir D] [--dry-run] [--retry] <PR>
    python3 tools/audit/seat/postmerge.py --self-test [--no-mutants]

Both merge paths (`merge_pr.sh`, and `merge_train.py`'s landing) call it once
the merge is confirmed. It runs, in order, and a failure in any is printed as
`OWED <step>: <why>` and never undoes the merge or stops the next step:

  record   `record_beat.py`: one record-issue line from the fixed template, posted by
           `tools/pr/gh_comment.py` with a byte-identical read-back.
  stage    `roster_sync.py --apply` derives the group's `done` stage from the
           merged pull request, the group resolved from the roster
           (`record_beat.resolve_group`), never guessed. A refused or raced
           sync queues `set-stage <GROUP> done --at-sha <merge sha>` on the
           beat's roster drain (below) and prints `stage QUEUED <line>`: the
           direct push is kept first, and the drain, which retries nothing it
           refused but records each refusal in its events, is the one writer
           of the retry (a second push loop here lost every race against a
           backlogged drain). With no group, or a queue it cannot write, it
           prints `set-stage owed <GROUP>|no-group <merge sha>` and is owed.
  marks    each merged-body line `Carry N: built here (<KEY>, ...)` or `Carry
           N: dismissed (<KEY>, <reason>)` is one `mark-carry <GROUP> --match
           <KEY> implemented <merge sha>|dismissed <reason>` op on the drain,
           keyed on KEY because the body counts carries from 1 and the roster
           from 0. KEY must be contained in exactly one carry of the group; a
           line naming no key, or one hitting zero or two carries, prints
           `OWED mark: ...` and queues nothing. A carry already marked is
           skipped. Marks queue before the stage op, so `done` reads them.

THE QUEUE is `<state dir>/roster-drain.queue`, the file beat_jobs.py's
roster-drain row runs. Every line postmerge appends ends `# postmerge <merge
sha>` (roster_queue's grammar drops a `#` word and what follows); a line
already in the queue, marked or not, is not appended again, so a rerun for one
merge queues nothing. The new lines go in one `O_APPEND` write, each
newline-terminated: the drain runs only terminated lines.
  main     `merge_train.py classify <merge sha> --main`: main's own suite
           state, the one rule the train and the sweep read (no third). RED or
           unreadable is owed; WAIT (the push's checks still running) is not.

The state docs are the plan-beat's alone (beat_jobs.py `plan-beat`): a second
writer here raced it and its rejected push printed `OWED docs: rc 2: hi`.

An owed step is opened in the ledger as the event `postmerge-owed`
(`ledger.py open postmerge-owed <pr> <merge-sha40> <why>`); `--retry` after a
fully clean run closes it (`ledger.py close postmerge-owed ... <how>`), the
only closer that kind has. Exit 0 when nothing is owed, else 1, after the
lines. `--dry-run` prints the exact comment and every command and runs none.
"""
from __future__ import annotations

import argparse
import os
import re
import shlex
import sys
from pathlib import Path

SEAT = Path(__file__).resolve().parent
sys.path.insert(0, str(SEAT))
import record_beat as rb  # noqa: E402
import roster_lib  # noqa: E402  the carry-mark grammar

QUEUE = "roster-drain.queue"
#: A body's carry disposition line: bullet optional, the key the first comma-separated
#: field inside the parentheses. "Carry N: not built here" does not match.
DISPOSED = re.compile(r"^[ \t]*(?:[-*][ \t]+)?Carry (\d+): (built here|dismissed)\b(?: \(([^)\n]*)\))?", re.M)

ROOT = rb.ROOT
PY = [sys.executable, "-I"]


def steps(pr: int, repo: str, state_dir: Path, sha: str, group: str) -> "list[tuple[str, list, bool]]":
    """(name, argv, mutating): the commands after the comment, in order."""
    seat = str(SEAT)
    return [
        ("stage", [*PY, f"{seat}/roster_sync.py", "--repo", repo, "--apply"], True),
        ("main", [*PY, f"{seat}/merge_train.py", "classify", sha, "--repo", repo, "--main"], False),
    ]


def refusal_detail(o: str) -> str:
    """The step's last line, led by the lint ERROR lines a refusal printed: the
    TOTAL line alone never named what the gate refused (P435)."""
    lines = [ln.strip() for ln in o.strip().splitlines()]
    if not lines:
        return "no output"
    errs = [ln for ln in lines if ln.startswith("ERROR")][:3]
    return " | ".join(errs + [lines[-1]])[:300]


def derive_marks(body: str, roster: "dict | None", group: str, sha: str) -> "tuple[list[str], list[str]]":
    """(mark-carry op lines, owed reasons) for the body's DISPOSED lines,
    each keyed on its quoted text and checked to hit exactly one carry."""
    lines = list(DISPOSED.finditer(body or ""))
    g = next((x for x in (roster or {}).get("groups", []) if x.get("group") == group), None)
    if lines and g is None:
        return [], [f"{len(lines)} carry disposition line(s) and no roster group {group}"]
    ops, owed = [], []
    for m in lines:
        n, kind, inner = m.groups()
        key, _, why = (inner or "").partition(",")
        key, why = key.strip(), why.strip()
        hits = [c for c in g.get("carry", []) if key and key in c]
        if not key or len(hits) != 1:
            owed.append(f"Carry {n}: {kind} key {key!r} hits {len(hits)} carries of {group}, not one")
            continue
        if roster_lib.carry_mark(hits[0]):
            continue  # marked already: a second mark is refused, so none is queued
        if kind == "dismissed" and (not why or "]" in why):
            owed.append(f"Carry {n}: dismissed names no reason a mark can hold: {why!r}")
            continue
        mark = f"implemented {sha}" if kind == "built here" else f"dismissed {shlex.quote(why)}"
        ops.append(f"mark-carry {group} --match {shlex.quote(key)} {mark}")
    return ops, owed


def enqueue(state_dir: Path, ops: "list[str]", sha: str) -> "list[str]":
    """Append each op not already queued for this merge; return the appended lines."""
    path = state_dir / QUEUE
    have = set()
    for raw in (path.read_text().splitlines() if path.exists() else ()):
        text = raw.strip()
        for pre in ("#done ", "#refused ", "#held "):
            text = text[len(pre):] if text.startswith(pre) else text
        have.add(text)
    new = [line for line in (f"{op}  # postmerge {sha}" for op in ops) if line not in have]
    if new:
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(fd, "".join(line + "\n" for line in new).encode())
        finally:
            os.close(fd)
    return new


def postmerge(pr: int, repo: str, state_dir: Path, dry: bool, retry: bool = False,
              run=rb.sh, out=print, roster=None) -> int:
    owed: "list[tuple[str, str]]" = []
    try:
        f = rb.facts(pr, repo, run)
    except rb.Owed as e:
        out(f"OWED record: {e}")
        return 1  # no full sha: nothing below can name its subject
    sha = f["sha"]
    roster_now = roster if roster is not None else rb.load_roster(run)
    group = rb.resolve_group(roster_now, f["branch"], pr)
    try:
        rb.record(pr, repo, state_dir, f, group, dry, run, out)
    except rb.Owed as e:
        owed.append(("record", str(e)))
    marks, unkeyed = derive_marks(f.get("body", ""), roster_now, group, sha) if group != rb.NO_GROUP else ([], [])
    owed += [("mark", why) for why in unkeyed]
    for name, argv, mutating in steps(pr, repo, state_dir, sha, group):
        if dry:
            out(f"DRY-RUN {name}: " + " ".join(argv))
            continue
        code, o = run(argv)
        last = refusal_detail(o)
        if name == "main":
            out(f"main {last}")
            if code == 3:  # WAIT: the push's own checks are still running
                continue
        if name == "stage":
            queued = marks + ([f"set-stage {group} done --at-sha {sha}"] if code != 0 else [])
            if not queued:
                continue  # a clean sync and no mark: nothing to queue, nothing owed
            try:
                if group == rb.NO_GROUP:
                    raise OSError("no group to queue")
                new = enqueue(state_dir, queued, sha)
            except OSError as e:
                if code == 0:
                    owed.append(("mark", f"queue: {e}"))
                    continue
                owed.append((name, f"rc {code}: {last}"))
                out(f"set-stage owed {group} {sha}" if group != rb.NO_GROUP else f"set-stage owed no-group {sha}")
                continue
            if code != 0:
                out(f"stage refused rc {code}: {last}")
            for line in new:
                out(f"{'stage' if line.startswith('set-stage ') else 'mark'} QUEUED {line}")
            continue
        if code != 0:
            owed.append((name, f"rc {code}: {last}"))
    if dry:
        for op in marks:
            out(f"DRY-RUN queue: {op}  # postmerge {sha}")
    for name, why in owed:
        out(f"OWED {name}: {why}")
    ledger = [*PY, f"{SEAT}/ledger.py"]
    if owed and not dry:
        run([*ledger, "open", "postmerge-owed", str(pr), sha, "; ".join(f"{n}: {w}" for n, w in owed)[:300]])
    elif not owed and retry and not dry:
        run([*ledger, "close", "postmerge-owed", str(pr), sha, "a clean postmerge rerun"])
    if not owed:
        out(f"postmerge #{pr} {sha}: nothing owed")
    return 1 if owed else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pr", nargs="?", type=int)
    ap.add_argument("--repo", default=rb.DEFAULT_REPO)
    ap.add_argument("--state-dir", default=os.environ.get("HPO_STATE_DIR")
                    or str(Path.home() / ".local/state/hpo"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retry", action="store_true", help="a rerun of an owed merge: a clean run closes the event")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--no-mutants", action="store_true", help="the self-test without its mutant pass")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test(mutants=not a.no_mutants)
    if a.pr is None:
        ap.error("give the merged <PR>")
    return postmerge(a.pr, a.repo, Path(a.state_dir), a.dry_run, a.retry)


#: (site, replacement, the case it must turn red), each run on a temp copy.
MUTANTS = {
    "null": ("", "", ""),  # no edit: the copy must pass whole, or a crash would read as every kill
    "no_newline": ('os.write(fd, "".join(line + "\\n" for line in new).encode())',
                   'os.write(fd, "".join(line for line in new).encode())',
                   "(i) a refused or raced stage queues exactly one terminated line for the merge, owing nothing"),
    "no_idempotence_key": ('    new = [line for line in (f"{op}  # postmerge {sha}" for op in ops) if line not in have]',
                           '    new = [line for line in (f"{op}  # postmerge {sha}" for op in ops)]',
                           "(ii) a second postmerge run for that merge queues nothing, the first line marked or not"),
    "marks_by_index": ('        hits = [c for c in g.get("carry", []) if key and key in c]',
                       '        hits = [c for c in g.get("carry", [])[int(n):int(n) + 1]]\n        key = hits[0][:20] if hits else key',
                       "(i) #3470's body yields exactly the two marks batch 236 queued by hand, keyed on text"),
    "two_hits_taken": ('        if not key or len(hits) != 1:', '        if not key or not hits:',
                       "a key hitting two carries, none, or no key is OWED and queues nothing; a marked carry is skipped"),
    "empty_queue_owed": ("            if not queued:\n                continue", "            if False:\n                continue",
                         "a clean sync with no roster group owes nothing, queues nothing and opens no ledger event"),
    "stage_not_queued": ('            queued = marks + ([f"set-stage {group} done --at-sha {sha}"] if code != 0 else [])',
                         '            queued = marks',
                         "(i) a refused or raced stage queues exactly one terminated line for the merge, owing nothing"),
}


def self_test(mutants: bool = True) -> int:
    import json
    import subprocess
    import tempfile
    fails, n = [], [0]

    def check(name, ok, got=""):
        n[0] += 1
        if not ok:
            fails.append(f"{name} (got: {got})")
            print("FAIL", fails[-1], flush=True)

    full = "c" * 40
    roster = {"groups": [{"group": "R10-X", "resume": {"branch": "fix/r10-x"}}]}
    det = refusal_detail("x\n  ERROR   [G-1] cite: a.py:9 moved\nTOTAL: 1 error(s)\n")
    check("refusal_detail leads with the lint ERROR line", "G-1" in det and det.endswith("TOTAL: 1 error(s)"), det)
    check("refusal_detail of plain output is its last line (null control)",
          refusal_detail("a\nb\n") == "b" and refusal_detail("") == "no output")

    def fake(rc=None, said=None):
        rc, said = rc or {}, said or {}
        log = []

        def run(argv, stdin=None, cwd=None):
            log.append(list(argv))
            j = " ".join(map(str, argv))
            if argv[:3] == ["gh", "pr", "view"]:
                return 0, json.dumps({"state": "MERGED", "mergeCommit": {"oid": full},
                                      "headRefName": "fix/r10-x",
                                      "closingIssuesReferences": [{"number": 5}]})
            if "rev-parse" in j:
                return 0, full + "\n"
            for key in ("gh_comment.py", "roster_sync.py", "classify", "ledger.py"):
                if key in j:
                    return rc.get(key, 0), said.get(key, f"{key} said" + (" REFUSED" if rc.get(key) else ""))
            return 0, ""
        return run, log

    def go(rc=None, dry=False, retry=False, said=None, state=None, body="", ros=None):
        run, log = fake(rc, said)
        lines = []
        real = rb.facts
        rb.facts = lambda *a, **k: {**real(*a, **k), "body": body}  # the fake's gh answer carries no body
        try:
            with tempfile.TemporaryDirectory() as td:
                code = postmerge(7, rb.DEFAULT_REPO, Path(state or td), dry, retry, run, lines.append,
                                 roster if ros is None else ros)
        finally:
            rb.facts = real
        return code, lines, [" ".join(map(str, a)) for a in log]

    code, lines, log = go()
    check("a clean run owes nothing, exits 0 and says so", code == 0 and lines[-1].endswith("nothing owed"), lines)
    check("a clean run runs the comment, the sync and the main read, once each",
          [sum(k in c for c in log) for k in ("gh_comment.py post", "roster_sync.py",
                                              "merge_train.py classify")] == [1, 1, 1], log)
    check("postmerge runs no state_docs.py (the plan-beat owns the state docs)",
          not any("state_docs.py" in c for c in log), log)
    code, lines, log = go(dry=True)
    check("the dry run prints the exact comment and every command, runs none, exits 0",
          code == 0 and lines[0] == f"DRY-RUN comment: Merged #7 {full} (R10-X). Closed issues: #5. Leaves #{rb.RECORD_ISSUE} open."
          and [l.split(":")[0] for l in lines[1:4]] == ["DRY-RUN command", "DRY-RUN stage", "DRY-RUN main"]
          and not any(k in c for c in log for k in ("gh_comment", "roster_sync", "classify", "ledger")),
          lines)
    for key, step in (("gh_comment.py", "record"), ("classify", "main")):
        code, lines, log = go({key: 1})
        owed = [l for l in lines if l.startswith("OWED ")]
        check(f"a refused {step} step prints OWED {step}, exits non-zero, after the other steps ran",
              code == 1 and len(owed) == 1 and owed[0].startswith(f"OWED {step}:")
              and sum("roster_sync.py" in c or "gh_comment" in c for c in log) >= 2, lines)
        check(f"... and opens postmerge-owed for the pull request and the full merge sha ({step})",
              any(f"ledger.py open postmerge-owed 7 {full} " in c for c in log), log)
    import roster_queue as rq
    stage_line = f"set-stage R10-X done --at-sha {full}  # postmerge {full}"
    with tempfile.TemporaryDirectory() as st:
        q = Path(st) / QUEUE
        code, lines, _ = go({"roster_sync.py": 1}, state=st)
        first = q.read_text() if q.exists() else ""
        check("(i) a refused or raced stage queues exactly one terminated line for the merge, owing nothing",
              code == 0 and first == stage_line + "\n" and f"stage QUEUED {stage_line}" in lines
              and not any(l.startswith("OWED") for l in lines), (first, lines))
        check("... and that line parses as the set-stage op it names, replay-safe",
              rq.parse_line(first) == ("set-stage", "R10-X", "done", ["--at-sha", full])
              and rq.replay_unsafe("set-stage", ["--at-sha", full]) is None, rq.parse_line(first))
        q.write_text(f"#done {first}" + "set-stage R10-Y done\n")
        code, lines, _ = go({"roster_sync.py": 1}, state=st)
        check("(ii) a second postmerge run for that merge queues nothing, the first line marked or not",
              q.read_text() == f"#done {stage_line}\nset-stage R10-Y done\n"
              and not any("QUEUED" in l for l in lines), lines)
    with tempfile.TemporaryDirectory() as st:
        code, lines, _ = go(state=st)
        check("(iii) null control: a sync that landed queues nothing and creates no queue",
              code == 0 and not (Path(st) / QUEUE).exists() and not any("QUEUED" in l for l in lines), lines)
    with tempfile.TemporaryDirectory() as st:
        (Path(st) / QUEUE).mkdir()  # a queue that cannot be written
        code, lines, log = go({"roster_sync.py": 1}, state=st)
        check("a refused stage whose queue cannot be written is owed: set-stage owed <GROUP> <merge sha>",
              code == 1 and f"set-stage owed R10-X {full}" in lines
              and any(l.startswith("OWED stage: rc 1:") for l in lines)
              and any(f"ledger.py open postmerge-owed 7 {full} " in c for c in log), lines)
    with tempfile.TemporaryDirectory() as st:
        code, lines, _ = go({"roster_sync.py": 1}, state=st, ros={"groups": []})
        check("a refused stage with no roster group queues nothing and is owed as no-group",
              code == 1 and f"set-stage owed no-group {full}" in lines and not (Path(st) / QUEUE).exists(), lines)
    with tempfile.TemporaryDirectory() as st:
        code, lines, log = go(state=st, ros={"groups": []}, body="- x. Carry 1: built here")
        check("a clean sync with no roster group owes nothing, queues nothing and opens no ledger event",
              code == 0 and lines[-1].endswith("nothing owed") and not any(l.startswith("OWED") for l in lines)
              and not (Path(st) / QUEUE).exists() and not any("ledger.py open" in c for c in log), lines)
    gate = ("roster_edit: LINT GATE REFUSED the push\n  ERROR   [G-1] cite: a.py:9 moved\n\n"
            "TOTAL: 1 error(s) across 1 file(s)\nthe commit is local at 0123 in /w; nothing pushed\n")
    code, lines, _ = go({"roster_sync.py": 3}, said={"roster_sync.py": gate})
    check("a stage refused by the lint gate prints its ERROR line, not only the last line (P435)",
          any(l.startswith("stage refused rc 3: ") and "[G-1] cite: a.py:9" in l for l in lines), lines)
    # (v) replay of #3447 (merge ceb3070ccb, group R10-OUTSIDE-DIAG-REDACT-LOCATION), whose stage was routed by hand
    merged = "ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e"
    with tempfile.TemporaryDirectory() as st:
        enqueue(Path(st), [f"set-stage R10-OUTSIDE-DIAG-REDACT-LOCATION done --at-sha {merged}"], merged)
        got = (Path(st) / QUEUE).read_text()
    parsed = rq.parse_line(got)
    check("(v) #3447's derived stage op passes roster_queue.parse_line and replay_unsafe",
          parsed == ("set-stage", "R10-OUTSIDE-DIAG-REDACT-LOCATION", "done", ["--at-sha", merged])
          and rq.replay_unsafe(parsed[0], parsed[3]) is None, got)
    # marks: the #3470 replay (merge be86e36a56, R10-TRAIN-RESIDUE-P2; triage batch 236 queued its two marks by hand)
    m3470 = "be86e36a560fde88cc758cefcee322b9087a5deb"
    owed_key = "Carry 3: left for a later part; it stays on the roster."
    body3470 = ("Builds carries 17 and 18.\n\n" + "".join(f"- Carry {i}: left for a later part; it stays on the roster.\n"
                                                       for i in range(1, 17))
                + "- Carry 17: built here (TRAIN-POLICY-REASON-STALE-CONTEXT, `rollup_states`).\n"
                "- Carry 18: built here (TRAIN-UNDRAFT-EVERY-ROUTE, `record_drafts` and the `land` draft arm).\n")
    carries = [f"C{i} owed text" for i in range(16)] + [
        "TRAIN-POLICY-REASON-STALE-CONTEXT (triage: x#P608), in merge_train.py policy_refusal",
        "TRAIN-UNDRAFT-EVERY-ROUTE (triage: x#P609), in merge_train.py undraft()"] + [f"C{i} tail" for i in range(18, 23)]
    r3470 = {"groups": [{"group": "R10-TRAIN-RESIDUE-P2", "carry": carries}]}
    ops, why = derive_marks(body3470, r3470, "R10-TRAIN-RESIDUE-P2", m3470)
    want = [f"mark-carry R10-TRAIN-RESIDUE-P2 --match TRAIN-POLICY-REASON-STALE-CONTEXT implemented {m3470}",
            f"mark-carry R10-TRAIN-RESIDUE-P2 --match TRAIN-UNDRAFT-EVERY-ROUTE implemented {m3470}"]
    check("(i) #3470's body yields exactly the two marks batch 236 queued by hand, keyed on text", ops == want and not why,
          (ops, why))
    check("... each passes roster_queue.parse_line and replay_unsafe as a --match op",
          all(rq.parse_line(o)[:2] == ("mark-carry", "R10-TRAIN-RESIDUE-P2")
              and rq.replay_unsafe("mark-carry", rq.parse_line(o)[3]) is None for o in ops), ops)
    check("(iii) null control: a body with no built or dismissed line yields no op and owes nothing",
          derive_marks("Carry 1: left for a later part.\n- Carry 2: not built here. Carry: R10-X\n" + owed_key,
                        r3470, "R10-TRAIN-RESIDUE-P2", m3470) == ([], []))
    two = {"groups": [{"group": "G", "carry": ["KEY-A one", "KEY-A two", "KEY-B [implemented: abc1234]", "plain"]}]}
    ops, why = derive_marks("- Carry 1: built here (KEY-A, x)\n- Carry 2: built here.\n- Carry 3: built here (NONE)\n"
                            "- Carry 4: built here (KEY-B)\n- Carry 5: dismissed (plain, superseded by #12)\n"
                            "- Carry 6: dismissed (plain)\n", two, "G", m3470)
    check("a key hitting two carries, none, or no key is OWED and queues nothing; a marked carry is skipped",
          ops == ["mark-carry G --match plain dismissed 'superseded by #12'"]
          and [w.split(":")[0] for w in why] == ["Carry 1", "Carry 2", "Carry 3", "Carry 6"], (ops, why))
    check("a dismissed op's reason survives roster_queue's grammar whole, its '#' inside quotes",
          rq.parse_line(ops[0] + f"  # postmerge {m3470}") == ("mark-carry", "G", "", ["--match", "plain", "dismissed",
                                                                                       "superseded by #12"]),
          rq.parse_line(ops[0]))
    with tempfile.TemporaryDirectory() as st:
        code, lines, _ = go({"roster_sync.py": 1}, state=st, body=body3470,
                            ros={"groups": [{**r3470["groups"][0], "group": "R10-X", "resume": {"branch": "fix/r10-x"}}]})
        got = (Path(st) / QUEUE).read_text().splitlines()
        check("the marks queue before the stage op, all in one append, each ending the merge's tag",
              [g.split()[0] for g in got] == ["mark-carry", "mark-carry", "set-stage"]
              and all(g.endswith(f"  # postmerge {full}") for g in got)
              and sum(l.startswith("mark QUEUED ") for l in lines) == 2, (got, lines))
    code, lines, _ = go(body="- Carry 1: built here (NOPE)\n")
    check("an unkeyed body line is owed as `OWED mark:` and the run exits non-zero",
          code == 1 and any(l.startswith("OWED mark: Carry 1:") for l in lines), lines)
    code, lines, log = go({"classify": 3})
    check("main WAIT (checks still running) is printed, not owed", code == 0 and
          any(l.startswith("main ") for l in lines) and not any(l.startswith("OWED") for l in lines), lines)
    code, lines, log = go(retry=True)
    check("--retry after a clean run closes the event, the only closer",
          any(f"ledger.py close postmerge-owed 7 {full} " in c for c in log), log)
    code, lines, log = go()
    check("without --retry a clean run closes nothing (null control)",
          not any("ledger.py" in c for c in log), log)
    # CARRY 3: a beat this tool runs is never also handed to an agent by the
    # contract owning the post-merge bookkeeping, or it runs twice. The beats are
    # read from `steps()` itself, so a step added there is checked here unedited.
    beats = {f"{rb.__name__}.py", "gh_comment.py"} | {
        Path(argv[2]).name + ("" if argv[3].startswith("-") else " " + argv[3])
        for _, argv, _ in steps(1, "o/r", Path("."), full, "R10-X")}
    check("the beats are read from steps(): a subcommand is kept, an option is not",
          {"roster_sync.py", "merge_train.py classify"} <= beats, sorted(beats))

    def handed(text: str) -> "list[str]":
        return sorted(b for b in beats if b in text)
    orch = (ROOT / "dev/governance/roles/orchestrator.md").read_text()
    sec = orch.split("\n## 11.")[1].split("\n## ")[0] if "\n## 11." in orch else ""
    owner = sec + (ROOT / "dev/governance/roles/standing-merge.md").read_text()
    check("orchestrator.md section 11 still holds the after-each-merge duty this pin reads",
          "After each merge" in sec, sec[:80])
    check("orchestrator.md section 11 and standing-merge.md hand an agent no beat this tool runs (CARRY 3)",
          handed(owner) == [], handed(owner))
    check("a contract handing an agent `roster_sync.py --apply` is caught (null control)",
          handed(owner + "\n- After each merge: run `roster_sync.py --apply`.") == ["roster_sync.py"])
    if mutants:
        src = Path(__file__).read_text()
        code_part, sep, table = src.partition("\n#: (site, replacement")  # sites are counted in the code, not this table
        for name, (old, new, case) in MUTANTS.items():
            n[0] += 1
            if old and code_part.count(old) != 1:
                check(f"mutant {name}: its site appears once", False, code_part.count(old))
                continue
            with tempfile.TemporaryDirectory() as td:
                mp = Path(td) / "postmerge.py"
                mp.write_text(code_part.replace(old, new) + sep + table)
                r = subprocess.run([sys.executable, str(mp), "--self-test", "--no-mutants"],  # not -I: PYTHONPATH finds the seat modules
                                   capture_output=True, text=True, cwd=str(ROOT),
                                   env={**os.environ, "PYTHONPATH": str(SEAT)})
            killed = f"FAIL {case}" in r.stdout if case else ("0 failed" in r.stdout and "FAIL" not in r.stdout)
            print(f"  {'ok  ' if killed else 'FAIL'} mutant {name} " + (f"killed by: {case}" if case else "passes whole"), flush=True)
            if not killed:
                fails.append(f"mutant {name}")
    print(f"postmerge self-test: {n[0]} checks, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
