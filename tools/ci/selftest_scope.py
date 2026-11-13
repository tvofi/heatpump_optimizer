#!/usr/bin/env python3
"""Scope governance.yml's instrument-self-tests steps by their measured read sets.

    python3 -I tools/ci/selftest_scope.py select --base REF [--head REF]
    python3 -I tools/ci/selftest_scope.py select --change M:docs/x.md [--change A:PATH]...
    python3 -I tools/ci/selftest_scope.py ids
    python3 -I tools/ci/selftest_scope.py record [--step ID]... [--out PATH]
    python3 -I tools/ci/selftest_scope.py prune --step ID --drop KIND:ITEM [--drop ...]
    python3 -I tools/ci/selftest_scope.py static
    python3 -I tools/ci/selftest_scope.py check --traces DIR [--write PATH]
    python3 -I tools/ci/selftest_scope.py settle
    python3 -I tools/ci/selftest_scope.py --self-test [--wrapper PATH] [--workflow PATH]

WHY (R10-CI-SELFTEST-SCOPE, owner lever 3, #201 comment 6707834331).
`tools/` is INERT in tests/closure.py, so no tool has a closure there and this
job ran every step on every pull request that touched anything but product.
Now a step runs on a pull request only when the diff reaches its MEASURED read
set, the way CLAUDE.md rule 1 selects test scripts from tests/closures.json,
and every push to main runs every step and re-measures them all.

THE TABLE, `tools/ci/selftest_closures.json`, is measured, never written by
hand: `record` runs the job's steps in order, each through
tools/ci/selftest_step.sh with SELFTEST_TRACE set, so every process a step
starts (bash, python, node, git) runs under `strace -f`, and folds the traces.
Per gated step it records:

  files   tracked files a process opened or executed;
  probes  repo paths a process stat'ed, tested or failed to open -- a file
          added or deleted there changes what the step sees;
  dirs    tracked directories a process listed;
  index   whether a process opened the git index (it reads the file list);
  objects whether a process opened the object store (it reads committed
          content of paths no trace names);
  run_sha the sha256 of the step's `run:` text the record was taken from.

THE SELECTION, `select`, on a pull request (prelude.py calls `selection`):
  FULL (every step) when the table is unreadable, when it is stale (its step
  set or a run_sha differs from the workflow's), when the diff touches a gate
  file (GATE_FILES), or when it ADDS a file under tools/ -- a new tool file
  has no recorded closure, so it runs every step;
  otherwise a step runs when a changed path is in its files, when it read the
  object store, or when the path is added or deleted and is one of its
  probes, sits in one of its dirs, or the step read the index.
Every other event is FULL. `MODE: SCOPED -- 0 step(s) run` and `MODE: FULL`
mean opposite things: key on the mode line.

THE DRIFT CHECK, `check`, runs on every push to main over the traces that
run took: it fails naming every step whose committed entry misses a file,
probe, directory or flag the run measured, and every gated step with no
entry. Over-approximation (an entry naming a file no longer read) is safe
and is reported, not refused. `--write` saves the run's own measurement,
which main uploads as the `selftest-closures` artifact: commit that file, or
re-record with `record` (Linux, strace).
THE SETTLED INDEX, `settle`, runs untraced before any step is (CI's strace
step; `record` itself): a fresh checkout leaves racily clean index entries,
whose content the first index-refreshing git command re-reads, so without it
those reads land in whichever traced step refreshes first.

BLIND SPOTS, stated: a path a process named relative to a working directory
the trace does not decorate (a non-*at syscall after a chdir) is resolved
against the repository root; a read through a network or a cache outside the
checkout is not a repo read; a git command in WORKTREE_GIT that opens the
object store does not set `objects` (its worktree reads are traced), so one
handed a revision reads committed content the record does not name; a step
whose behaviour depends on the
environment rather than the tree is not scoped by any table.
"""
from __future__ import annotations

import contextlib
import functools
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/governance.yml"
JOB = "instrument-self-tests"
TABLE = "tools/ci/selftest_closures.json"
WRAPPER = "tools/ci/selftest_step.sh"
SELF = "tools/ci/selftest_scope.py"
# A change to any of these changes which steps exist, what they run or how
# they are chosen: every step runs.
GATE_FILES = frozenset({WORKFLOW, ".github/workflows/ci.yml", TABLE, WRAPPER, SELF,
                        "tools/ci/prelude.py"})
NEW_FILE_PREFIX = "tools/"
UNGATED = ("scope", "strace", "launch", "drift", "unread")  # they choose, trace, start, audit
TRACE_DIR = "selftest-trace"
SCOPE_FILE = "selftest-scope.txt"    # under RUNNER_TEMP: the launcher's `sel` reads it

TABLE_COMMENT = (
    "MEASURED, not written by hand. Regenerate with `python3 tools/ci/selftest_scope.py "
    "record` on Linux with strace; every push to main re-measures each step and "
    "fails if an entry misses what the run read (R10-CI-SELFTEST-SCOPE).")


# ---------------------------------------------------------------------------
# the job's steps, read without a YAML library (prelude.py runs under -I)

class Step:
    def __init__(self, name: str = "", sid: str = "", cond: str = "", run: str | None = None):
        self.name, self.id, self.cond, self.run = name, sid, cond, run

    @property
    def run_sha(self) -> str:
        return hashlib.sha256((self.run or "").encode()).hexdigest()

    @property
    def gated(self) -> bool:
        return bool(self.id) and f"steps.scope.outputs.{self.id} == 'true'" in self.cond

    def waits_on(self) -> list[str]:
        return re.findall(r"\bbg_wait\s+([\w-]+)", self.run or "")


_KEY = re.compile(r"^(?P<lead>      - |        )(?P<key>[\w-]+):\s?(?P<val>.*)$")


def job_steps(text: str, job: str = JOB) -> list[Step]:
    """The steps of `job`, each with its name, id, if and dedented run text."""
    lines = text.splitlines()
    try:
        start = lines.index(f"  {job}:") + 1
    except ValueError:
        return []
    end = next((i for i in range(start, len(lines)) if re.match(r" {0,2}\S", lines[i])),
               len(lines))
    steps: list[Step] = []
    i = start
    while i < end and lines[i].strip() != "steps:":
        i += 1
    i += 1
    while i < end:
        m = _KEY.match(lines[i])
        i += 1
        if not m:
            continue
        if m.group("lead") == "      - ":
            steps.append(Step())
        key, val, st = m.group("key"), m.group("val"), steps[-1]
        if key == "name":
            st.name = val.strip()
        elif key == "id":
            st.id = val.strip()
        elif key == "if":
            st.cond = val.strip()
        elif key == "run":
            if re.fullmatch(r"[|>][-+0-9]*\s*", val):
                body = []
                while i < end and (not lines[i].strip() or lines[i].startswith(" " * 10)):
                    body.append(lines[i][10:])
                    i += 1
                while body and not body[-1].strip():
                    body.pop()
                st.run = "\n".join(body) + "\n"
            else:
                st.run = val.strip() + "\n"
    return steps


def workflow_steps(root: Path = ROOT) -> list[Step]:
    return job_steps((root / WORKFLOW).read_text())


def gated_ids(steps: list[Step]) -> list[str]:
    return [s.id for s in steps if s.gated]


def wiring_gaps(steps: list[Step]) -> list[str]:
    """Every way the job's gating disagrees with itself."""
    gaps = []
    ids = [s.id for s in steps if s.id]
    for sid in sorted({x for x in ids if ids.count(x) > 1}):
        gaps.append(f"DUPLICATE id {sid}")
    for s in steps:
        if s.run is None or s.id in UNGATED:
            continue
        if not s.gated:
            gaps.append(f"UNGATED step {s.name!r}: its if: does not read "
                        f"steps.scope.outputs.<its own id>")
    launch = next((s for s in steps if s.id == "launch"), None)
    waiters = {n: s.id for s in steps if s.id != "launch" for n in s.waits_on()}
    for n, sid in sorted(waiters.items()):
        if sid != n:
            gaps.append(f"MISNAMED waiter {sid}: it reads {n}, so its id must be {n}")
    # The launcher's commands: past its library's heredoc, comments dropped.
    body = (launch.run or "").split("\nLIB\n")[-1] if launch else ""
    body = "\n".join(x for x in body.splitlines() if not x.lstrip().startswith("#"))
    started = re.findall(r"\bbg_(?:start|run)\s+([\w-]+)", body)
    for n in started:
        if not re.search(rf"\bsel {re.escape(n)}\b[^\n]*\bbg_(?:start|run) {re.escape(n)}\b", body):
            gaps.append(f"UNSELECTED start {n}: the launcher starts it without `sel {n}`")
        if n not in waiters:
            gaps.append(f"UNREAD start {n}: no step waits on it")
    return gaps


SETTLE_CALL = re.compile(r"^python3 -I tools/ci/selftest_scope\.py settle$", re.M)


def settle_gaps(steps: list[Step]) -> list[str]:
    """CI's half of the settled index (R10-HOTFIX-PREPR-READSET): an untraced
    step ordered before the job's first traced one (a gated step, or `launch`,
    which starts traced ones) runs `settle` as a line of its own, so a failure
    fails the step. `record` settles itself; on a pull request the step never
    runs, so this static read is the only pin on the line."""
    first = next((i for i, s in enumerate(steps) if s.gated or s.id == "launch"), len(steps))
    if any(s.id in UNGATED and SETTLE_CALL.search(s.run or "") for s in steps[:first]):
        return []
    return ["UNSETTLED job: no untraced step before its first traced one runs "
            "`python3 -I tools/ci/selftest_scope.py settle` on a line of its own"]


# ---------------------------------------------------------------------------
# the table

def load_table(path: Path) -> dict | None:
    try:
        doc = json.loads(path.read_text())
        steps = doc["steps"]
        if not isinstance(steps, dict) or not all(isinstance(v, dict) for v in steps.values()):
            return None
        return doc
    except (OSError, ValueError, KeyError, TypeError):
        return None


def stale(table: dict, steps: list[Step]) -> str:
    """'' when the table describes exactly these gated steps, else why not."""
    by_id = {s.id: s for s in steps if s.gated}
    have = set(table["steps"])
    if have != set(by_id):
        return (f"its steps differ from the workflow's: missing {sorted(set(by_id) - have)}, "
                f"extra {sorted(have - set(by_id))}")
    moved = sorted(i for i, s in by_id.items() if table["steps"][i].get("run_sha") != s.run_sha)
    return f"run text changed since it was recorded: {moved}" if moved else ""


def covers(entries, path: str) -> bool:
    """Whether a `files` list names `path`: the path itself, or `D/**` for an
    ancestor D (a directory the record read every tracked file of)."""
    entries = entries if isinstance(entries, (set, frozenset)) else set(entries)
    return path in entries or any(f"{a}/**" in entries for a in _ancestors(path) if a != ".")


def collapse(files: set[str], tracked: set[str]) -> list[str]:
    """(Idempotent: a `D/**` entry already in `files` is kept.)"""
    done = {f for f in files if f.endswith("/**")}
    files = {f for f in files if not covers(done, f)} - done
    return sorted(set(_collapse(files, tracked)) | done)


def _collapse(files: set[str], tracked: set[str]) -> list[str]:
    """`files` with each topmost directory whose every tracked file was read
    (two or more) written `D/**`: the table's size, losslessly at record time,
    and a file added under D later is taken as read, which is safe."""
    total: dict[str, int] = {}
    for f in tracked:
        for a in _ancestors(f):
            total[a] = total.get(a, 0) + 1
    read: dict[str, int] = {}
    for f in files:
        for a in _ancestors(f):
            read[a] = read.get(a, 0) + 1
    out = set()
    for f in files:
        whole = [a for a in _ancestors(f) if a != "." and total.get(a, 0) >= 2
                 and read.get(a) == total.get(a)]
        out.add(f"{whole[-1]}/**" if whole else f)
    return sorted(out)


def compact_probes(probes: set[str], dirs: set[str], tracked: set[str]) -> list[str]:
    """Probes less those a listed directory already answers for (an add or
    delete under one selects the step anyway), then collapsed like files."""
    keep = {p for p in probes if not p.endswith("/**")
            and not any(a in dirs for a in _ancestors(p))}
    return sorted(collapse(keep, tracked) + [p for p in probes if p.endswith("/**")])


