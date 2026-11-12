#!/usr/bin/env python3
"""The tracked mutant driver: apply one textual edit, run a command, restore.

    python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd '<argv>' [--copy-tree | --in-place] [--fork-cap N]
    python3 tools/audit/seat/mutant_run.py --diff <base>...HEAD --cmd '<argv>' [--max-mutants N] [--report-only] [--list]
    python3 -I tools/audit/seat/mutant_run.py --self-test

SPEC MODE. `mutants.json` is a list of {name, file, old, new}. An automatic
NULL mutant with no edit runs first and must be reported SURVIVED: a command
that fails on the unedited tree kills every mutant for the wrong reason, so
`KILLED NULL` ends the run at rc 3 before any mutant is applied. One
`KILLED name` or `SURVIVED name` line per mutant (a non-zero command exit
kills). Refusals, rc 2, before anything runs: a spec entry that is malformed,
a name used twice or named NULL, an `old` that does not occur exactly once in
its file, and a target file that differs from HEAD.

WHERE IT RUNS. By default in a `git archive` copy of the tree, so a kill cannot
leave production mutated; `--copy-tree` names that default. The #363
`recorded_at` check fails in a copy on every mutant, baseline included, so a
command that reaches it needs `--in-place`: the mutant is written into the
working tree under `dev/audit/harnesses/mutant_guard.py`, which refuses a
target that differs from HEAD and restores it under SIGTERM, SIGINT and exit.
Under either mode a signal kills the running command's process group first.

FORK CAP (R10-MUTANT-RUN-FORKCAP). The command runs in its own session; its family (session, process group, every process
carrying the run's MUTANT_RUN_TOKEN, and every descendant of the driver, which is a child
subreaper (PR_SET_CHILD_SUBREAPER) while the command runs, so a descendant that setsid'd,
setpgid'd, cleared its environment or was orphaned still counts) is polled every 0.5 s and killed whole, also at exit; a family holding more than `--fork-cap` processes (default 256, 0
turns the cap off) is SIGKILLed whole and reported `FORKCAP <name>` (diff mode:
`FORKCAP file:line OPERATOR  <mutated line>`), never KILLED: a mutant that makes
a self-test re-enter itself (a chain 700 deep once exhausted a host's `ulimit -u`)
was stopped by the cap, not by a test pinning it, so it is unresolved. A diff
run with a FORKCAP line exits 1 (rc 0 under `--report-only`); `survivor_list.py`
reads only SURVIVED lines. A FORKCAP on the NULL run is rc 3, as KILLED NULL is.

DIFF MODE (R10-MUTANT-RUN-DRIVER, card 4). `--diff base...HEAD` reads the
ADDED lines of the Python files the three-dot diff touches (not under tests/ or
dev/, not inside a multi-line string) and mutates each with six operators:

  GUARD_OFF   `if cond:` / `elif cond:` becomes `if False:`
  RETURN_DEL  `return ...` becomes `pass`
  CMP_BOUND   the first of < <= > >= moves one step (< to <=, >= to >)
  CALL_DEL    a bare `f(...)` statement becomes `pass` (print and _LOGGER calls
              are left alone: they pin no behaviour)
  CONST_SWAP  the first number moves (n to n+1, 0.0 to 1.0) or, with none,
              the first True/False flips
  STMT_DEL    from the head file's ast, each simple statement (assignment,
              expression, delete, raise, assert, return) an added line falls in
              is replaced whole, however many lines it spans, by `pass` at its
              indent; the report line is `SURVIVED <file>:<first line> STMT_DEL  pass`.
              Left alone: a statement sharing its lines with other code, a
              docstring or bare constant, print and _LOGGER calls, imports and
              compound headers, and any statement CALL_DEL or RETURN_DEL already
              deletes to the same text

A mutant that does not compile is skipped. The command runs once unedited (rc 3
`BASELINE FAILS` if it fails: nothing is then readable) and once per mutant;
one `SURVIVED file:line OPERATOR  <mutated line>` line is printed per survivor
and nothing for a kill. rc 0 when nothing survived (an empty diff included),
1 on survivors unless `--report-only`. A survivor is answered in the PR body;
an equivalent one still needs a survivor_triage record. `--list` prints the
mutants without running. The command is the group's named self-test or
`python3 tools/audit/seat/features_block.py "<marker>"`.

NO PROCFS. Where /proc is absent (macOS, the BSDs) the process table comes from
`ps -axo pid=,stat=,ppid=,pgid=` with the session from os.getsid; the token leg
reads nothing, and with no subreaper there either, a descendant that left the
session is not followed.

The procfs root is `MUTANT_RUN_PROCFS` (default /proc): a path that does not
exist makes the host one without procfs, in this process and every driver it
starts, so a Linux host runs the macOS path.

`--self-test` builds throwaway repositories and runs every arm above. It reads
the process table three ways on every host: with no procfs root, through a faked
root it writes from the live table, and through the host's own /proc. A case the
host cannot run (its own /proc where there is none, a child subreaper where
prctl is absent) prints one `skip` line naming why and is counted on the
`skipped` line above the summary.
"""
from __future__ import annotations

import argparse
import ast
import ctypes
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REFUSE_RC, SURVIVE_RC, BROKEN_RC = 2, 1, 3
TIMEOUT_RC, FORKCAP_RC = -1, -2  # run_cmd's two non-exit outcomes: a kill, and a stop that proves nothing
FORKCAP = [256]  # processes one command's session may hold (--fork-cap); 0 turns the cap off
FORKCAP_POLL_S = 0.5
PROCFS = [Path(os.environ.get("MUTANT_RUN_PROCFS", "/proc"))]  # the procfs root; one that does not exist is a host without procfs
OPERATORS = ("GUARD_OFF", "RETURN_DEL", "CMP_BOUND", "CALL_DEL", "CONST_SWAP", "STMT_DEL")
_SIMPLE = (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Expr, ast.Delete, ast.Raise, ast.Assert, ast.Return)
SKIP_PREFIXES = ("tests/", "dev/")
_STR = re.compile(r"""("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')""")
_CMP = re.compile(r"(?<![<>=!\-])(<=|>=|<|>)(?![<>=])")
_NUM = re.compile(r"(?<![\w.])(\d+\.\d+|\d+)(?![\w.])")
_BOOL = re.compile(r"\b(True|False)\b")
_CALL = re.compile(r"^(?:await\s+)?[A-Za-z_][\w.]*\(.*\)$")
_BOUND = {"<": "<=", "<=": "<", ">": ">=", ">=": ">"}

_child: list = []  # the running command, for the signal handler


class Refusal(Exception):
    pass


def git(root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=text)


# --- running one command ----------------------------------------------------
PR_SET_CHILD_SUBREAPER, PR_GET_CHILD_SUBREAPER = 36, 37  # linux/prctl.h


