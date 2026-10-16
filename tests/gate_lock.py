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

That single lease serialises the commands that must run ALONE -- those that
measure the machine, so their numbers are comparable only with nothing else
running: ``stress.py`` and ``harness_headers.py``. Commands that are
multi-minute CPU-bound but do not measure take instead from the heavy-slot
POOL (``take_slot``/``release_slot``, ``heavy_slots()`` slots under the `slots`
subdirectory; #2267), which is what makes nudge.md's four-prepr cap mechanical
instead of advisory. ``needs_lease`` classifies a scope into the three answers
``run.sh`` dispatches on: ``lease``, ``slot`` or ``none``.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
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
# --- the heavy-slot pool (R10-PREPR-CAP, #2267) ------------------------------
# The single lease above serialises one exclusive holder (stress.py). Proving a
# branch is *runnable* is throughput-bound instead: several commands that each
# load the box may share it up to a cap, and until now the cap was the
# orchestrator's, held by hand (nudge.md step 8) and enforced by nothing. A pool
# of HEAVY_SLOTS slots, taken by `take_slot`, is that cap made mechanical.
#
# THE POOL IS ITS OWN LOCK DIR, `lock_dir/<POOL_DIRNAME>`, for two reasons. Its
# reclaim tests read `flock_available` and `_abandoned_hold` on the directory
# they reclaim in, and a pool sharing the single lease's directory would read
# that lease's flock -- a stress run holding it would freeze every dead slot
# until expiry. And a shared directory would put the pool's waiters and the
# lease's waiters in one FIFO, so the oldest waiter for either resource would
# hold the head. Its own directory (and its own `ticket-` queue) keeps the two
# resources independent, and its files are a plain second naming of the same
# Owner/ticket/expiry primitives the single lease uses.
HEAVY_SLOTS = 4
SLOT_PREFIX = "slot-"
POOL_DIRNAME = "slots"
# The slot-count override, and the owner's mark that lets it rise above the cap.
SLOTS_ENV = "HPO_HEAVY_SLOTS"
SLOTS_OWNER_ENV = "HPO_HEAVY_SLOTS_OWNER"
# The label a slot holder exports so its nested heavy steps join that slot
# instead of taking a second (prepr.sh's step 1b sets it; derive_closures.sh
# and run.sh's lease arm read it).
SLOT_LABEL_ENV = "HPO_SLOT_LABEL"
# The recordings (tests/closures.json's `recorded.seconds`) at or above this are
# the multi-minute CPU side: they join the slots. Below it they are seconds and
# run unleased. stress.py (760 s) and harness_headers.py (100 s) measure the
# machine and take the exclusive lease whatever this says.
SLOT_MIN_SECONDS = 69
MACHINE_MEASURING = ("tests/stress.py", "tests/harness_headers.py")
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


def _read_at(owner_path: Path) -> Owner | None:
    if not owner_path.is_file():
        return None
    try:
        return parse_owner(owner_path.read_text())
    except (OSError, ValueError):
        return None


def read_owner(lock_dir: Path) -> Owner | None:
    return _read_at(lock_dir / OWNER_NAME)


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


def _steal(owner_path: Path, seen: Owner) -> None:
    """Remove a dead owner by rename, so one of two stealers wins and a fresh
    owner written in between is put back rather than deleted. Takes the owner
    file, not the lock dir, so the single lease's ``owner`` and a pooled
    ``slot-<i>`` file are stolen by the same code (#2267)."""
    lock_dir = owner_path.parent
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
                _steal(lock_dir / OWNER_NAME, owner)
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


# --- the heavy-slot pool (#2267) --------------------------------------------
# The same Owner/ticket/expiry/steal primitives as the single lease above, over
# a fixed set of POOL slots instead of one owner file. `take_slot` returns the
# slot index it claimed so a caller can name the slot it holds; `release_slot`
# frees the slot a label holds, whichever index that is.


def pool_dir(lock_dir: Path = DEFAULT_LOCK_DIR) -> Path:
    """Where the pool's slot files and queue live (see POOL_DIRNAME)."""
    return lock_dir / POOL_DIRNAME


def _slot_path(pool: Path, index: int) -> Path:
    return pool / f"{SLOT_PREFIX}{index:03d}"


def _slot_of(pool: Path, slots: int, label: str) -> tuple[int, Owner] | None:
    """The slot ``label`` already holds, so a re-take is idempotent."""
    for i in range(slots):
        owner = _read_at(_slot_path(pool, i))
        if owner is not None and owner.label == label:
            return i, owner
    return None


def _free_slot(pool: Path, slots: int) -> int | None:
    """The first slot that may be claimed, stealing an expired or orphaned one.

    A missing file is free; an unreadable one is a broken holder, not a live
    one, and is replaced. A dead named pid is stolen at once (#1143's rule for
    the single lease), and the pool directory's own flock -- never held, since
    only the single lease takes flock -- makes ``_orphaned``'s gate honest.
    """
    for i in range(slots):
        path = _slot_path(pool, i)
        owner = _read_at(path)
        if owner is None:
            if not path.is_file():
                return i
            path.unlink(missing_ok=True)  # unparseable: no live holder to lose
            return i
        if owner.expired or _orphaned(pool, owner):
            _steal(path, owner)
            return i
    return None


def _held_slots(pool: Path, slots: int) -> str:
    """A one-line description of the holders, for the waiting message."""
    who = []
    for i in range(slots):
        owner = _read_at(_slot_path(pool, i))
        if owner is not None:
            who.append(f"{i}:{owner.label} until {owner.expires_at}")
    return "; ".join(who) or "none"


def take_slot(
    label: str,
    *,
    lock_dir: Path = DEFAULT_LOCK_DIR,
    slots: int | None = None,
    lease_seconds: int = LEASE_SECONDS,
    wait: bool = True,
    owner_pid: int | None = None,
) -> tuple[int, Owner]:
    """Claim one of ``slots`` heavy slots for ``label``; return (index, owner).

    First come, first served like the single lease: while every slot is held a
    caller queues behind older live tickets and takes the next slot to free, so
    a fifth caller waits rather than loading the box. ``owner_pid`` names a
    process that outlives the commands holding the slot, so a later take steals
    a slot whose seat has exited (#1143). ``slots`` defaults to `heavy_slots()`,
    the pool's own capacity.
    """
    if slots is None:
        slots = heavy_slots()
    if slots < 1:
        raise ValueError("slots must be at least 1")
    pool = pool_dir(lock_dir)
    said, ticket = False, None
    try:
        while True:
            _ensure_lock_dir(pool)
            mine = _slot_of(pool, slots, label)
            if mine is not None:
                index, owner = mine
                fresh = Owner(
                    label=label,
                    taken_at=owner.taken_at,
                    expires_at=datetime.now(UTC) + timedelta(seconds=lease_seconds),
                    pid=owner_pid if owner_pid is not None else owner.pid,
                )
                fresh.write(_slot_path(pool, index))
                return index, fresh
            free = _free_slot(pool, slots)
            if free is not None:
                queue = _queue(pool)
                if not queue or queue[0][0] == ticket:
                    fresh = _new_owner(label, lease_seconds, owner_pid)
                    if fresh.create(_slot_path(pool, free)):
                        return free, fresh
                    continue  # another caller won the O_EXCL create; try again
                held = f"{queue[0][1]}, queued first"
            else:
                held = _held_slots(pool, slots)
            if not wait:
                raise BlockingIOError(f"all {slots} heavy slots held: {held}")
            ticket = _enqueue(pool, label, ticket)
            if not said:
                print(f"gate_lock: waiting for a heavy slot ({held})", file=sys.stderr)
                said = True
            time.sleep(WAIT_POLL_SECS)
    finally:
        if ticket is not None:
            ticket.unlink(missing_ok=True)


def release_slot(
    label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR, slots: int | None = None
) -> bool:
    """Free the one slot ``label`` holds. False when it held none."""
    slots = heavy_slots() if slots is None else slots
    pool = pool_dir(lock_dir)
    mine = _slot_of(pool, slots, label)
    if mine is None:
        return False
    index, _owner = mine
    _slot_path(pool, index).unlink(missing_ok=True)  # the queue stays
    return True


def slots_status(
    *, lock_dir: Path = DEFAULT_LOCK_DIR, slots: int | None = None
) -> dict[str, object]:
    slots = heavy_slots() if slots is None else slots
    pool = pool_dir(lock_dir)
    holders: list[Owner | None] = []
    for i in range(slots):
        holders.append(_read_at(_slot_path(pool, i)))
    return {
        "pool_dir": str(pool),
        "slots": slots,
        "holders": holders,
        "queue": [who for _, who in _queue(pool)] if pool.exists() else [],
    }


def slot_auto_lease(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR,
                    owner_pid: int | None = None) -> int:
    """Take one heavy slot for ``argv``, run it with the slot's label exported,
    and release on any exit -- run.sh's counterpart to ``auto_lease``.

    ``HPO_SLOT_LABEL`` reaches the child, so a heavy step of ``argv`` that is
    itself leased (a nested run.sh, derive_closures.sh) joins this slot instead
    of taking a second."""
    take_slot(label, lock_dir=lock_dir, owner_pid=owner_pid)
    env = {**os.environ, SLOT_LABEL_ENV: label}
    try:
        return run_group(argv, env)
    finally:
        with contextlib.suppress(RuntimeError):
            release_slot(label, lock_dir=lock_dir)


def flock_wrap(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR) -> int:
    """Renew the lease, hold flock for ``argv``, release flock on exit.

    A renew refused because another label waits releases and takes again, at
    the back of the queue. A label that holds no lease fails at once: it means
    *I hold it already*, and taking one here would leave it held after the run."""
    try:
        renew(label, lock_dir=lock_dir)
    except RenewRefused as exc:
        print(f"gate_lock: {exc}; {label} re-queues", file=sys.stderr)
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


def _recorded_seconds(script: str) -> float | None:
    """``tests/closures.json``'s recorded runtime for ``script``, or None.

    The classifier below is derived from this, never carried: a script that
    gets heavier moves itself into the slots the next time the recordings are
    re-taken. None means the table has no such script, which is a script the
    tree has not run under instrumentation and so owes no slot.
    """
    recorded = Path(__file__).resolve().parent / "closures.json"
    try:
        data = json.loads(recorded.read_text())
        entry = data.get("recorded", {}).get(script)
    except (OSError, ValueError, AttributeError):
        return None
    return entry.get("seconds") if isinstance(entry, dict) else None


def needs_lease(scope_run: str) -> str:
    """``lease``, ``slot`` or ``none`` for the script(s) in run.sh's SCOPE_RUN.

    The rule (gate-scoping.md): a script that MEASURES the machine runs alone,
    under the exclusive lease; one that is multi-minute CPU-bound joins the
    four slots; one that takes seconds runs unleased. ``scope_run`` is run.sh's
    SCOPE_RUN file; empty means MODE: FULL, whose suite carries stress.py, so
    an empty scope is the exclusive lease.

    Fail closed: a scope this cannot classify -- a recording table it cannot
    read, or a name it does not know -- is leased rather than left unleased,
    so the unclassified case costs serialisation and never concurrency.
    """
    if not scope_run:
        return "lease"
    try:
        names = Path(scope_run).read_text().split()
    except OSError:
        return "lease"
    if any(name in MACHINE_MEASURING for name in names):
        return "lease"
    table = Path(__file__).resolve().parent / "closures.json"
    try:
        json.loads(table.read_text()).get("recorded", {})
    except (OSError, ValueError):
        return "lease"
    if any((s := _recorded_seconds(name)) is not None and s >= SLOT_MIN_SECONDS
           for name in names):
        return "slot"
    return "none"


def heavy_slots() -> int:
    """The pool's capacity: ``HEAVY_SLOTS``, or ``$HPO_HEAVY_SLOTS`` within it.

    Raising the cap ABOVE ``HEAVY_SLOTS`` is the owner's: the override is
    honoured above the cap only with ``$HPO_HEAVY_SLOTS_OWNER`` set, so no seat
    raises the box's concurrency by exporting one variable. A value that does
    not parse, or is below 1, reads as the cap rather than as something else.
    """
    raw = os.environ.get(SLOTS_ENV)
    if not raw:
        return HEAVY_SLOTS
    try:
        count = int(raw)
    except ValueError:
        return HEAVY_SLOTS
    if count < 1:
        return HEAVY_SLOTS
    if count > HEAVY_SLOTS and os.environ.get(SLOTS_OWNER_ENV) != "1":
        return HEAVY_SLOTS
    return count


def holding_slot() -> bool:
    """Whether ``$HPO_SLOT_LABEL`` says this process is already inside a slot.

    A nested heavy step (derive_closures.sh under a prepr, a multi-minute suite
    script under run.sh) joins the slot it was given instead of taking a
    second, so one prepr costs one slot however many heavy steps it spawns.
    """
    return bool(os.environ.get(SLOT_LABEL_ENV))


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


def _cmd_slot_take(args: argparse.Namespace) -> int:
    index, owner = take_slot(
        args.label,
        lock_dir=args.lock_dir,
        slots=args.slots,
        lease_seconds=args.lease_seconds,
        wait=not args.no_wait,
        owner_pid=args.owner_pid,
    )
    print(
        f"taken slot={index} label={owner.label} expires_at={owner.expires_at.isoformat()}",
        file=sys.stderr,
    )
    return 0


def _cmd_slot_release(args: argparse.Namespace) -> int:
    if release_slot(args.label, lock_dir=args.lock_dir, slots=args.slots):
        print("released", file=sys.stderr)
        return 0
    print("no slot", file=sys.stderr)
    return 0


def _cmd_slot_status(args: argparse.Namespace) -> int:
    info = slots_status(lock_dir=args.lock_dir, slots=args.slots)
    held = [
        f"{i}:{o.label}({'expired' if o.expired else 'live'})"
        for i, o in enumerate(info["holders"]) if o is not None
    ]
    print(
        f"{info['pool_dir']}: {len(held)}/{info['slots']} slots held "
        f"[{', '.join(held) or '-'}] queue={','.join(info['queue']) or '-'}"
    )
    return 0


def _cmd_flock_wrap(args: argparse.Namespace) -> int:
    try:
        return flock_wrap(args.label, args.argv, lock_dir=args.lock_dir)
    except RuntimeError as exc:  # a label never taken: refuse, run nothing
        print(f"gate_lock: flock-wrap refused, {args.label} holds no lease: {exc}", file=sys.stderr)
        return 1


def _cmd_auto_lease(args: argparse.Namespace) -> int:
    argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    return auto_lease(args.label, argv, lock_dir=args.lock_dir)


def _cmd_slot_auto_lease(args: argparse.Namespace) -> int:
    argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    return slot_auto_lease(args.label, argv, lock_dir=args.lock_dir,
                           owner_pid=args.owner_pid)


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

    nl_p = sub.add_parser(
        "needs-lease", help="print how run.sh's scope should run: lease|slot|none"
    )
    nl_p.add_argument("scope_run", help="run.sh's SCOPE_RUN; empty means MODE: FULL")
    nl_p.set_defaults(func=lambda a: print(needs_lease(a.scope_run)))

    auto_p = sub.add_parser("auto-lease", help="take, hold flock for a command, release")
    auto_p.add_argument("--label", required=True)
    auto_p.add_argument("argv", nargs=argparse.REMAINDER, help="command after --")
    auto_p.set_defaults(func=_cmd_auto_lease)

    slot_take_p = sub.add_parser(
        "slot-take", help="take one of the heavy slots (#2267)"
    )
    slot_take_p.add_argument("--label", required=True)
    slot_take_p.add_argument("--slots", type=int, default=None)
    slot_take_p.add_argument("--lease-seconds", type=int, default=LEASE_SECONDS)
    slot_take_p.add_argument("--no-wait", action="store_true")
    slot_take_p.add_argument("--owner-pid", type=int, default=None)
    slot_take_p.set_defaults(func=_cmd_slot_take)

    slot_rel_p = sub.add_parser("slot-release", help="free the slot a label holds")
    slot_rel_p.add_argument("--label", required=True)
    slot_rel_p.add_argument("--slots", type=int, default=None)
    slot_rel_p.set_defaults(func=_cmd_slot_release)

    slot_st_p = sub.add_parser("slot-status", help="print the heavy-slot pool state")
    slot_st_p.add_argument("--slots", type=int, default=None)
    slot_st_p.set_defaults(func=_cmd_slot_status)

    slot_auto_p = sub.add_parser(
        "slot-auto-lease", help="take a heavy slot, run a command inside it, release"
    )
    slot_auto_p.add_argument("--label", required=True)
    slot_auto_p.add_argument("--owner-pid", type=int, default=None)
    slot_auto_p.add_argument("argv", nargs=argparse.REMAINDER, help="command after --")
    slot_auto_p.set_defaults(func=_cmd_slot_auto_lease)

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
