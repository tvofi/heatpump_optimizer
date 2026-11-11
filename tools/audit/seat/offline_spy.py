#!/usr/bin/env python3
"""Run a seat instrument's --self-test and count what it reaches outside.

    python3 -I tools/audit/seat/offline_spy.py <file> [<file> ...]
    python3 -I tools/audit/seat/offline_spy.py --self-test

WHY THIS EXISTS. A self-test is wired into CI only once it is shown to run
offline (R10-SEAT-SELFTESTS-CI): a step that reaches `gh`, the network or a
real remote from a runner either flakes or acts. "It stubs everything" is a
claim; this is the instrument that measures it, and a reviewer re-runs it.

WHAT IT COUNTS, per file, with the file's `--self-test` run from the tree
root under a throwaway HOME and TMPDIR:
  network     a socket connect or DNS lookup from the Python process (refused,
              so it cannot succeed), plus every call of gh, curl, wget, ssh,
              scp or nc found on PATH (refused with exit 97)
  remote_git  a call of the wrapped git that can reach a remote (the
              subcommands push, fetch, pull, ls-remote, clone; remote
              update/show/prune; submodule) whose
              target URL, resolved through the cwd's remotes, is not a
              local path (GIT_STUB below says how each target is read)
  subprocess  process creations from the Python process (Popen, system,
              posix_spawn, spawn*, fork); `n/a` for a shell file, whose every
              `grep` is one, so a count would measure nothing
A file is REFUSED when its self-test exits non-zero or any network or
remote_git call was counted. Where /usr/bin/sandbox-exec exists (macOS), the
run also denies outbound IP and writes outside the temporary directories, so
a client reached by an absolute path, which PATH cannot intercept, still
cannot connect; the line names the backstop that applied.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLIENTS = ("gh", "curl", "wget", "ssh", "scp", "nc")
URL_RE = re.compile(r"(?:https?|ssh|git)://|[\w.-]+@[\w.-]+:")
TIMEOUT_S = 600  # the slowest file measured took under a minute
SANDBOX = Path("/usr/bin/sandbox-exec")
SANDBOX_PROFILE = """(version 1)
(allow default)
(deny network-outbound (remote ip))
(deny file-write*)
(allow file-write* (subpath (param "TMP")) (subpath "/dev")
  (subpath "/private/tmp") (subpath "/private/var/folders"))
"""

CLIENT_STUB = """#!/bin/sh
printf '%s\\t%s\\n' "$(basename "$0")" "$(printf '%s ' "$@" | tr '\\n\\t' '  ')" >> "$SPY_LOG.sh"
echo "offline_spy: $(basename "$0") refused" >&2
exit 97
"""

# The git wrapper logs one line per call: the subcommand, and for one that can
# reach a remote, the URL it would use -- clone's arguments; for push, fetch,
# pull and ls-remote the first positional argument after the subcommand
# (default origin) resolved through the cwd's remotes; for `remote update`,
# `remote show`, `remote prune` and submodule, every configured remote. It
# then runs the real git.
GIT_STUB = """#!/bin/sh
sub=""; skip=""; after=0; pos=""; cdir=.
for a in "$@"; do
  if [ "$skip" = C ]; then cdir=$a; skip=""; continue; fi
  if [ -n "$skip" ]; then skip=""; continue; fi
  if [ $after = 0 ]; then
    case $a in -C) skip=C ;; -c|--git-dir|--work-tree) skip=1 ;; -*) ;; *) sub=$a; after=1 ;; esac
  else
    case $a in -*) ;; *) [ -z "$pos" ] && pos=$a ;; esac
  fi
done
urls=""
case $sub in
  clone) urls="$*" ;;
  push|fetch|pull|ls-remote)
    r=${pos:-origin}
    urls=$("$SPY_REAL_GIT" -C "$cdir" remote get-url "$r" 2>/dev/null) || urls=$r ;;
  remote) case $pos in update|show|prune)
    urls=$("$SPY_REAL_GIT" -C "$cdir" remote -v 2>/dev/null | awk '{print $2}') ;; esac ;;
  submodule) urls=$("$SPY_REAL_GIT" -C "$cdir" remote -v 2>/dev/null | awk '{print $2}') ;;