def _ancestors(path: str) -> list[str]:
    parts = path.split("/")[:-1]
    return ["/".join(parts[:k]) or "." for k in range(len(parts), -1, -1)]


def select(changes: list[tuple[str, str]], table: dict | None, steps: list[Step]) -> dict:
    """{'mode': 'FULL'|'SCOPED', 'why': str, 'ids': [...]} for (status, path) changes."""
    every = gated_ids(steps)

    def full(why: str) -> dict:
        return {"mode": "FULL", "why": why, "ids": every}

    if table is None:
        return full("the table is unreadable")
    why = stale(table, steps)
    if why:
        return full(f"the table is stale: {why}")
    if not changes:
        return full("no changed files to scope on")
    gate = sorted(p for _, p in changes if p in GATE_FILES)
    if gate:
        return full(f"a gate file changed: {gate}")
    # Exact names only: a `D/**` entry says every file D held was read, which
    # is no record of a file D did not hold yet.
    known = set().union(*(set(e.get("files", ())) | set(e.get("probes", ()))
                          for e in table["steps"].values()))
    new = sorted(p for st, p in changes if st == "A" and p.startswith(NEW_FILE_PREFIX)
                 and p not in known)
    if new:
        return full(f"a new {NEW_FILE_PREFIX} file has no recorded closure: {new}")
    picked = []
    for sid in every:
        e = table["steps"][sid]
        files, probes, dirs = set(e.get("files", ())), set(e.get("probes", ())), set(e.get("dirs", ()))
        for st, p in changes:
            if covers(files, p) or e.get("objects"):
                break
            if st in ("A", "D") and (covers(probes, p) or e.get("index")
                                     or any(a in dirs for a in _ancestors(p))):
                break
        else:
            continue
        picked.append(sid)
    return {"mode": "SCOPED", "why": "", "ids": picked}


def mode_line(plan: dict) -> str:
    if plan["mode"] == "FULL":
        return f"MODE: FULL -- every step runs ({plan['why']})"
    return f"MODE: SCOPED -- {len(plan['ids'])} step(s) run"


def output(plan: dict) -> str:
    """The prelude's `selftests` value: 'all', 'none', or the ids."""
    if plan["mode"] == "FULL":
        return "all"
    return " ".join(plan["ids"]) or "none"


def diff_changes(base: str, head: str = "HEAD", cwd: Path = ROOT) -> list[tuple[str, str]] | None:
    """(status, path) for `base...head`, both sides of a rename; None when git cannot say."""
    r = subprocess.run(["git", "diff", "--no-renames", "--name-status", f"{base}...{head}"],
                       cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    out = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            out.append((parts[0][:1], parts[1]))
    return out


def selection(base: str, head: str, root: Path = ROOT) -> str:
    """The prelude's entry point: the `selftests` output for a pull request."""
    try:
        steps = workflow_steps(root)
    except OSError:
        return "all"
    # git unable to diff gives no changes, and an empty diff is FULL.
    return output(select(diff_changes(base, head, root) or [], load_table(root / TABLE), steps))


# ---------------------------------------------------------------------------
# folding traces

_CALL = re.compile(r"^(?P<pid>\d+)\s+(?P<rest>.*)$")
_STR = r'"((?:[^"\\]|\\.)*)"'
_FD = r"(?:AT_FDCWD|-?\d+)(?:<([^>]*)>)?"
_AT = re.compile(rf"^(openat2?|newfstatat|fstatat64|statx|faccessat2?|readlinkat|execveat)\({_FD},\s*{_STR}")
_PLAIN = re.compile(rf"^(open|creat|stat|lstat|stat64|lstat64|access|readlink|execve)\({_STR}")
_RET = re.compile(r"\)\s+=\s+(-?\d+)(?:<([^>]*)>)?(?:\s|$)")
_END = re.compile(r"^(\d+)\s+\+\+\+ (?:exited with|killed by) ")   # strace -q's exit line
_OPENS = ("openat", "openat2", "open", "creat")
_EXECS = ("execve", "execveat")


def _unescape(s: str) -> str:
    try:
        return bytes(s, "utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8", "replace")
    except (UnicodeDecodeError, ValueError):
        return s


def _git_dirs(root: Path) -> tuple[Path, Path]:
    """(this checkout's git dir, the common dir holding objects/): two paths
    in a linked worktree, one otherwise; both absolute, whatever our cwd."""
    def rev(arg):
        r = subprocess.run(["git", "rev-parse", "--path-format=absolute", arg], cwd=root,
                           capture_output=True, text=True)
        return Path(os.path.realpath(r.stdout.strip() if r.returncode == 0 else root / ".git"))
    return rev("--git-dir"), rev("--git-common-dir")


def trace_events(lines):
    """(pid, call, resolved absolute path, ok, line) per relevant syscall line
    of an iterable of trace lines, joining a call strace split into
    `<unfinished ...>` and `resumed`."""
    pending: dict[str, str] = {}
    for line in lines:
        m = _CALL.match(line.rstrip("\n"))
        if not m:
            continue
        pid, rest = m.group("pid"), m.group("rest")
        if rest.endswith("<unfinished ...>"):
            pending[pid] = rest[: -len("<unfinished ...>")]
            continue
        r = re.match(r"^<\.\.\. \w+ resumed>(.*)$", rest)
        if r:
            if pid not in pending:
                continue
            rest = pending.pop(pid) + r.group(1)
        at, plain = _AT.match(rest), _PLAIN.match(rest)
        if at:
            call, base, raw = at.group(1), at.group(2), _unescape(at.group(3))
        elif plain:
            call, base, raw = plain.group(1), None, _unescape(plain.group(2))
        else:
            continue
        if not raw:
            continue                      # an fd's own stat (AT_EMPTY_PATH)
        ret = _RET.search(rest)
        ok = bool(ret) and int(ret.group(1)) >= 0
        if call in _OPENS and ok and ret.group(2):
            path = ret.group(2)
        else:                             # an absolute `raw` replaces the base
            path = os.path.join(base or str(ROOT), raw)
        yield pid, call, os.path.normpath(path), ok, rest


# Git subcommands whose content reads are the worktree's, which the trace
# names file by file; the object store they also open (a pack to resolve the
# index) carries no content they report. A revision handed to one of them
# (`git grep PAT HEAD`) is a blind spot, stated in the module docstring.
WORKTREE_GIT = frozenset({"grep", "ls-files", "status", "check-ignore", "check-attr",
                          "diff-files", "rev-parse", "config", "var"})


def _git_subcommand(line: str) -> str:
    """The subcommand an execve of git runs ('' for anything else)."""
    m = re.search(r'execve\("[^"]*/git", \[(.*?)\]', line)
    if not m:
        return ""
    args = re.findall(_STR, m.group(1))[1:]
    while args and args[0].startswith("-"):
        args = args[2:] if args[0] in ("-C", "-c") else args[1:]
    return args[0] if args else ""


_NOT_A_NAME = re.compile(r"[:\[\]^~*?]|\.\.\.|^\.merge_file_|^[0-9a-f]{40}$|^[0-9a-f]{64}$")


def probe_path(rel: str, tracked_dirs: set[str]) -> bool:
    """Whether a probed path is one a diff could add or delete: under a
    tracked directory, not a cache, and a file name rather than a string a
    process handed to a path syscall (`pipe:[N]`, `REV:path`, `A...B`, git's
    `.merge_file_*` temporaries, a commit id) -- those differ run to run and
    name nothing (two recordings of one tree, compared step by step); nor
    `.git`, which no diff adds (a linked worktree's is a file in `.`)."""
    parts = rel.split("/")
    parent = "/".join(parts[:-1]) or "."
    return (parent in tracked_dirs and parts[0] != ".git" and "__pycache__" not in parts
            and "node_modules" not in parts and not _NOT_A_NAME.search(parts[-1]))


def _pyc_source(rel: str) -> str:
    m = re.fullmatch(r"(.*/)?__pycache__/([^/]+?)\.[^/.]+(?:\.opt-\d)?\.pyc", rel)
    return f"{m.group(1) or ''}{m.group(2)}.py" if m else rel


def trace_end(lines, seen: dict):
    """The lines, passed through; sets seen["root"] to the first process's pid
    and adds every pid strace saw exit to seen["ended"]."""
    seen.setdefault("root", None)
    seen.setdefault("ended", set())
    for line in lines:
        e = _END.match(line)
        if e:
            seen["ended"].add(e.group(1))
        elif seen["root"] is None and (c := _CALL.match(line)):
            seen["root"] = c.group("pid")
        yield line


def trace_state(seen: dict) -> str:
    """EMPTY (no traced call), PARTIAL (its first process never exited: strace
    stopped before the step ended) or '' (whole), over trace_end's `seen`."""
    if seen.get("root") is None:
        return "EMPTY"
    return "" if seen["root"] in seen["ended"] else "PARTIAL"


def fold_trace(lines, root: Path, tracked: set[str], tracked_dirs: set[str],
               git_dir: Path, common_dir: Path) -> dict:
    files, probes, dirs = set(), set(), set()
    flags = {"index": False, "objects": False}
    gits: set[str] = set()                # the git subcommands that set `objects`
    real_root = os.path.realpath(root)
    git_cmd: dict[str, str] = {}          # pid -> the git subcommand it exec'd
    realpath = functools.lru_cache(maxsize=None)(os.path.realpath)  # paths repeat by the million
    for pid, call, path, ok, line in trace_events(lines):
        is_dir = "O_DIRECTORY" in line
        if call in _EXECS and ok:
            git_cmd[pid] = _git_subcommand(line)
        real = realpath(path) if ok else path
        for gd in {str(git_dir), str(common_dir)}:
            if real.startswith(gd + "/"):
                sub = real[len(gd) + 1:]
                if call in _OPENS and ok and sub == "index" and gd == str(git_dir):
                    flags["index"] = True
                if (call in _OPENS and ok and sub.startswith("objects/")
                        and git_cmd.get(pid) not in WORKTREE_GIT):
                    flags["objects"] = True
                    gits.add(git_cmd.get(pid) or "?")
        for cand in (path, real):
            if cand == real_root or cand.startswith(real_root + "/"):
                rel = cand[len(real_root) + 1:] if cand != real_root else "."
                break
            if cand == str(root) or cand.startswith(str(root) + "/"):
                rel = cand[len(str(root)) + 1:] if cand != str(root) else "."
                break
        else:
            continue
        rel = _pyc_source(rel)              # .git/ is neither tracked nor a tracked dir
        if is_dir and ok and call in _OPENS:
            if rel in tracked_dirs:
                dirs.add(rel)
        elif ok and call in _OPENS + _EXECS and rel in tracked:
            files.add(rel)
        elif probe_path(rel, tracked_dirs):
            probes.add(rel)
    return {"files": files, "probes": probes, "dirs": dirs, "git": gits, **flags}


def _tracked(root: Path) -> tuple[set[str], set[str]]:
    r = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True, check=True)
    files = {f for f in r.stdout.split("\0") if f}
    dirs = {"."}
    for f in files:
        dirs.update(a for a in _ancestors(f) if a != ".")
    return files, dirs


def _ignored(root: Path, paths: set[str]) -> set[str]:
    r = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"], cwd=root,
                       input="\0".join(sorted(paths)) + "\0", capture_output=True, text=True)
    return {p for p in r.stdout.split("\0") if p}


