#!/usr/bin/env python3
"""The roster seat's queue runner: one roster_edit.py op per queue line.

    python3 -I tools/audit/seat/roster_queue.py run FIRST LAST --queue Q --report R \
        --edit-checkout DIR --worktree WT --lint-clone LC [--alive FILE] [--branch B]
    python3 -I tools/audit/seat/roster_queue.py readback SHA GROUP TEXTFILE
    python3 -I tools/audit/seat/roster_queue.py run all --mark ... [--batch]
    python3 -I tools/audit/seat/roster_queue.py loop [--every 300] ...
    python3 -I tools/audit/seat/roster_queue.py release-held --queue Q --edit-checkout DIR
    python3 -I tools/audit/seat/roster_queue.py unwired --edit-checkout DIR --open-issues FILE [--ref REF]
    python3 -I tools/audit/seat/roster_queue.py show --edit-checkout DIR [--ref REF] [--stage S] [GROUP]
    python3 -I tools/audit/seat/roster_queue.py diff --edit-checkout DIR REF_A REF_B
    python3 -I tools/audit/seat/roster_queue.py --self-test

`show` and `diff` are read-only (`git show` of the roster at a ref, nothing
written, nothing fetched): one line per group or every field of one group, and
what changed between two refs (added, removed and changed groups and fields,
carry entries by text; rc 1 when the refs differ, as diff's). They replace the
scratch copies a seat rebuilds to read the roster.

`run` applies queue lines FIRST..LAST (1-based; blank and `#` lines skipped, a
leading line number dropped). Each line is `<op> <group> [arg] [--flag value ...]`, passed to
`roster_edit.py` with `--push`. WHY IT EXISTS: the lint gate refuses a push
whose `--lint-cwd` is not exactly `origin/main`, and main moves faster than a
checkout another seat owns can be kept level (2026-10-24: four refusals). So
the runner lints from `--lint-clone`, a checkout it owns, fetched and detached
at `origin/main` before every attempt, and retries up to four times when the
refusal is that main moved or the push lost a race with a clean lint
(the roster worktree is removed between attempts). It never moves
`--edit-checkout` (the orchestrator's), which only supplies the roster and the
shims; the editor is `--editor` or the roster_edit.py beside this script, the
same file for `run` and `run --batch` (`resolve_editor`). A refusal is reported, never forced.

LINE GRAMMAR (one parser for `run`, `--batch` and `loop`): an unquoted word that
begins with `#` ends the line (a `#` inside a word, or a quoted `'a # b'`,
stays); the first token after the group is the value unless it is a flag, and
`--flag value` pairs reach roster_edit as flags. `--mark` rewrites each applied
line in place as `#done <line>` (pushed, read-back not FAILED) or `#refused
<line>`, re-reading the queue at write time and replacing it atomically, so a
line appended meanwhile survives; `all` (with --mark) is every unmarked op line;
`#` lines (`#done`, `#refused`, `#held`, `#note`) are never applied. `--batch`
parses every line with roster_edit.parse_op, applies them in ONE worktree and
pushes once (a refused op is rolled back and skipped; any batch-level failure
falls back to the single-op path). `loop` re-provisions a missing --lint-clone,
then runs `all --mark` every --every seconds. `release-held` frees `#held
append-carry` lines whose batch file is on origin/main; `unwired` lists open
issues no roster group lists (carry_audit's ISSUE-UNLISTED).

Every `append-carry <group> @file` is read back from the pushed commit: the
roster JSON at that SHA must hold the file's text exactly as one carry entry.
`readback` prints the figures; the report line says FAILED when none match.
One report line per op: `roster: <op> <group> pushed <sha9> [| readback: ...]`
or `roster: <op> <group> refused rc=N <last three lines>`. `--alive` is
touched after each report line. Blind spot, stated: only append-carry with an
@file is read back here; other ops are read from the roster JSON by the caller.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROSTER_REL = "dev/programme/rosters/wave-r10-groups.json"
MOVED = "not origin/main"
SEAT_DIR = Path(__file__).resolve().parent


def resolve_editor(a):
    """THE editor, resolved once for `run` and `run --batch` alike: the
    `--editor` the caller passed, else the roster_edit.py beside this script.
    Never a file under --edit-checkout, which supplies the roster and the shims
    only, so a single-op run and a batch can never execute two versions, and
    the self-test's throwaway clone (no roster_edit.py) needs none."""
    return str(a.editor or SEAT_DIR / "roster_edit.py")


def load_editor(path):
    """The editor at `path` as a module, for the batch path (the single-op path
    runs the same file as a subprocess). Raises when it is not a roster_edit."""
    if "def batch_edit" not in Path(path).read_text():
        raise RuntimeError(f"{path} is not a roster_edit.py (no batch_edit)")  # run nothing
    spec = importlib.util.spec_from_file_location("roster_edit_batch", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for need in ("parse_op", "make_edit", "batch_edit", "write_roster"):
        if not hasattr(mod, need):
            raise RuntimeError(f"{path} has no {need}: not a roster_edit.py")
    return mod


def _git(*a, cwd=None, env=None):
    return subprocess.run(["git", *a], cwd=cwd, env=env, capture_output=True, text=True)


def _walk(o, grp):
    if isinstance(o, dict):
        if grp in (o.get("group"), o.get("id"), o.get("name")) and "carry" in o:
            yield o
        for v in o.values():
            yield from _walk(v, grp)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v, grp)


def readback(sha, grp, fn, cwd=None, rel=ROSTER_REL):
    """One line: the carry count, the indices equal to the file's text, the
    last entry's lengths. Raises when the SHA, roster or group is absent."""
    s = _git("show", f"{sha}:{rel}", cwd=cwd)
    if s.returncode:
        raise RuntimeError(f"no {rel} at {sha}: {s.stderr.strip()[-120:]}")
    g = next(_walk(json.loads(s.stdout), grp), None)
    if g is None:
        raise RuntimeError(f"group {grp} not in the roster at {sha}")
    want = Path(fn).read_text().strip()
    c = g["carry"]
    hit = [i for i, x in enumerate(c) if x.strip() == want]
    last = c[-1] if c else ""
    return (f"{grp} {sha[:9]} n_carry={len(c)} exact-match-index={hit} "
            f"last120={last[:120]!r} len={len(last)}/{len(want)}"), bool(hit)


def readback_text(sha, grp, text, cwd=None, rel=ROSTER_REL):
    """True when the first 60 characters of an inline carry are inside a carry
    entry of `grp` in the roster at `sha` (the LANDED test of the old loops)."""
    s = _git("show", f"{sha}:{rel}", cwd=cwd)
    if s.returncode:
        raise RuntimeError(f"no {rel} at {sha}: {s.stderr.strip()[-120:]}")
    g = next(_walk(json.loads(s.stdout), grp), None)
    if g is None:
        raise RuntimeError(f"group {grp} not in the roster at {sha}")
    want = text.strip()[:60]
    return any(want in x for x in g["carry"])


