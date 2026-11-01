#!/usr/bin/env python3
"""The tracked mutant driver: apply one textual edit, run a command, restore.

    python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd '<argv>' [--copy-tree | --in-place]
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

DIFF MODE (R10-MUTANT-RUN-DRIVER, card 4). `--diff base...HEAD` reads the
ADDED lines of the Python files the three-dot diff touches (not under tests/ or
dev/, not inside a multi-line string) and mutates each with five operators:

  GUARD_OFF   `if cond:` / `elif cond:` becomes `if False:`
  RETURN_DEL  `return ...` becomes `pass`
  CMP_BOUND   the first of < <= > >= moves one step (< to <=, >= to >)
  CALL_DEL    a bare `f(...)` statement becomes `pass` (print and _LOGGER calls
              are left alone: they pin no behaviour)
  CONST_SWAP  the first number moves (n to n+1, 0.0 to 1.0) or, with none,
              the first True/False flips

A mutant that does not compile is skipped. The command runs once unedited (rc 3
`BASELINE FAILS` if it fails: nothing is then readable) and once per mutant;
one `SURVIVED file:line OPERATOR  <mutated line>` line is printed per survivor
and nothing for a kill. rc 0 when nothing survived (an empty diff included),
1 on survivors unless `--report-only`. A survivor is answered in the PR body;
an equivalent one still needs a survivor_triage record. `--list` prints the
mutants without running. The command is the group's named self-test or
`python3 tools/audit/seat/features_block.py "<marker>"`.

`--self-test` builds throwaway repositories and runs every arm above.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REFUSE_RC, SURVIVE_RC, BROKEN_RC = 2, 1, 3
OPERATORS = ("GUARD_OFF", "RETURN_DEL", "CMP_BOUND", "CALL_DEL", "CONST_SWAP")
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
def run_cmd(argv: list[str], cwd: Path, timeout: float) -> int:
    """Exit status of the command; a timeout is -1 (a kill: the mutant hangs)."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.Popen(argv, cwd=str(cwd), env=env, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _child.append(p)
    try:
        return p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        _killpg(p)
        p.wait()
        return -1
    finally:
        _child.clear()


def _killpg(p) -> None:
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


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
            for p in _child:
                _killpg(p)
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
    if run_cmd(argv, ws.dir, timeout) != 0:
        print("KILLED NULL", flush=True)
        print("mutant_run: the null mutant was killed, the command fails on the unedited tree", file=sys.stderr)
        return BROKEN_RC
    print("SURVIVED NULL", flush=True)
    for m in spec:
        text = ws.path(m["file"]).read_text(encoding="utf-8")
        rc = ws.apply(m["file"], text.replace(m["old"], m["new"], 1), argv, timeout)
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
    return found


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
            if ws.apply(rel, text, argv, timeout) == 0:
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
    ap.add_argument("--max-mutants", type=int, default=0)
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--path", action="append", default=[], help="diff mode: only files under this prefix (repeatable)")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
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
'''
PINNED = ("from lib import clamp\n"
          "assert clamp(-1, 0, 5) == 0 and clamp(9, 0, 5) == 5 and clamp(3, 0, 5) == 3\n"
          "assert clamp(0, 0, 5) == 0 and clamp(5, 0, 5) == 5\n")
NORM_PINNED = ("from lib import norm\nimport lib\nseen = []\nlib.note = seen.append\n"
               "assert norm(-1) == 0 and norm(0) == 0 and norm(2) == 4 and seen == [0, 2]\n")
LOOSE = "from lib import clamp\nassert clamp(3, 0, 5) == 3\n"


def _self_test() -> int:
    import time
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_init
    fails = checks = 0

    def check(name: str, ok: bool) -> None:
        nonlocal fails, checks
        checks += 1
        fails += not ok
        print(("  ok   " if ok else "  FAIL ") + name)

    tmp = Path(tempfile.mkdtemp(prefix="mutrun-st-"))
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

        def drive(*args, sig=None, watch=None):
            p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--root", str(repo), *args],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=senv, cwd=str(repo))
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
                   f"    pathlib.Path('{flag}').write_text('x'); time.sleep(60)\"")
            rc, out, err = drive("--spec", str(spec), "--cmd", cmd, mode, sig=signal.SIGTERM, watch=flag.exists)
            clean = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", "lib.py"],
                                   capture_output=True, text=True, env=env).stdout == ""
            check(f"SIGTERM mid-mutant ({mode}): rc 143, tree byte-identical, no copy left behind",
                  rc == 143 and clean and (repo / "lib.py").read_text() == LIB and not listing())
            flag.unlink(missing_ok=True)

        # diff mode
        (repo / "lib.py").write_text(LIB2)
        g("commit", "-q", "-am", "add norm")
        rng = f"{base}...HEAD"
        rc, out, _ = drive("--diff", rng, "--list")
        ops = {l.split()[2] for l in out.splitlines() if l.startswith("MUTANT ")}
        check("diff: the added lines yield all five operators", ops == set(OPERATORS))
        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_norm.py")
        check("diff: a self-test that pins the guard, return, bound, call and constant leaves no survivor, rc 0",
              rc == 0 and "SURVIVED" not in out)
        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_loose.py")
        survivors = [l for l in out.splitlines() if l.startswith("SURVIVED ")]
        check("diff: a self-test that does not pin them leaves survivors, rc 1, one line each",
              rc == 1 and len(survivors) >= 5 and {l.split()[2] for l in survivors} == set(OPERATORS))
        rc, out, _ = drive("--diff", rng, "--cmd", "python3 check_loose.py", "--report-only")
        check("diff: --report-only prints the survivors and exits 0", rc == 0 and "SURVIVED" in out)
        rc, out, _ = drive("--diff", rng, "--cmd", 'python3 -c "raise SystemExit(1)"')
        check("diff: a command failing on the unedited tree is BASELINE FAILS, rc 3", rc == 3 and "BASELINE FAILS" in out)
        rc, out, _ = drive("--diff", f"HEAD...HEAD", "--cmd", "python3 check_loose.py")
        check("diff: an empty diff prints no survivor and exits 0 (null control)", rc == 0 and out == "")
        status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True, env=env).stdout
        check("diff: the working tree is clean after every run", status == "" and not listing())
        check("operators: no mutant for a comment, an import or a def, and no CALL_DEL for a log call",
              not any(list(mutate_line(s)) for s in ("# if x < 1:", "import a1", "def f(x=1):"))
              and "CALL_DEL" not in {o for o, _ in mutate_line("    _LOGGER.info(x)")})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"mutant_run self-test: {checks} checks, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(_self_test())
    sys.exit(main(sys.argv[1:]))