def fold(trace_dir: Path, steps: list[Step], root: Path = ROOT) -> tuple[dict[str, dict], list[str]]:
    """(each gated step's measured entry, the refusals): an entry folds the
    step's own trace and its waited-on bg traces; a refusal names a bg trace
    missing beside its step's own, and an EMPTY or PARTIAL trace, which
    measure less than the step read. A step with no trace of its own has no
    entry, which drift refuses as UNMEASURED."""
    tracked, tracked_dirs = _tracked(root)
    git_dir, common_dir = _git_dirs(root)
    out: dict[str, dict] = {}
    broken: list[str] = []
    for s in steps:
        if not s.gated:
            continue
        sources = [trace_dir / f"step-{s.id}.trace"] + [trace_dir / f"bg-{n}.trace" for n in s.waits_on()]
        if not sources[0].is_file():
            continue
        acc = {"files": set(), "probes": set(), "dirs": set(), "git": set(),
               "index": False, "objects": False}
        for src in sources:
            if not src.is_file():
                broken.append(f"MISSING trace {src.name} (step {s.id}): its detached self-test left none")
                continue
            seen: dict = {}
            with open(src, errors="replace") as fh:
                got = fold_trace(trace_end(fh, seen), root, tracked, tracked_dirs, git_dir, common_dir)
            state = trace_state(seen)
            if state:
                broken.append(f"{state} trace {src.name} (step {s.id}): "
                              + ("no traced call" if state == "EMPTY" else "its first process never exited"))
            for k in ("files", "probes", "dirs", "git"):
                acc[k] |= got[k]
            for k in ("index", "objects"):
                acc[k] = acc[k] or got[k]
        acc["probes"] -= acc["files"]
        out[s.id] = acc
    ignored = _ignored(root, set().union(*(e["probes"] for e in out.values())) if out else set())
    gone = [r.rstrip("/") for r in retired_paths(root)]
    ignored |= {p for e in out.values() for p in e["probes"]
                if any(p == r or p.startswith(r + "/") for r in gone)}
    return {sid: {"run_sha": next(s.run_sha for s in steps if s.id == sid),
                  "files": sorted(e["files"]), "probes": sorted(e["probes"] - ignored),
                  "dirs": sorted(e["dirs"]), "index": e["index"], "objects": e["objects"],
                  "git": sorted(e["git"])}
            for sid, e in out.items()}, broken


def _under_scoped(sid: str, kind: str, miss: list[str]) -> str:
    more = f" (+{len(miss) - 8} more)" if len(miss) > 8 else ""
    return f"UNDER-SCOPED step {sid}: {kind} misses {miss[:8]}{more}"


def drift(table: dict | None, measured: dict[str, dict], steps: list[Step]) -> tuple[list[str], list[str]]:
    """(refusals, notes): what the committed table misses, and what it over-names."""
    refuse, notes = [], []
    if table is None:
        return ["UNREADABLE the committed table"], notes
    for sid in gated_ids(steps):
        if sid not in measured:
            refuse.append(f"UNMEASURED step {sid}: this run left no trace of it")
            continue
        e, m = table["steps"].get(sid), measured[sid]
        if e is None:
            refuse.append(f"UNRECORDED step {sid}: the table has no entry")
            continue
        if e.get("run_sha") != m["run_sha"]:
            refuse.append(f"STALE step {sid}: its run text changed since the record")
        have, dirs = set(e.get("files", ())), set(e.get("dirs", ()))
        probes = set(e.get("probes", ()))
        misses = {
            "files": [f for f in m["files"] if not covers(have, f)],
            "probes": [p for p in m["probes"] if not covers(probes, p)
                       and not any(a in dirs for a in _ancestors(p))],
            "dirs": sorted(set(m["dirs"]) - dirs)}
        refuse += [_under_scoped(sid, k, sorted(v)) for k, v in misses.items() if v]
        gone = {"files": [f for f in have if f not in set(m["files"]) and not (
                    f.endswith("/**") and any(x.startswith(f[:-2]) for x in m["files"]))],
                "dirs": sorted(dirs - set(m["dirs"]))}
        notes += [f"over-scoped step {sid}: {len(v)} {k} no longer measured" for k, v in gone.items() if v]
        for k in ("index", "objects"):
            if m[k] and not e.get(k):
                refuse.append(f"UNDER-SCOPED step {sid}: it read the {k}, the table says not")
    for sid in sorted(set(table["steps"]) - set(gated_ids(steps))):
        refuse.append(f"EXTRA entry {sid}: no gated step has that id")
    return refuse, notes


# ---------------------------------------------------------------------------
# recording: the job, replayed through the same wrapper CI uses

def _index_path(root: Path, env: dict | None = None) -> Path:
    out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-path", "index"],
                         cwd=root, env=env, capture_output=True, text=True).stdout.strip()
    return Path(out) if out else root / ".git" / "index"


def racy_entries(root: Path, env: dict | None = None) -> list[str]:
    """Tracked files whose mtime second is not before the index's own: git
    cannot vouch for them from stat data, so the next index-refreshing
    command (`git status`, `git diff`) opens and hashes each one. The second
    is the coarser of git's two racy tests (with and without USE_NSEC)."""
    try:
        stamp = int(_index_path(root, env).stat().st_mtime)
    except OSError:
        return []
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=root, env=env,
                            capture_output=True, text=True).stdout.split("\0")
    racy = []
    for rel in filter(None, listed):
        with contextlib.suppress(OSError):
            if int((root / rel).lstat().st_mtime) >= stamp:
                racy.append(rel)
    return sorted(racy)


def settle_index(root: Path, env: dict | None = None) -> int:
    """Rewrite the index in a second later than every tracked file's mtime,
    so no entry is racily clean when a traced step starts. Without it the
    content reads of a fresh checkout's last-written files fall to whichever
    traced process first refreshes the index -- a read set that moves with
    scheduling, not with the tree (R10-HOTFIX-PREPR-READSET)."""
    racy = racy_entries(root, env)
    if not racy:
        return 0
    newest = max(int((root / r).lstat().st_mtime) for r in racy if (root / r).exists())
    if newest > time.time() + 5:
        print(f"selftest_scope: settle: {racy[0]} is stamped in the future, so no index can vouch for it",
              file=sys.stderr)
        return 1
    # File and index stamps come from the kernel's coarse clock, which lags
    # time.time() by up to a tick: a rewrite just past the second boundary
    # can still be stamped in the old second, so wait past it and retry.
    for _ in range(3):
        while time.time() < newest + 1.1:
            time.sleep(0.05)
        subprocess.run(["git", "update-index", "-q", "--really-refresh", "--force-write-index"],
                       cwd=root, env=env, capture_output=True)
        left = racy_entries(root, env)
        if not left:
            return 0
        newest = max(int((root / r).lstat().st_mtime) for r in left if (root / r).exists())
    print(f"selftest_scope: settle left {len(left)} racily clean index entr(ies), e.g. {left[0]}",
          file=sys.stderr)
    return 1


LIST_KINDS = ("files", "probes", "dirs", "git")
FLAG_KINDS = ("index", "objects")


def union_entry(old: dict | None, new: dict) -> dict:
    """The committed entry with the new recording added: a record is taken at
    one checkout and one trace, so it may miss a read the table holds from
    another (R10-RCA-SELFTEST-SCOPE-DRIFT: replacing dropped 660, 8 and 10
    entries in three merges). Over-approximation is safe, so no read leaves."""
    old = old or {}
    got = {k: sorted(set(old.get(k, ())) | set(new[k])) for k in LIST_KINDS}
    got["probes"] = [p for p in got["probes"] if p not in set(got["files"])]
    return {**new, **got, **{k: bool(old.get(k)) or bool(new[k]) for k in FLAG_KINDS}}


def union_record(old: dict | None, measured: dict[str, dict], gated: set[str]) -> dict[str, dict]:
    """The table `record` writes: every committed entry (a step not re-measured
    stays as it is), each measured step unioned over its own, less steps the
    workflow no longer gates -- a removed step is not a dropped read."""
    entries = dict(old["steps"]) if old else {}
    for sid, m in measured.items():
        entries[sid] = union_entry(entries.get(sid), m)
    return {k: v for k, v in entries.items() if k in gated}


def prune_entries(table: dict, step: str, drops: list[str]) -> tuple[dict[str, dict], list[str]]:
    """(entries, unknown): `table` less each `KIND:ITEM` of `step`, the one
    way a read leaves the table (an index or objects flag is `KIND:` alone).
    The shrink guard still refuses a drop of a path the diff does not delete."""
    entries = {k: dict(v) for k, v in table["steps"].items()}
    unknown = []
    if step not in entries:
        return entries, [f"no step {step}"]
    for d in drops:
        kind, _, item = d.partition(":")
        if kind in FLAG_KINDS and not item and entries[step].get(kind):
            entries[step][kind] = False
        elif kind in LIST_KINDS and item in entries[step].get(kind, ()):
            entries[step][kind] = [x for x in entries[step][kind] if x != item]
        else:
            unknown.append(d)
    return entries, unknown


def shrink_drops(base: dict | None, head: dict | None, deleted: set[str], remaining: set[str]) -> list[str]:
    """What `head`'s table drops of `base`'s, step by step: each files, probes,
    dirs or git item and each index or objects flag the base entry names that
    the head's entry does not, unless the diff deletes the path (`deleted`; a
    directory or `D/**` item whose every file went, given `remaining`, the
    head's tracked files). A step the head does not gate or the base lacks is
    not a drop. A base item is kept when the head names it, covers it with a
    `D/**` entry, or reads it as a file (a probe), or lists its directory."""
    if not base or not head:
        return []
    out = []

    def gone(item: str) -> bool:
        p = item[:-3] if item.endswith("/**") else item
        return p in deleted or (any(d.startswith(p + "/") for d in deleted)
                                and not any(r.startswith(p + "/") for r in remaining))
    for sid, b in sorted(base["steps"].items()):
        h = head["steps"].get(sid)
        if h is None:
            continue
        files, dirs, probes = set(h.get("files", ())), set(h.get("dirs", ())), set(h.get("probes", ()))
        kept = {"files": lambda x: covers(files, x),
                "probes": lambda x: covers(probes, x) or covers(files, x)
                or any(a in dirs for a in _ancestors(x)),
                "dirs": lambda x: x in dirs,
                "git": lambda x: x in set(h.get("git", ()))}
        for k in LIST_KINDS:
            miss = sorted(x for x in b.get(k, ()) if not kept[k](x) and (k == "git" or not gone(x)))
            if miss:
                out.append(f"SHRUNK step {sid}: the head's entry drops {len(miss)} {k} the base names, "
                           f"e.g. {miss[0]} -- a re-record unions; a read leaves by `prune`, and only a "
                           f"path this diff deletes may")
        out += [f"SHRUNK step {sid}: the head's entry drops the {k} flag the base sets"
                for k in FLAG_KINDS if b.get(k) and not h.get(k)]
    return out


def table_base(root: Path, env: dict | None = None) -> tuple[str | None, str]:
    """(revision, problem): the revision the guard compares against --
    SELFTEST_BASE; else the merge base with the pull request's base branch
    (GITHUB_BASE_REF, whose checkout is a merge commit); else the first parent
    (a push to main); None without one. A named base that does not resolve is
    the problem, never a pass: a shallow or base-less checkout would otherwise
    leave the guard unevaluated and `static` green."""
    env = os.environ if env is None else env
    cands = []
    if env.get("SELFTEST_BASE"):
        cands.append(env["SELFTEST_BASE"])
    if env.get("GITHUB_BASE_REF"):
        cands.append(f"origin/{env['GITHUB_BASE_REF']}")
    for c in cands:
        r = subprocess.run(["git", "merge-base", c, "HEAD"], cwd=root, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip(), ""
        return None, (f"UNRESOLVED base {c}: no merge base with HEAD, so the table's shrink cannot be "
                      f"judged -- fetch it (a shallow checkout has none); it is not guessed around")
    r = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD^1"], cwd=root, capture_output=True, text=True)
    return (r.stdout.strip() if r.returncode == 0 else None), ""


def shrink_gaps(root: Path, base: str | None) -> list[str]:
    """The guard over `base`..HEAD in the repository at `root`: nothing when the
    diff leaves the table alone or `base` has no readable table."""
    if base is None:
        return []
    diff = subprocess.run(["git", "diff", "--no-renames", "--name-status", base, "HEAD"],
                          cwd=root, capture_output=True, text=True)
    if diff.returncode != 0:
        return [f"UNREADABLE the diff {base[:12]}..HEAD: the table's shrink cannot be judged"]
    rows = [l.split("\t", 1) for l in diff.stdout.splitlines() if "\t" in l]
    if TABLE not in {p for _, p in rows}:
        return []
    shown = subprocess.run(["git", "show", f"{base}:{TABLE}"], cwd=root, capture_output=True, text=True)
    try:
        before = json.loads(shown.stdout) if shown.returncode == 0 else None
    except ValueError:
        before = None
    tree = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=root, capture_output=True, text=True)
    return shrink_drops(before, load_table(root / TABLE), {p for st, p in rows if st == "D"},
                        set(tree.stdout.splitlines()))