def _split(ln):
    """Shell words of `ln`, ending at an unquoted word that begins with `#`
    (shell semantics: `@/p/b#1.txt` and `s6-batch8.md#P70` keep their `#`, a
    quoted `'a # b'` is one word). Not shlex's comments=True, which cuts a `#`
    in the middle of a word (P300). Words are split by the one lexer, then
    each dequoted; a line it cannot dequote falls back to plain shlex.split."""
    try:
        lex = shlex.shlex(ln, posix=False)
        lex.whitespace_split, lex.commenters = True, ""
        out = []
        for tok in lex:
            if tok.startswith("#"):
                break
            out.append("".join(shlex.split(tok)))
        return out
    except ValueError:
        return shlex.split(ln)


def parse_line(ln):
    """`(op, group, value, flags)` of one queue line, or None for a blank or
    `#` line. THE ONE FLAG GRAMMAR, shared by `run`, `--batch` and `loop`: the
    first token after the group is the value unless it is a flag, and every
    `--flag value` after it reaches roster_edit as a flag, never folded into
    the value (`set-stage G done --at-sha S` once wrote stage "done --at-sha
    S", 2026-10-27)."""
    if not ln.strip() or ln.lstrip().startswith("#"):
        return None
    t = _split(ln)
    if t and t[0][0].isdigit():
        t = t[1:]
    if len(t) < 2:
        return None
    # A flag (`--match TEXT` on drop-carry) is never the op's positional value:
    # everything from the first `--` token on is passed through to roster_edit.
    rest = t[2:]
    if rest and rest[0].startswith("--"):
        return t[0], t[1], "", rest
    return t[0], t[1], (rest[0] if rest else ""), rest[1:]


def replay_unsafe(op, extra):
    """Why a queue may not run `op`, or None. A queue line can run twice: a
    pass killed after its push and before its record replays it
    (R10-RCA-ROSTER-DRAIN-REPLAY: 18 carries dropped, 2026-11-10). A carry op
    keyed by INDEX resolves again on the list its first run shifted, so a
    replayed `drop-carry G 6` deletes a second entry; `--match TEXT` refuses
    on replay instead. An index stays legitimate by hand, run once."""
    if op in ("drop-carry", "mark-carry") and "--match" not in extra:
        return (f"{op} by index is refused in a queue: a replay re-resolves the "
                "index on the shifted carry list; key it --match TEXT")
    return None


def mark_line(queue, ln, tag):
    """Rewrite the first unmarked line equal to `ln` as `#<tag> <ln>`. The
    queue is re-read at write time, so a line another writer appended since
    the run began is kept, and replaced through a temp file in the same
    directory by os.replace, so a reader never sees a half-written queue."""
    return replace_line(queue, ln, f"#{tag} {ln}")


def replace_line(queue, old, new):
    """Replace the first line equal to `old` by `new` (the queue re-read now)."""
    q = Path(queue)
    lines = q.read_text().split("\n")
    for i, x in enumerate(lines):
        if x == old:
            lines[i] = new
            break
    else:
        return False
    fd, tmp = tempfile.mkstemp(dir=q.parent, prefix=q.name + ".")
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(lines))
    os.replace(tmp, q)
    return True


def run_queue(a, python=None):
    env = dict(os.environ)
    env["HPO_ROSTER_LANE"] = "queue-runner"  # roster_edit.LANE_ENV: structural ops need it
    shims = Path(a.edit_checkout, "tools/audit/seat/shims")
    if shims.is_dir():
        env["PATH"] = f"{shims}:{env['PATH']}"
    editor = resolve_editor(a)
    py = python or "seat-python3"

    def sh(*c):
        return subprocess.run(c, capture_output=True, text=True, env=env, cwd=a.edit_checkout)

    def rep(s):
        with open(a.report, "a") as f:
            f.write(s + "\n")
        if a.alive:
            Path(a.alive).touch()

    for flag, d in (("--lint-clone", a.lint_clone), ("--edit-checkout", a.edit_checkout)):
        if not Path(d).is_dir():
            # The clone is the caller's to provision; nothing is re-cloned. Refused
            # by name before any op, with a report line so a reader of the report's
            # last line cannot take the previous run's line as this run's result.
            msg = f"roster: {flag} {d} is not a directory; no op attempted, provision it"
            print(msg, file=sys.stderr)
            rep(msg)
            return 2
    sh("git", "fetch", "-q", "origin")  # fetch only: the edit checkout is never moved
    mark = getattr(a, "mark", False)
    allq = str(a.first) == "all"
    if allq and not mark:
        print("roster: `all` needs --mark (a cursor-less run must mark what it applied)",
              file=sys.stderr)
        return 2
    qlines = Path(a.queue).read_text().split("\n")
    lines = qlines if allq else qlines[int(a.first) - 1:int(a.last)]
    if getattr(a, "batch", False):
        return _run_batch(a, sh, rep, py, editor, lines, mark)
    for ln in lines:
        p = parse_line(ln)
        if not p:
            continue
        op, g, arg, extra = p
        why = replay_unsafe(op, extra)
        if why:
            rep(f"roster: {op} {g} refused rc=2 {why}")
            if mark:
                mark_line(a.queue, ln, "refused")
            continue
        try:
            ok = _run_op(a, sh, rep, py, editor, op, g, arg, extra)
        except Exception as e:  # noqa: BLE001 - every op attempted writes one line
            rep(f"roster: {op} {g} FAILED {type(e).__name__}: {e}"[:400].replace("\n", " "))
            return 1
        if mark:
            mark_line(a.queue, ln, "done" if ok else "refused")
    return 0


