#!/usr/bin/env python3
"""Scope governance.yml's instrument-self-tests steps by their measured read sets.

    python3 -I tools/ci/selftest_scope.py select --base REF [--head REF]
    python3 -I tools/ci/selftest_scope.py ids
    python3 -I tools/ci/selftest_scope.py record [--step ID]... [--out PATH]
    python3 -I tools/ci/selftest_scope.py check --traces DIR [--write PATH]
    python3 -I tools/ci/selftest_scope.py --self-test

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

import hashlib
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
        if not steps:
            continue
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
    known_files = set().union(*(set(e.get("files", ())) for e in table["steps"].values()))
    known = known_files | set().union(*(set(e.get("probes", ())) for e in table["steps"].values()))
    new = sorted(p for st, p in changes if st == "A" and p.startswith(NEW_FILE_PREFIX)
                 and p not in known and not covers(known_files, p))
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
    changes = diff_changes(base, head, root)
    if changes is None:
        return "all"
    return output(select(changes, load_table(root / TABLE), steps))


# ---------------------------------------------------------------------------
# folding traces

_CALL = re.compile(r"^(?P<pid>\d+)\s+(?P<rest>.*)$")
_STR = r'"((?:[^"\\]|\\.)*)"'
_FD = r"(?:AT_FDCWD|-?\d+)(?:<([^>]*)>)?"
_AT = re.compile(rf"^(openat2?|newfstatat|fstatat64|statx|faccessat2?|readlinkat|execveat)\({_FD},\s*{_STR}")
_PLAIN = re.compile(rf"^(open|creat|stat|lstat|stat64|lstat64|access|readlink|execve)\({_STR}")
_RET = re.compile(r"\)\s+=\s+(-?\d+)(?:<([^>]*)>)?(?:\s|$)")
_OPENS = ("openat", "openat2", "open", "creat")
_EXECS = ("execve", "execveat")


def _unescape(s: str) -> str:
    try:
        return bytes(s, "utf-8").decode("unicode_escape").encode("latin-1").decode("utf-8", "replace")
    except (UnicodeDecodeError, ValueError):
        return s


def _git_dirs(root: Path) -> tuple[Path, Path]:
    def rev(arg):
        r = subprocess.run(["git", "rev-parse", arg], cwd=root, capture_output=True, text=True)
        return Path(os.path.realpath(r.stdout.strip() if r.returncode == 0 else root / ".git"))
    return rev("--absolute-git-dir"), Path(os.path.realpath(root / rev("--git-common-dir")))


def trace_events(text: str):
    """(pid, call, resolved absolute path, ok, line) per relevant syscall line,
    joining a call strace split into `<unfinished ...>` and `resumed`."""
    pending: dict[str, str] = {}
    for line in text.splitlines():
        m = _CALL.match(line)
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
        elif raw.startswith("/"):
            path = raw
        else:
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


_NOT_A_NAME = re.compile(r"[:\[\]^~*?]|\.\.\.|^\.merge_file_")


def probe_path(rel: str, tracked_dirs: set[str]) -> bool:
    """Whether a probed path is one a diff could add or delete: under a
    tracked directory, not a cache, and a file name rather than a string a
    process handed to a path syscall (`pipe:[N]`, `REV:path`, `A...B`, git's
    `.merge_file_*` temporaries) -- those differ run to run and name nothing
    (two recordings of one tree, compared step by step)."""
    parts = rel.split("/")
    parent = "/".join(parts[:-1]) or "."
    return (parent in tracked_dirs and "__pycache__" not in parts and "node_modules" not in parts
            and not _NOT_A_NAME.search(parts[-1]))


def _pyc_source(rel: str) -> str:
    m = re.fullmatch(r"(.*/)?__pycache__/([^/]+?)\.[^/.]+(?:\.opt-\d)?\.pyc", rel)
    return f"{m.group(1) or ''}{m.group(2)}.py" if m else rel


def fold_trace(text: str, root: Path, tracked: set[str], tracked_dirs: set[str],
               git_dir: Path, common_dir: Path) -> dict:
    files, probes, dirs = set(), set(), set()
    flags = {"index": False, "objects": False}
    gits: set[str] = set()                # the git subcommands that set `objects`
    real_root = os.path.realpath(root)
    git_cmd: dict[str, str] = {}          # pid -> the git subcommand it exec'd
    for pid, call, path, ok, line in trace_events(text):
        is_dir = "O_DIRECTORY" in line
        if call in _EXECS and ok:
            git_cmd[pid] = _git_subcommand(line)
        real = os.path.realpath(path) if ok else path
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
        if rel == ".git" or rel.startswith(".git/") or "/.git/" in rel:
            continue
        rel = _pyc_source(rel)
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
    if not paths:
        return set()
    r = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"], cwd=root,
                       input="\0".join(sorted(paths)) + "\0", capture_output=True, text=True)
    return {p for p in r.stdout.split("\0") if p}


def fold(trace_dir: Path, steps: list[Step], root: Path = ROOT) -> dict[str, dict]:
    """Each gated step's measured entry: its own trace and its waited-on bg traces."""
    tracked, tracked_dirs = _tracked(root)
    git_dir, common_dir = _git_dirs(root)
    out: dict[str, dict] = {}
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
                continue
            got = fold_trace(src.read_text(errors="replace"), root, tracked, tracked_dirs,
                             git_dir, common_dir)
            for k in ("files", "probes", "dirs", "git"):
                acc[k] |= got[k]
            for k in ("index", "objects"):
                acc[k] = acc[k] or got[k]
        acc["probes"] -= acc["files"]
        out[s.id] = acc
    ignored = _ignored(root, set().union(*(e["probes"] for e in out.values())) if out else set())
    return {sid: {"run_sha": next(s.run_sha for s in steps if s.id == sid),
                  "files": sorted(e["files"]), "probes": sorted(e["probes"] - ignored),
                  "dirs": sorted(e["dirs"]), "index": e["index"], "objects": e["objects"],
                  "git": sorted(e["git"])}
            for sid, e in out.items()}


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
        have = set(e.get("files", ()))
        miss = sorted(f for f in m["files"] if not covers(have, f))
        if miss:
            refuse.append(f"UNDER-SCOPED step {sid}: files misses {miss[:8]}"
                          + (f" (+{len(miss) - 8} more)" if len(miss) > 8 else ""))
        gone = [f for f in have if not (f.endswith("/**") and any(
            x.startswith(f[:-2]) for x in m["files"])) and f not in set(m["files"])]
        if gone:
            notes.append(f"over-scoped step {sid}: {len(gone)} files no longer measured")
        probes = set(e.get("probes", ()))
        miss = sorted(p for p in m["probes"] if not covers(probes, p)
                      and not any(a in set(e.get("dirs", ())) for a in _ancestors(p)))
        if miss:
            refuse.append(f"UNDER-SCOPED step {sid}: probes misses {miss[:8]}"
                          + (f" (+{len(miss) - 8} more)" if len(miss) > 8 else ""))
        for k in ("dirs",):
            miss = sorted(set(m[k]) - set(e.get(k, ())))
            if miss:
                refuse.append(f"UNDER-SCOPED step {sid}: {k} misses {miss[:8]}"
                              + (f" (+{len(miss) - 8} more)" if len(miss) > 8 else ""))
            extra = set(e.get(k, ())) - set(m[k])
            if extra:
                notes.append(f"over-scoped step {sid}: {len(extra)} {k} no longer measured")
        for k in ("index", "objects"):
            if m[k] and not e.get(k):
                refuse.append(f"UNDER-SCOPED step {sid}: it read the {k}, the table says not")
    for sid in sorted(set(table["steps"]) - set(gated_ids(steps))):
        refuse.append(f"EXTRA entry {sid}: no gated step has that id")
    return refuse, notes