def record(root: Path, only: list[str] | None, out: Path) -> int:
    if shutil.which("strace") is None:
        print("selftest_scope: record needs strace (Linux)", file=sys.stderr)
        return 2
    if settle_index(root):
        return 1
    steps = workflow_steps(root)
    gaps = wiring_gaps(steps)
    if gaps:
        print("\n".join(gaps), file=sys.stderr)
        return 1
    want = set(only or gated_ids(steps))
    unknown = want - set(gated_ids(steps))
    if unknown:
        print(f"selftest_scope: no gated step {sorted(unknown)}", file=sys.stderr)
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="selftest-record-"))
    env = dict(os.environ, RUNNER_TEMP=str(tmp), SELFTEST_TRACE="1", HPO_JOB_GRADES="nothing")
    # A seat profile sourced through BASH_ENV may reset RUNNER_TEMP in every
    # step's shell (the cloud seat's does), which would split the traces and
    # the scope file from this run's directory; PATH is already inherited.
    env.pop("BASH_ENV", None)
    (tmp / SCOPE_FILE).write_text("".join(f"{i}\n" for i in want))
    failed = []
    for s in steps:
        if s.run is None or s.id in ("scope", "strace", "drift") or (s.gated and s.id not in want):
            continue
        script = tmp / f"{s.id or 'step'}.sh"
        script.write_text(s.run)
        t0 = time.time()
        r = subprocess.run(["bash", WRAPPER, str(script)], cwd=root, capture_output=True, text=True,
                           env={**env, "GITHUB_ACTION": s.id or "unnamed"})
        print(f"{'OK  ' if r.returncode == 0 else 'FAIL'} {time.time() - t0:7.1f}s {s.id}", flush=True)
        if r.returncode:
            failed.append(s.id)
            print((r.stdout + r.stderr)[-1500:], flush=True)
    measured, broken = fold(tmp / TRACE_DIR, steps, root)
    shutil.rmtree(tmp, ignore_errors=True)    # gigabytes of traces on a full record
    for line in broken:
        print(line, flush=True)
    entries = union_record(load_table(out), measured, set(gated_ids(steps)))
    write_table(out, entries, root)
    print(f"selftest_scope: recorded {len(measured)} step(s) into {out}; "
          f"{len(failed)} failed {failed}, {len(broken)} broken trace(s)")
    return 1 if failed or broken else 0


def _traced() -> bool:
    """Whether a tracer holds this process: main's traced run of this very
    step, where a nested strace could not attach (one tracer per process)."""
    try:
        return any(l.split()[1] != "0" for l in Path("/proc/self/status").read_text().splitlines()
                   if l.startswith("TracerPid:"))
    except (OSError, IndexError):
        return False


def retired_paths(root: Path) -> list[str]:
    """tests/layout.py's LANDED retired paths at `root` (none without it). A
    diff re-adding a file under one is refused there (`placement`), so a probe
    of one can select nothing, and naming it would be a new reference to a
    retired path, which the same guard refuses."""
    if not (root / "tests" / "layout.py").is_file():
        return []
    sys.path.insert(0, str(root / "tests"))
    try:
        import layout
    finally:
        sys.path.pop(0)
    manifest = layout.load(root)
    return [r["old"] for r in layout.landed(layout.tracked(root), manifest["retired"],
                                            manifest.get("ref_namespaces", ()))]


def write_table(out: Path, entries: dict[str, dict], root: Path = ROOT) -> None:
    tracked, _ = _tracked(root)
    entries = {k: {**v, "files": collapse(set(v["files"]), tracked),
                   "probes": compact_probes(set(v["probes"]), set(v["dirs"]), tracked)}
               for k, v in entries.items()}
    out.write_text(json.dumps({"_comment": TABLE_COMMENT, "workflow": WORKFLOW, "job": JOB,
                               "steps": dict(sorted(entries.items()))}, indent=1) + "\n")


def check_cli(trace_dir: Path, write: Path | None = None, root: Path = ROOT) -> int:
    steps = workflow_steps(root)
    gaps = wiring_gaps(steps)
    measured, broken = fold(trace_dir, steps, root)
    if write is not None:
        write_table(write, measured, root)  # this run's measurement, to commit as the table
    refuse, notes = drift(load_table(root / TABLE), measured, steps)
    refuse = broken + refuse
    for line in gaps + refuse:
        print(f"  {line}")
    for line in notes:
        print(f"  note: {line}")
    print(f"selftest_scope check: {len(gated_ids(steps))} gated step(s), "
          f"{len(gaps) + len(refuse)} refusal(s)")
    return 1 if gaps or refuse else 0


def static_check(root: Path = ROOT) -> int:
    """The pull-request side: the job's gating is consistent and the table is
    not stale against it. No tracing; the drift check is main's."""
    steps = workflow_steps(root)
    problems = wiring_gaps(steps) + settle_gaps(steps)
    table = load_table(root / TABLE)
    if table is None:
        problems.append(f"UNREADABLE {TABLE}")
    else:
        why = stale(table, steps)
        if why:
            problems.append(f"STALE {TABLE}: {why} -- re-record the changed step(s) with "
                            f"`python3 {SELF} record --step ID`")
    base, unresolved = table_base(root)
    problems += [unresolved] if unresolved else shrink_gaps(root, base)
    for p in problems:
        print(f"  {p}")
    print(f"selftest_scope static: {len(gated_ids(steps))} gated step(s), {len(problems)} problem(s)")
    return 1 if problems else 0


# ---------------------------------------------------------------------------

def self_test(wrapper: Path = ROOT / WRAPPER, workflow: Path = ROOT / WORKFLOW) -> int:
    """The self-test under a controlled environment: the base selectors the
    caller exported (GITHUB_BASE_REF on a pull_request event, SELFTEST_BASE) name
    a ref the scratch fixtures lack, so they never reach a fixture call."""
    held = {k: os.environ.pop(k) for k in ("GITHUB_BASE_REF", "SELFTEST_BASE") if k in os.environ}
    try:
        return _self_test(wrapper, workflow)
    finally:
        os.environ.update(held)