def _subreaper(on: int) -> int:
    """Set this process's child-subreaper flag (PR_SET_CHILD_SUBREAPER: an orphaned descendant is
    reparented to this process, not to init, so it stays in the ppid-closure whatever it does to
    its session or environment); return the previous flag, -1 where prctl is unavailable."""
    try:
        libc, prev = ctypes.CDLL(None, use_errno=True), ctypes.c_int(0)
        if libc.prctl(PR_GET_CHILD_SUBREAPER, ctypes.byref(prev), 0, 0, 0) or libc.prctl(PR_SET_CHILD_SUBREAPER, on, 0, 0, 0):
            return -1
        return prev.value
    except (OSError, AttributeError):
        return -1


def _ptable() -> list[tuple[int, str, int, int, int | None]]:
    """(pid, state, ppid, pgrp, session) of every process. From the procfs root where it exists; on
    a host without procfs (macOS, the BSDs) from `ps`, the session from os.getsid (None where refused)."""
    rows = []
    try:
        names = os.listdir(PROCFS[0])
    except FileNotFoundError:
        ps = subprocess.Popen(["ps", "-axo", "pid=,stat=,ppid=,pgid="], stdout=subprocess.PIPE, text=True)
        listing = ps.communicate()[0]
        if ps.returncode:
            raise OSError(f"ps exited {ps.returncode}: no process table, so no fork cap")
        for line in listing.splitlines():
            try:
                pid, state, ppid, pgrp = line.split()
                if int(pid) == ps.pid:
                    continue  # the listing's own process, a child of this driver: never the command's
                try:
                    session = os.getsid(int(pid))
                except OSError:
                    session = None  # exited since the listing, or another session's to hide
                rows.append((int(pid), state[:1], int(ppid), int(pgrp), session))
            except ValueError:
                continue
        return rows
    for d in filter(str.isdigit, names):
        try:
            stat = (PROCFS[0] / d / "stat").read_text()
            state, ppid, pgrp, session = stat[stat.rindex(")") + 2:].split()[:4]
            rows.append((int(d), state, int(ppid), int(pgrp), int(session)))
        except (OSError, ValueError):
            continue  # exited between the listing and the read
    return rows


def _carries(pid: int, mark: bytes) -> bool:
    """Whether `pid`'s environment holds `mark`; False where it cannot be read (not ours, exited,
    or no procfs: on such a host only the session, group and ppid legs find a member)."""
    try:
        env = (PROCFS[0] / str(pid) / "environ").read_bytes()
    except OSError:
        env = b""
    return mark in env.split(b"\0")


def family(sid: int, token: str, skip: frozenset = frozenset(), root: int = 0) -> list[int]:
    """Live processes of the command `sid` started: its session, its process group, any that still
    carries the run's token in its environment, and, given `root` (this driver, a subreaper while
    the command runs), every descendant of `root` but those of its children in `skip` (children it
    had before the command). The ppid leg is the one a descendant cannot leave: setsid, setpgid,
    a cleared environment and an exited parent all keep it under `root`. Zombies are not counted."""
    me, mark, kids, out = os.getpid(), ("MUTANT_RUN_TOKEN=" + token).encode(), {}, set()
    for pid, state, ppid, pgrp, session in _ptable():
        if pid == me or state == "Z":
            continue
        kids.setdefault(ppid, []).append(pid)
        if sid in (pgrp, session) or _carries(pid, mark):
            out.add(pid)
    todo, seen = ([c for c in kids.get(root, []) if c not in skip] if root else []), set()
    while todo:
        pid = todo.pop()
        if pid not in seen:
            seen.add(pid)
            todo.extend(kids.get(pid, []))
    return sorted(out | seen)


def _reap(skip: frozenset, keep: int) -> None:
    """Collect the exit status of every orphan reparented to this subreaper (children not in
    `skip` and not the command `keep`, which Popen waits for), so dead ones leave no zombie."""
    me = os.getpid()
    for pid, _state, ppid, _pgrp, _session in _ptable():
        if ppid == me and pid != keep and pid not in skip:
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                continue


def _kill_family(sid: int, token: str, skip: frozenset = frozenset(), root: int = 0) -> None:
    """SIGKILL every member until none is left (a member may fork while the list is taken)."""
    for _ in range(20):
        pids = family(sid, token, skip, root)
        if root:
            _reap(skip, sid)
        if not pids:
            return
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        time.sleep(0.05)