# ---------------------------------------------------------------------------
# recording: the job, replayed through the same wrapper CI uses

def record(root: Path, only: list[str] | None, out: Path) -> int:
    if shutil.which("strace") is None:
        print("selftest_scope: record needs strace (Linux)", file=sys.stderr)
        return 2
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
    measured = fold(tmp / TRACE_DIR, steps, root)
    old = load_table(out)
    entries = dict(old["steps"]) if old and only else {}
    entries.update(measured)
    entries = {k: v for k, v in entries.items() if k in set(gated_ids(steps))}
    write_table(out, entries)
    print(f"selftest_scope: recorded {len(measured)} step(s) into {out}; "
          f"{len(failed)} failed {failed}")
    return 1 if failed else 0


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
    measured = fold(trace_dir, steps, root)
    if write is not None:
        write_table(write, measured)        # this run's measurement, to commit as the table
    refuse, notes = drift(load_table(root / TABLE), measured, steps)
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
    problems = wiring_gaps(steps)
    table = load_table(root / TABLE)
    if table is None:
        problems.append(f"UNREADABLE {TABLE}")
    else:
        why = stale(table, steps)
        if why:
            problems.append(f"STALE {TABLE}: {why} -- re-record the changed step(s) with "
                            f"`python3 {SELF} record --step ID`")
    for p in problems:
        print(f"  {p}")
    print(f"selftest_scope static: {len(gated_ids(steps))} gated step(s), {len(problems)} problem(s)")
    return 1 if problems else 0