esac
printf 'git\\t%s\\t%s\\n' "$sub" "$(printf '%s' "$urls" | tr '\\n\\t' '  ')" >> "$SPY_LOG.sh"
exec "$SPY_REAL_GIT" "$@"
"""


def _launch_py(argv: list[str]) -> int:
    """`--exec-py <file> args`: run <file> as __main__ with its calls logged."""
    import runpy
    import socket

    log = os.environ["SPY_LOG"]

    def note(kind: str, what: object) -> None:
        with open(log, "a") as fh:
            fh.write(json.dumps({"kind": kind, "what": str(what)[:300]}) + "\n")

    popen_init = subprocess.Popen.__init__

    def spy_popen(self, args, *a, **kw):
        note("subprocess", args)
        return popen_init(self, args, *a, **kw)

    subprocess.Popen.__init__ = spy_popen
    for name in ("system", "posix_spawn", "posix_spawnp", "spawnv", "spawnve",
                 "spawnvp", "spawnvpe", "fork", "forkpty"):
        if hasattr(os, name):
            def wrap(*a, _orig=getattr(os, name), _name=name, **kw):
                note("subprocess", [_name, *map(str, a[:2])])
                return _orig(*a, **kw)
            setattr(os, name, wrap)

    def refuse(kind):
        def f(*a, **kw):
            note("network", [kind, *map(str, a[:1])])
            raise OSError(f"offline_spy: network refused ({kind})")
        return f

    connect = socket.socket.connect

    def spy_connect(self, addr):
        if self.family == getattr(socket, "AF_UNIX", object()):
            return connect(self, addr)
        return refuse("connect")(addr)

    socket.socket.connect = spy_connect
    socket.socket.connect_ex = spy_connect
    for name in ("getaddrinfo", "gethostbyname", "gethostbyname_ex", "create_connection"):
        setattr(socket, name, refuse(name))
    path = argv[0]
    sys.argv = argv
    # As `python3 <file>` does. Whether a step passes -I is the step's own
    # check (M0 in the harness); what is measured here is what the file reaches.
    sys.path.insert(0, str(Path(path).resolve().parent))
    try:
        runpy.run_path(path, run_name="__main__")
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    return 0


def _remote_git(line: str) -> bool:
    parts = line.rstrip("\n").split("\t")
    # The wrapper records a target only for a subcommand that can reach one.
    return (len(parts) == 3 and bool(parts[1])
            and bool(URL_RE.search(parts[2])))


def spy(target: Path, root: Path = ROOT, sandbox: bool = True) -> dict:
    """Run `target --self-test` from `root` and return what it reached."""
    # Nested under another spy, PATH's git is that spy's wrapper: take the real
    # one it recorded, or the wrapper would exec itself forever.
    real_git = os.environ.get("SPY_REAL_GIT") or shutil.which("git") or "git"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = os.path.realpath(tmp)
        bindir = Path(tmp, "spybin")
        bindir.mkdir()
        for name in CLIENTS:
            (bindir / name).write_text(CLIENT_STUB)
        (bindir / "git").write_text(GIT_STUB)
        for interp in ("python3", "python"):
            (bindir / interp).symlink_to(sys.executable)
        for f in bindir.iterdir():
            if not f.is_symlink():
                f.chmod(0o755)
        home = Path(tmp, "home")
        home.mkdir()
        log = Path(tmp, "spy.log")
        log.write_text("")
        Path(f"{log}.sh").write_text("")
        if target.suffix == ".py":
            cmd = [sys.executable, "-I", str(Path(__file__).resolve()), "--exec-py",
                   str(target), "--self-test"]
        else:
            cmd = ["bash", str(target), "--self-test"]
        backstop = "none"
        if sandbox and SANDBOX.exists():
            prof = Path(tmp, "net.sb")
            prof.write_text(SANDBOX_PROFILE)
            cmd = [str(SANDBOX), "-D", f"TMP={tmp}", "-f", str(prof), *cmd]
            backstop = "sandbox-exec"
        env = {"HOME": str(home), "TMPDIR": tmp, "LANG": "C.UTF-8",
               "PATH": f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}",
               "SPY_LOG": str(log), "SPY_REAL_GIT": real_git,
               "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            proc = subprocess.run(cmd, cwd=root, env=env, capture_output=True,
                                  text=True, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:
            partial = exc.stdout or ""
            if isinstance(partial, bytes):
                partial = partial.decode(errors="replace")
            proc = subprocess.CompletedProcess(cmd, 124, partial,
                                               f"offline_spy: timed out after {TIMEOUT_S}s")
        events = [json.loads(x) for x in log.read_text().splitlines() if x.strip()]
        sh = [x for x in Path(f"{log}.sh").read_text().splitlines() if x.strip()]
    out = (proc.stdout + proc.stderr).strip().splitlines()
    tally = next((x for x in reversed(out) if re.search(r"self-test|checks|PASS", x)), "")
    return {
        "rc": proc.returncode,
        "subprocess": (sum(e["kind"] == "subprocess" for e in events)
                       if target.suffix == ".py" else None),
        "network": (sum(e["kind"] == "network" for e in events)
                    + sum(x.split("\t", 1)[0] in CLIENTS for x in sh)),
        "remote_git": sum(_remote_git(x) for x in sh if x.startswith("git\t")),
        "git": sum(x.startswith("git\t") for x in sh),
        "backstop": backstop,
        "tally": tally,
        "output": "\n".join(out[-20:]),
    }


def refused(r: dict) -> bool:
    return r["rc"] != 0 or r["network"] > 0 or r["remote_git"] > 0


def self_test() -> int:
    passed = failed = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f" ({detail})"))

    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        # The shell fixtures build their repositories through the tree's one
        # helper (tests/throwaway_git.sh), whose git calls the wrapper counts.
        tg = f'. "{ROOT}/tests/throwaway_git.sh"; throwaway_git_env; d=$(mktemp -d); '
        fx = {
            "pure.py": "print('pure self-test: 1 checks, 0 failed')\n",
            "sub.py": "import subprocess\nsubprocess.run(['true'])\n",
            "net.py": ("import socket\ntry:\n    socket.create_connection(('example.invalid', 443), 1)\n"
                       "except OSError:\n    pass\n"),
            "fail.py": "raise SystemExit(1)\n",
            "gh.sh": "gh api user >/dev/null 2>&1; exit 0\n",
            "remote.sh": "git ls-remote https://127.0.0.1:9/r.git >/dev/null 2>&1; exit 0\n",
            "cwdurl.sh": (tg + 'throwaway_git_init "$d/w" -q && git -C "$d/w" remote add origin '
                          'https://example.invalid/w.git && throwaway_git_init "$d/o" -q --bare && '
                          'cd "$d/w" && throwaway_git_clone -q "$d/o" "$d/c" && '
                          'git -C "$d/c" fetch -q origin; exit 0\n'),
            "fetchurl.sh": (tg + 'throwaway_git_init "$d/w" -q && git -C "$d/w" remote add origin '
                            'https://example.invalid/w.git && git -C "$d/w" fetch -q 2>/dev/null; exit 0\n'),
            "local.sh": (tg + 'throwaway_git_init "$d/o" -q --bare && throwaway_git_clone -q "$d/o" "$d/c" '
                         '2>/dev/null; git -C "$d/c" fetch -q origin 2>/dev/null; exit 0\n'),
        }
        for name, body in fx.items():
            (t / name).write_text(body)
        r = {name: spy(t / name, root=t) for name in fx}
    check("a pure Python self-test is accepted (null control)",
          not refused(r["pure.py"]) and r["pure.py"]["subprocess"] == 0, r["pure.py"])
    check("a subprocess the Python file starts is counted",
          r["sub.py"]["subprocess"] == 1, r["sub.py"])
    check("a socket connect is counted and refused",
          r["net.py"]["network"] == 1 and refused(r["net.py"]), r["net.py"])
    check("a non-zero exit is refused", refused(r["fail.py"]), r["fail.py"])
    check("a gh call from a shell file is counted and refused",
          r["gh.sh"]["network"] == 1 and refused(r["gh.sh"]), r["gh.sh"])
    check("a git call naming a URL remote is counted and refused",
          r["remote.sh"]["remote_git"] == 1 and refused(r["remote.sh"]), r["remote.sh"])
    check("clone and fetch against a local bare repository are not remote "
          "(null control for the URL rule)",
          r["local.sh"]["git"] >= 3 and r["local.sh"]["remote_git"] == 0
          and not refused(r["local.sh"]), r["local.sh"])
    check("a clone of a local path from a cwd whose origin is a URL is not remote",
          r["cwdurl.sh"]["remote_git"] == 0 and r["cwdurl.sh"]["git"] >= 3, r["cwdurl.sh"])
    check("a bare fetch resolves origin through the cwd's remotes and is remote",
          r["fetchurl.sh"]["remote_git"] == 1, r["fetchurl.sh"])
    check("a shell file's subprocess count is n/a, never a zero",
          r["gh.sh"]["subprocess"] is None, r["gh.sh"])
    print(f"offline_spy self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--exec-py"]:
        return _launch_py(argv[1:])
    if argv == ["--self-test"]:
        return self_test()
    if not argv or any(a.startswith("-") for a in argv):
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    bad = 0
    for a in argv:
        p = Path(a)
        r = spy(p if p.is_absolute() else ROOT / p)
        bad += refused(r)
        sub = "n/a" if r["subprocess"] is None else r["subprocess"]
        print(f"offline_spy: {a} rc={r['rc']} network={r['network']} "
              f"remote_git={r['remote_git']} git={r['git']} subprocess={sub} "
              f"backstop={r['backstop']} {'REFUSED' if refused(r) else 'offline'} | {r['tally']}")
        if refused(r):
            print(r["output"], file=sys.stderr)
    print(f"offline_spy: {len(argv)} files, {bad} refused")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