def _run_batch(a, sh, rep, py, editor, lines, mark):
    """`run --batch`: every applicable line through roster_edit's own parser and
    checks, ONE lint and ONE push (0.36 s a line against 1-3 min). A refused
    op is rolled back and skipped. Any batch-level failure (a lint refusal, a
    gate refusal of the joint text, a lost race) falls back to the single-op
    path for every line, so a bad line never strands the others."""
    items = []
    for ln in lines:
        p = parse_line(ln)
        why = p and replay_unsafe(p[0], p[3])
        if why:
            rep(f"roster: {p[0]} {p[1]} refused rc=2 {why}")
            if mark:
                mark_line(a.queue, ln, "refused")
        elif p:
            items.append((ln, p))
    if not items:
        return 0
    common = ["--checkout", a.edit_checkout, "--worktree", a.worktree,
              "--lint-cwd", a.lint_clone]
    if a.branch:
        common += ["--branch", a.branch]
    try:
        re_ = load_editor(editor)
        edits, good = [], []
        for ln, (op, g, arg, extra) in items:
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):  # argparse's usage noise
                    args, value, rest = re_.parse_op(
                        [op, g] + ([arg] if arg else []) + extra + common)
                edits.append(re_.make_edit(args, value, rest))
                good.append((ln, (op, g, arg, extra)))
            except (SystemExit, re_.Refuse) as e:
                # one line the parser refuses: name it, batch the rest (P417)
                why = (err.getvalue().strip().splitlines() or [str(e)])[-1]
                rep(f"roster: {op} {g} refused rc=2 {why[:300]}")
                if mark:
                    mark_line(a.queue, ln, "refused")
        items = good
        if not items:
            return 0
        edit, results = re_.batch_edit(edits)
        _git("fetch", "-q", "origin", cwd=a.lint_clone)
        _git("checkout", "-q", "--detach", "origin/main", cwd=a.lint_clone)
        re_.fetch_origin(a.edit_checkout)
        ref, branch = re_.roster_target(a.edit_checkout, None, a.branch, None)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = re_.write_roster(a.edit_checkout, ref, branch, a.worktree, None,
                                  f"roster_edit batch of {len(items)} ({re_.SELF})",
                                  True, a.lint_clone, "batch", edit)
        m = re.search(r"pushed \S+ at ([0-9a-f]+)", buf.getvalue())
        if rc != 0 or not (m or not any(r is None for r in results)):
            raise RuntimeError(f"batch rc={rc}")
    except (SystemExit, Exception) as e:  # noqa: BLE001 - say what, then fall back
        rep(f"roster: batch failed {type(e).__name__}: {str(e)[:300]}".replace("\n", " "))
        rc, m, results = 1, None, None
    if results is None:
        rep("roster: batch fell back to the single-op path")
        b = argparse.Namespace(**{**vars(a), "batch": False})
        return run_queue(b, python=py)
    for (ln, (op, g, arg, extra)), why in zip(items, results):
        if why is None:
            rep(f"roster: {op} {g} pushed {(m.group(1)[:9] if m else 'no-change')}")
        else:
            rep(f"roster: {op} {g} refused rc=2 {why[:300]}")
        if mark:
            mark_line(a.queue, ln, "done" if why is None else "refused")
    return 0


def refresh_lint(a):
    """Detach --lint-clone at the SHA roster_edit's lint gate will compare it with: the edit checkout's
    origin/main after a fetch. Returns "" or why not. The checks of the old pair (fetch, detach, both
    unchecked) failed silently for four attempts in a row and the gate then refused as the stale-worktree trap."""
    f = _git("fetch", "-q", "origin", "main", cwd=a.edit_checkout)
    sha = _git("rev-parse", "origin/main", cwd=a.edit_checkout).stdout.strip()
    if not sha:
        return f"edit checkout has no origin/main ({f.stderr.strip()[-120:]})"
    if not Path(a.lint_clone).is_dir():
        return f"{a.lint_clone} is not a directory, wanted {sha[:12]}"
    c = _git("checkout", "-q", "--detach", sha, cwd=a.lint_clone)
    if c.returncode != 0:  # the object is not in the clone's store yet: fetch it, then retry once
        _git("fetch", "-q", "origin", "main", cwd=a.lint_clone)
        c = _git("checkout", "-q", "--detach", sha, cwd=a.lint_clone)
    head = _git("rev-parse", "HEAD", cwd=a.lint_clone).stdout.strip()
    if c.returncode != 0 or head != sha:
        return f"{a.lint_clone} at {head[:12]}, wanted {sha[:12]}: {c.stderr.strip()[-120:]}"
    return ""


def refusal_tail(out):
    """What a refused op reports: the last three lines, or, for a lint-gate
    refusal, the ERROR lines under its banner -- the TOTAL line alone never
    named the citation (P435)."""
    lines = out.strip().split("\n")
    for i, ln in enumerate(lines):
        if "LINT GATE REFUSED" in ln:
            return " | ".join(lines[i + 1:i + 6])[:700]
    return " | ".join(lines[-3:])[:400]


def _run_op(a, sh, rep, py, editor, op, g, arg, extra):
    """One op: exactly one report line, or an exception for the caller to report."""
    cmd = [py, editor, op, g] + ([arg] if arg else []) + extra + [
        "--checkout", a.edit_checkout, "--worktree", a.worktree,
        "--lint-cwd", a.lint_clone, "--push"]
    if a.branch:
        cmd += ["--branch", a.branch]
    for attempt in (1, 2, 3, 4):
        err = refresh_lint(a)
        if err:
            rep(f"roster: {op} {g} refused rc=2 lint clone not refreshed: {err}"[:400])
            return False
        r = sh(*cmd)
        out = r.stdout + r.stderr
        m = re.search(r"pushed handoff\S* at ([0-9a-f]+)", out)
        if r.returncode == 0 and m:
            rb = ""
            if op == "append-carry" and arg.startswith("@"):
                try:
                    rb = " | readback: " + readback(m.group(1), g, arg[1:], cwd=a.worktree)[0]
                except Exception as e:  # noqa: BLE001 - reported, not hidden
                    rb = f" | readback: FAILED {str(e)[-200:]}"
            if op == "append-carry" and arg and not arg.startswith("@"):
                try:
                    hit = readback_text(m.group(1), g, arg, cwd=a.worktree)
                    rb = " | readback: " + ("LANDED" if hit else "FAILED not-landed")
                except Exception as e:  # noqa: BLE001
                    rb = f" | readback: FAILED {str(e)[-200:]}"
            rep(f"roster: {op} {g} pushed {m.group(1)[:9]}{rb}")
            return "FAILED" not in rb
        if attempt < 4 and (MOVED in out or ("failed to push" in out and "lint gate: TOTAL: 0" in out)):
            sh("git", "worktree", "remove", "--force", a.worktree)
            continue
        rep(f"roster: {op} {g} refused rc={r.returncode} " + refusal_tail(out))
        # A refusal leaves the edit as a local commit in the worktree; the next op would meet it as
        # "HEAD is on no origin ref" and be refused for this op's fault (172 such lines in one drain log).
        sh("git", "-C", a.edit_checkout, "worktree", "remove", "--force", a.worktree)
        return False


HELD = "#held "
BATCH_FILE_RE = re.compile(r"dev/programme/[A-Za-z0-9_./-]+\.md")


def heal_clone(a):
    """Provision a missing --lint-clone as a detached worktree of the edit
    checkout at origin/main: the `loop` self-heal. `run` still refuses a missing
    clone by name (#3020). The edit checkout's branches and files are untouched."""
    if Path(a.lint_clone).is_dir():
        return False
    r = _git("worktree", "add", "-q", "--detach", a.lint_clone, "origin/main",
             cwd=a.edit_checkout)
    if r.returncode:
        raise RuntimeError(f"lint clone self-heal failed: {r.stderr.strip()[-200:]}")
    return True