# ---------------------------------------------------------------------------

def self_test() -> int:
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
        got = fold_trace(log, root, tracked, tdirs, g, g)
        ck("fold: opens and execs of tracked files are files, a resumed open joined",
           got["files"] == {"tools/x/a.py", "tools/x/lib.py", "tests/lane.py"})
        ck("fold: a failed stat is a probe, an fd's own stat and an outside path are nothing",
           got["probes"] == {"tools/x/a.json"})
        ck("fold: a listed tracked directory is a dir", got["dirs"] == {"dev/governance/rules"})
        junk = fold_trace("\n".join(
            f'9 newfstatat(AT_FDCWD<{root}>, "{n}", 0x1, 0) = -1 ENOENT (x)' for n in (
                "pipe:[123]", "HEAD:tools/x/a.py", "abc...HEAD", "abc^1", ".merge_file_Xy12",
                "objects/00/abcd", "tools/x/new.json")), root, tracked, tdirs, g, g)
        ck("fold: strings that name no file are not probes; a name in a tracked directory is",
           junk["probes"] == {"tools/x/new.json"})
        ck("fold: the index open is flagged, no object read", got["index"] and not got["objects"])
        got2 = fold_trace(f'9 openat(AT_FDCWD<{root}>, ".git/objects/pack/p.pack", O_RDONLY) = 3<{g}/objects/pack/p.pack>',
                          root, tracked, tdirs, g, g)
        ck("fold: an object-store open is flagged and names no file",
           got2["objects"] and not got2["files"])
        got3 = fold_trace("\n".join([
            '9 execve("/usr/bin/git", ["git", "-C", "/r", "grep", "-l", "x"], 0x0 /* 1 var */) = 0',
            f'9 openat(AT_FDCWD<{root}>, ".git/objects/pack/p.pack", O_RDONLY) = 3<{g}/objects/pack/p.pack>']),
            root, tracked, tdirs, g, g)
        ck("fold: a worktree git command (grep) opening the object store does not flag it",
           not got3["objects"])
        got4 = fold_trace("\n".join([
            '9 execve("/usr/bin/git", ["git", "show", "HEAD:x"], 0x0 /* 1 var */) = 0',
            f'9 openat(AT_FDCWD<{root}>, ".git/objects/pack/p.pack", O_RDONLY) = 3<{g}/objects/pack/p.pack>']),
            root, tracked, tdirs, g, g)
        ck("fold: ... and `git show` opening it does (null control)", got4["objects"])
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
        ck("drift: a step this run did not trace is refused",
           drift(full_table, {k: v for k, v in measured.items() if k != "slow"}, st2)[0]
           == ["UNMEASURED step slow: this run left no trace of it"])

    # The live job: its gating is consistent (the seat's own null control).
    live = workflow_steps(ROOT)
    ck(f"the live job parses ({len(live)} steps) and its gating is consistent",
       len(live) > 3 and wiring_gaps(live) == [])
    print(f"selftest_scope self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if argv == ["ids"]:
        print(" ".join(gated_ids(workflow_steps())))
        return 0
    if argv == ["static"]:
        return static_check()
    if argv[:1] == ["select"] and "--base" in argv:
        base = argv[argv.index("--base") + 1]
        head = argv[argv.index("--head") + 1] if "--head" in argv else "HEAD"
        steps = workflow_steps()
        changes = diff_changes(base, head)
        plan = select(changes or [], load_table(ROOT / TABLE), steps) if changes is not None else \
            {"mode": "FULL", "why": "git cannot diff", "ids": gated_ids(steps)}
        print(mode_line(plan))
        for i in plan["ids"]:
            print(f"  run {i}")
        return 0
    if argv[:1] == ["record"]:
        only = [argv[k + 1] for k, a in enumerate(argv) if a == "--step"]
        out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else ROOT / TABLE
        return record(ROOT, only or None, out.resolve())
    if argv[:1] == ["check"] and "--traces" in argv:
        write = Path(argv[argv.index("--write") + 1]) if "--write" in argv else None
        return check_cli(Path(argv[argv.index("--traces") + 1]), write)
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