def run_cmd(argv: list[str], cwd: Path, timeout: float) -> int:
    """Exit status of the command; TIMEOUT_RC (-1) is a kill (the mutant hangs); FORKCAP_RC (-2)
    is the session holding more than FORKCAP[0] processes (a re-entering self-test), which proves
    nothing about the test pinning the mutant and is never a kill."""
    token = f"{os.getpid()}-{time.monotonic_ns()}"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", MUTANT_RUN_TOKEN=token)
    prev = _subreaper(1)
    root = os.getpid() if prev >= 0 else 0
    skip = frozenset(family(0, token, root=root)) if root else frozenset()  # children (and theirs) from before
    p = subprocess.Popen(argv, cwd=str(cwd), env=env, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _child.append((p, token, skip, root))
    fam = lambda: family(p.pid, token, skip, root)  # noqa: E731
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                rc = p.wait(timeout=max(0.0, min(FORKCAP_POLL_S, deadline - time.monotonic())))
                if FORKCAP[0] and len(fam()) > FORKCAP[0]:
                    rc = FORKCAP_RC
                return rc
            except subprocess.TimeoutExpired:
                pass
            if root:
                _reap(skip, p.pid)
            if time.monotonic() >= deadline:
                _kill_family(p.pid, token, skip, root)
                p.wait()
                return TIMEOUT_RC
            if FORKCAP[0] and len(fam()) > FORKCAP[0]:
                _kill_family(p.pid, token, skip, root)
                p.wait()
                return FORKCAP_RC
    finally:
        _kill_family(p.pid, token, skip, root)  # a daemon outliving its command is the command's, not the next mutant's
        _child.clear()
        if prev >= 0:
            _subreaper(prev)


class Workspace:
    """Where mutants are written: an archive copy of a tree, or the working tree under the guard."""

    def __init__(self, root: Path, files: list[str], in_place: bool, rev: str = "HEAD"):
        self.root, self.in_place = root, in_place
        self.copy: Path | None = None
        self.rels = sorted(set(files))
        if in_place:
            sys.dont_write_bytecode = True  # no __pycache__ beside the tracked guard
            sys.path.insert(0, str(root / "dev" / "audit" / "harnesses"))
            import mutant_guard  # noqa: PLC0415 -- the shared restore-on-kill guard
            self.finish = mutant_guard.arm(self.rels, root=root)
            self.dir = root
        else:
            dirty = [r for r in self.rels if git(root, "diff", "--quiet", "HEAD", "--", r).returncode]
            if dirty and rev == "HEAD":
                raise Refusal("target differs from HEAD (a copy would test HEAD, not the edit): " + ", ".join(dirty))
            self.copy = Path(tempfile.mkdtemp(prefix="mutant_run-"))
            arc = subprocess.Popen(["git", "-C", str(root), "archive", rev], stdout=subprocess.PIPE)
            tar = subprocess.run(["tar", "-x", "-C", str(self.copy)], stdin=arc.stdout, capture_output=True)
            arc.stdout.close()
            if arc.wait() or tar.returncode:
                self.close()
                raise Refusal("git archive of " + rev + " failed")
            self.dir = self.copy
        prev = {sg: signal.getsignal(sg) for sg in (signal.SIGTERM, signal.SIGINT)}

        def on_signal(signum, frame):
            for p, token, skip, root in _child:
                _kill_family(p.pid, token, skip, root)
            self.close()
            h = prev[signum]
            if callable(h):
                h(signum, frame)  # the guard restores in place and exits 128+signal
            os._exit(128 + signum)

        for sg in prev:
            signal.signal(sg, on_signal)

    def path(self, rel: str) -> Path:
        return self.dir / rel

    def close(self) -> None:
        if self.copy is not None:
            shutil.rmtree(self.copy, ignore_errors=True)
            self.copy = None

    def apply(self, rel: str, text: str, run: list[str], timeout: float) -> int:
        """Write `text` over `rel`, run, put the original bytes back."""
        target = self.path(rel)
        orig = target.read_bytes()
        try:
            target.write_text(text, encoding="utf-8")
            return run_cmd(run, self.dir, timeout)
        finally:
            target.write_bytes(orig)


# --- spec mode -------------------------------------------------------------
def load_spec(path: str, root: Path) -> list[dict]:
    try:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Refusal(f"spec unreadable: {e}")
    if not isinstance(spec, list):
        raise Refusal("spec is not a list")
    seen = {"NULL"}
    for i, m in enumerate(spec):
        if not isinstance(m, dict) or set(m) != {"name", "file", "old", "new"} \
                or not all(isinstance(v, str) for v in m.values()):
            raise Refusal(f"spec entry {i} is not {{name, file, old, new}} strings")
        if m["name"] in seen:
            raise Refusal(f"mutant name {m['name']!r} is used twice or is NULL")
        seen.add(m["name"])
        if not m["old"] or m["old"] == m["new"]:
            raise Refusal(f"mutant {m['name']}: old is empty or equals new")
        f = root / m["file"]
        if not f.is_file():
            raise Refusal(f"mutant {m['name']}: {m['file']} is not a file")
        n = f.read_text(encoding="utf-8").count(m["old"])
        if n != 1:
            raise Refusal(f"mutant {m['name']}: old text occurs {n} times in {m['file']}, not exactly once")
    return spec


def run_spec(spec: list[dict], argv: list[str], ws: Workspace, timeout: float) -> int:
    rc = run_cmd(argv, ws.dir, timeout)
    if rc == FORKCAP_RC:
        print("FORKCAP NULL", flush=True)
        print("mutant_run: the unedited tree forked past --fork-cap, nothing is readable", file=sys.stderr)
        return BROKEN_RC
    if rc != 0:
        print("KILLED NULL", flush=True)
        print("mutant_run: the null mutant was killed, the command fails on the unedited tree", file=sys.stderr)
        return BROKEN_RC
    print("SURVIVED NULL", flush=True)
    for m in spec:
        text = ws.path(m["file"]).read_text(encoding="utf-8")
        rc = ws.apply(m["file"], text.replace(m["old"], m["new"], 1), argv, timeout)
        if rc == FORKCAP_RC:
            print("FORKCAP " + m["name"], flush=True)
            continue
        print(("SURVIVED " if rc == 0 else "KILLED ") + m["name"], flush=True)
    return 0


# --- diff mode -------------------------------------------------------------
def added_lines(root: Path, rng: str, only: tuple = ()) -> dict[str, list[int]]:
    r = git(root, "diff", "-U0", "--no-color", "--diff-filter=AM", rng, "--", "*.py")
    if r.returncode:
        raise Refusal("git diff " + rng + " failed: " + r.stderr.strip())
    out: dict[str, list[int]] = {}
    cur, ln = None, 0
    for line in r.stdout.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
            out.setdefault(cur, [])
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            ln = int(m.group(1))
        elif cur and line.startswith("+") and not line.startswith("+++"):
            out[cur].append(ln)
            ln += 1
    return {f: v for f, v in out.items() if v and not f.startswith(SKIP_PREFIXES) and (not only or f.startswith(only))}


def string_lines(src: str) -> set[int]:
    """Lines inside a multi-line string literal (docstrings, f-string bodies)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    lines: set[int] = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Constant, ast.JoinedStr)) and getattr(n, "end_lineno", None) \
                and (isinstance(n, ast.JoinedStr) or isinstance(n.value, str)) and n.end_lineno > n.lineno:
            lines.update(range(n.lineno, n.end_lineno + 1))
    return lines


def _mask(s: str) -> str:
    return _STR.sub(lambda m: "x" * len(m.group(0)), s)


def mutate_line(line: str):
    """Yield (OPERATOR, mutated line) for one source line."""
    body = line.lstrip()
    if not body or body.startswith(("#", "import ", "from ", "def ", "class ", "@")):
        return
    ind = line[: len(line) - len(body)]
    masked = _mask(line)
    code = masked.split("#", 1)[0].rstrip()
    mc = code.lstrip()
    if re.match(r"(if|elif)\s", mc) and code.endswith(":"):
        yield "GUARD_OFF", f"{ind}{mc.split(None, 1)[0]} False:"
    if re.match(r"return\b", mc) and mc.count("(") == mc.count(")"):
        yield "RETURN_DEL", f"{ind}pass"
    m = _CMP.search(code)
    if m:
        yield "CMP_BOUND", line[: m.start()] + _BOUND[m.group(1)] + line[m.end():]
    if _CALL.match(mc) and not mc.startswith(("print(", "_LOGGER.")) and mc.count("(") == mc.count(")"):
        yield "CALL_DEL", f"{ind}pass"
    m = _NUM.search(code)
    if m:
        tok = m.group(1)
        new = (str(int(tok) + 1) if "." not in tok else ("1.0" if float(tok) == 0 else str(float(tok) * 2)))
        yield "CONST_SWAP", line[: m.start()] + new + line[m.end():]
    else:
        m = _BOOL.search(code)
        if m:
            yield "CONST_SWAP", line[: m.start()] + ("False" if m.group(1) == "True" else "True") + line[m.end():]


def diff_mutants(root: Path, rng: str, rev_root: Path, only: tuple = ()) -> list[tuple[str, int, str, str, str]]:
    """(file, line, operator, mutated file text, mutated line) for every compiling mutant."""
    found = []
    for rel, nums in sorted(added_lines(root, rng, only).items()):
        src = (rev_root / rel).read_text(encoding="utf-8")
        lines = src.splitlines(keepends=True)
        skip = string_lines(src)
        for n in nums:
            if n in skip or n > len(lines):
                continue
            raw = lines[n - 1]
            eol = raw[len(raw.rstrip("\r\n")):]
            for op, new in mutate_line(raw.rstrip("\r\n")):
                text = "".join(lines[: n - 1]) + new + eol + "".join(lines[n:])
                if text == src:
                    continue
                try:
                    compile(text, rel, "exec")
                except (SyntaxError, ValueError):
                    continue
                found.append((rel, n, op, text, new.strip()))
        found.extend(_stmt_del(rel, src, lines, nums, {m[3] for m in found if m[0] == rel}))
    return found


def _stmt_del(rel: str, src: str, lines: list[str], nums: list[int], have: set[str]) -> list[tuple]:
    """STMT_DEL: each simple statement an added line falls in, whole, becomes `pass` at its indent.

    Skipped: a statement sharing its lines with other code (`a = 1; b = 2`, `if x: y = 1`),
    a docstring or bare constant, a print or _LOGGER call, and any text another operator already
    produced (a single-line CALL_DEL or RETURN_DEL), so a statement is one mutant, not two.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []
    for node in sorted((x for x in ast.walk(tree) if isinstance(x, _SIMPLE)), key=lambda x: x.lineno):
        lo, hi = node.lineno, node.end_lineno
        if not any(lo <= n <= hi for n in nums):
            continue
        if isinstance(node, ast.Expr):
            v = node.value
            if isinstance(v, ast.Constant):
                continue
            if isinstance(v, ast.Call) and ast.unparse(v.func).split(".")[0] in ("print", "_LOGGER"):
                continue
        first, last = lines[lo - 1].rstrip("\r\n"), lines[hi - 1].rstrip("\r\n")
        head = first.encode()[: node.col_offset].decode()
        tail = last.encode()[node.end_col_offset:].decode().strip()
        if head.strip() or (tail and not tail.startswith("#")):
            continue
        eol = lines[lo - 1][len(first):]
        text = "".join(lines[: lo - 1]) + head + "pass" + eol + "".join(lines[hi:])
        if text == src or text in have:
            continue
        try:
            compile(text, rel, "exec")
        except (SyntaxError, ValueError):
            continue
        have.add(text)
        out.append((rel, lo, "STMT_DEL", text, "pass"))
    return out


def run_diff(rng: str, argv: list[str], root: Path, in_place: bool, timeout: float,
             limit: int, report_only: bool, list_only: bool, only: tuple = ()) -> int:
    right = rng.split("...")[-1] if "..." in rng else "HEAD"
    rev = right or "HEAD"
    if "..." not in rng:
        raise Refusal("--diff wants base...HEAD (three-dot), got " + rng)
    if in_place and rev != "HEAD":
        raise Refusal("--in-place mutates the working tree, whose diff end must be HEAD")
    files = sorted(added_lines(root, rng, only))
    if not files:
        return 0
    if in_place:
        ws = Workspace(root, files, True)
        rev_root = root
    else:
        ws = Workspace(root, files, False, rev=rev)
        rev_root = ws.dir
    try:
        mutants = diff_mutants(root, rng, rev_root, only)
        if limit:
            mutants = mutants[:limit]
        if list_only:
            for rel, n, op, _t, new in mutants:
                print(f"MUTANT {rel}:{n} {op}  {new}")
            return 0
        if not mutants:
            return 0
        if run_cmd(argv, ws.dir, timeout) != 0:
            print("BASELINE FAILS: the command fails on the unedited tree; no mutant was run")
            return BROKEN_RC
        survivors = 0
        for rel, n, op, text, new in mutants:
            rc = ws.apply(rel, text, argv, timeout)
            if rc == FORKCAP_RC:  # unresolved, not killed: listed apart from SURVIVED so survivor_list.py skips it
                survivors += 1
                print(f"FORKCAP {rel}:{n} {op}  {new}", flush=True)
            elif rc == 0:
                survivors += 1
                print(f"SURVIVED {rel}:{n} {op}  {new}", flush=True)
        return 0 if (report_only or not survivors) else SURVIVE_RC
    finally:
        ws.close() if not in_place else ws.finish()


# --- entry point -----------------------------------------------------------
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spec")
    ap.add_argument("--diff")
    ap.add_argument("--cmd")
    ap.add_argument("--copy-tree", action="store_true", help="the default: run in a git-archive copy")
    ap.add_argument("--in-place", action="store_true", help="mutate the working tree under mutant_guard")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--timeout", type=float, default=600.0)
    ap.add_argument("--fork-cap", type=int, default=FORKCAP[0],
                    help="kill the command's session past this many processes and report FORKCAP (0: no cap)")
    ap.add_argument("--max-mutants", type=int, default=0)
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--path", action="append", default=[], help="diff mode: only files under this prefix (repeatable)")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    FORKCAP[0] = a.fork_cap
    try:
        if a.copy_tree and a.in_place:
            raise Refusal("--copy-tree and --in-place exclude each other")
        if bool(a.spec) == bool(a.diff):
            raise Refusal("give exactly one of --spec and --diff")
        if not a.cmd and not a.list:
            raise Refusal("--cmd '<argv>' is required")
        cmd = shlex.split(a.cmd or "true")
        if a.spec:
            spec = load_spec(a.spec, root)
            ws = Workspace(root, [m["file"] for m in spec], a.in_place)
            try:
                return run_spec(spec, cmd, ws, a.timeout)
            finally:
                ws.close() if not a.in_place else ws.finish()
        return run_diff(a.diff, cmd, root, a.in_place, a.timeout, a.max_mutants, a.report_only, a.list, tuple(a.path))
    except Refusal as e:
        print("mutant_run: refusing: " + str(e), file=sys.stderr)
        return REFUSE_RC


# --- self-test ---------------------------------------------------------------
LIB = '''def clamp(x, lo, hi):
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x
'''
LIB2 = LIB + '''

def norm(x):
    if x < 0:
        return 0
    scale = 2
    note(x)
    return x * scale


def note(x):
    pass


def label():
    """Say it.

    if x < 1:
        return 7
    """
    msg = "a < b"  # c > d
    on = True
    return msg, on
'''
PINNED = ("from lib import clamp\n"
          "assert clamp(-1, 0, 5) == 0 and clamp(9, 0, 5) == 5 and clamp(3, 0, 5) == 3\n"
          "assert clamp(0, 0, 5) == 0 and clamp(5, 0, 5) == 5\n")
NORM_PINNED = ("from lib import norm\nimport lib\nseen = []\nlib.note = seen.append\n"
               "assert norm(-1) == 0 and norm(0) == 0 and norm(2) == 4 and seen == [0, 2]\n"
               "assert lib.label() == ('a < b', True)\n")
STM = '''import os


def f(x):
    """Doc."""
    total = x + 1
    kept = x * 2
    wide = (x +
            1 +
            2)
    print(os.sep)
    return kept
'''
SHR = 'def g(x):\n    a = 1; b = 2\n    if x: y = 1\n    c = 3  # note\n    return a\n'
STM_PINNED = "from stm import f\nassert f(3) == 6\n"
LOOSE = "from lib import clamp\nassert clamp(3, 0, 5) == 3\n"


def _can_subreap() -> bool:
    """Whether this host has a child subreaper (Linux prctl); the flag is restored as found."""
    prev = _subreaper(1)
    return prev >= 0 and _subreaper(prev) >= 0


def _no_session(sid: int) -> bool:
    """True once no process has session id `sid` (polled for up to 5 s)."""
    for _ in range(50):
        if not family(sid, ""):
            return True
        time.sleep(0.1)
    return False


def _zombie(pid: int) -> None:
    """Return once `pid` is a zombie, i.e. exited and not yet reaped (polled for up to 5 s)."""
    for _ in range(50):
        if any(row[0] == pid and row[1] == "Z" for row in _ptable()):
            return
        time.sleep(0.1)


def _gone(pid: str) -> bool:
    """True once the process `pid` no longer exists (polled for up to 5 s)."""
    for _ in range(50):
        try:
            os.kill(int(pid), 0)
        except (ProcessLookupError, ValueError):
            return True
        time.sleep(0.1)
    return False


class _Procfs:
    """The procfs root is `root` for the life of the block: the platform, injected."""

    def __init__(self, root: Path):
        self.root = root

    def __enter__(self):
        self.saved, PROCFS[0] = PROCFS[0], self.root

    def __exit__(self, *exc):
        PROCFS[0] = self.saved


def _fake_procfs(root: Path, environ: dict[int, bytes]) -> Path:
    """Write the live process table under `root` as procfs lays it out (`<pid>/stat`, and
    `<pid>/environ` for the pids in `environ`), so the procfs readers run on a host without one.
    Every comm holds `) `, which a stat line is split after the LAST of."""
    for pid, state, ppid, pgrp, session in _ptable():
        (root / str(pid)).mkdir(parents=True)
        (root / str(pid) / "stat").write_text(f"{pid} (a) b) {state} {ppid} {pgrp} {session or 0} 0 -1\n")
        if pid in environ:
            (root / str(pid) / "environ").write_bytes(environ[pid])
    (root / "self").mkdir()  # procfs holds names that are no pid
    return root


def _procless_checks(check, skip, tmp: Path, host: Path = Path("/proc")) -> None:
    """family() and _reap() read the process table alike with no procfs, through a faked procfs
    root, and through the host's own (`host`), a leg skipped, counted, where the host has none."""
    (tmp / "ps").write_text("#!/bin/sh\nexit 7\n")
    (tmp / "ps").chmod(0o755)
    tok = f"st-{os.getpid()}"
    check("procfs: a Linux host has one, so its leg below is not skipped there",
          (Path("/proc", "self", "stat").is_file()) == sys.platform.startswith("linux"))
    for label, root in (("with no procfs", None), ("through a faked procfs root", tmp / "fake-proc"),
                        ("through the host's procfs (null control)", host)):
        procfs = root is not None
        if root == host and not (host / "self" / "stat").is_file():
            skip(f"no-procfs: {label}, all five arms", f"this host has no {host}; the faked root above drives the same readers")
            continue
        lone = subprocess.Popen(["sleep", "30"], start_new_session=True)
        kid = subprocess.Popen(["sleep", "30"], env=dict(os.environ, MUTANT_RUN_TOKEN=tok + "0"))  # a near miss
        marked = subprocess.Popen(["sleep", "30"], start_new_session=True, env=dict(os.environ, MUTANT_RUN_TOKEN=tok))
        dead = subprocess.Popen(["true"], start_new_session=True)  # a zombie session leader: `ps` stat `Zs`, not `Z`
        _zombie(dead.pid)  # exited, still unreaped (os.waitid's WNOWAIT, which macOS lacks)
        try:
            if root == tmp / "fake-proc":
                mark = f"MUTANT_RUN_TOKEN={tok}".encode()
                _fake_procfs(root, {marked.pid: b"A=1\0" + mark + b"\0", kid.pid: mark + b"0\0A=" + mark + b"\0"})
            with _Procfs(root or tmp / "no-proc"):
                try:
                    by_session, by_root = family(lone.pid, ""), family(lone.pid, "", skip=frozenset({marked.pid}), root=os.getpid())
                    by_token = family(lone.pid, tok)
                    _reap(frozenset({kid.pid, marked.pid}), lone.pid)
                    err = ""
                except Exception as e:  # noqa: BLE001 -- the failure is the finding, reported as a FAIL
                    by_session, by_root, by_token, err = [], [], [], f"{type(e).__name__}: {e}"
                path, os.environ["PATH"] = os.environ["PATH"], f"{tmp}{os.pathsep}{os.environ['PATH']}"
                try:
                    broken = repr(family(lone.pid, ""))
                except OSError as e:
                    broken = str(e)
                finally:
                    os.environ["PATH"] = path
            check(f"no-procfs: {label}, family() finds a command by its session" + (f" ({err})" if err else ""),
                  lone.pid in by_session and kid.pid not in by_session)
            check(f"no-procfs: {label}, family() finds the driver's descendants by ppid, zombies excluded",
                  set(by_root) == {kid.pid, lone.pid})  # never `dead`, nor the `ps` that listed the table
            check(f"no-procfs: {label}, a process that left the session is found by its token "
                  + ("(the environ leg), and one carrying a longer token is not" if procfs else "only with procfs (no environ leg without it)"),
                  (marked.pid in by_token) == procfs and kid.pid not in by_token and not err)
            check(f"no-procfs: {label}, _reap() collects a dead child it does not skip",
                  dead.pid not in {row[0] for row in _ptable()} and not err)
            check(f"no-procfs: {label}, a failing `ps` " + ("is never read: the table is procfs" if procfs
                  else "refuses (OSError), never an empty table that turns the cap off"),
                  broken.startswith("ps exited 7") != procfs)
        finally:
            for p in (lone, kid, marked):
                p.kill()
                p.wait()
            dead.returncode = 0  # reaped by _reap above: Popen must not wait again


def _self_test() -> int:
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_init
    fails = checks = skips = 0

    def check(name: str, ok: bool) -> None:
        nonlocal fails, checks
        checks += 1
        fails += not ok
        print(("  ok   " if ok else "  FAIL ") + name)

    def skip(name: str, why: str) -> None:
        nonlocal skips
        skips += 1
        print(f"  skip {name} -- {why}")

    tmp = Path(tempfile.mkdtemp(prefix="mutrun-st-"))
    _procless_checks(check, skip, tmp)
    scratch = tmp / "tmpdir"
    scratch.mkdir()
    try:
        repo = tmp / "repo"
        repo.mkdir()
        env = throwaway_git_init(repo, "-q", "-b", "main")
        g = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, env=env)  # noqa: E731
        for name, body in (("lib.py", LIB), ("check_pinned.py", PINNED), ("check_loose.py", LOOSE),
                           ("check_norm.py", NORM_PINNED)):
            (repo / name).write_text(body)
        (repo / "dev" / "audit" / "harnesses").mkdir(parents=True)
        shutil.copy(ROOT / "dev" / "audit" / "harnesses" / "mutant_guard.py", repo / "dev/audit/harnesses/mutant_guard.py")
        (repo / "custom_components" / "heatpump_optimizer").mkdir(parents=True)
        (repo / "custom_components/heatpump_optimizer/manifest.json").write_text("{}\n")
        g("add", "-A")
        g("commit", "-q", "-m", "base")
        base = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, env=env).stdout.strip()
        senv = dict(env, TMPDIR=str(scratch), PYTHONPATH="")

        def drive(*args, sig=None, watch=None, procfs=None):
            p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--root", str(repo), *args],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=str(repo),
                                 env=dict(senv, MUTANT_RUN_PROCFS=str(procfs)) if procfs else senv)
            if sig:
                for _ in range(150):
                    if watch():
                        break
                    time.sleep(0.1)
                p.send_signal(sig)
            out, err = p.communicate(timeout=120)
            return p.returncode, out, err

        spec = tmp / "spec.json"

        def write_spec(entries):
            spec.write_text(json.dumps(entries))

        bad = {"name": "ret_hi", "file": "lib.py", "old": "return lo", "new": "return hi"}
        write_spec([bad])
        pin = "python3 check_pinned.py"
        rc, out, _ = drive("--spec", str(spec), "--cmd", pin)
        check("spec: the NULL mutant reports SURVIVED and a pinned mutant KILLED",
              rc == 0 and out.splitlines() == ["SURVIVED NULL", "KILLED ret_hi"])
        rc, out, _ = drive("--spec", str(spec), "--cmd", "python3 check_loose.py", "--copy-tree")
        check("spec: a command that does not pin the line reports the mutant SURVIVED",
              rc == 0 and out.splitlines() == ["SURVIVED NULL", "SURVIVED ret_hi"])
        rc, out, _ = drive("--spec", str(spec), "--cmd", 'python3 -c "raise SystemExit(1)"')
        check("spec: a killed NULL is a broken harness, rc 3, and no mutant ran",
              rc == 3 and out.splitlines() == ["KILLED NULL"])
        write_spec([{**bad, "old": "return"}])
        rc, out, err = drive("--spec", str(spec), "--cmd", pin)
        check("spec: an old text occurring twice is refused, rc 2, nothing run", rc == 2 and out == "" and "3 times" in err)
        write_spec([bad, {**bad, "file": "lib.py"}])
        rc, out, err = drive("--spec", str(spec), "--cmd", pin)
        check("spec: a name used twice is refused, rc 2", rc == 2 and out == "")
        write_spec([bad])
        (repo / "lib.py").write_text(LIB + "# dirty\n")
        rc, out, err = drive("--spec", str(spec), "--cmd", pin)
        check("spec: a target that differs from HEAD is refused, rc 2", rc == 2 and out == "" and "lib.py" in err)
        rc, out, err = drive("--spec", str(spec), "--cmd", pin, "--in-place")
        check("spec: --in-place refuses the same dirty target, rc 2", rc == 2 and out == "")
        g("checkout", "--", "lib.py")

        # two mutants: the second is only readable if the first was put back
        write_spec([bad, {"name": "no_edit_equiv", "file": "lib.py", "old": "    return x\n", "new": "    return x  # same\n"}])
        rc, out, _ = drive("--spec", str(spec), "--cmd", pin)
        check("spec: the file is restored between mutants (the second, an equivalent edit, SURVIVES)",
              out.splitlines() == ["SURVIVED NULL", "KILLED ret_hi", "SURVIVED no_edit_equiv"])

        # a kill mid-run
        write_spec([bad])
        flag = tmp / "running.flag"
        slow = f"python3 -c \"import pathlib, time; pathlib.Path('{flag}').write_text('x'); time.sleep(60)\""
        listing = lambda: {p.name for p in scratch.iterdir()}  # noqa: E731
        for mode in ("--copy-tree", "--in-place"):
            flag.unlink(missing_ok=True)
            # NULL runs first and would sleep: make the command fast on the unedited tree
            cmd = ("python3 -c \"import pathlib, sys, time\n"
                   "src = pathlib.Path('lib.py').read_text()\n"
                   "if 'return hi\\n    if x > hi' in src:\n"
                   f"    pathlib.Path('{flag}').write_text(str(__import__('os').getpid())); time.sleep(60)\"")
            rc, out, err = drive("--spec", str(spec), "--cmd", cmd, mode, sig=signal.SIGTERM, watch=flag.exists)
            clean = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", "lib.py"],
                                   capture_output=True, text=True, env=env).stdout == ""
            check(f"SIGTERM mid-mutant ({mode}): rc 143, tree byte-identical, no copy left behind",
                  rc == 143 and clean and (repo / "lib.py").read_text() == LIB and not listing())
            check(f"SIGTERM mid-mutant ({mode}): the running command was killed with the driver", _gone(flag.read_text()))
            flag.unlink(missing_ok=True)

        # a hung mutant is a kill, and its process group goes with it
        pidf = tmp / "hung.pid"
        hang = ("python3 -c \"import pathlib, time\n"
                "if 'return hi\\n    if x > hi' in pathlib.Path('lib.py').read_text():\n"
                f"    pathlib.Path('{pidf}').write_text(str(__import__('os').getpid())); time.sleep(60)\"")
        t0 = time.monotonic()
        rc, out, _ = drive("--spec", str(spec), "--cmd", hang, "--timeout", "2")
        check("spec: a mutant that hangs past --timeout is KILLED, and its command is killed rather than waited out",
              rc == 0 and out.splitlines() == ["SURVIVED NULL", "KILLED ret_hi"] and time.monotonic() - t0 < 30
              and _gone(pidf.read_text()))
        for label, body in (("not a list", "{}"), ("not JSON", "[oops"), ("missing keys", '[{"name": "a"}]'),
                            ("empty old", json.dumps([{**bad, "old": ""}])), ("old equals new", json.dumps([{**bad, "new": "return lo"}])),
                            ("absent file", json.dumps([{**bad, "file": "nope.py"}])),
                            ("old absent", json.dumps([{**bad, "old": "zzz"}])), ("NULL name", json.dumps([{**bad, "name": "NULL"}]))):
            spec.write_text(body)
            rc, out, _ = drive("--spec", str(spec), "--cmd", pin)
            check(f"spec: {label} is refused, rc 2, nothing run", rc == 2 and out == "")
        write_spec([bad])
        for label, args in (("both --spec and --diff", ["--spec", str(spec), "--diff", "a...b", "--cmd", pin]),
                            ("neither", ["--cmd", pin]), ("no --cmd", ["--spec", str(spec)]),
                            ("--copy-tree with --in-place", ["--spec", str(spec), "--cmd", pin, "--copy-tree", "--in-place"]),
                            ("--in-place with a diff end that is not HEAD", ["--diff", f"{base}...{base}", "--cmd", pin, "--in-place"]),
                            ("a two-dot --diff", ["--diff", "HEAD", "--cmd", pin]),
                            ("an unresolvable --diff base", ["--diff", "nobase...HEAD", "--cmd", pin])):
            rc, out, _ = drive(*args)
            check(f"main: {label} is refused, rc 2", rc == 2 and out == "")

        # diff mode
        (repo / "lib.py").write_text(LIB2)
        g("commit", "-q", "-am", "add norm")
        rng = f"{base}...HEAD"
        rc, out, _ = drive("--diff", rng, "--list")
        ops = {l.split()[2] for l in out.splitlines() if l.startswith("MUTANT ")}
        check("diff: the added lines yield all six operators", ops == set(OPERATORS))
        rc, out, _ = drive("--diff", rng, "--list")
        listed = [l for l in out.splitlines() if l.startswith("MUTANT ")]
        src2 = LIB2.splitlines()
        doc = {i + 1 for i, l in enumerate(src2) if l.strip() in ("if x < 1:", "return 7", "Say it.") or l.strip().startswith('"""')}
        msg = next(i + 1 for i, l in enumerate(src2) if l.strip().startswith("msg ="))
        check("diff: no mutant inside a multi-line string, and none from a < or # inside a string literal",
              doc and not any(int(l.split()[1].split(":")[1]) in doc | {msg} for l in listed if l.split()[2] != "STMT_DEL"))
        check("diff: a True constant is flipped", any(l.endswith("on = False") for l in listed))
        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_norm.py")
        check("diff: a self-test that pins the guard, return, bound, call and constant leaves no survivor, rc 0",
              rc == 0 and "SURVIVED" not in out)
        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_loose.py")
        survivors = [l for l in out.splitlines() if l.startswith("SURVIVED ")]
        check("diff: a self-test that does not pin them leaves survivors, rc 1, one line each",
              rc == 1 and len(survivors) >= 5 and {l.split()[2] for l in survivors} == set(OPERATORS))
        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_norm.py", "--in-place")
        clean = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True, env=env).stdout == ""
        check("diff: --in-place over a pinning command leaves no survivor and the tree clean", rc == 0 and out == "" and clean)
        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_loose.py", "--in-place", "--max-mutants", "4")
        check("diff: --max-mutants caps the pass (4 mutants, at most 4 lines)", rc == 1 and 0 < len(out.splitlines()) <= 4)
        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_loose.py", "--report-only")
        check("diff: --report-only prints the survivors and exits 0", rc == 0 and "SURVIVED" in out)
        rc, out, _ = drive("--diff", rng, "--cmd", 'python3 -c "raise SystemExit(1)"')
        check("diff: a command failing on the unedited tree is BASELINE FAILS, rc 3", rc == 3 and "BASELINE FAILS" in out)
        rc, out, _ = drive("--diff", f"HEAD...HEAD", "--cmd", "python3 check_loose.py")
        check("diff: an empty diff prints no survivor and exits 0 (null control)", rc == 0 and out == "")
        status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True, env=env).stdout
        check("diff: the working tree is clean after every run", status == "" and not listing())

        # fork cap: a command that forks a chain without end is stopped and left no process behind
        chain, gate, pidf = tmp / "chain.sh", tmp / "gate.sh", tmp / "gate.pid"
        chain.write_text('n=$1; [ "$n" -le 0 ] && exit 0; sleep 0.02; sh "$0" $((n - 1))\n')
        gate.write_text(f'echo $$ > {pidf}; grep -q "return lo" lib.py && exit 0; sh {chain} "$1"\n')
        write_spec([bad])
        t0 = time.monotonic()
        rc, out, _ = drive("--spec", str(spec), "--cmd", f"sh {gate} 120", "--fork-cap", "32", "--timeout", "60")
        check("forkcap: an endless-style chain past a cap of 32 is FORKCAP, within seconds, never KILLED",
              rc == 0 and out.splitlines() == ["SURVIVED NULL", "FORKCAP ret_hi"] and time.monotonic() - t0 < 20)
        check("forkcap: no process of the capped session is left", _no_session(int(pidf.read_text())))
        capped = ("--spec", str(spec), "--cmd", f"sh {gate} 120", "--fork-cap", "32", "--timeout", "60")
        rc, out, _ = drive(*capped, procfs=tmp / "no-proc")
        check("forkcap: a driver whose MUTANT_RUN_PROCFS names no directory caps the same chain from `ps` (the macOS path, on any host)",
              rc == 0 and out.splitlines() == ["SURVIVED NULL", "FORKCAP ret_hi"])
        (tmp / "empty-proc").mkdir()
        rc, out, _ = drive(*capped, procfs=tmp / "empty-proc")
        check("forkcap: a driver whose MUTANT_RUN_PROCFS names an empty root sees no process, so the chain runs out (the root named is the one read)",
              rc == 0 and out.splitlines() == ["SURVIVED NULL", "SURVIVED ret_hi"])
        rc, out, _ = drive("--spec", str(spec), "--cmd", f"sh {gate} 120", "--fork-cap", "0", "--timeout", "60")
        check("forkcap: with the cap off the same chain runs out unbounded-by-the-driver and SURVIVES (mutation proof)",
              rc == 0 and out.splitlines() == ["SURVIVED NULL", "SURVIVED ret_hi"])
        rc, out, _ = drive("--spec", str(spec), "--cmd", f"sh {gate} 10", "--fork-cap", "32")
        check("forkcap: a bounded 10-process command under the same cap is unaffected (null control)",
              rc == 0 and out.splitlines() == ["SURVIVED NULL", "SURVIVED ret_hi"])

        # fork cap in the other two modes: a null run that re-enters, and a diff-mode mutant that does
        write_spec([bad])
        rc, out, err = drive("--spec", str(spec), "--cmd", f"sh {chain} 120", "--fork-cap", "32", "--timeout", "60")
        check("forkcap: a command that forks past the cap on the unedited tree is FORKCAP NULL, rc 3, no mutant run",
              rc == 3 and out.splitlines() == ["FORKCAP NULL"] and "forked past --fork-cap" in err)
        orig = tmp / "lib_orig.py"
        orig.write_text(LIB2)
        t0 = time.monotonic()
        rc, out, _ = drive("--diff", rng, "--path", "lib.py", "--max-mutants", "2", "--fork-cap", "32", "--timeout", "60",
                           "--cmd", f"sh -c 'cmp -s lib.py {orig} && exit 0; sh {chain} 120'")
        fl = out.splitlines()
        check("forkcap: a diff-mode mutant that forks past the cap is FORKCAP file:line OPERATOR, rc 1, never SURVIVED or KILLED",
              rc == 1 and len(fl) == 2 and all(re.match(r"FORKCAP lib\.py:\d+ [A-Z_]+  ", l) for l in fl)
              and time.monotonic() - t0 < 40)
        rc, out, _ = drive("--diff", rng, "--path", "lib.py", "--max-mutants", "2", "--fork-cap", "32", "--report-only",
                           "--cmd", f"sh -c 'cmp -s lib.py {orig} && exit 0; sh {chain} 120'")
        check("forkcap: under --report-only the same diff-mode FORKCAP lines print and rc is 0",
              rc == 0 and len(out.splitlines()) == 2 and all(l.startswith("FORKCAP ") for l in out.splitlines()))

        # fork cap: descendants that leave the process group or the session are still the command's
        esc = tmp / "esc.py"
        esc.write_text("import os, sys, time\n"
                       "mode, n = sys.argv[1], int(sys.argv[2])\n"
                       "if n <= 0:\n    time.sleep(120)\n    sys.exit(0)\n"
                       "pid = os.fork()\n"
                       "if pid == 0:\n"
                       "    {'pgrp': lambda: os.setpgid(0, 0), 'session': os.setsid, 'cleanenv': os.setsid, 'plain': lambda: None}[mode]()\n"
                       "    env = {} if mode == 'cleanenv' else os.environ\n"
                       "    os.execve(sys.executable, [sys.executable, sys.argv[0], mode, str(n - 1)], env)\n"
                       "time.sleep(0.02)\n"
                       "os.waitpid(pid, 0)\n")
        # a descendant that left the session is followed by the ppid leg alone once its environment is gone:
        # a host with no child subreaper (macOS, the BSDs) cannot run these cases, and says so per case
        check("subreaper: a Linux host has one, so no case below is skipped there", _can_subreap() == sys.platform.startswith("linux"))
        why = None if _can_subreap() else "no child subreaper (PR_SET_CHILD_SUBREAPER) on this host, so nothing follows a descendant out of its session"
        for mode in ("pgrp", "session", "cleanenv"):
            if why and mode != "pgrp":
                skip(f"forkcap: a chain that leaves its {mode} at every link", why)
                continue
            write_spec([bad])
            t0 = time.monotonic()
            rc, out, _ = drive("--spec", str(spec), "--cmd", f"sh -c 'grep -q \"return lo\" lib.py && exit 0; python3 {esc} {mode} 120'",
                               "--fork-cap", "32", "--timeout", "60")
            check(f"forkcap: a chain that leaves its {mode} at every link is FORKCAP, not waited out",
                  rc == 0 and out.splitlines() == ["SURVIVED NULL", "FORKCAP ret_hi"] and time.monotonic() - t0 < 30)
            left = subprocess.run(["pgrep", "-f", f"{esc} {mode}"], capture_output=True, text=True).stdout.split()
            check(f"forkcap: no {mode}-leaving descendant outlives the run", not left)
            for pid in left:
                os.kill(int(pid), signal.SIGKILL)
        for case, launch in (("left the session", "python3"), ("left the session, cleared its environment", f"env -i {sys.executable}")):
            name = f"forkcap: a daemon that {case} and outlived its command is killed at the command's exit"
            if why:
                skip(name, why)
                continue
            write_spec([bad])
            rc, out, _ = drive("--spec", str(spec), "--cmd",
                               f"sh -c 'setsid {launch} {esc} plain 0 </dev/null >/dev/null 2>&1 & exit 0'", "--timeout", "60")
            left = subprocess.run(["pgrep", "-f", f"{esc} plain 0"], capture_output=True, text=True).stdout.split()
            check(name, rc == 0 and not left)
            for pid in left:
                os.kill(int(pid), signal.SIGKILL)

        # STMT_DEL
        g("commit", "-q", "--allow-empty", "-m", "marker")
        before = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, env=env).stdout.strip()
        (repo / "stm.py").write_text(STM)
        (repo / "check_stm.py").write_text(STM_PINNED)
        g("add", "-A")
        g("commit", "-q", "-m", "add stm")
        rc, out, _ = drive("--diff", f"{before}...HEAD", "--list", "--path", "stm.py")
        sd = [l for l in out.splitlines() if " STMT_DEL " in l]
        sites = sorted(int(l.split()[1].split(":")[1]) for l in sd)
        check("STMT_DEL: one mutant per simple statement, a three-line continuation exactly once at its first line, "
              "none for an import, a docstring, a print or a compound header", sites == [6, 7, 8])
        rc, out, _ = drive("--diff", f"{before}...HEAD", "--cmd", "python3 check_stm.py", "--report-only", "--path", "stm.py")
        got = sorted(l.split()[:3] for l in out.splitlines() if " STMT_DEL " in l)
        check("STMT_DEL: the unpinned assignments SURVIVE and the pinned one is KILLED",
              got == [["SURVIVED", "stm.py:6", "STMT_DEL"], ["SURVIVED", "stm.py:8", "STMT_DEL"]])
        (repo / "stm.py").write_text(STM.replace('"""Doc."""', '"""Doc, reworded."""') + "# a comment\n")
        g("commit", "-q", "-am", "doc only")
        rc, out, _ = drive("--diff", "HEAD~1...HEAD", "--list")
        check("STMT_DEL: a comment- and docstring-only diff lists none (null control)", " STMT_DEL " not in out)
        # STMT_DEL on a shared line: `a = 1; b = 2` and `if x: y = 1` are skipped, a trailing comment is not
        (repo / "shr.py").write_text(SHR)
        g("add", "-A")
        g("commit", "-q", "-m", "add shr")
        rc, out, _ = drive("--diff", "HEAD~1...HEAD", "--list", "--path", "shr.py")
        sites = sorted(int(l.split()[1].split(":")[1]) for l in out.splitlines() if " STMT_DEL " in l)
        check("STMT_DEL: a statement sharing its line (`a = 1; b = 2`, `if x: y = 1`) is skipped; a statement with a "
              "trailing comment is not (the return is RETURN_DEL's)", sites == [4])
        check("operators: no mutant for a comment, an import or a def, and no CALL_DEL for a log call",
              not any(list(mutate_line(s)) for s in ("# if x < 1:", "import a1", "def f(x=1):"))
              and "CALL_DEL" not in {o for o, _ in mutate_line("    _LOGGER.info(x)")})
        check("skip: each case this host cannot run is counted, once: four without a child subreaper, one without /proc",
              skips == (0 if _can_subreap() else 4) + (0 if Path("/proc", "self", "stat").is_file() else 1))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"mutant_run self-test: {skips} skipped (each printed above as a `skip` line with its reason)")
    print(f"mutant_run self-test: {checks} checks, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(_self_test())
    sys.exit(main(sys.argv[1:]))