def loop_queue(a, once=False, sleep=None, python=None):
    """`loop --every N`: heal the lint clone, apply every unmarked line with
    marking, wait N seconds, repeat. The same runner and line grammar as `run`."""
    import time
    sleep = sleep or time.sleep
    while True:
        heal_clone(a)
        run_queue(argparse.Namespace(**{**vars(a), "first": "all", "last": None,
                                        "mark": True}), python=python)
        if once:
            return 0
        sleep(a.every)


def release_held(queue, checkout):
    """`#held append-carry` lines whose batch file (a dev/programme/... .md path
    in the line) exists on origin/main lose the `#held ` prefix and run next
    pass. Returns (released, still_held) line lists."""
    _git("fetch", "-q", "origin", "main", cwd=checkout)
    released, held = [], []
    for ln in Path(queue).read_text().split("\n"):
        if not ln.startswith(HELD + "append-carry"):
            continue
        files = BATCH_FILE_RE.findall(ln)
        if files and all(_git("cat-file", "-e", f"origin/main:{f}", cwd=checkout).returncode == 0
                         for f in files):
            if replace_line(queue, ln, ln[len(HELD):]):
                released.append(ln)
        else:
            held.append(ln)
    return released, held


def unwired(roster, open_issues):
    """Open issue numbers no roster group lists (carry_audit's ISSUE-UNLISTED)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import carry_audit
    return [x for x in carry_audit.roster_report(roster, {}, set(open_issues))
            if x.startswith("ISSUE-UNLISTED")]


def roster_at(ref, cwd, rel=ROSTER_REL):
    """The roster JSON at `ref`, read with `git show` only (read-only; carry 8)."""
    s = _git("show", f"{ref}:{rel}", cwd=cwd)
    if s.returncode:
        raise RuntimeError(f"no {rel} at {ref}: {s.stderr.strip()[-120:]}")
    return json.loads(s.stdout)


def _groups(roster):
    return {g["group"]: g for g in roster.get("groups", [])
            if isinstance(g, dict) and "group" in g}


def _short(v, n=70):
    t = json.dumps(v, sort_keys=True) if not isinstance(v, str) else v
    return t if len(t) <= n else t[:n - 1] + "~"


def show_roster(roster, group=None, stage=None):
    """Lines for `show`: one line per group (`GROUP stage pr=N after=K carries=N`,
    optionally only one `resume.stage`), or every field of one group, its carry
    entries numbered and the brief cut to 100 characters. None when `group`
    names no group."""
    gs = _groups(roster)
    if group is not None:
        g = gs.get(group)
        if g is None:
            return None
        out = [f"{group}"]
        for k, v in g.items():
            if k == "resume" and isinstance(v, dict):
                out += [f"  resume.{rk}: {_short(rv, 100)}" for rk, rv in v.items()]
            elif k == "carry":
                out.append(f"  carry: {len(v)} entries")
                out += [f"    [{i}] {_short(c, 100)}" for i, c in enumerate(v)]
            elif k == "brief":
                out.append(f"  brief: {len(v)} chars: {_short(v, 100)}")
            else:
                out.append(f"  {k}: {_short(v, 100)}")
        return out
    out = []
    for name, g in gs.items():
        r = g.get("resume") or {}
        if stage and r.get("stage") != stage:
            continue
        out.append(f"{name} {r.get('stage')} pr={r.get('pr')} after={len(g.get('after') or [])} "
                   f"carries={len(g.get('carry') or [])}")
    return out


def diff_rosters(a, b):
    """Lines describing what changed from roster `a` to `b`: `+ G` an added
    group, `- G` a removed one, `~ G field: old -> new` a changed field
    (`resume.<key>` for the resume dict), `~ G carry +<text>` / `-<text>` per
    carry entry added or removed, `~ G brief` with the two lengths. Empty when
    the rosters hold the same groups, field for field."""
    ga, gb = _groups(a), _groups(b)
    out = [f"- {g}" for g in ga if g not in gb] + [f"+ {g}" for g in gb if g not in ga]
    for g in ga:
        if g not in gb:
            continue
        x, y = ga[g], gb[g]
        flat = lambda d: {**{k: v for k, v in d.items() if k != "resume"},  # noqa: E731
                          **{f"resume.{k}": v for k, v in (d.get("resume") or {}).items()}}
        fx, fy = flat(x), flat(y)
        for k in dict.fromkeys([*fx, *fy]):
            if fx.get(k) == fy.get(k):
                continue
            if k == "carry":
                ca, cb = fx.get(k) or [], fy.get(k) or []
                out += [f"~ {g} carry -{_short(c, 90)}" for c in ca if c not in cb]
                out += [f"~ {g} carry +{_short(c, 90)}" for c in cb if c not in ca]
            elif k == "brief":
                out.append(f"~ {g} brief {len(fx.get(k) or '')} -> {len(fy.get(k) or '')} chars")
            else:
                out.append(f"~ {g} {k}: {_short(fx.get(k))} -> {_short(fy.get(k))}")
    return out


def _raises(f):
    try:
        f()
    except Exception:  # noqa: BLE001
        return True
    return False


def _self_test():
    fails = []
    n = [0]

    def ck(name, ok, got=""):
        n[0] += 1
        if not ok:
            fails.append(name)
            print("FAIL", name, f"(got: {got})" if got != "" else "")

    ck("parse: numbered", parse_line("7 set-stage G done") == ("set-stage", "G", "done", []))
    ck("parse: blank/comment", parse_line("") is None and parse_line("# x") is None)
    ck("parse: quoted arg", parse_line("append-carry G 'a b'") == ("append-carry", "G", "a b", []))
    ck("parse: drop-carry --match keeps the flag and its text",
       parse_line("drop-carry G --match 'x.py:1-2'") == ("drop-carry", "G", "", ["--match", "x.py:1-2"]))
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        repo = t / "repo"
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
        from throwaway_git import throwaway_git_init
        env = throwaway_git_init(repo, "-q")
        (repo / ROSTER_REL).parent.mkdir(parents=True)
        (repo / ROSTER_REL).write_text(json.dumps({"groups": [{"group": "G", "carry": ["one", "two\nlines"]}]}))
        _git("add", "-A", cwd=repo, env=env)
        _git("commit", "-qm", "r", cwd=repo, env=env)
        sha = _git("rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
        (t / "c.txt").write_text("two\nlines\n")
        (t / "d.txt").write_text("three")
        line, ok = readback(sha, "G", t / "c.txt", cwd=repo)
        ck("readback: exact match found at index 1", ok and "exact-match-index=[1]" in line and "n_carry=2" in line)
        line, ok = readback(sha, "G", t / "d.txt", cwd=repo)
        ck("readback: absent text is no match (null control)", not ok and "exact-match-index=[]" in line)
        try:
            readback(sha, "NOPE", t / "c.txt", cwd=repo)
            ck("readback: unknown group raises", False)
        except RuntimeError:
            ck("readback: unknown group raises", True)

        # run_queue against a stub editor and a stub origin
        _git("update-ref", "refs/remotes/origin/main", sha, cwd=repo, env=env)  # refresh_lint compares with it
        _git("-c", "user.name=x", "-c", "user.email=x@x", "commit", "-q", "--allow-empty", "-m", "ahead",
             cwd=repo, env=env)
        ahead = _git("rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
        _git("update-ref", "refs/remotes/origin/main", ahead, cwd=repo, env=env)
        ck("refresh_lint: detaches the lint clone at the edit checkout's origin/main, with no network",
           refresh_lint(argparse.Namespace(edit_checkout=str(repo), lint_clone=str(repo))) == ""
           and _git("rev-parse", "HEAD", cwd=repo, env=env).stdout.strip() == ahead)
        ck("refresh_lint: names the clone that did not move (null control: a missing clone is refused)",
           "wanted" in refresh_lint(argparse.Namespace(edit_checkout=str(repo), lint_clone=str(t / "nowhere"))))
        stub = t / "stub.py"
        (t / "calls").write_text("")
        (t / "mode").write_text("moved1")
        stub.write_text(
            "import sys,pathlib\n"
            f"c=pathlib.Path({str(t / 'calls')!r}); m=pathlib.Path({str(t / 'mode')!r})\n"
            "c.write_text(c.read_text()+' '.join(sys.argv[2:5])+'\\n')\n"
            f"pathlib.Path({str(t / 'argv')!r}).open('a').write(' '.join(sys.argv[1:])+'\\n')\n"
            f"import os; pathlib.Path({str(t / 'lane')!r}).write_text(os.environ.get('HPO_ROSTER_LANE', 'absent'))\n"
            "if 'BAD' in sys.argv: print('REFUSED: unknown group'); sys.exit(2)\n"
            "if m.read_text()=='moved1':\n"
            "    m.write_text('ok'); print('--lint-cwd x is not origin/main'); sys.exit(3)\n"
            f"print('pushed handoff/x at {sha}')\n")
        q = t / "q.txt"
        q.write_text(f"1 append-carry G @{t / 'c.txt'}\n# skip\n\n2 set-stage BAD done\n3 set-stage G done\n4 drop-carry G --match 'x.py:1-2'\n")
        a = argparse.Namespace(first=1, last=6, queue=str(q), report=str(t / "rep"),
                               edit_checkout=str(repo), worktree=str(repo), lint_clone=str(repo),
                               alive=str(t / "alive"), branch=None, editor=str(stub))
        run_queue(a, python=sys.executable)
        rep = (t / "rep").read_text().strip().split("\n")
        calls = (t / "calls").read_text().strip().split("\n")
        ck("run: one report line per op", len(rep) == 4)
        ck("run: moved main retried (first op called twice)", calls[0] == calls[1])
        ck("run: pushed + readback on append-carry", rep[0].startswith("roster: append-carry G pushed " + sha[:9])
           and "exact-match-index=[1]" in rep[0])
        ck("run: refusal reported, not retried", "refused rc=2" in rep[1] and sum("BAD" in c for c in calls) == 1)
        ck("run: later op still runs", rep[2] == f"roster: set-stage G pushed {sha[:9]}")
        dl = [x for x in (t / "argv").read_text().split("\n") if x.startswith("drop-carry")]
        ck("run: drop-carry --match reaches the editor as a flag, not a value",
           len(dl) == 1 and dl[0].startswith("drop-carry G --match x.py:1-2 --checkout ")
           and rep[3] == f"roster: drop-carry G pushed {sha[:9]}")
        ck("run: the child editor carries the roster lane marker (roster_edit.LANE_ENV)",
           (t / "lane").read_text() == "queue-runner")
        ck("run: alive touched", (t / "alive").exists())
        # A clone that exists but cannot reach the SHA (empty store, no origin): the HEAD check refuses
        # it, and _run_op reports that refusal without running the editor.
        lc0 = t / "lc_empty"
        throwaway_git_init(lc0, "-q")
        why = refresh_lint(argparse.Namespace(edit_checkout=str(repo), lint_clone=str(lc0)))
        ck("refresh_lint: a clone whose checkout fails is refused, not passed", f"wanted {ahead[:12]}" in why, why)
        before, r0 = (t / "calls").read_text(), []
        _run_op(argparse.Namespace(**{**vars(a), "lint_clone": str(lc0)}),
                lambda *c, **k: subprocess.run(c, capture_output=True, text=True),
                r0.append, sys.executable, str(stub), "set-stage", "G", "", [])
        ck("run: an unrefreshed lint clone is reported by name and the editor never runs",
           len(r0) == 1 and "refused rc=2 lint clone not refreshed" in r0[0]
           and (t / "calls").read_text() == before, r0)
        # P315 / #3020: a failing op writes its own FAILED line and stops the run;
        # a missing lint clone is refused by name, rc 2, before any op.
        (t / "rep2").write_text("")
        q2 = t / "q2.txt"
        q2.write_text("1 set-stage G done\n2 set-stage H done\n3 set-stage I done\n")
        a2 = argparse.Namespace(**{**vars(a), "queue": str(q2), "report": str(t / "rep2"),
                                   "first": 1, "last": 3, "worktree": str(t / "boom")})
        (t / "mode").write_text("ok")
        ck("run: clean op writes its normal line (null control)",
           run_queue(a2, python=sys.executable) == 0
           and (t / "rep2").read_text().strip().split("\n")
           == [f"roster: set-stage {g_} pushed {sha[:9]}" for g_ in "GHI"])
        (t / "rep2").write_text("")
        real_sh = subprocess.run

        def boom(c, *x, **k):
            if "H" in c:
                raise FileNotFoundError("clone vanished")
            return real_sh(c, *x, **k)
        subprocess.run = boom
        try:
            rc2 = run_queue(a2, python=sys.executable)
        finally:
            subprocess.run = real_sh
        r2 = (t / "rep2").read_text().strip().split("\n")
        ck("run: an exception writes a FAILED line for that op and stops, rc 1",
           rc2 == 1 and r2[0] == f"roster: set-stage G pushed {sha[:9]}"
           and r2[1] == "roster: set-stage H FAILED FileNotFoundError: clone vanished"
           and len(r2) == 2)
        # carry 13(2): a pass cut short (the drain's timeout) keeps every mark already written
        q2.write_text("1 set-stage G done\n2 set-stage H done\n3 set-stage I done\n")
        (t / "rep2").write_text("")
        subprocess.run = boom
        try:
            run_queue(argparse.Namespace(**{**vars(a2), "mark": True}), python=sys.executable)
        finally:
            subprocess.run = real_sh
        ck("run --mark: a pass that dies mid-queue keeps the marks already written, later lines stay unmarked",
           q2.read_text().split("\n")[:3] == ["#done 1 set-stage G done", "2 set-stage H done",
                                              "3 set-stage I done"], q2.read_text())
        (t / "rep3").write_text("roster: set-stage G byte-identical\n")
        a3 = argparse.Namespace(**{**vars(a2), "report": str(t / "rep3"),
                                   "lint_clone": str(t / "no-such-clone")})
        rc3 = run_queue(a3, python=sys.executable)
        r3 = (t / "rep3").read_text().strip().split("\n")
        ck("run: a missing --lint-clone is refused by name, rc 2, before any op",
           rc3 == 2 and "--lint-clone" in r3[-1] and "no-such-clone" in r3[-1]
           and len(r3) == 2 and not (t / "no-such-clone").exists())

    # --- R10-ROSTER-WRITE-SWEEP: comment grammar, flags, marking, batch, loop
    ck("parse: a trailing ` # comment` is dropped (carry 11)",
       parse_line("set-stage G done # #2955 merged aced2589") == ("set-stage", "G", "done", []))
    ck("parse: a # inside a word is kept (null)",
       parse_line("append-carry G @/p/b#1.txt") == ("append-carry", "G", "@/p/b#1.txt", []))
    ck("parse: an unquoted drop-carry --match keeps its #P (null)",
       parse_line("drop-carry G --match s6-batch8.md#P70")
       == ("drop-carry", "G", "", ["--match", "s6-batch8.md#P70"]))
    ck("parse: a quoted 'a # b' stays one argument (null)",
       parse_line("append-carry G 'a # b' # note") == ("append-carry", "G", "a # b", []))
    ck("parse: set-stage keeps --at-sha a flag, not part of the value (carry 14)",
       parse_line("set-stage G done --at-sha abc1234")
       == ("set-stage", "G", "done", ["--at-sha", "abc1234"]))
    with tempfile.TemporaryDirectory() as t2:
        t = Path(t2)
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
        from throwaway_git import throwaway_git_init, throwaway_git_clone
        repo = t / "repo"
        env = throwaway_git_init(repo, "-q", "-b", "main")
        (repo / "dev/programme/triage").mkdir(parents=True)
        (repo / "dev/programme/triage/b.md").write_text("batch\n")
        (repo / ROSTER_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / ROSTER_REL).write_text(json.dumps({"groups": [{"group": "G", "carry": ["hello carry"], "issues": [5]}]}))
        _git("add", "-A", cwd=repo, env=env)
        _git("commit", "-qm", "r", cwd=repo, env=env)
        sha = _git("rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
        clone = t / "clone"
        throwaway_git_clone(repo, clone, "-q")
        stub = t / "stub2.py"
        stub.write_text(
            "import sys,pathlib\n"
            f"q=pathlib.Path({str(t / 'q.txt')!r}); app=pathlib.Path({str(t / 'append')!r})\n"
            "if app.exists():\n"
            "    app.unlink(); q.write_text(q.read_text()+'\\n9 set-stage LATE done')\n"
            "if 'BAD' in sys.argv: print('REFUSED: no group'); sys.exit(2)\n"
            f"print('pushed handoff/x at {sha}')\n")
        base = argparse.Namespace(first=1, last=4, queue=str(t / "q.txt"), report=str(t / "rep"),
                                  edit_checkout=str(clone), worktree=str(clone),
                                  lint_clone=str(clone), alive=None, branch=None,
                                  editor=str(stub))
        body = "1 set-stage G done # why\n2 set-stage BAD done\n# a note\n3 set-stage H done"

        def fresh(text=body):
            (t / "q.txt").write_text(text)
            (t / "rep").write_text("")
        fresh()
        before = (t / "q.txt").read_bytes()
        run_queue(base, python=sys.executable)
        ck("run: without --mark the queue is byte-identical (null)",
           (t / "q.txt").read_bytes() == before)
        fresh()
        (t / "append").write_text("")
        run_queue(argparse.Namespace(**{**vars(base), "mark": True}), python=sys.executable)
        got = (t / "q.txt").read_text().split("\n")
        ck("run --mark: a pushed op is `#done`, a refused op `#refused`",
           got[0] == "#done 1 set-stage G done # why" and got[1] == "#refused 2 set-stage BAD done"
           and got[3] == "#done 3 set-stage H done", got)
        ck("run --mark: a line appended after the run's first read survives",
           got[-1] == "9 set-stage LATE done" and got[2] == "# a note", got)
        fresh()
        rc = run_queue(argparse.Namespace(**{**vars(base), "first": "all", "last": None}),
                       python=sys.executable)
        ck("run all without --mark is refused, nothing applied (rc 2)",
           rc == 2 and (t / "q.txt").read_bytes() == body.encode())
        fresh()
        run_queue(argparse.Namespace(**{**vars(base), "first": "all", "last": None, "mark": True}),
                  python=sys.executable)
        ck("run all --mark applies every unmarked op line, no cursor",
           (t / "q.txt").read_text().split("\n")[3].startswith("#done 3 set-stage H"))
        run_queue(argparse.Namespace(**{**vars(base), "first": "all", "last": None, "mark": True}),
                  python=sys.executable)
        ck("a marked line is never applied again", (t / "rep").read_text().count("\n") == 3)
        # write_roster's real refusal shape: banner, the new ERROR lines, then
        # the lint's own last three lines (an ERROR, its CARRY line, a blank),
        # TOTAL, and the commit-is-local line -- the old three-line tail held
        # only the blank, TOTAL and that last line, never an ERROR.
        gate = ("lint gate: running\nroster_edit: LINT GATE REFUSED the push\n"
                "  ERROR   [G-1] cite: a.py:9 moved\n"
                "  CARRY: G-1 re-pin a.py:9\n\n"
                "TOTAL: 1 error(s) across 1 file(s)\n"
                "the commit is local at 0123456789ab in /w (detached); nothing pushed\n")
        ck("refusal_tail: the fixture's old three-line tail names no ERROR (precondition)",
           "ERROR" not in " | ".join(gate.strip().split("\n")[-3:]))
        ck("refusal_tail: a lint-gate refusal reports the ERROR line, not only TOTAL",
           "[G-1] cite: a.py:9" in refusal_tail(gate) and "TOTAL: 1" in refusal_tail(gate),
           refusal_tail(gate))
        stub3 = t / "stub3.py"
        stub3.write_text("import sys\nsys.stderr.write(" + repr(gate) + ")\nsys.exit(3)\n")
        fresh("1 set-stage G done\n")
        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 1,
                                        "editor": str(stub3)}), python=sys.executable)
        rr = (t / "rep").read_text().strip()
        ck("run: a lint-gate refusal's report line names the refused citation",
           rr.startswith("roster: set-stage G refused rc=3 ") and "[G-1] cite: a.py:9" in rr, rr)
        ck("refusal_tail: other output is its last three lines (null)",
           refusal_tail("a\nb\nc\nd") == "b | c | d")
        # inline append-carry readback (LANDED test, first 60 chars)
        ck("readback_text: the carry's first 60 chars are found",
           readback_text(sha, "G", "hello carry", cwd=clone))
        ck("readback_text: an absent carry is not landed (null)",
           not readback_text(sha, "G", "never written", cwd=clone))
        # --batch: a line the batch cannot parse falls back to the single path
        fresh("1 bogus-op G done\n")
        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 1, "batch": True}),
                  python=sys.executable)
        rr = (t / "rep").read_text().split("\n")
        ck("run --batch: a batch-level failure falls back to the single-op path",
           rr[0].startswith("roster: batch failed RuntimeError") and "no batch_edit" in rr[0]
           and rr[1] == "roster: batch fell back to the single-op path"
           and rr[2] == f"roster: bogus-op G pushed {sha[:9]}", rr)
        # ONE editor for both paths (resolve_editor), named by what each path ran
        seen = []
        real_load = load_editor

        def spy(path):
            seen.append(path)
            return real_load(path)
        globals()["load_editor"] = spy
        fresh("1 set-stage G done\n")
        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 1, "batch": True}),
                  python=sys.executable)
        globals()["load_editor"] = real_load
        ck("run --batch loads the passed --editor, and its fallback runs that same file",
           seen == [str(stub)] and f"roster: set-stage G pushed {sha[:9]}"
           in (t / "rep").read_text().split("\n"), seen)
        ck("resolve_editor: no --editor is the roster_edit.py beside this script, never the edit checkout",
           resolve_editor(argparse.Namespace(editor=None, edit_checkout=str(clone)))
           == str(Path(__file__).resolve().parent / "roster_edit.py")
           and not (clone / "tools/audit/seat/roster_edit.py").exists())
        marker = t / "ran"
        ghost = t / "ghost.py"
        ghost.write_text(f"open({str(marker)!r}, 'w').write('x')\n")
        ck("load_editor: a file that is no roster_edit is refused unexecuted",
           _raises(lambda: load_editor(str(ghost))) and not marker.exists())
        fresh("1 set-stage G done\n")
        real_ed = str(Path(__file__).resolve().parent / "roster_edit.py")
        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 1, "batch": True,
                                        "editor": real_ed}), python=sys.executable)
        ck("run --batch: a batch whose every op is refused reports each refused, no fallback",
           (t / "rep").read_text().startswith("roster: set-stage G refused rc=2"))
        # P417: one malformed line is named and refused; the rest still batch
        fresh("1 bogus-op G done\n2 set-stage G done\n")
        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 2, "batch": True,
                                        "editor": real_ed}), python=sys.executable)
        rr = (t / "rep").read_text().split("\n")
        ck("run --batch: a malformed line is named and refused, the rest still batch (no fallback)",
           rr[0].startswith("roster: bogus-op G refused rc=2")
           and rr[1].startswith("roster: set-stage G refused rc=2")
           and "fell back" not in "\n".join(rr), rr)
        # ... and under --mark the malformed line is marked, so no later pass re-runs it
        fresh("1 bogus-op G done\n2 set-stage G done\n")
        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 2, "batch": True,
                                        "mark": True, "editor": real_ed}), python=sys.executable)
        got = (t / "q.txt").read_text().split("\n")
        ck("run --batch --mark: a malformed line is marked `#refused`",
           got[0] == "#refused 1 bogus-op G done", got)
        # R10-RCA-ROSTER-DRAIN-REPLAY: a carry op keyed by index is refused unrun on both paths
        fresh("1 drop-carry G 1\n2 mark-carry G 0 dismissed x\n3 drop-carry G --match one\n")
        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 3, "mark": True}),
                  python=sys.executable)
        rr, got = (t / "rep").read_text().split("\n"), (t / "q.txt").read_text().split("\n")
        ck("run: drop-carry and mark-carry by index are refused and marked, never pushed",
           rr[0].startswith("roster: drop-carry G refused rc=2 drop-carry by index")
           and rr[1].startswith("roster: mark-carry G refused rc=2 mark-carry by index")
           and got[:2] == ["#refused 1 drop-carry G 1", "#refused 2 mark-carry G 0 dismissed x"], rr)
        ck("run: drop-carry --match still reaches the editor (null control)",
           rr[2] == f"roster: drop-carry G pushed {sha[:9]}", rr)
        fresh("1 drop-carry G 0\n")
        run_queue(argparse.Namespace(**{**vars(base), "first": 1, "last": 1, "batch": True,
                                        "mark": True, "editor": real_ed}), python=sys.executable)
        rr = (t / "rep").read_text().split("\n")
        ck("run --batch: drop-carry by index is refused before the batch, and marked",
           rr[0].startswith("roster: drop-carry G refused rc=2 drop-carry by index")
           and (t / "q.txt").read_text().startswith("#refused 1 drop-carry G 0"), rr)
        # release-held: a held carry waits for its batch file on origin/main
        (t / "q.txt").write_text(
            "#held append-carry G 'x dev/programme/triage/b.md#P1'\n"
            "#held append-carry G 'y dev/programme/triage/absent.md#P2'\n")
        rel, held = release_held(str(t / "q.txt"), str(clone))
        q2 = (t / "q.txt").read_text().split("\n")
        ck("release-held: a held line whose batch file exists is released",
           len(rel) == 1 and q2[0].startswith("append-carry G"), q2)
        ck("release-held: a held line whose batch file is absent stays held (null)",
           len(held) == 1 and q2[1].startswith("#held "), q2)
        # unwired sweep
        ros = {"groups": [{"group": "G", "issues": [5], "resume": {"stage": "not-started"}}]}
        ck("unwired: an open issue no group lists is reported",
           unwired(ros, [5, 9]) == ["ISSUE-UNLISTED #9"])
        ck("unwired: every open issue listed reports nothing (null)", unwired(ros, [5]) == [])
        # show / diff (carry 8): read-only, over `git show` of two refs
        base_r = json.loads(_git("show", f"{sha}:{ROSTER_REL}", cwd=repo).stdout)
        new_r = json.loads(json.dumps(base_r))
        new_r["groups"][0]["carry"].append("second carry")
        new_r["groups"][0]["resume"] = {"stage": "done", "pr": 7}
        new_r["groups"].append({"group": "H", "carry": [], "resume": {"stage": "not-started"}})
        (repo / ROSTER_REL).write_text(json.dumps(new_r))
        _git("commit", "-qam", "r2", cwd=repo, env=env)
        sha2 = _git("rev-parse", "HEAD", cwd=repo, env=env).stdout.strip()
        before = (repo / ROSTER_REL).read_bytes()
        d = diff_rosters(roster_at(sha, repo), roster_at(sha2, repo))
        ck("diff: an added group, a changed resume field and an added carry are each one line",
           d[0] == "+ H" and "~ G carry +second carry" in d
           and "~ G resume.stage: null -> done" in d, d)
        ck("diff: a removed group is `- G`",
           diff_rosters(roster_at(sha2, repo), roster_at(sha, repo))[0] == "- H"
           and "~ G carry -second carry" in diff_rosters(roster_at(sha2, repo), roster_at(sha, repo)))
        ck("diff: the same ref twice is empty (null)",
           diff_rosters(roster_at(sha2, repo), roster_at(sha2, repo)) == [])
        ck("diff: a carry entry replaced by another is one - and one +, not unchanged (count alone is blind)",
           sorted(x[:11] for x in diff_rosters({"groups": [{"group": "G", "carry": ["a"]}]},
                                               {"groups": [{"group": "G", "carry": ["b"]}]}))
           == ["~ G carry +", "~ G carry -"])
        ck("show: one line per group, the stage and pr in it",
           show_roster(roster_at(sha2, repo))
           == ["G done pr=7 after=0 carries=2", "H not-started pr=None after=0 carries=0"])
        ck("show --stage keeps only that stage (null: no filter lists both)",
           show_roster(roster_at(sha2, repo), stage="done") == ["G done pr=7 after=0 carries=2"])
        one = show_roster(roster_at(sha2, repo), "G")
        ck("show G: every field, carries numbered, the brief absent here",
           one[0] == "G" and "  resume.pr: 7" in one and "    [1] second carry" in one
           and "  issues: [5]" in one, one)
        ck("show: an unknown group is None, which the CLI makes rc 2",
           show_roster(roster_at(sha2, repo), "NOPE") is None
           and main(["show", "--edit-checkout", str(repo), "--ref", sha2, "NOPE"]) == 2)
        ck("diff CLI: rc 1 when the refs differ, 0 when not, 2 for a missing ref",
           main(["diff", "--edit-checkout", str(repo), sha, sha2]) == 1
           and main(["diff", "--edit-checkout", str(repo), sha2, sha2]) == 0
           and main(["diff", "--edit-checkout", str(repo), sha, "nosuchref"]) == 2)
        ck("show and diff write nothing: the working tree and the index are as they were",
           (repo / ROSTER_REL).read_bytes() == before
           and _git("status", "--porcelain", cwd=repo, env=env).stdout == "")
        # loop: heals a missing lint clone, then applies and marks
        fresh("1 set-stage G done\n")
        lc = t / "healed"
        run_a = argparse.Namespace(**{**vars(base), "lint_clone": str(lc), "every": 1})
        loop_queue(run_a, once=True, python=sys.executable)
        ck("loop: a missing lint clone is re-provisioned from origin, then the pass runs",
           (lc / ".git").exists() and (t / "q.txt").read_text().startswith("#done 1 set-stage G done"))
    print(f"roster_queue self-test: {n[0]} checks, {len(fails)} failed")
    return 1 if fails else 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["--self-test"]:
        return _self_test()
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("first", help="1-based first line, or `all` (needs --mark)")
    r.add_argument("last", nargs="?", type=int)
    r.add_argument("--mark", action="store_true",
                   help="rewrite each applied line as `#done <line>` (pushed) "
                        "or `#refused <line>`")
    r.add_argument("--batch", action="store_true",
                   help="all lines in one worktree: one lint, one push")
    lp = sub.add_parser("loop")
    for sp in (r, lp):
        for k in ("queue", "report", "edit-checkout", "worktree", "lint-clone"):
            sp.add_argument("--" + k, required=True)
        sp.add_argument("--alive")
        sp.add_argument("--branch")
        sp.add_argument("--editor")
    lp.add_argument("--every", type=int, default=300)
    lp.add_argument("--batch", action="store_true")
    rh = sub.add_parser("release-held")
    rh.add_argument("--queue", required=True)
    rh.add_argument("--edit-checkout", required=True)
    uw = sub.add_parser("unwired")
    uw.add_argument("--edit-checkout", required=True)
    uw.add_argument("--ref", default="origin/main")
    uw.add_argument("--open-issues", required=True,
                    help="JSON list of open issue numbers (or gh issue objects)")
    sh_ = sub.add_parser("show")
    sh_.add_argument("--edit-checkout", required=True)
    sh_.add_argument("--ref", default="origin/main")
    sh_.add_argument("--stage", help="only groups whose resume.stage is this")
    sh_.add_argument("group", nargs="?")
    df = sub.add_parser("diff")
    df.add_argument("--edit-checkout", required=True)
    df.add_argument("ref_a")
    df.add_argument("ref_b")
    b = sub.add_parser("readback")
    b.add_argument("sha")
    b.add_argument("group")
    b.add_argument("file")
    a = p.parse_args(argv)
    if a.cmd == "run":
        if a.first != "all" and (a.last is None or not a.first.isdigit()):
            p.error("run needs FIRST LAST, or `all` with --mark")
        return run_queue(a)
    if a.cmd == "loop":
        return loop_queue(a)
    if a.cmd == "release-held":
        released, held = release_held(a.queue, a.edit_checkout)
        for ln in released:
            print("RELEASED", ln[len(HELD):][:100])
        for ln in held:
            print("held    ", ln[len(HELD):][:100])
        return 0
    if a.cmd == "unwired":
        s_ = _git("show", f"{a.ref}:{ROSTER_REL}", cwd=a.edit_checkout)
        if s_.returncode:
            print(f"no {ROSTER_REL} at {a.ref}", file=sys.stderr)
            return 2
        nums = [x if isinstance(x, int) else x.get("number")
                for x in json.loads(Path(a.open_issues).read_text())]
        out = unwired(json.loads(s_.stdout), [n for n in nums if isinstance(n, int)])
        print("\n".join(out) or "no unwired open issue")
        return 1 if out else 0
    if a.cmd in ("show", "diff"):
        try:
            if a.cmd == "show":
                lines = show_roster(roster_at(a.ref, a.edit_checkout), a.group, a.stage)
                if lines is None:
                    print(f"no group {a.group} in the roster at {a.ref}", file=sys.stderr)
                    return 2
            else:
                lines = diff_rosters(roster_at(a.ref_a, a.edit_checkout),
                                     roster_at(a.ref_b, a.edit_checkout))
        except RuntimeError as e:
            print(e, file=sys.stderr)
            return 2
        print("\n".join(lines) or ("no difference" if a.cmd == "diff" else "no group"))
        return 1 if (a.cmd == "diff" and lines) else 0
    line, ok = readback(a.sha, a.group, a.file)
    print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