def _self_test(wrapper: Path, workflow: Path) -> int:
    """The refusals, over fixtures; `wrapper` is the selftest_step.sh and
    `workflow` the live job's file under test (selftest_scope_mutants.sh hands
    either a mutant)."""
    passed = failed = 0

    def ck(name: str, ok: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    wf = (
        "jobs:\n"
        f"  {JOB}:\n"
        "    runs-on: x\n"
        "    steps:\n"
        "      - uses: actions/checkout@x\n"
        "      - name: Choose\n"
        "        id: scope\n"
        "        run: echo\n"
        "      - name: Launch\n"
        "        id: launch\n"
        "        run: |\n"
        "          sel slow && bg_start slow bash tools/x/slow.sh --self-test\n"
        "      - name: A\n"
        "        id: a\n"
        "        if: steps.scope.outputs.a == 'true'\n"
        "        run: python3 -I tools/x/a.py --self-test\n"
        "      - name: B\n"
        "        id: b\n"
        "        if: ${{ !cancelled() && steps.scope.outputs.b == 'true' }}\n"
        "        run: |\n"
        "          set -o pipefail\n"
        "          python3 -I tools/x/b.py --self-test\n"
        "      - name: Slow\n"
        "        id: slow\n"
        "        if: ${{ !cancelled() && steps.scope.outputs.slow == 'true' }}\n"
        "        run: |\n"
        "          bg_wait slow\n"
        "      - name: Unread\n"
        "        id: unread\n"
        "        if: ${{ !cancelled() }}\n"
        "        run: bg_unread\n"
        "  next-job:\n"
        "    steps:\n"
        "      - name: Z\n"
        "        id: z\n"
        "        if: steps.scope.outputs.z == 'true'\n"
        "        run: true\n")
    steps = job_steps(wf)
    ck("the parser reads the job's steps and stops at the next job",
       [s.id for s in steps] == ["", "scope", "launch", "a", "b", "slow", "unread"])
    ck("a block run is dedented, an inline one kept",
       steps[4].run == "set -o pipefail\npython3 -I tools/x/b.py --self-test\n"
       and steps[3].run == "python3 -I tools/x/a.py --self-test\n")
    ck("run_sha is the sha256 of the step's own run text",
       steps[3].run_sha == hashlib.sha256(steps[3].run.encode()).hexdigest()
       and steps[3].run_sha != steps[4].run_sha)
    ck("a workflow without the job has no steps", job_steps("jobs:\n  other:\n    steps: []\n") == [])
    ck("a job with no steps key, last in its file, has no steps",
       job_steps(f"jobs:\n  {JOB}:\n    runs-on: x\n") == [])
    last = job_steps(f"jobs:\n  {JOB}:\n    steps:\n      - name: L\n        id: l\n"
                     "        run: |\n          echo one\n          echo two\n")
    ck("a job last in its file, steps: right under its header, keeps its last block run",
       [(x.id, x.run) for x in last] == [("l", "echo one\necho two\n")])
    ck("gated steps are those whose if reads their own scope output",
       gated_ids(steps) == ["a", "b", "slow"])
    ck("a consistent job has no wiring gap (null control)", wiring_gaps(steps) == [])
    ck("a run step with no gate is named",
       any(g.startswith("UNGATED step 'A'") for g in
           wiring_gaps(job_steps(wf.replace("        if: steps.scope.outputs.a == 'true'\n", "")))))
    ck("a launcher start without its sel guard is named",
       wiring_gaps(job_steps(wf.replace("sel slow && ", ""))) == ["UNSELECTED start slow: the "
                                                                    "launcher starts it without `sel slow`"])
    ck("a waiter whose id is not its name is named",
       any(g.startswith("MISNAMED") for g in wiring_gaps(job_steps(wf.replace("id: slow", "id: slo")
                                                                    .replace("outputs.slow", "outputs.slo")))))

    def entry(step, files=(), probes=(), dirs=(), index=False, objects=False):
        return {"run_sha": step.run_sha, "files": list(files), "probes": list(probes),
                "dirs": list(dirs), "index": index, "objects": objects}

    a, b, slow = steps[3], steps[4], steps[5]
    table = {"steps": {
        "a": entry(a, files=["tools/x/a.py", "tests/lane.py"], probes=["tools/x/a.json"]),
        "b": entry(b, files=["tools/x/b.py"], dirs=["dev/governance/rules"]),
        "slow": entry(slow, files=["tools/x/slow.sh"], index=True)}}
    S = lambda *ch: select(list(ch), table, steps)  # noqa: E731
    # The brief's failing test: a diff touching no tools/ file, and no file
    # any step read, selects zero steps.
    plan = S(("M", "dev/programme/delivery/1.md"), ("M", "docs/x.md"))
    ck("a diff touching no tools/ file and no measured read selects zero steps",
       plan == {"mode": "SCOPED", "why": "", "ids": []} and output(plan) == "none"
       and mode_line(plan) == "MODE: SCOPED -- 0 step(s) run")
    ck("a diff touching a file in one step's closure selects that step alone",
       S(("M", "tools/x/b.py"))["ids"] == ["b"])
    ck("... and a file outside tools/ that a step read selects it",
       S(("M", "tests/lane.py"))["ids"] == ["a"])
    ck("an added file at a probed path selects the prober",
       S(("A", "tools/x/a.json"))["ids"] == ["a", "slow"])
    ck("a modified file that is only a probe selects nothing",
       S(("M", "tools/x/a.json"))["ids"] == [])
    ck("an added file in a listed directory selects the lister; the index reader takes any add",
       S(("A", "dev/governance/rules/new.md"))["ids"] == ["b", "slow"])
    ck("a modified file in a listed directory selects only the index reader's add rule: none",
       S(("M", "dev/governance/rules/old.md"))["ids"] == [])
    ck("collapse: a directory whose every tracked file was read is written D/**, "
       "a partly-read one file by file",
       collapse({"a/x", "a/y", "a/s/z", "b/x"}, {"a/x", "a/y", "a/s/z", "b/x", "b/y"})
       == ["a/**", "b/x"])
    ck("covers: D/** covers a file under D, added later too, and not a sibling of D",
       covers(["a/**"], "a/s/new") and not covers(["a/**"], "ab/x") and covers(["b/x"], "b/x"))
    ck("a modified file under a collapsed directory selects the reader",
       select([("M", "dev/governance/rules/x.md")],
              {"steps": {**table["steps"], "b": entry(b, files=["dev/governance/**"])}},
              steps)["ids"] == ["b"])
    ck("a step that read the object store takes every diff",
       select([("M", "docs/x.md")], {"steps": {**table["steps"], "a": entry(a, objects=True)}},
              steps)["ids"] == ["a"])
    ck("a new tools/ file with no recorded closure runs every step",
       S(("A", "tools/x/new.py"))["mode"] == "FULL")
    ck("... even under a directory a step read whole (D/** names no file D did not hold)",
       select([("A", "tools/x/new.py")], {"steps": {**table["steps"], "b": entry(b, files=["tools/**"])}},
              steps)["mode"] == "FULL")
    for gate in sorted(GATE_FILES):
        ck(f"a gate file runs every step: {gate}", S(("M", gate))["mode"] == "FULL")
    ck("an unreadable table runs every step (fail closed)",
       select([("M", "docs/x.md")], None, steps)["ids"] == ["a", "b", "slow"])
    ck("a table missing a step is stale: every step",
       select([("M", "docs/x.md")], {"steps": {k: v for k, v in table["steps"].items() if k != "b"}},
              steps)["mode"] == "FULL")
    ck("a table whose run_sha lags the workflow is stale: every step",
       select([("M", "docs/x.md")], {"steps": {**table["steps"], "a": {**table["steps"]["a"],
                                                                       "run_sha": "0"}}},
              steps)["mode"] == "FULL")
    ck("an empty diff runs every step (fail closed)", S()["mode"] == "FULL" and output(S()) == "all")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.json"
        p.write_text("{not json")
        ck("a table that does not parse loads as None", load_table(p) is None)
        p.write_text(json.dumps({"steps": {"a": []}}))
        ck("a table whose entries are not objects loads as None", load_table(p) is None)

    # Folding: a synthetic strace log over a throwaway tree, every git call in
    # it under the shared helper's environment (tests/throwaway_git.py).
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init
    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
        root = Path(os.path.realpath(td))
        for f in ("tools/x/a.py", "tools/x/lib.py", "dev/governance/rules/r.md", "tests/lane.py"):
            (root / f).parent.mkdir(parents=True, exist_ok=True)
            (root / f).write_text("x\n")
        (root / "tools/x/__pycache__").mkdir()
        (root / "tools/x/__pycache__/lib.cpython-312.pyc").write_text("")
        subprocess.run(["git", "add", "."], cwd=root, env=throwaway_git_init(root, "-q"), check=True)
        g = root / ".git"
        log = "\n".join([
            f'10 execve("{root}/tools/x/a.py", ["a.py"], 0x0 /* 3 vars */) = 0',
            f'10 openat(AT_FDCWD<{root}>, "tools/x/lib.py", O_RDONLY|O_CLOEXEC) = 3<{root}/tools/x/lib.py>',
            f'11 openat(AT_FDCWD<{root}>, "tests/lane.py", O_RDONLY <unfinished ...>',
            f'10 newfstatat(AT_FDCWD<{root}>, "tools/x/a.json", 0x7ff, 0) = -1 ENOENT (No such file)',
            f'11 <... openat resumed>) = 4<{root}/tests/lane.py>',
            f'10 openat(AT_FDCWD<{root}>, "dev/governance/rules", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 5<{root}/dev/governance/rules>',
            f'10 openat(AT_FDCWD<{root}>, "tools/x/__pycache__/lib.cpython-312.pyc", O_RDONLY) = 6<{root}/tools/x/__pycache__/lib.cpython-312.pyc>',
            f'12 openat(AT_FDCWD<{root}>, ".git/index", O_RDONLY) = 7<{g}/index>',
            f'12 newfstatat(5<{root}/dev/governance/rules>, "", {{}}, AT_EMPTY_PATH) = 0',
            '12 openat(AT_FDCWD</tmp>, "/etc/passwd", O_RDONLY) = 8</etc/passwd>',
        ])
        tracked, tdirs = _tracked(root)
        got = fold_trace(log.splitlines(), root, tracked, tdirs, g, g)
        ck("fold: opens and execs of tracked files are files, a resumed open joined",
           got["files"] == {"tools/x/a.py", "tools/x/lib.py", "tests/lane.py"})
        ck("fold: a failed stat is a probe, an fd's own stat and an outside path are nothing",
           got["probes"] == {"tools/x/a.json"})
        ck("fold: a listed tracked directory is a dir", got["dirs"] == {"dev/governance/rules"})
        junk = fold_trace([
            f'9 newfstatat(AT_FDCWD<{root}>, "{n}", 0x1, 0) = -1 ENOENT (x)' for n in (
                "pipe:[123]", "HEAD:tools/x/a.py", "abc...HEAD", "abc^1", ".merge_file_Xy12",
                "objects/00/abcd", "tools/nodir/f.json", ".git", "d2e4d2d10cfe15b9ec51c36422029718e8367f1c",
                "tools/x/new.json")], root, tracked, tdirs, g, g)
        ck("fold: strings that name no file are not probes; a name in a tracked directory is",
           junk["probes"] == {"tools/x/new.json"})
        ck("fold: the index open is flagged, no object read", got["index"] and not got["objects"])
        got2 = fold_trace([f'9 openat(AT_FDCWD<{root}>, ".git/objects/pack/p.pack", O_RDONLY) = 3<{g}/objects/pack/p.pack>'],
                          root, tracked, tdirs, g, g)
        ck("fold: an object-store open is flagged and names no file",
           got2["objects"] and not got2["files"])
        got3 = fold_trace([
            '9 execve("/usr/bin/git", ["git", "-C", "/r", "grep", "-l", "x"], 0x0 /* 1 var */) = 0',
            f'9 openat(AT_FDCWD<{root}>, ".git/objects/pack/p.pack", O_RDONLY) = 3<{g}/objects/pack/p.pack>'],
            root, tracked, tdirs, g, g)
        ck("fold: a worktree git command (grep) opening the object store does not flag it",
           not got3["objects"])
        got4 = fold_trace([
            '9 execve("/usr/bin/git", ["git", "show", "HEAD:x"], 0x0 /* 1 var */) = 0',
            f'9 openat(AT_FDCWD<{root}>, ".git/objects/pack/p.pack", O_RDONLY) = 3<{g}/objects/pack/p.pack>'],
            root, tracked, tdirs, g, g)
        ck("fold: ... and `git show` opening it does (null control), naming the subcommand",
           got4["objects"] and got4["git"] == {"show"} and got3["git"] == set())
        link = Path(td + "-link")
        link.symlink_to(root)
        try:
            via = fold_trace([
                f'9 openat(AT_FDCWD<{root}>, "tools/x/a.py", O_RDONLY) = 3<{root}/tools/x/a.py>',
                f'9 newfstatat(AT_FDCWD<{link}>, "tools/x/b.json", 0x1, 0) = -1 ENOENT (x)'],
                link, tracked, tdirs, g, g)
            ck("fold: a root reached through a symlink takes resolved and unresolved paths alike",
               via["files"] == {"tools/x/a.py"} and via["probes"] == {"tools/x/b.json"})
        finally:
            link.unlink()
        # The mutant the brief names: a table that omits a file a step reads
        # is shown red by the drift check; the full table is clean.
        wf2 = wf.replace("tools/x/a.py --self-test", "tools/x/a.py --self-test ")
        st2 = job_steps(wf2)
        measured = {"a": {**entry(st2[3], files=sorted(got["files"]), probes=sorted(got["probes"]),
                                  dirs=sorted(got["dirs"]), index=True)},
                    "b": entry(st2[4]), "slow": entry(st2[5])}
        full_table = {"steps": json.loads(json.dumps(measured))}
        refuse, _ = drift(full_table, measured, st2)
        ck("drift: a table naming every measured read refuses nothing (null control)", refuse == [])
        short = json.loads(json.dumps(full_table))
        short["steps"]["a"]["files"].remove("tests/lane.py")
        refuse, _ = drift(short, measured, st2)
        ck("drift: a table that omits a file a step reads is refused, naming it",
           refuse == ["UNDER-SCOPED step a: files misses ['tests/lane.py']"])
        short = json.loads(json.dumps(full_table))
        short["steps"]["a"]["index"] = False
        ck("drift: a table that drops a flag the run set is refused",
           drift(short, measured, st2)[0] == ["UNDER-SCOPED step a: it read the index, the table says not"])
        short = json.loads(json.dumps(full_table))
        del short["steps"]["b"]
        ck("drift: a gated step with no entry is refused",
           drift(short, measured, st2)[0] == ["UNRECORDED step b: the table has no entry"])
        over = json.loads(json.dumps(full_table))
        over["steps"]["b"]["files"].append("tools/x/gone.py")
        r, n = drift(over, measured, st2)
        ck("drift: an over-scoped entry is a note, not a refusal", r == [] and len(n) == 1)
        coll = json.loads(json.dumps(full_table))
        coll["steps"]["a"]["files"] = ["tools/**", "tests/lane.py"]
        ck("drift: a collapsed D/** entry covers the files measured under D",
           drift(coll, measured, st2)[0] == [])
        many = json.loads(json.dumps(measured))
        many["a"]["files"] = [f"tools/x/m{i}.py" for i in range(9)]
        r9 = drift(full_table, many, st2)[0]
        many["a"]["files"] = many["a"]["files"][:8]
        r8 = drift(full_table, many, st2)[0]
        ck("drift: nine misses name eight and count the ninth, eight name all eight",
           len(r9) == 1 and r9[0].endswith("(+1 more)") and len(r8) == 1 and "more)" not in r8[0])
        pm = json.loads(json.dumps(measured))
        pm["a"]["probes"] += ["tools/x/gone.json", "dev/governance/rules/new.md"]
        pm["a"]["dirs"] += ["docs"]
        ck("drift: a new probe and a new listed directory are refused; a probe under a listed dir is not",
           drift(full_table, pm, st2)[0] == ["UNDER-SCOPED step a: probes misses ['tools/x/gone.json']",
                                             "UNDER-SCOPED step a: dirs misses ['docs']"])
        od = json.loads(json.dumps(full_table))
        od["steps"]["a"]["dirs"] += ["docs"]
        od["steps"]["a"]["files"] += ["ab/**"]
        om = json.loads(json.dumps(measured))
        om["a"]["files"] += ["abc/x.py"]
        ck("drift: a directory and a D/** no longer measured are notes (ab/** does not cover abc/x.py)",
           drift(od, om, st2) == (["UNDER-SCOPED step a: files misses ['abc/x.py']"],
                                  ["over-scoped step a: 1 files no longer measured",
                                   "over-scoped step a: 1 dirs no longer measured"]))
        sa = json.loads(json.dumps(full_table))
        sa["steps"]["a"]["run_sha"] = "0"
        sa["steps"]["zz"] = {}
        ck("drift: a lagging run_sha and an entry no gated step has are refused",
           drift(sa, measured, st2)[0] == ["STALE step a: its run text changed since the record",
                                           "EXTRA entry zz: no gated step has that id"])
        ck("drift: no table is refused", drift(None, measured, st2)[0] == ["UNREADABLE the committed table"])
        ck("drift: a step this run did not trace is refused",
           drift(full_table, {k: v for k, v in measured.items() if k != "slow"}, st2)[0]
           == ["UNMEASURED step slow: this run left no trace of it"])

    # The edges a seat's run reaches but the cases above do not.
    ck("a duplicated step id is named", "DUPLICATE id a" in wiring_gaps(
        job_steps(wf.replace("        id: b\n", "        id: a\n"))))
    ck("a launcher start no step waits on is named", "UNREAD start lone: no step waits on it" in wiring_gaps(
        job_steps(wf.replace("sel slow && bg_start slow", "sel lone && bg_start lone"))))
    ck("mode lines: FULL carries its reason, SCOPED its count",
       mode_line({"mode": "FULL", "why": "w", "ids": ["a"]}) == "MODE: FULL -- every step runs (w)"
       and mode_line({"mode": "SCOPED", "why": "", "ids": ["a", "b"]}) == "MODE: SCOPED -- 2 step(s) run"
       and output({"mode": "SCOPED", "why": "", "ids": ["a", "b"]}) == "a b")
    ck("ancestors run from the parent up to the root, once each",
       _ancestors("a/b/c") == ["a/b", "a", "."] and _ancestors("c") == ["."])
    ck("collapse takes a two-file directory read whole, not a one-file one",
       collapse({"a/x", "a/y", "c/z"}, {"a/x", "a/y", "c/z"}) == ["a/**", "c/z"])
    ck("compact_probes drops a probe under a listed directory and keeps the rest",
       compact_probes({"d/p", "e/p", "f/**"}, {"d"}, {"e/q"}) == ["e/p", "f/**"])
    ck("an undecodable escape is kept as written", _unescape("\\x4") == "\\x4")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.json"
        p.write_text(json.dumps({"steps": {"a": {"files": []}}}))
        ck("a well-formed table loads", load_table(p) == {"steps": {"a": {"files": []}}})

    # selection end to end over a throwaway repository: the prelude's entry.
    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
        root = Path(os.path.realpath(td))
        env = throwaway_git_init(root, "-q")
        git = lambda *a: subprocess.run(["git", *a], cwd=root, env=env, check=True,  # noqa: E731
                                        capture_output=True, text=True).stdout.strip()
        (root / WORKFLOW).parent.mkdir(parents=True)
        (root / WORKFLOW).write_text(wf)
        (root / TABLE).parent.mkdir(parents=True)
        (root / TABLE).write_text(json.dumps(table))
        for f in ("tools/x/b.py", "docs/old.md"):
            (root / f).parent.mkdir(parents=True, exist_ok=True)
            (root / f).write_text("1\n")
        git("add", "-A"); git("commit", "-qm", "base")
        base = git("rev-parse", "HEAD")
        (root / "tools/x/b.py").write_text("2\n")
        (root / "docs/new.md").write_text("n\n")
        (root / "docs/old.md").unlink()
        git("add", "-A"); git("commit", "-qm", "head")
        ck("diff_changes reads status and path, one row per file",
           sorted(diff_changes(base, "HEAD", root)) ==
           [("A", "docs/new.md"), ("D", "docs/old.md"), ("M", "tools/x/b.py")])
        ck("diff_changes is None when git cannot diff", diff_changes("nosuchref", "HEAD", root) is None)
        ck("selection: the PR's diff picks its steps (b, and the index reader on the add)",
           selection(base, "HEAD", root) == "b slow")
        ck("selection: a base git cannot resolve runs every step", selection("nosuchref", "HEAD", root) == "all")
        ck("selection: with no workflow, every step", selection(base, "HEAD", root / "nowhere") == "all")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["select", "--base", base, "--head", "HEAD"], root)
            main(["select", "--base", "nosuchref"], root)
        ck("select --base/--head reads the diff; a base git cannot diff is FULL",
           out.getvalue().startswith("MODE: SCOPED -- 2 step(s) run\n  run b\n  run slow\n")
           and "MODE: FULL -- every step runs (git cannot diff)" in out.getvalue())
        gd, cd = _git_dirs(root)
        ck("git dirs: a plain repository's git dir is its common dir", gd == cd == root / ".git")
        git("worktree", "add", "-q", str(root / "wt2"), base)
        gd2, cd2 = _git_dirs(root / "wt2")
        ck("git dirs: a linked worktree's git dir is its own, its common dir the main one",
           gd2 == root / ".git" / "worktrees" / "wt2" and cd2 == root / ".git")

    # trace lines strace prints that are no syscall, a resume with no start,
    # and an open through an undecorated fd, which only the result names.
    with tempfile.TemporaryDirectory() as td:
        root = Path(os.path.realpath(td))
        ev = list(trace_events([
            "strace: Process 7 attached",
            '8 <... openat resumed>) = 3</x>',
            f'9 openat(3, "lib.py", O_RDONLY) = 4<{root}/tools/x/lib.py>']))
        ck("trace_events skips non-syscall lines and orphan resumes, and takes an open's result path",
           [(e[1], e[2]) for e in ev] == [("openat", f"{root}/tools/x/lib.py")])

    # The recorder end to end, over a throwaway repository: the CI wrapper,
    # strace, a detached self-test attributed to its waiter, the fold, the
    # table, then the drift check and the CLI over it. Needs strace (Linux).
    lib = ("bg_run() { if bash tools/ci/selftest_step.sh --as \"$1\" \"${@:2}\" > \"$RUNNER_TEMP/$1.log\" 2>&1; "
           "then echo 0 > \"$RUNNER_TEMP/$1.rc\"; else echo 1 > \"$RUNNER_TEMP/$1.rc\"; fi; }\n"
           "sel() { grep -qx -- \"$1\" \"$RUNNER_TEMP/selftest-scope.txt\"; }\n")
    e2e = (f"jobs:\n  {JOB}:\n    steps:\n"
           "      - name: Launch\n        id: launch\n        run: |\n"
           + "".join(f"          {x}\n" for x in lib.splitlines()) +
           "          ! sel slow || bg_run slow cat tools/x/slow.sh\n"
           "      - name: A\n        id: a\n        if: steps.scope.outputs.a == 'true'\n        run: |\n"
           "          cat tools/x/a.py > /dev/null\n          test -f tools/x/maybe.json || true\n"
           "          ls docs > /dev/null\n"
           "      - name: Slow\n        id: slow\n        if: steps.scope.outputs.slow == 'true'\n"
           "        run: |\n          bg_wait() { test \"$(cat \"$RUNNER_TEMP/$1.rc\")\" = 0; }\n"
           "          bg_wait slow\n")
    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
        root = Path(os.path.realpath(td))
        env = throwaway_git_init(root, "-q")
        for rel, body in ((WORKFLOW, e2e), ("tools/x/a.py", "a\n"), ("tools/x/slow.sh", "s\n"),
                          ("docs/d.md", "d\n"), (WRAPPER, wrapper.read_text())):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(body)
        subprocess.run(["git", "add", "-A"], cwd=root, env=env, check=True)
        if shutil.which("strace") is None or _traced():
            print("  skip the recorder end to end: no strace here, or this run is itself traced")
        else:
            ns = _index_path(root).stat().st_mtime_ns
            os.utime(root / "tools/x/a.py", ns=(ns, ns))
            racy_before = racy_entries(root)
            out = io.StringIO()
            scratch, tempfile.tempdir = tempfile.tempdir, str(root.parent / f"{root.name}-tmp")
            os.makedirs(tempfile.tempdir)
            try:
                with contextlib.redirect_stdout(out):
                    rc = main(["record"], root)
                left = os.listdir(tempfile.tempdir)
            finally:
                shutil.rmtree(tempfile.tempdir, ignore_errors=True)
                tempfile.tempdir = scratch
            t = load_table(root / TABLE) or {"steps": {}}
            a_e, slow_e = t["steps"].get("a", {}), t["steps"].get("slow", {})
            ck(f"record: a traced run of the job writes one entry per gated step (rc={rc})",
               rc == 0 and sorted(t["steps"]) == ["a", "slow"])
            ck("record: a step's open is a file, its failed test -f a probe, its ls a dir",
               "tools/x/a.py" in a_e.get("files", ()) and "tools/x/maybe.json" in a_e.get("probes", ())
               and "docs" in a_e.get("dirs", ()) and a_e.get("run_sha") == job_steps(e2e)[1].run_sha)
            ck("record: a detached self-test's reads are its waiter's",
               "tools/x/slow.sh" in slow_e.get("files", ()) and "tools/x/slow.sh" not in a_e.get("files", ()))
            ck("record: it leaves no trace directory behind", left == [])
            ck("record: it settles a racy index before tracing (racy before, none after)",
               "tools/x/a.py" in racy_before and racy_entries(root) == [])
            part = root / "part.json"
            part.write_text(json.dumps({"steps": {"slow": {"run_sha": "old", "files": [], "probes": [],
                                                           "dirs": [], "index": False, "objects": False}}}))
            with contextlib.redirect_stdout(io.StringIO()):
                rc1 = main(["record", "--step", "a", "--out", str(part)], root)
            pt = load_table(part) or {"steps": {}}
            ck("record --step --out: the step is re-measured into that file, the other entries kept",
               rc1 == 0 and pt["steps"].get("slow", {}).get("run_sha") == "old"
               and "tools/x/a.py" in pt["steps"].get("a", {}).get("files", ()))
            buf, err = io.StringIO(), io.StringIO()
            path, os.environ["PATH"] = os.environ["PATH"], ""
            try:
                with contextlib.redirect_stderr(err):
                    rc_ns = main(["record"], root)
            finally:
                os.environ["PATH"] = path
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc_unk = main(["record", "--step", "nosuch"], root)
                (root / WORKFLOW).write_text(e2e.replace("cat tools/x/a.py > /dev/null", "false"))
                rc_fail = main(["record", "--step", "a", "--out", str(root / "f.json")], root)
                (root / WORKFLOW).write_text(e2e.replace("! sel slow || ", ""))
                rc_gap = main(["record", "--out", str(root / "g.json")], root)
                (root / WORKFLOW).write_text(e2e)
            ck("record refuses with no strace (2), an unknown step (2), an inconsistent job (1), "
               "and fails a failing step (1), naming it",
               (rc_ns, rc_unk, rc_gap, rc_fail) == (2, 2, 1, 1) and "needs strace" in err.getvalue()
               and "no gated step ['nosuch']" in err.getvalue() and "UNSELECTED start slow" in err.getvalue()
               and "1 failed ['a']" in buf.getvalue() and "FAIL" in buf.getvalue())
            probe = ("import sys; sys.path.insert(0, sys.argv[1]); import selftest_scope as s; "
                     "print(s._traced())")
            seen = [subprocess.run(pre + [sys.executable, "-I", "-c", probe, str(ROOT / "tools/ci")],
                                   capture_output=True, text=True).stdout.strip()
                    for pre in ([], ["strace", "-f", "-qq", "-o", os.devnull])]
            ck("_traced: False untraced, True under strace", seen == ["False", "True"])
        # Needs no strace and no freedom from a tracer: the stub is the tracer.
        hollow = root.parent / f"{root.name}-hollow"   # an strace that writes empty traces
        hollow.mkdir()
        (hollow / "strace").write_text('#!/bin/bash\nwhile [ "$1" != -- ]; do [ "$1" != -o ] || : > "$2"; '
                                       'shift; done; shift; exec "$@"\n')
        (hollow / "strace").chmod(0o755)
        buf, path = io.StringIO(), os.environ["PATH"]
        os.environ["PATH"] = f"{hollow}{os.pathsep}{path}"
        try:
            with contextlib.redirect_stdout(buf):
                rc_e = main(["record", "--out", str(root / "e.json")], root)
        finally:
            os.environ["PATH"] = path
            shutil.rmtree(hollow)
        ck("record: an empty trace fails the record, naming it",
           rc_e == 1 and "EMPTY trace step-a.trace (step a)" in buf.getvalue())
        # The drift check and the CLI over a synthetic trace directory.
        (root / TABLE).parent.mkdir(parents=True, exist_ok=True)
        st3 = job_steps(e2e)
        write_table(root / TABLE, {"a": {"run_sha": st3[1].run_sha, "files": ["tools/x/a.py"], "probes": [],
                                         "dirs": [], "index": False, "objects": False, "git": []},
                                   "slow": {"run_sha": st3[2].run_sha, "files": [], "probes": [], "dirs": [],
                                            "index": False, "objects": False, "git": []}}, root)
        tdir = root / "traces"
        tdir.mkdir()

        def whole(*calls: str) -> str:   # a trace strace -q finished: its first process exited
            return "".join(f"{c}\n" for c in calls) + "5 +++ exited with 0 +++\n"
        (tdir / "step-a.trace").write_text(whole(
            f'5 openat(AT_FDCWD<{root}>, "tools/x/a.py", O_RDONLY) = 3<{root}/tools/x/a.py>'))
        (tdir / "step-slow.trace").write_text(whole('5 execve("/bin/true", ["true"], 0x0 /* 1 var */) = 0'))
        (tdir / "bg-slow.trace").write_text(whole('5 execve("/bin/true", ["true"], 0x0 /* 1 var */) = 0'))
        (tdir / "step-launch.trace").write_text(whole(
            f'5 openat(AT_FDCWD<{root}>, "docs/d.md", O_RDONLY) = 3<{root}/docs/d.md>'))
        folded, broken = fold(tdir, st3, root)
        ck("fold: an ungated step's trace is no entry; a gated one with no trace is absent",
           sorted(folded) == ["a", "slow"] and broken == []
           and sorted(fold(tdir, [x for x in st3 if x.id != "slow"] + [Step("Z", "z",
                      "steps.scope.outputs.z == 'true'", "true\n")], root)[0]) == ["a"])
        # A trace strace left EMPTY or PARTIAL, or a waited-on bg trace that is
        # MISSING, measured less than the step read: refused by name, never
        # folded as a whole measurement (R10-HOTFIX-SELFTEST-SCOPE-HANG).
        keep = (tdir / "bg-slow.trace").read_text()
        for name, body, want in (
                ("bg-slow.trace", None, "MISSING trace bg-slow.trace (step slow)"),
                ("bg-slow.trace", "", "EMPTY trace bg-slow.trace (step slow)"),
                ("bg-slow.trace", "--- SIGCHLD {si_signo=SIGCHLD} ---\n", "EMPTY trace bg-slow.trace (step slow)"),
                ("bg-slow.trace", keep.replace("5 +++ exited with 0 +++\n", ""),
                 "PARTIAL trace bg-slow.trace (step slow)"),
                ("bg-slow.trace", keep.replace("5 +++ exited with 0 +++", "6 +++ exited with 0 +++"),
                 "PARTIAL trace bg-slow.trace (step slow)"),
                ("step-a.trace", "", "EMPTY trace step-a.trace (step a)")):
            was = (tdir / name).read_text()
            if body is None:
                (tdir / name).unlink()
            else:
                (tdir / name).write_text(body)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc_t = main(["check", "--traces", str(tdir)], root)
            ck(f"check: {want.split(' (')[0].lower()} is refused, naming it ({body!r:.20})",
               rc_t == 1 and f"  {want}: " in out.getvalue() and ", 1 refusal(s)" in out.getvalue())
            (tdir / name).write_text(was)
        (tdir / "bg-slow.trace").write_text(keep.replace("5 +++ exited with 0 +++", "5 +++ killed by SIGKILL +++"))
        ck("fold: a first process killed by a signal ended its trace (null control: whole)",
           fold(tdir, st3, root)[1] == [])
        (tdir / "bg-slow.trace").write_text(keep)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc_ok = main(["check", "--traces", str(tdir), "--write", str(root / "m.json")], root)
        ck("check: a table naming every read passes, and --write saves the measurement",
           rc_ok == 0 and "2 gated step(s), 0 refusal(s)" in out.getvalue()
           and (load_table(root / "m.json") or {}).get("steps", {}).get("a", {}).get("files") == ["tools/x/a.py"])
        (tdir / "step-slow.trace").write_text(whole(
            f'5 openat(AT_FDCWD<{root}>, "docs/d.md", O_RDONLY) = 3<{root}/docs/d.md>'))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc_bad = main(["check", "--traces", str(tdir)], root)
        ck("check: a read the table misses fails, naming the step and the file",
           rc_bad == 1 and "UNDER-SCOPED step slow: files misses ['docs/d.md']" in out.getvalue()
           and ", 1 refusal(s)" in out.getvalue())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc_us = main(["static"], root)
        ck("static: a job that never settles the index is refused (UNSETTLED)",
           rc_us == 1 and "UNSETTLED job" in out.getvalue())
        settled = e2e.replace("      - name: Launch\n", "      - name: Strace\n        id: strace\n"
                              "        run: python3 -I tools/ci/selftest_scope.py settle\n"
                              "      - name: Launch\n", 1)
        (root / WORKFLOW).write_text(settled)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rcs = [main(["static"], root), main(["ids"], root),
                   main(["select", "--change", "M:tools/x/a.py"], root)]
        ck("static, ids and select over a fresh table",
           rcs == [0, 0, 0] and "0 problem(s)" in out.getvalue() and "a slow\n" in out.getvalue()
           and "MODE: SCOPED -- 1 step(s) run\n  run a\n" in out.getvalue())
        (root / WORKFLOW).write_text(settled.replace("cat tools/x/a.py", "cat tools/x/a.py tools/x/a.py"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc_st = main(["static"], root)
        ck("static: a step whose run text changed since the record is refused",
           rc_st == 1 and "STALE" in out.getvalue())
        (root / TABLE).write_text("{")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc_un = main(["static"], root)
        ck("static: an unreadable table is refused", rc_un == 1 and f"UNREADABLE {TABLE}" in out.getvalue())
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            ck("an unknown command is a usage error", main(["frobnicate"], root) == 2)

    # The wrapper over stub PATHs (no strace needed): which steps it traces,
    # with which flags, and what it does when SELFTEST_TRACE is set and no
    # strace is on PATH (R10-HOTFIX-SELFTEST-SCOPE-HANG: the install step,
    # traced, could not run sudo; the drift step, traced, never finished).
    with tempfile.TemporaryDirectory() as td:
        t = Path(os.path.realpath(td))
        stub, bare = t / "stub", t / "bare"
        for d in (stub, bare):
            d.mkdir()
            for tool in ("bash", "mkdir"):
                (d / tool).symlink_to(shutil.which(tool))
        (stub / "strace").write_text('#!/bin/bash\necho "$*" >> "$RUNNER_TEMP/strace-calls"\n'
                                     'while [ "$1" != -- ]; do shift; done; shift; exec "$@"\n')
        (stub / "strace").chmod(0o755)
        (t / "s.sh").write_text('echo "ran $GITHUB_ACTION"\n')

        def wrap(path_dir: Path, sid: str, *args: str) -> tuple[int, str, str, str]:
            calls = t / "strace-calls"
            calls.unlink(missing_ok=True)
            r = subprocess.run(["bash", str(wrapper), *args], capture_output=True, text=True,
                               env={"PATH": str(path_dir), "RUNNER_TEMP": str(t),
                                    "SELFTEST_TRACE": "1", "GITHUB_ACTION": sid})
            return r.returncode, r.stdout, r.stderr, calls.read_text() if calls.exists() else ""
        untraced = [wrap(stub, sid, str(t / "s.sh")) for sid in UNGATED]
        ck(f"wrapper: the ungated steps {list(UNGATED)} run untraced",
           all(u[0] == 0 and u[1] == f"ran {sid}\n" and u[3] == "" for u, sid in zip(untraced, UNGATED)))
        rc, so, _, calls = wrap(stub, "a", str(t / "s.sh"))
        ck("wrapper: a gated step runs under strace -q into step-ID.trace (null control)",
           rc == 0 and so == "ran a\n" and f"-o {t}/selftest-trace/step-a.trace -- bash" in calls
           and " -q " in f" {calls} " and "-qq" not in calls)
        rc, so, _, calls = wrap(stub, "", "--as", "n", "bash", str(t / "s.sh"))
        ck("wrapper: --as NAME runs under strace -q into bg-NAME.trace",
           rc == 0 and f"-o {t}/selftest-trace/bg-n.trace -- bash" in calls and " -q " in f" {calls} ")
        ran = [wrap(bare, "a", str(t / "s.sh")), wrap(bare, "", "--as", "n", "bash", str(t / "s.sh"))]
        ck("wrapper: no strace on PATH runs the step and the --as command untraced, saying so",
           all(r[0] == 0 and r[1].startswith("ran ") and "no strace is on PATH" in r[2] for r in ran))
        m = re.search(r'^UNTRACED="([^"]*)"$', wrapper.read_text(), re.M)
        ck("wrapper: its UNTRACED list is UNGATED", bool(m) and sorted(m.group(1).split()) == sorted(UNGATED))

    # A racily clean index (R10-HOTFIX-PREPR-READSET): entries whose file
    # mtime second is not before the index's, which a fresh checkout leaves
    # for the files it wrote last. The first index-refreshing git command
    # re-reads each one's content, so those reads land in whichever traced
    # step runs it first (main run 42780661829: prepr's `git status`).
    # `settle` clears them before any step is traced; a racy fixture is its
    # control.
    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
        root = Path(os.path.realpath(td))
        env = throwaway_git_init(root, "-q")
        names = [f"docs/f{n}.md" for n in range(3)]
        for rel in names:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(f"{rel}\n")
        subprocess.run(["git", "add", "-A"], cwd=root, env=env, check=True)

        def make_racy() -> None:   # every file stamped with the index's own mtime
            ns = _index_path(root, env).stat().st_mtime_ns
            for rel in names:
                os.utime(root / rel, ns=(ns, ns))
        make_racy()
        ck("racy_entries: files stamped in the index's own second are named (the control)",
           racy_entries(root, env) == names)
        traced_status = shutil.which("strace") is not None and not _traced()

        def status_reads() -> set[str]:
            log = root.parent / f"{root.name}-status.trace"
            subprocess.run(["strace", "-f", "-q", "-y", "-e", "trace=%file", "-o", str(log),
                            "git", "status", "--porcelain"], cwd=root, env=env, capture_output=True)
            got = fold_trace(log.read_text().splitlines(), root, set(names), {"docs"}, *_git_dirs(root))
            log.unlink()
            return got["files"]
        if traced_status:
            make_racy()
            ck("a git status over that racy index opens every racy file (the control)",
               status_reads() == set(names))
            make_racy()
        rc = settle_index(root, env)
        ck(f"settle: no index entry is left racily clean (rc={rc})", rc == 0 and racy_entries(root, env) == [])
        if traced_status:
            ck("and a git status after it opens no tracked file", status_reads() == set())
        else:
            print("  skip the traced git status over a racy index: no strace here, or this run is itself traced")
        ck("settle over an index with no racy entry changes nothing (rc 0)", settle_index(root, env) == 0)
        make_racy()
        rc = main(["settle"], root)
        ck(f"the `settle` command settles that racy index (rc={rc}; racy before it, none after)",
           rc == 0 and racy_entries(root, env) == [])

    # The settle call's place in a job (settle_gaps): an untraced step before
    # the first traced one, on a line of its own; the null control first.
    gate = "steps.scope.outputs.a == 'true'"
    call = "python3 -I tools/ci/selftest_scope.py settle\n"

    def job(strace_run: str, a_first: bool = False, after: str = "") -> list[Step]:
        a = Step("A", "a", gate, "x\n" + (call if a_first else ""))
        head = [Step("Choose", "scope", "", "echo\n"), Step("Strace", "strace", "", strace_run)]
        return head + ([a] if a_first else []) + [Step("Launch", "launch", "", "x\n" + after)] + \
            ([] if a_first else [a])
    ck("settle_gaps: an untraced step before the first traced one settling passes (null control)",
       settle_gaps(job("apt\n" + call)) == [])
    ck("settle_gaps: no settle call is refused", settle_gaps(job("apt\n")) != [])
    ck("settle_gaps: a settle whose failure is swallowed is refused",
       settle_gaps(job("apt\n" + call.replace("\n", " || true\n"))) != [])
    ck("settle_gaps: a settle only in a traced (gated) step is refused",
       settle_gaps(job("apt\n", a_first=True)) != [])
    ck("settle_gaps: a settle only in launch, which starts traced steps, is refused",
       settle_gaps(job("apt\n", after=call)) != [])

    # R10-SELFTEST-SCOPE-UNION-GUARD: `record` unions over the committed entry,
    # and the table may not shrink in a diff (the null controls come first).
    def ent(files=(), probes=(), dirs=(), git=(), index=False, objects=False, sha="s"):
        return {"run_sha": sha, "files": list(files), "probes": list(probes), "dirs": list(dirs),
                "git": list(git), "index": index, "objects": objects}
    held = {"steps": {"a": ent(["f1", "f2"], ["p1"], ["d1"], ["rev-list"], True, True),
                      "b": ent(["g1"]), "gone": ent(["h1"])}}
    new_a = ent(["f2", "f3"], ["p2", "f3"], ["d2"], ["add"], False, False, sha="t")
    got = union_record(held, {"a": new_a}, {"a", "b"})
    ck("union_record: recording one step over an entry holding reads the trace lacks keeps them",
       got["a"]["files"] == ["f1", "f2", "f3"] and got["a"]["probes"] == ["p1", "p2"]
       and got["a"]["dirs"] == ["d1", "d2"] and got["a"]["git"] == ["add", "rev-list"]
       and got["a"]["index"] and got["a"]["objects"] and got["a"]["run_sha"] == "t")
    ck("union_record: a step not re-measured is kept, a step the workflow no longer gates is not",
       got["b"] == held["steps"]["b"] and "gone" not in got)
    ck("union_record: with no committed table the measurement is the entry",
       union_record(None, {"a": new_a}, {"a"})["a"]["files"] == ["f2", "f3"])
    pruned, unknown = prune_entries(held, "a", ["files:f1", "index:", "git:rev-list"])
    ck("prune_entries: a named read leaves, nothing else does",
       unknown == [] and pruned["a"]["files"] == ["f2"] and not pruned["a"]["index"]
       and pruned["a"]["git"] == [] and pruned["a"]["objects"] and pruned["b"] == held["steps"]["b"])
    ck("prune_entries: a read the entry does not hold is reported, not ignored",
       prune_entries(held, "a", ["files:nope"])[1] == ["files:nope"]
       and prune_entries(held, "zz", ["files:f1"])[1] == ["no step zz"])
    head_add = {"steps": {**held["steps"], "a": union_entry(held["steps"]["a"], new_a)}}
    ck("shrink_drops: an additive head drops nothing (null control)",
       shrink_drops(held, head_add, set(), {"f1"}) == [])
    head_drop = {"steps": {**held["steps"], "a": ent(["f2"], [], ["d1"], [], True, False)}}
    miss = shrink_drops(held, head_drop, set(), {"f1"})
    ck("shrink_drops: a head entry dropping a file, a probe, a git item and a flag is refused, each named",
       len(miss) == 4 and all("SHRUNK step a" in m for m in miss)
       and any("files" in m for m in miss) and any("probes" in m for m in miss)
       and any("git" in m for m in miss) and any("objects flag" in m for m in miss))
    left = shrink_drops(held, head_drop, {"f1", "p1"}, set())
    ck("shrink_drops: the file and probe drops are exempt for paths the diff deletes, the rest stay",
       len(left) == 2 and any("git" in m for m in left) and any("objects flag" in m for m in left))
    ck("shrink_drops: a git item or a flag is never exempt by deletion",
       len(shrink_drops(held, head_drop, {"f1", "p1", "rev-list"}, set())) == 2)
    ck("shrink_drops: a step removed from the workflow, or a new one, is not a drop",
       shrink_drops(held, {"steps": {"b": held["steps"]["b"]}}, set(), set()) == []
       and shrink_drops({"steps": {}}, held, set(), set()) == [])
    ck("shrink_drops: a file read now through a D/** entry, or a probe now a file, is kept",
       shrink_drops({"steps": {"a": ent(["t/x", "t/y"], ["t/z"])}},
                    {"steps": {"a": ent(["t/**", "t/z"])}}, set(), set()) == [])
    dir_b, dir_h = {"steps": {"a": ent([], [], ["t"])}}, {"steps": {"a": ent()}}
    ck("shrink_drops: a directory whose every file the diff deleted is exempt, one with a survivor is not",
       shrink_drops(dir_b, dir_h, {"t/x"}, set()) == [] and len(shrink_drops(dir_b, dir_h, {"t/x"}, {"t/y"})) == 1)
    glob_b, glob_h = {"steps": {"a": ent(["t/**"])}}, {"steps": {"a": ent()}}
    ck("shrink_drops: a D/** item whose directory the diff emptied is exempt, one with a survivor is not",
       shrink_drops(glob_b, glob_h, {"t/x"}, set()) == [] and len(shrink_drops(glob_b, glob_h, {"t/x"}, {"t/y"})) == 1)
    probe_b, probe_dir = {"steps": {"a": ent([], ["t/q"])}}, {"steps": {"a": ent([], [], ["t"])}}
    ck("shrink_drops: a probe whose directory the head lists is kept, the same head without it is not",
       shrink_drops(probe_b, probe_dir, set(), {"t/x"}) == []
       and len(shrink_drops(probe_b, {"steps": {"a": ent([], [], ["u"])}}, set(), {"t/x"})) == 1)
    ck("shrink_drops: a probe of a path that exists nowhere is still a drop",
       len(shrink_drops(held, {"steps": {"a": ent(["f1", "f2"], [], ["d1"], ["rev-list"], True, True)}},
                        set(), set())) == 1)
    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
        gr = Path(os.path.realpath(td))
        env_g = throwaway_git_init(gr, "-q")

        def gitc(*a):
            return subprocess.run(["git", *a], cwd=gr, env=env_g, check=True, capture_output=True,
                                  text=True).stdout.strip()

        def commit(tbl, rm=()):
            (gr / TABLE).parent.mkdir(parents=True, exist_ok=True)
            (gr / TABLE).write_text(json.dumps(tbl))
            (gr / "f1").write_text("x")
            for r in rm:
                (gr / r).unlink()
            gitc("add", "-A")
            gitc("commit", "-qm", "c")
            return gitc("rev-parse", "HEAD")
        b0 = commit(held)
        commit(head_add)
        ck("shrink_gaps: a committed additive table change passes (null control)", shrink_gaps(gr, b0) == [])
        ck("shrink_gaps: a base the repository cannot diff against is refused, not passed",
           [x[:10] for x in shrink_gaps(gr, "0" * 40)] == ["UNREADABLE"])
        commit(head_drop)
        fx = shrink_gaps(gr, b0)
        ck("shrink_gaps: a committed diff dropping reads is refused",
           len(fx) == 4 and all(x.startswith("SHRUNK step a") for x in fx))
        (gr / "p1").write_text("x")
        gitc("add", "p1")
        gitc("commit", "-qm", "p1")
        b1 = gitc("rev-parse", "HEAD")
        commit(held)
        b1 = gitc("rev-parse", "HEAD")
        commit(head_drop, rm=("f1", "p1"))
        ck("shrink_gaps: the same drops with the paths deleted by the diff leave only git and the flag",
           len(shrink_gaps(gr, b1)) == 2)
        (gr / WORKFLOW).parent.mkdir(parents=True, exist_ok=True)
        (gr / WORKFLOW).write_text(wf)
        out = io.StringIO()
        os.environ["SELFTEST_BASE"] = b1
        try:
            with contextlib.redirect_stdout(out):
                rc_sh = main(["static"], gr)
        finally:
            del os.environ["SELFTEST_BASE"]
        ck("static: the shrink guard is part of it (rc 1, naming the step)",
           rc_sh == 1 and "SHRUNK step a" in out.getvalue())
        ck("shrink_gaps: with no base, or a diff that leaves the table alone, there is nothing to judge",
           shrink_gaps(gr, None) == [] and shrink_gaps(gr, gitc("rev-parse", "HEAD")) == [])
        ck("table_base: the first parent without a named base, the merge base with one",
           table_base(gr, {}) == (gitc("rev-parse", "HEAD^1"), "")
           and table_base(gr, {"SELFTEST_BASE": b0}) == (b0, ""))
        ck("table_base: a named base that does not resolve is a problem, not a base",
           all(table_base(gr, e)[0] is None and table_base(gr, e)[1].startswith(f"UNRESOLVED base {n}")
               for e, n in (({"GITHUB_BASE_REF": "nonesuch"}, "origin/nonesuch"),
                            ({"SELFTEST_BASE": "nonesuch"}, "nonesuch"))))

        def static_at(base: str) -> tuple[int, str]:
            out = io.StringIO()
            os.environ["SELFTEST_BASE"] = base
            try:
                with contextlib.redirect_stdout(out):
                    rc = main(["static"], gr)
            finally:
                del os.environ["SELFTEST_BASE"]
            return rc, out.getvalue()
        rc_ok, out_ok = static_at(gitc("rev-parse", "HEAD"))
        rc_un, out_un = static_at("nonesuch")
        n_ok, n_un = (o.count("\n  ") + o.startswith("  ") for o in (out_ok, out_un))
        ck(f"static: a base that does not resolve adds one problem line ({n_ok} -> {n_un}, rc {rc_un}); "
           f"one that resolves adds none (null control: the fixture's own lines only)",
           "UNRESOLVED" not in out_ok and "SHRUNK" not in out_ok and f"{n_ok} problem(s)" in out_ok
           and rc_un == 1 and "UNRESOLVED base nonesuch" in out_un and n_un == n_ok + 1
           and f"{n_un} problem(s)" in out_un)

        # The prune CLI, the one sanctioned way a read leaves the table: it
        # writes the table, and refuses a drop the entry does not hold with the
        # file left byte-identical (the valid drop beside it is not applied).
        (gr / TABLE).write_text(json.dumps(held))
        before = (gr / TABLE).read_bytes()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc_unk = main(["prune", "--step", "a", "--drop", "files:f2", "--drop", "files:nope"], gr)
            rc_nostep = main(["prune", "--step", "zz", "--drop", "files:f1"], gr)
        ck("prune: an unknown drop or step is refused (rc 1), naming it, the table byte-identical",
           rc_unk == 1 and rc_nostep == 1 and "files:nope" in err.getvalue()
           and "no step zz" in err.getvalue() and (gr / TABLE).read_bytes() == before)
        rc_pr = main(["prune", "--step", "a", "--drop", "files:f2", "--drop", "objects:"], gr)
        after = load_table(gr / TABLE)
        ck("prune: a held drop writes the table, less exactly that read",
           rc_pr == 0 and after is not None and after["steps"]["a"]["files"] == ["f1"]
           and not after["steps"]["a"]["objects"] and after["steps"]["a"]["index"]
           and after["steps"]["a"]["dirs"] == ["d1"] and after["steps"]["b"]["files"] == ["g1"])

    # The live table names no landed retired path (tests/layout.py's guard
    # refuses a new reference to one, and a diff re-adding one), and the
    # list it is checked against is not empty (the check's own precondition).
    if not (ROOT / ".git").exists():
        print("  skip the live table's retired-path check: no git work tree here (a `git archive` copy)")
    else:
        gone = [r.rstrip("/") for r in retired_paths(ROOT)]
        live_t = load_table(ROOT / TABLE) or {"steps": {}}
        named = sorted({p for e in live_t["steps"].values() for k in ("files", "probes", "dirs")
                        for p in e.get(k, ()) if any(p == r or p.startswith(r + "/") for r in gone)})
        ck(f"the committed table names no landed retired path ({len(gone)} retired; named: {named[:3]})",
           bool(gone) and named == [] and retired_paths(Path(tempfile.gettempdir())) == [])

    # The live job: its gating is consistent (the seat's own null control).
    live = job_steps(workflow.read_text())
    ck(f"the live job parses ({len(live)} steps) and its gating is consistent",
       len(live) > 3 and wiring_gaps(live) == [])
    ck("the live job settles the index in an untraced step before its first traced one",
       settle_gaps(live) == [])
    print(f"selftest_scope self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str], root: Path = ROOT) -> int:
    opts = dict(zip(argv[1::2], argv[2::2]))
    if argv[:1] == ["--self-test"] and len(argv) % 2 == 1 and set(opts) <= {"--wrapper", "--workflow"}:
        rc = self_test(Path(opts.get("--wrapper", ROOT / WRAPPER)).resolve(),
                       Path(opts.get("--workflow", ROOT / WORKFLOW)).resolve())
        return rc if isinstance(rc, int) else 1  # a self-test that returned nothing did not pass
    if argv == ["ids"]:
        print(" ".join(gated_ids(workflow_steps(root))))
        return 0
    if argv == ["static"]:
        return static_check(root)
    if argv == ["settle"]:
        return settle_index(root)
    if argv[:1] == ["select"] and ("--base" in argv or "--change" in argv):
        steps = workflow_steps(root)
        if "--change" in argv:          # a hypothetical diff: STATUS:PATH ...
            changes = [tuple(argv[k + 1].split(":", 1)) for k, a in enumerate(argv) if a == "--change"]
        else:
            base = argv[argv.index("--base") + 1]
            head = argv[argv.index("--head") + 1] if "--head" in argv else "HEAD"
            changes = diff_changes(base, head, root)
        plan = select(changes or [], load_table(root / TABLE), steps) if changes is not None else \
            {"mode": "FULL", "why": "git cannot diff", "ids": gated_ids(steps)}
        print(mode_line(plan))
        for i in plan["ids"]:
            print(f"  run {i}")
        return 0
    if argv[:1] == ["record"]:
        only = [argv[k + 1] for k, a in enumerate(argv) if a == "--step"]
        out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else root / TABLE
        return record(root, only or None, out.resolve())
    if argv[:1] == ["prune"] and "--step" in argv and "--drop" in argv:
        table = load_table(root / TABLE)
        step = argv[argv.index("--step") + 1]
        drops = [argv[k + 1] for k, a in enumerate(argv) if a == "--drop"]
        if table is None:
            print(f"selftest_scope: UNREADABLE {TABLE}", file=sys.stderr)
            return 1
        entries, unknown = prune_entries(table, step, drops)
        if unknown:
            print(f"selftest_scope: not in the table, nothing written: {unknown}", file=sys.stderr)
            return 1
        write_table(root / TABLE, entries, root)
        return 0
    if argv[:1] == ["check"] and "--traces" in argv:
        write = Path(argv[argv.index("--write") + 1]) if "--write" in argv else None
        return check_cli(Path(argv[argv.index("--traces") + 1]), write, root)
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
