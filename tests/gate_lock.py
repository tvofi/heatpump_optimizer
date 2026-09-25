#!/usr/bin/env python3
"""Renewed-lease gate lock with flock for local stress runs (#404).

Serialises anything that runs ``tests/stress.py`` on a shared box. The owner
file carries an ``expires_at`` lease and an agent label. ``flock`` is held only
for the duration of a gate run; the lease covers the window between commands
when no process holds anything. An expired lease or an abandoned hold
(``holding`` marker, flock dropped) is taken without forensics so a waiter can
proceed after crash or expiry.

The owner file may also carry ``pid=`` — the process the holder names as its
own (``--owner-pid``;#1143). A lease that is neither expired nor holding-marked
but whose named process is gone, with nothing holding flock, is orphaned: take()
steals it at once instead of serialising the box behind a seat that has exited.
The probe is opt-in because no safe default exists — the pid that invoked this
process is a per-command shell (measured: it changes on every command), not the
seat, so trusting it would read a live seat as dead. A seat holding the lease
across commands passes the pid of a process that outlives them, e.g.
``--owner-pid $PPID``.

The lease is first come, first served. A waiter holds a ticket
(``ticket-<n>``); a free lease goes to the oldest LIVE ticket, and one whose
process is gone or whose ticket expired is skipped and removed. ``renew``
refuses (``RENEW_REFUSED_RC``) while another label's ticket waits: the holder
finishes its current run, releases, and takes again behind the waiter.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Above 735 s full gate / 560 s stress on the owner's box (#404).
LEASE_SECONDS = 1800
# The env override lets a demonstration run tests/run.sh against its own lock.
DEFAULT_LOCK_DIR = Path(os.environ.get("HPO_GATE_LOCK_DIR") or "/tmp/hpo-gate.lock")
OWNER_NAME = "owner"
FLOCK_NAME = "flock"
HOLDING_NAME = "holding"
WAIT_POLL_SECS = 5
TICKET_PREFIX = "ticket-"
# A waiter rewrites its ticket every poll; one this far past it is dead.
TICKET_SECONDS = 60
RENEW_REFUSED_RC = 75


class RenewRefused(RuntimeError):
    """Another label waits for the lease, so the holder may not extend it."""


@dataclass(frozen=True)
class Owner:
    label: str
    expires_at: datetime
    taken_at: datetime
    # The process the holder named as its own, if any (#1143). None means the
    # holder gave no liveness handle, and take() never probes for one.
    pid: int | None = None

    def _text(self) -> str:
        lines = [
            f"label={self.label}\n",
            f"expires_at={self.expires_at.isoformat()}\n",
            f"taken_at={self.taken_at.isoformat()}\n",
        ]
        if self.pid is not None:
            lines.append(f"pid={self.pid}\n")
        return "".join(lines)

    def write(self, path: Path) -> None:
        path.write_text(self._text())

    def create(self, path: Path) -> bool:
        """Write only if no owner exists: two takes in one instant cannot both win."""
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except (FileExistsError, FileNotFoundError):
            return False
        with os.fdopen(fd, "w") as f:
            f.write(self._text())
        return True

    @property
    def expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at


def _fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def parse_owner(text: str) -> Owner:
    fields = _fields(text)
    missing = {"label", "expires_at", "taken_at"} - fields.keys()
    if missing:
        raise ValueError(f"owner file missing {sorted(missing)}")
    pid: int | None = None
    if "pid" in fields:
        try:
            pid = int(fields["pid"])
        except ValueError:
            pid = None
    return Owner(
        label=fields["label"],
        expires_at=datetime.fromisoformat(fields["expires_at"]),
        taken_at=datetime.fromisoformat(fields["taken_at"]),
        pid=pid,
    )


def read_owner(lock_dir: Path) -> Owner | None:
    owner_path = lock_dir / OWNER_NAME
    if not owner_path.is_file():
        return None
    try:
        return parse_owner(owner_path.read_text())
    except (OSError, ValueError):
        return None


def _new_owner(label: str, lease_seconds: int, pid: int | None = None) -> Owner:
    now = datetime.now(UTC)
    return Owner(
        label=label,
        taken_at=now,
        expires_at=now + timedelta(seconds=lease_seconds),
        pid=pid,
    )


def _ensure_lock_dir(lock_dir: Path) -> None:
    lock_dir.mkdir(parents=True, exist_ok=True)
    (lock_dir / FLOCK_NAME).touch(exist_ok=True)


def _clear_lock(lock_dir: Path) -> None:
    if lock_dir.exists():
        for child in lock_dir.iterdir():
            child.unlink()
        lock_dir.rmdir()


@contextlib.contextmanager
def flock_context(lock_dir: Path, blocking: bool = True):
    """Advisory flock on ``lock_dir/flock``; released when the context exits.

    A blocking hold writes ``holding`` so a crash (marker left, flock
    dropped) is distinguishable from a live agent between commands.
    """
    _ensure_lock_dir(lock_dir)
    fd = os.open(lock_dir / FLOCK_NAME, os.O_RDWR)
    marked = False
    try:
        flags = fcntl.LOCK_EX
        if not blocking:
            flags |= fcntl.LOCK_NB
        fcntl.flock(fd, flags)
        if blocking:
            (lock_dir / HOLDING_NAME).write_text("holding\n")
            marked = True
        yield fd
    finally:
        if marked:
            (lock_dir / HOLDING_NAME).unlink(missing_ok=True)
        with contextlib.suppress(OSError):
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def flock_available(lock_dir: Path) -> bool:
    try:
        with flock_context(lock_dir, blocking=False):
            return True
    except BlockingIOError:
        return False


def _abandoned_hold(lock_dir: Path) -> bool:
    # Crash mid-hold: marker remains, kernel dropped flock (#475 steal).
    return (lock_dir / HOLDING_NAME).exists() and flock_available(lock_dir)


def _pid_alive(pid: int) -> bool:
    """Whether ``pid`` names a live process, unprivileged.

    A pid we may not signal (PermissionError) exists and is not ours, so it is
    alive. ``os.kill(pid, 0)`` is the probe; it never self-matches the way
    ``pgrep -f <pattern>`` does when the pattern sits in the caller's own
    command line (#1143 class a).
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _orphaned(lock_dir: Path, owner: Owner) -> bool:
    """A lease that named its owner's process and that process is gone (#1143).

    Requires all three: the owner recorded a pid, the pid is provably dead, and
    nothing holds flock. flock_available keeps the gate's own children honest —
    a gate that inherited the fd still holds flock after its parent is killed,
    and must not be read as orphaned. A pid the kernel has REUSED reads as
    alive and the lease is kept, which is conservative rather than wrong.
    """
    if owner.pid is None or owner.pid <= 0:
        return False
    if _pid_alive(owner.pid):
        return False
    return flock_available(lock_dir)


def _steal(lock_dir: Path, seen: Owner) -> None:
    """Remove a dead owner by rename, so one of two stealers wins and a fresh
    owner written in between is put back rather than deleted."""
    owner_path = lock_dir / OWNER_NAME
    grave = lock_dir / f"stale-{os.getpid()}-{time.monotonic_ns()}"
    try:
        os.rename(owner_path, grave)
    except FileNotFoundError:
        return
    try:
        if parse_owner(grave.read_text()) != seen:
            with contextlib.suppress(FileExistsError):
                os.link(grave, owner_path)
        else:
            (lock_dir / HOLDING_NAME).unlink(missing_ok=True)
    except (OSError, ValueError):
        pass
    grave.unlink(missing_ok=True)


def _ticket_tmp(lock_dir: Path, label: str) -> Path:
    """A ticket's full text in a private file, so no reader sees half of it."""
    tmp = lock_dir / f"tmp-{os.getpid()}-{time.monotonic_ns()}"
    expires = datetime.now(UTC) + timedelta(seconds=TICKET_SECONDS)
    tmp.write_text(f"label={label}\npid={os.getpid()}\nexpires_at={expires.isoformat()}\n")
    return tmp


def _enqueue(lock_dir: Path, label: str, ticket: Path | None) -> Path:
    """Refresh ``ticket`` in place, or join the back of the queue."""
    _ensure_lock_dir(lock_dir)
    tmp = _ticket_tmp(lock_dir, label)
    try:
        if ticket is not None and ticket.exists():
            os.replace(tmp, ticket)
            return ticket
        while True:
            seqs = [int(p.name[len(TICKET_PREFIX):]) for p in lock_dir.glob(TICKET_PREFIX + "*")
                    if p.name[len(TICKET_PREFIX):].isdigit()]
            path = lock_dir / f"{TICKET_PREFIX}{max(seqs, default=0) + 1:012d}"
            with contextlib.suppress(FileExistsError):
                os.link(tmp, path)
                return path
    finally:
        tmp.unlink(missing_ok=True)


def _queue(lock_dir: Path) -> list[tuple[Path, str]]:
    """Live tickets, oldest first; a dead or expired one is removed."""
    live = []
    for path in sorted(lock_dir.glob(TICKET_PREFIX + "*")):
        try:
            f = _fields(path.read_text())
            alive = (_pid_alive(int(f["pid"]))
                     and datetime.now(UTC) < datetime.fromisoformat(f["expires_at"]))
        except FileNotFoundError:
            continue
        except (OSError, KeyError, ValueError):
            alive = False
        if alive:
            live.append((path, f["label"]))
        else:
            path.unlink(missing_ok=True)
    return live


def take(
    label: str,
    *,
    lock_dir: Path = DEFAULT_LOCK_DIR,
    lease_seconds: int = LEASE_SECONDS,
    wait: bool = True,
    owner_pid: int | None = None,
) -> Owner:
    """Acquire the gate lease for ``label``, queueing behind older live tickets.

    ``owner_pid`` names a process that outlives the commands holding the lease
    (a seat's ``$PPID``). It is recorded in the owner file so a later take can
    steal an orphaned lease whose holder exited without releasing (#1143).
    """
    said, ticket = False, None
    try:
        while True:
            owner = read_owner(lock_dir)
            if owner is None:
                _ensure_lock_dir(lock_dir)
                queue = _queue(lock_dir)
                if not queue or queue[0][0] == ticket:
                    fresh = _new_owner(label, lease_seconds, owner_pid)
                    if fresh.create(lock_dir / OWNER_NAME):
                        return fresh
                    continue
                held = f"{queue[0][1]}, queued first"
            elif owner.label == label:
                (lock_dir / HOLDING_NAME).unlink(missing_ok=True)
                if owner.expired:
                    fresh = _new_owner(label, lease_seconds, owner_pid)
                    fresh.write(lock_dir / OWNER_NAME)
                    return fresh
                return renew(label, lock_dir=lock_dir, lease_seconds=lease_seconds,
                             owner_pid=owner_pid)
            elif owner.expired or _abandoned_hold(lock_dir) or _orphaned(lock_dir, owner):
                _steal(lock_dir, owner)
                continue
            else:
                held = f"{owner.label} until {owner.expires_at}"
            if not wait:
                raise BlockingIOError(f"gate held by {held}")
            ticket = _enqueue(lock_dir, label, ticket)
            if not said:
                print(f"gate_lock: waiting for the lease held by {held}"
                      " (yours? export HPO_GATE_LOCK_LABEL with that label)", file=sys.stderr)
                said = True
            time.sleep(WAIT_POLL_SECS)
    finally:
        if ticket is not None:
            ticket.unlink(missing_ok=True)


def renew(
    label: str,
    *,
    lock_dir: Path = DEFAULT_LOCK_DIR,
    lease_seconds: int = LEASE_SECONDS,
    owner_pid: int | None = None,
) -> Owner:
    owner = read_owner(lock_dir)
    if owner is None or owner.expired:
        raise RuntimeError("no live gate lease to renew")
    if owner.label != label:
        raise RuntimeError(f"lease held by {owner.label}, not {label}")
    waiting = [who for _, who in _queue(lock_dir) if who != label]
    if waiting:
        raise RenewRefused(
            f"renew refused: {waiting[0]} waits for the lease. Finish the current "
            f"stress.py run, release, and take again: you queue behind it")
    refreshed = Owner(
        label=label,
        taken_at=owner.taken_at,
        expires_at=datetime.now(UTC) + timedelta(seconds=lease_seconds),
        # A caller that names a pid sets it; one that does not leaves the
        # holder's own recorded pid standing rather than clearing it.
        pid=owner_pid if owner_pid is not None else owner.pid,
    )
    refreshed.write(lock_dir / OWNER_NAME)
    # Only between commands: a renew from inside a run keeps the marker, so a
    # SIGKILLed holder (marker left, flock dropped) is stolen at once, not at expiry.
    if flock_available(lock_dir):
        (lock_dir / HOLDING_NAME).unlink(missing_ok=True)
    return refreshed


def release(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR) -> bool:
    owner = read_owner(lock_dir)
    if owner is None:
        return False
    if owner.label != label:
        raise RuntimeError(f"lease held by {owner.label}, not {label}")
    (lock_dir / OWNER_NAME).unlink(missing_ok=True)  # the queue stays
    (lock_dir / HOLDING_NAME).unlink(missing_ok=True)
    return True


def status(lock_dir: Path = DEFAULT_LOCK_DIR) -> dict[str, object]:
    owner = read_owner(lock_dir)
    return {
        "lock_dir": str(lock_dir),
        "owner": owner,
        "queue": [who for _, who in _queue(lock_dir)] if lock_dir.exists() else [],
        "flock_available": flock_available(lock_dir) if lock_dir.exists() else True,
    }


def flock_wrap(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR) -> int:
    """Renew the lease, hold flock for ``argv``, release flock on exit.

    A renew refused (another label waits), expired or never taken releases what
    is ours and takes again, at the back of the queue."""
    try:
        renew(label, lock_dir=lock_dir)
    except RuntimeError as exc:
        print(f"gate_lock: {exc}; {label} takes the lease again", file=sys.stderr)
        with contextlib.suppress(RuntimeError):
            release(label, lock_dir=lock_dir)
        take(label, lock_dir=lock_dir)
    with flock_context(lock_dir, blocking=True) as fd:
        return run_group(argv, fd=fd)


def run_group(argv: list[str], env: dict[str, str] | None = None, fd: int | None = None) -> int:
    """Run ``argv`` as its own process group; on any exit, signal the group,
    so no child of the gate (stress.py) outlives the lease. The gate inherits the
    flock ``fd``: a SIGKILL of the holder alone leaves flock held until the whole
    gate is dead, so a successor never reads a live gate as an abandoned hold."""
    fds = () if fd is None else (fd,)
    proc = subprocess.Popen(argv, env=env, start_new_session=True, pass_fds=fds)
    try:
        return proc.wait()
    finally:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(proc.pid, sig)
            try:
                proc.wait(timeout=10)
                break
            except subprocess.TimeoutExpired:
                continue


def needs_lease(scope_run: str) -> bool:
    """run.sh's derived mode decides, not a seat's prediction of it.

    ``scope_run`` is run.sh's SCOPE_RUN: empty means MODE: FULL.
    """
    if not scope_run:
        return True
    return "tests/stress.py" in Path(scope_run).read_text().split()


@contextlib.contextmanager
def leased(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR):
    """Take the lease (queueing), hold flock inside, release on any exit."""
    take(label, lock_dir=lock_dir)
    try:
        with flock_context(lock_dir, blocking=True) as fd:
            yield fd
    finally:
        with contextlib.suppress(RuntimeError):
            release(label, lock_dir=lock_dir)


def auto_lease(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR) -> int:
    """Take the lease (queueing), hold flock for ``argv``, release on any exit."""
    env = {**os.environ, "HPO_GATE_LOCK_LABEL": label}
    with leased(label, lock_dir=lock_dir) as fd:
        return run_group(argv, env, fd)


def _cmd_take(args: argparse.Namespace) -> int:
    owner = take(
        args.label,
        lock_dir=args.lock_dir,
        lease_seconds=args.lease_seconds,
        wait=not args.no_wait,
        owner_pid=args.owner_pid,
    )
    print(
        f"taken label={owner.label} expires_at={owner.expires_at.isoformat()}",
        file=sys.stderr,
    )
    return 0


def _cmd_renew(args: argparse.Namespace) -> int:
    owner = renew(
        args.label,
        lock_dir=args.lock_dir,
        lease_seconds=args.lease_seconds,
        owner_pid=args.owner_pid,
    )
    print(f"renewed expires_at={owner.expires_at.isoformat()}", file=sys.stderr)
    return 0


def _cmd_release(args: argparse.Namespace) -> int:
    if release(args.label, lock_dir=args.lock_dir):
        print("released", file=sys.stderr)
        return 0
    print("no lock", file=sys.stderr)
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    info = status(lock_dir=args.lock_dir)
    owner = info["owner"]
    if owner is None:
        print(f"{info['lock_dir']}: no lease")
    else:
        state = "expired" if owner.expired else "live"
        pid = "" if owner.pid is None else f" pid={owner.pid}"
        print(
            f"{info['lock_dir']}: {state} label={owner.label}{pid} "
            f"expires_at={owner.expires_at.isoformat()} "
            f"flock_available={info['flock_available']} "
            f"queue={','.join(info['queue']) or '-'}"
        )
    return 0


def _cmd_flock_wrap(args: argparse.Namespace) -> int:
    return flock_wrap(args.label, args.argv, lock_dir=args.lock_dir)


def _cmd_auto_lease(args: argparse.Namespace) -> int:
    argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    return auto_lease(args.label, argv, lock_dir=args.lock_dir)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--lock-dir",
        type=Path,
        default=DEFAULT_LOCK_DIR,
        help=f"lock directory (default {DEFAULT_LOCK_DIR})",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    take_p = sub.add_parser("take", help="take or refresh the gate lease")
    take_p.add_argument("--label", required=True)
    take_p.add_argument("--lease-seconds", type=int, default=LEASE_SECONDS)
    take_p.add_argument("--no-wait", action="store_true")
    take_p.add_argument(
        "--owner-pid",
        type=int,
        default=None,
        help="pid of a process outliving your commands (e.g. $PPID); a later "
             "take steals this lease once that process is gone (#1143)",
    )
    take_p.set_defaults(func=_cmd_take)

    renew_p = sub.add_parser("renew", help="extend the lease for this label")
    renew_p.add_argument("--label", required=True)
    renew_p.add_argument("--lease-seconds", type=int, default=LEASE_SECONDS)
    renew_p.add_argument("--owner-pid", type=int, default=None)
    renew_p.set_defaults(func=_cmd_renew)

    rel_p = sub.add_parser("release", help="drop the lease for this label")
    rel_p.add_argument("--label", required=True)
    rel_p.set_defaults(func=_cmd_release)

    sub.add_parser("status", help="print lease and flock state").set_defaults(
        func=_cmd_status
    )

    wrap_p = sub.add_parser(
        "flock-wrap",
        help="renew, hold flock for a subprocess, release flock on exit",
    )
    wrap_p.add_argument("--label", required=True)
    wrap_p.add_argument("argv", nargs=argparse.REMAINDER, help="command after --")
    wrap_p.set_defaults(func=_cmd_flock_wrap)

    nl_p = sub.add_parser("needs-lease", help="exit 0 if run.sh's scope needs the lease")
    nl_p.add_argument("scope_run", help="run.sh's SCOPE_RUN; empty means MODE: FULL")
    nl_p.set_defaults(func=lambda a: print("lease" if needs_lease(a.scope_run) else "none"))

    auto_p = sub.add_parser("auto-lease", help="take, hold flock for a command, release")
    auto_p.add_argument("--label", required=True)
    auto_p.add_argument("argv", nargs=argparse.REMAINDER, help="command after --")
    auto_p.set_defaults(func=_cmd_auto_lease)

    return p


# --- acceptance (#404) -------------------------------------------------------


def _queue_cases(g) -> list[tuple[str, bool, str]]:
    """The queue's four cases, against module ``g`` -- this one, or origin/main's
    copy loaded beside it, where the first three fail and the null control holds."""
    import tempfile
    import threading

    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    out, poll = [], g.WAIT_POLL_SECS
    g.WAIT_POLL_SECS = 0.2

    def ticket(d: Path, n: int, who: str, pid: int, secs: int) -> None:
        g._ensure_lock_dir(d)
        at = (datetime.now(UTC) + timedelta(seconds=secs)).isoformat()
        (d / f"{TICKET_PREFIX}{n:012d}").write_text(f"label={who}\npid={pid}\nexpires_at={at}\n")

    def waiters(d: Path, labels: list[str], got: list[str]) -> list[threading.Thread]:
        def one(who: str) -> None:
            g.take(who, lock_dir=d, lease_seconds=60)
            got.append(who)
            time.sleep(0.1)
            g.release(who, lock_dir=d)
        ts = []
        for who in labels:  # each queues before the next starts
            ts.append(threading.Thread(target=one, args=(who,), daemon=True))
            ts[-1].start()
            time.sleep(0.3)
        return ts

    def jumps(d: Path, got: list[str]) -> bool:
        try:
            g.take("jumper", lock_dir=d, lease_seconds=60, wait=False)
        except BlockingIOError:
            return False
        got.append("jumper")
        g.release("jumper", lock_dir=d)
        return True

    def fifo(d: Path, got: list[str]) -> tuple[bool, str]:
        g.take("h", lock_dir=d, lease_seconds=60, wait=False)
        ts = waiters(d, ["a", "b", "c"], got)
        g.release("h", lock_dir=d)
        jumps(d, got)
        [t.join(10) for t in ts]
        return got == ["a", "b", "c"], f"order={got}"

    def renew_refused(d: Path, got: list[str]) -> tuple[bool, str]:
        g.take("h", lock_dir=d, lease_seconds=60, wait=False)
        ts = waiters(d, ["w"], got)
        try:
            g.renew("h", lock_dir=d, lease_seconds=60)
            refused = False
        except RuntimeError:
            refused = True
        g.release("h", lock_dir=d)
        g.take("h", lock_dir=d, lease_seconds=60)
        got.append("h")
        [t.join(10) for t in ts]
        g.release("h", lock_dir=d)
        return refused and got == ["w", "h"], f"refused={refused} order={got}"

    def dead_skipped(d: Path, got: list[str]) -> tuple[bool, str]:
        g.take("h", lock_dir=d, lease_seconds=60, wait=False)
        ticket(d, 1, "ghost", dead.pid, 600)
        ticket(d, 2, "stale", os.getpid(), -10)
        ts = waiters(d, ["a"], got)
        g.release("h", lock_dir=d)
        jumped = jumps(d, got)
        [t.join(10) for t in ts]
        return got == ["a"] and not jumped, f"order={got} jumped={jumped}"

    def null(d: Path, got: list[str]) -> tuple[bool, str]:
        first = g.take("h", lock_dir=d, lease_seconds=2, wait=False)
        ticket(d, 1, "ghost", dead.pid, 600)
        second = g.renew("h", lock_dir=d, lease_seconds=60)
        g.release("h", lock_dir=d)
        ticket(d, 1, "ghost", dead.pid, 600)
        nxt = g.take("n", lock_dir=d, lease_seconds=60, wait=False).label
        return second.expires_at > first.expires_at and nxt == "n", f"next={nxt}"

    cases = [
        ("FIFO: three waiters take in arrival order, no one jumps", fifo),
        ("renew is refused while a ticket waits; the holder re-queues behind", renew_refused),
        ("a dead or expired ticket is skipped, a live one behind it is not", dead_skipped),
        ("null control: with no live waiter renew extends and a take succeeds", null),
    ]
    try:
        with tempfile.TemporaryDirectory() as td:
            for i, (name, case) in enumerate(cases):
                try:
                    out.append((name, *case(Path(td) / str(i), [])))
                except Exception as exc:  # a crash is a red case, not a lost one
                    out.append((name, False, f"raised {exc!r}"))
    finally:
        g.WAIT_POLL_SECS = poll
    return out


def _acceptance() -> int:
    from harness import Results

    R = Results("gate lock acceptance (#404)")
    tmp = Path(os.environ.get("TMPDIR", "/tmp"))

    # 1. Expired lease taken without forensics.
    R.section("expired lease taken cleanly")
    d1 = tmp / f"hpo-gate-test-expired-{os.getpid()}"
    if d1.exists():
        _clear_lock(d1)
    d1.mkdir(parents=True, exist_ok=True)
    (d1 / FLOCK_NAME).touch()
    past = datetime.now(UTC) - timedelta(seconds=10)
    Owner("dead-agent", past, past).write(d1 / OWNER_NAME)
    try:
        new = take("successor", lock_dir=d1, lease_seconds=60, wait=False)
        R.check("expired lease replaced", new.label == "successor" and not new.expired)
    except BlockingIOError:
        R.check("expired lease replaced", False)

    # 2. Live agent between commands keeps the lock (renew).
    R.section("live agent between commands keeps lock")
    d2 = tmp / f"hpo-gate-test-renew-{os.getpid()}"
    if d2.exists():
        _clear_lock(d2)
    first = take("between-cmds", lock_dir=d2, lease_seconds=2, wait=False)
    time.sleep(1)
    R.check("holder pid irrelevant — lease still live", not first.expired)
    second = renew("between-cmds", lock_dir=d2, lease_seconds=60)
    R.check("renew extends lease", second.expires_at > first.expires_at)
    third = take("between-cmds", lock_dir=d2, lease_seconds=60, wait=False)
    R.check("re-take between commands is idempotent", third.label == "between-cmds")

    # 3. Crashed run releases via flock.
    R.section("crashed run releases flock")
    d3 = tmp / f"hpo-gate-test-flock-{os.getpid()}"
    if d3.exists():
        _clear_lock(d3)
    take("crasher", lock_dir=d3, lease_seconds=60, wait=False)
    holder_script = (
        "import time\n"
        "from pathlib import Path\n"
        "import gate_lock\n"
        f"lock_dir = Path('{d3}')\n"
        "gate_lock.take('crasher', lock_dir=lock_dir, wait=False)\n"
        "with gate_lock.flock_context(lock_dir):\n"
        "    time.sleep(30)\n"
    )
    holder = subprocess.Popen(
        [sys.executable, "-c", holder_script],
        cwd=Path(__file__).resolve().parent,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent)},
    )
    time.sleep(0.5)
    R.check("flock held during gate", not flock_available(d3))
    holder.kill()
    holder.wait(timeout=5)
    time.sleep(0.2)
    R.check("flock released after crash", flock_available(d3))
    try:
        nxt = take("successor", lock_dir=d3, lease_seconds=60, wait=False)
        R.check("successor takes after crash", nxt.label == "successor")
    except BlockingIOError:
        R.check("successor takes after crash", False)

    # 4. Two agents contend — one queues.
    R.section("two agents contend")
    d4 = tmp / f"hpo-gate-test-queue-{os.getpid()}"
    if d4.exists():
        _clear_lock(d4)
    take("holder", lock_dir=d4, lease_seconds=60, wait=False)
    t0 = time.monotonic()
    try:
        take("waiter", lock_dir=d4, lease_seconds=60, wait=False)
        R.check("contention without wait should not succeed", False)
    except BlockingIOError:
        R.check("second agent blocked on live lease", True)
    release("holder", lock_dir=d4)
    waiter = take("waiter", lock_dir=d4, lease_seconds=60, wait=False)
    waited = time.monotonic() - t0
    R.check("waiter acquired after release", waiter.label == "waiter")
    R.check("no pid forensics required", waited < 5)

    # 5. Expired same-label take rewrites owner (#479 residual).
    R.section("expired same-label take")
    d5 = tmp / f"hpo-gate-test-same-expired-{os.getpid()}"
    if d5.exists():
        _clear_lock(d5)
    _ensure_lock_dir(d5)
    past = datetime.now(UTC) - timedelta(seconds=10)
    Owner("holder", past, past).write(d5 / OWNER_NAME)
    (d5 / FLOCK_NAME).touch()
    try:
        renewed = take("holder", lock_dir=d5, lease_seconds=60, wait=False)
        R.check(
            "expired same-label take succeeds",
            renewed.label == "holder" and not renewed.expired,
        )
    except RuntimeError:
        R.check("expired same-label take succeeds", False)

    # 6. Same-label return after crash clears holding.
    R.section("same-label return clears holding")
    d6 = tmp / f"hpo-gate-test-same-return-{os.getpid()}"
    if d6.exists():
        _clear_lock(d6)
    take("holder", lock_dir=d6, lease_seconds=60, wait=False)
    holder_script = (
        "import time\n"
        "from pathlib import Path\n"
        "import gate_lock\n"
        f"lock_dir = Path('{d6}')\n"
        "gate_lock.take('holder', lock_dir=lock_dir, wait=False)\n"
        "with gate_lock.flock_context(lock_dir):\n"
        "    time.sleep(30)\n"
    )
    holder = subprocess.Popen(
        [sys.executable, "-c", holder_script],
        cwd=Path(__file__).resolve().parent,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent)},
    )
    time.sleep(0.5)
    holder.kill()
    holder.wait(timeout=5)
    time.sleep(0.2)
    take("holder", lock_dir=d6, lease_seconds=60, wait=False)
    R.check("holding cleared after same-label return", not (d6 / HOLDING_NAME).exists())
    try:
        take("waiter", lock_dir=d6, lease_seconds=60, wait=False)
        R.check("waiter blocked after same-label return", False)
    except BlockingIOError:
        R.check("waiter blocked after same-label return", True)

    R.section("the queue")
    for name, ok, detail in _queue_cases(sys.modules[__name__]):
        R.check(name, ok, detail)

    for d in (d1, d2, d3, d4, d5, d6):
        if d.exists():
            _clear_lock(d)

    return R.close("gate lock acceptance checks")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--accept":
        sys.exit(_acceptance())
    for sig in (signal.SIGTERM, signal.SIGHUP):  # so run_group and release run
        signal.signal(sig, lambda n, _f: sys.exit(128 + n))
    args = _parser().parse_args()
    if args.cmd == "flock-wrap" and args.argv[:1] == ["--"]:
        args.argv = args.argv[1:]
    try:
        sys.exit(args.func(args))
    except RenewRefused as exc:
        print(f"gate_lock: {exc}", file=sys.stderr)
        sys.exit(RENEW_REFUSED_RC)
