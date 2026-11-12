#!/usr/bin/env python3
"""One writer per standing seat, and one orchestrator session: the generation token and the session lock.

    python3 tools/audit/seat/seat_gen.py bump <seat>          # the orchestrator, starting a replacement
    python3 tools/audit/seat/seat_gen.py check <seat> <gen>   # exit 1 + SUPERSEDED when a higher one is held
    python3 tools/audit/seat/seat_gen.py check-env            # check "$HPO_SEAT_GEN" (<seat>=<gen>); unset passes
    python3 tools/audit/seat/seat_gen.py lock [--pid N]       # the resume step: take or refuse the session lock
    python3 tools/audit/seat/seat_gen.py --self-test

`bump` writes `$HPO_STATE_DIR/<seat>.gen` (`<n> <epoch>`, n monotonic) under a flock and prints n; the
seat's prompt carries n. A writer that applies a seat's queue lines (`roster_queue.run_queue`,
`bus.sh dispatch`, `merge_train.train_add`) calls `check-env` before its first write and stops on
SUPERSEDED, so a superseded seat's lingering job cannot write. An unset `HPO_SEAT_GEN` behaves as
before: the orchestrator's own calls carry none. Killing the old task is an agent tool, not scriptable here.

`lock` records the session binary's pid -- the first ancestor whose command matches SESSION_RE, never
`$PPID`, which dies with the call -- and its process start time (`ps -o etimes=` back from now; 0 if ps cannot say) in `$HPO_STATE_DIR/session.lock`. A holder pid
that is alive AND whose `ps -p <pid> -o command=` matches the session binary, and is not the caller's own
session, refuses (exit 1, both pids printed); a gone pid, or one naming another command (a reused pid),
is stale and taken over. Liveness is read from the pid, never from stop lines: a reboot leaves none.
"""
from __future__ import annotations

import fcntl
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SESSION_RE = re.compile(r"(?:^|/)claude(?:\s|$)")  # the session binary's command, as ps prints it


def state_dir() -> Path:
    d = os.environ.get("HPO_STATE_DIR")
    if not d:
        raise SystemExit("seat_gen: HPO_STATE_DIR is unset")
    return Path(d)


def read_gen(path: Path) -> "int | None":
    """The held generation, None when no file, ValueError when it is garbage."""
    try:
        text = path.read_text()
    except OSError:
        return None
    return int(text.split()[0])


def bump(sd: Path, seat: str, now: float) -> int:
    sd.mkdir(parents=True, exist_ok=True)
    path = sd / f"{seat}.gen"
    with open(sd / f".{seat}.gen.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        n = (read_gen(path) or 0) + 1
        tmp = path.with_name(f".{path.name}.{os.getpid()}")
        tmp.write_text(f"{n} {int(now)}\n")
        os.replace(tmp, path)
    return n


def check(sd: Path, seat: str, gen: int) -> "tuple[int, str]":
    """(0, '') when `gen` is current, (1, SUPERSEDED ...) when a higher one is held, (2, why) when unreadable."""
    try:
        held = read_gen(sd / f"{seat}.gen")
    except ValueError:
        return 2, f"seat_gen: UNREADABLE {seat}.gen"
    if held is not None and held > gen:
        return 1, f"SUPERSEDED {seat} gen={gen} held={held}"
    return 0, ""


def check_env(env=os.environ) -> "tuple[int, str]":
    spec = env.get("HPO_SEAT_GEN", "")
    if not spec:
        return 0, ""
    seat, _, gen = spec.partition("=")
    if not seat or not gen.isdigit() or not env.get("HPO_STATE_DIR"):
        return 2, f"seat_gen: UNREADABLE HPO_SEAT_GEN={spec!r}"
    return check(Path(env["HPO_STATE_DIR"]), seat, int(gen))


def ps_command(pid: int) -> str:
    r = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def ppid_of(pid: int) -> int:
    r = subprocess.run(["ps", "-p", str(pid), "-o", "ppid="], capture_output=True, text=True)
    return int(r.stdout.strip() or 0) if r.returncode == 0 else 0


def ps_start(pid: int, now: float) -> int:
    """The process start time (epoch): now minus `ps -o etimes=`; 0 when ps cannot say."""
    r = subprocess.run(["ps", "-p", str(pid), "-o", "etimes="], capture_output=True, text=True)
    try:
        return int(now) - int(r.stdout.strip())
    except ValueError:
        return 0


def session_pid(start: int, command=ps_command, parent=ppid_of) -> "int | None":
    """The first ancestor of `start` (itself included) whose command is the session binary."""
    pid, seen = start, set()
    while pid > 1 and pid not in seen:
        seen.add(pid)
        if SESSION_RE.search(command(pid)):
            return pid
        pid = parent(pid)
    return None


def lock(sd: Path, mine: int, now: float, command=ps_command, start=ps_start) -> "tuple[int, str]":
    sd.mkdir(parents=True, exist_ok=True)
    path = sd / "session.lock"
    with open(sd / ".session.lock.flock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)  # read-decide-write is one step, as in bump
        try:
            held = int(path.read_text().split()[0])
        except (OSError, ValueError, IndexError):
            held = 0
        if held and held != mine and SESSION_RE.search(command(held)):
            return 1, f"seat_gen: REFUSED session lock held by pid {held} (this session is pid {mine}); stop and dispatch nothing"
        tmp = path.with_name(f".session.lock.{os.getpid()}")
        tmp.write_text(f"{mine} {start(mine, now)}\n")
        os.replace(tmp, path)
    return 0, f"seat_gen: session lock taken by pid {mine}" + (f" (stale holder {held})" if held and held != mine else "")


def main(argv: "list[str]") -> int:
    if argv[:1] == ["--self-test"]:
        import seat_gen_selftest
        return seat_gen_selftest.run(Path(__file__).resolve(), mutants="--no-mutants" not in argv)
    cmd, args = (argv[0], argv[1:]) if argv else ("", [])
    if cmd == "bump" and len(args) == 1:
        print(bump(state_dir(), args[0], time.time()))
        return 0
    if cmd == "check" and len(args) == 2 and args[1].isdigit():
        rc, msg = check(state_dir(), args[0], int(args[1]))
    elif cmd == "check-env" and not args:
        rc, msg = check_env()
    elif cmd == "lock" and (not args or (args[0] == "--pid" and len(args) == 2 and args[1].isdigit())):
        mine = int(args[1]) if args else session_pid(os.getpid())
        if not mine:
            print("seat_gen: UNREADABLE no ancestor is the session binary", file=sys.stderr)
            return 2
        rc, msg = lock(state_dir(), mine, time.time())
    else:
        print(__doc__, file=sys.stderr)
        return 2
    if msg:
        print(msg)
    return rc


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main(sys.argv[1:]))
