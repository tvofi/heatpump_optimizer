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

The lease is first come, first served WITHIN a priority band. A waiter holds a
ticket (``ticket-<n>``); a free lease goes to the oldest LIVE ticket in the
highest band present, and one whose process is gone or whose ticket expired is
skipped and removed. ``renew`` refuses (``RENEW_REFUSED_RC``) while another
label's ticket waits: the holder finishes its current run, releases, and takes
again behind the waiter.

A waiter may declare a priority: ``take``/``take_slot`` read
``$HPO_GATE_PRIORITY`` (0 normal, 1 high, 2 urgent), or take a ``priority=``
argument that wins over it. THE LEASE NEVER DECIDES WHO DESERVES ONE: which
group is on the critical path is the caller's policy, and ``tools/pr/prepr.sh``
derives it from the round roster's critical-path file. A ticket with no
priority, a malformed one or an unreadable field is 0 and never crashes the
queue. Aging keeps normal work from starving: a waiter past
``PRIORITY_AGING_SECONDS`` (600 s) is promoted to ``PRIORITY_MAX``, so it
overtakes any higher priority that arrived later, while arrival still orders
the band. The window sits between the pool's 69 s ``SLOT_MIN_SECONDS`` and the
1800 s ``LEASE_SECONDS``: long enough that priority orders a burst of heavy
work, short enough that a steady stream of urgent tickets cannot hold a normal
waiter indefinitely. A ticket rewrite keeps its ``priority`` and its original
``queued_at`` -- the poll that refreshes it must not reset its age. The
heavy-slot pool below obeys the same rule in its own directory.

That single lease serialises the commands that must run ALONE -- those that
measure the machine, so their numbers are comparable only with nothing else
running: ``stress.py`` and ``harness_headers.py``. Commands that are
multi-minute CPU-bound but do not measure take instead from the heavy-slot
POOL (``take_slot``/``release_slot``, ``heavy_slots()`` slots under the `slots`
subdirectory; #2267), which is what makes nudge.md's four-prepr cap mechanical
instead of advisory. ``needs_lease`` classifies a scope into the three answers
``run.sh`` dispatches on: ``lease``, ``slot`` or ``none``.

A pool slot is held for the LIFE of its run, not for its lease: the taker's pid
is recorded and an expired slot is freed only when that pid is gone, because
under load a prepr routinely runs past ``LEASE_SECONDS`` and expiry-stealing
admitted a fifth while the first still ran. The exclusive lease keeps its
expiry rule, since a stress run measures the machine and must not be extended
past a waiter. ``slot-status`` counts both witnesses of an over-subscribed
pool: holders alive past their lease, and runs that could not take a slot at
all (``slot-unleased``).
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
# --- priority (#gate-priority, tvofi 2026-10-20) -----------------------------
# The lease carries an integer priority; it never decides who deserves one. The
# environment channel is what a caller prepr.sh cannot edit uses, and the
# ``priority=`` argument is what a Python caller or a test uses (it wins).
PRIORITY_ENV = "HPO_GATE_PRIORITY"
PRIORITY_NORMAL = 0
PRIORITY_MAX = 2
# A waiter this old is promoted to PRIORITY_MAX, so a normal ticket overtakes a
# higher priority that arrived later (module docstring states the rationale).
PRIORITY_AGING_SECONDS = 600
# --- the pool's liveness rule (R10-GATE-PRIORITY, tvofi 2026-10-20) ----------
# A slot is held for the LIFE of its run. `take_slot` records a pid (the
# caller's, else its own) and `_free_slot` frees an expired slot only when that
# pid is gone: a prepr under load routinely outlives the 30-minute lease, and
# expiry-based stealing let a later run take the freed slot while the first was
# still running, so the pool admitted more heavy runs than HEAVY_SLOTS while
# reporting the cap. The exclusive lease keeps its expiry rule -- a stress run
# measures the machine and must not be extended past a waiter.
UNLEASED_PREFIX = "unleased-"


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


def _ticket_tmp(lock_dir: Path, label: str, priority: int, queued_at: datetime) -> Path:
    """A ticket's full text in a private file, so no reader sees half of it."""
    tmp = lock_dir / f"tmp-{os.getpid()}-{time.monotonic_ns()}"
    expires = datetime.now(UTC) + timedelta(seconds=TICKET_SECONDS)
    tmp.write_text(
        f"label={label}\npid={os.getpid()}\nexpires_at={expires.isoformat()}\n"
        f"priority={priority}\nqueued_at={queued_at.isoformat()}\n"
    )
    return tmp


def _ticket_queued_at(ticket: Path | None) -> datetime:
    """The arrival stamp a rewritten ticket keeps, or now for a new one.

    ``_enqueue`` rewrites its ticket every poll, so an arrival time taken fresh
    at each rewrite would reset the waiter's age and aging would never fire.
    Only this process rewrites its own ticket, so a plain read is enough; a
    missing, unreadable or naive stamp starts the wait now rather than at an
    unknowable instant (fixer.md step 16).
    """
    if ticket is not None:
        try:
            stamp = datetime.fromisoformat(_fields(ticket.read_text())["queued_at"])
            if stamp.tzinfo is not None:
                return stamp
        except (OSError, KeyError, ValueError):
            pass
    return datetime.now(UTC)


def _enqueue(lock_dir: Path, label: str, ticket: Path | None, *,
             priority: int = PRIORITY_NORMAL) -> Path:
    """Refresh ``ticket`` in place, or join the back of the queue."""
    _ensure_lock_dir(lock_dir)
    tmp = _ticket_tmp(lock_dir, label, priority, _ticket_queued_at(ticket))
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


def _read_priority(raw: str | None) -> int:
    """A declared priority as an int in ``0..PRIORITY_MAX``; 0 for anything else.

    Absent, empty, non-integer and out-of-range values all land in the range
    rather than outranking work or crashing the queue: a caller's typo must not
    lift it above the owner's scale. This is the one parse the lease uses, on
    both the environment channel and a ticket's own field.
    """
    if not raw:
        return PRIORITY_NORMAL
    try:
        value = int(str(raw).strip())
    except ValueError:
        return PRIORITY_NORMAL
    return max(PRIORITY_NORMAL, min(PRIORITY_MAX, value))


def _declared_priority(priority: int | None) -> int:
    """The argument when given, else ``$HPO_GATE_PRIORITY``, else 0.

    Read once when a take begins: a waiter keeps the priority it declared for
    its whole wait, including every ticket rewrite.
    """
    if priority is not None:
        return _read_priority(str(priority))
    return _read_priority(os.environ.get(PRIORITY_ENV))


def _stamp_or_now(raw: str | None, now: datetime) -> datetime:
    """An aware arrival stamp, or ``now`` when it is absent, unreadable or naive."""
    try:
        stamp = datetime.fromisoformat(raw) if raw else None
    except ValueError:
        return now
    if stamp is None or stamp.tzinfo is None:
        return now
    return stamp


@dataclass(frozen=True)
class Waiter:
    """One live ticket: where it queues, who waits, and what it declared."""
    path: Path
    label: str
    priority: int
    queued_at: datetime

    def effective(self, now: datetime) -> int:
        """The priority the queue orders it by: aged waiters sit at the top."""
        if now - self.queued_at >= timedelta(seconds=PRIORITY_AGING_SECONDS):
            return PRIORITY_MAX
        return self.priority


def _queue(lock_dir: Path, now: datetime | None = None) -> list[Waiter]:
    """Live tickets, in the order the next free resource goes.

    Highest effective priority first, then arrival (the ``ticket-<n>``
    sequence, which a rewrite keeps). A ticket past ``PRIORITY_AGING_SECONDS``
    is promoted to ``PRIORITY_MAX``, so an aged normal waiter overtakes any
    priority that arrived later; arrival still orders within a band, so two
    aged waiters keep their FIFO order. Missing or malformed fields read as
    priority 0 and arrival now, and a dead or expired ticket is removed.
    """
    now = datetime.now(UTC) if now is None else now
    live: list[tuple[int, str, Waiter]] = []
    for path in sorted(lock_dir.glob(TICKET_PREFIX + "*")):
        try:
            f = _fields(path.read_text())
            alive = (_pid_alive(int(f["pid"]))
                     and now < datetime.fromisoformat(f["expires_at"]))
        except FileNotFoundError:
            continue
        except (OSError, KeyError, ValueError):
            alive = False
        if alive:
            waiter = Waiter(
                path=path,
                label=f["label"],
                priority=_read_priority(f.get("priority")),
                queued_at=_stamp_or_now(f.get("queued_at"), now),
            )
            live.append((-waiter.effective(now), path.name, waiter))
        else:
            path.unlink(missing_ok=True)
    live.sort(key=lambda row: (row[0], row[1]))
    return [waiter for _, _, waiter in live]


def take(
    label: str,
    *,
    lock_dir: Path = DEFAULT_LOCK_DIR,
    lease_seconds: int = LEASE_SECONDS,
    wait: bool = True,
    owner_pid: int | None = None,
    priority: int | None = None,
) -> Owner:
    """Acquire the gate lease for ``label``, queueing behind older live tickets.

    ``owner_pid`` names a process that outlives the commands holding the lease
    (a seat's ``$PPID``). It is recorded in the owner file so a later take can
    steal an orphaned lease whose holder exited without releasing (#1143).
    ``priority`` (or ``$HPO_GATE_PRIORITY``) places the waiter ahead of older
    tickets in a lower band; see the module docstring.
    """
    prio = _declared_priority(priority)
    said, ticket = False, None
    try:
        while True:
            owner = read_owner(lock_dir)
            if owner is None:
                _ensure_lock_dir(lock_dir)
                queue = _queue(lock_dir)
                if not queue or queue[0].path == ticket:
                    fresh = _new_owner(label, lease_seconds, owner_pid)
                    if fresh.create(lock_dir / OWNER_NAME):
                        return fresh
                    continue
                held = f"{queue[0].label}, at the head of the queue"
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
            ticket = _enqueue(lock_dir, label, ticket, priority=prio)
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
    # Any other label's ticket refuses, whatever priority it declared: a
    # priority tenant queues like everyone else and never extends past a waiter.
    waiting = [waiter.label for waiter in _queue(lock_dir) if waiter.label != label]
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
        "queue": [waiter.label for waiter in _queue(lock_dir)] if lock_dir.exists() else [],
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
    """The first slot that may be claimed, stealing an orphaned or unheld one.

    A missing file is free; an unreadable one is a broken holder, not a live
    one, and is replaced. A dead named pid is stolen at once (#1143's rule for
    the single lease), and the pool directory's own flock -- never held, since
    only the single lease takes flock -- makes ``_orphaned``'s gate honest.

    An expired slot whose named process is ALIVE is not free: the pool's lease
    is a liveness handle, so a run that outlives ``lease_seconds`` keeps its
    slot instead of being silently unleased beside an admitted fifth. Only a
    slot with no pid at all -- a hand-written or older-version file, where
    nothing proves the run is alive -- is freed on expiry.
    """
    for i in range(slots):
        path = _slot_path(pool, i)
        owner = _read_at(path)
        if owner is None:
            if not path.is_file():
                return i
            path.unlink(missing_ok=True)  # unparseable: no live holder to lose
            return i
        if _orphaned(pool, owner) or (owner.expired and owner.pid is None):
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
    priority: int | None = None,
) -> tuple[int, Owner]:
    """Claim one of ``slots`` heavy slots for ``label``; return (index, owner).

    Priority, then arrival like the single lease: while every slot is held a
    caller queues behind older live tickets, and a free slot goes to the oldest
    ticket in the highest band present, so a fifth caller waits rather than
    loading the box. ``owner_pid`` names a process that outlives the commands
    holding the slot, so a later take steals a slot whose seat has exited
    (#1143); when it is omitted the taking process's own pid is recorded, and
    that live pid is what holds the slot past ``expires_at`` (``_free_slot``).
    ``slots`` defaults to `heavy_slots()`, the pool's own capacity.
    ``priority`` (or ``$HPO_GATE_PRIORITY``) orders the waiter; see the module
    docstring.
    """
    if slots is None:
        slots = heavy_slots()
    if slots < 1:
        raise ValueError("slots must be at least 1")
    prio = _declared_priority(priority)
    # A slot is held for one process's run, so the pool always records SOME
    # pid: the caller's (a shell that outlives a one-shot take) or this
    # process's (a slot-auto-lease wrapping the run). The single lease keeps
    # its opt-in rule because it is held ACROSS commands, where the invoker's
    # pid is a per-command shell (#1143).
    holder_pid = owner_pid if owner_pid is not None else os.getpid()
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
                    pid=owner_pid if owner_pid is not None else (owner.pid or holder_pid),
                )
                fresh.write(_slot_path(pool, index))
                return index, fresh
            free = _free_slot(pool, slots)
            if free is not None:
                queue = _queue(pool)
                if not queue or queue[0].path == ticket:
                    fresh = _new_owner(label, lease_seconds, holder_pid)
                    if fresh.create(_slot_path(pool, free)):
                        return free, fresh
                    continue  # another caller won the O_EXCL create; try again
                held = f"{queue[0].label}, at the head of the queue"
            else:
                held = _held_slots(pool, slots)
            if not wait:
                raise BlockingIOError(f"all {slots} heavy slots held: {held}")
            ticket = _enqueue(pool, label, ticket, priority=prio)
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


def _unleased(pool: Path) -> list[str]:
    """Runs that could not take a slot and are executing anyway (live pids).

    The marker is written by ``mark_unleased`` -- `prepr.sh`'s failed-take arm --
    and a dead one is removed here, so the count is of runs actually in flight.
    """
    found = []
    for path in sorted(pool.glob(UNLEASED_PREFIX + "*")):
        try:
            pid = int(_fields(path.read_text()).get("pid", ""))
        except (OSError, ValueError):
            path.unlink(missing_ok=True)
            continue
        if _pid_alive(pid):
            found.append(path.name[len(UNLEASED_PREFIX):])
        else:
            path.unlink(missing_ok=True)
    return found


def _marker_path(pool: Path, label: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-._" else "-" for c in label)
    return pool / f"{UNLEASED_PREFIX}{safe}"


def mark_unleased(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR,
                  pid: int | None = None) -> Path:
    """Record that ``label`` runs unleased, counted by `slots_status`.

    The witness a failed take owes: a pool that cannot admit a run must be
    visible to the next orchestrator, not inferred from load.
    """
    pool = pool_dir(lock_dir)
    _ensure_lock_dir(pool)
    path = _marker_path(pool, label)
    path.write_text(f"pid={os.getpid() if pid is None else pid}\nlabel={label}\n")
    return path


def clear_unleased(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR) -> bool:
    """Remove ``label``'s unleased marker; False when it carried none."""
    path = _marker_path(pool_dir(lock_dir), label)
    existed = path.exists()
    path.unlink(missing_ok=True)
    return existed


def slots_status(
    *, lock_dir: Path = DEFAULT_LOCK_DIR, slots: int | None = None
) -> dict[str, object]:
    slots = heavy_slots() if slots is None else slots
    pool = pool_dir(lock_dir)
    holders: list[Owner | None] = []
    for i in range(slots):
        holders.append(_read_at(_slot_path(pool, i)))
    # Two witnesses of an over-subscribed pool: holders whose named process is
    # still running past their lease (they hold, and the lease was too short),
    # and runs that never got a slot at all.
    past_lease = [
        f"{i}:{owner.label}" for i, owner in enumerate(holders)
        if owner is not None and owner.expired
        and owner.pid is not None and _pid_alive(owner.pid)
    ]
    return {
        "pool_dir": str(pool),
        "slots": slots,
        "holders": holders,
        "queue": [waiter.label for waiter in _queue(pool)] if pool.exists() else [],
        "past_lease": past_lease,
        "unleased": _unleased(pool) if pool.exists() else [],
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
    re-taken. None means the table has no such script -- a script nothing has
    timed, which `needs_lease` sends to the slots rather than unleased.
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

    Two fail-closed arms, deliberately different. A scope that names a
    MACHINE_MEASURING script is leased whatever the recordings say. And a name
    the recordings do NOT carry -- `tests/rolling.py` is the one run.sh
    dispatches, gated behind `SLOW=1` so nothing ever timed it -- JOINS THE
    SLOTS: an untimed script's weight is unknown, and the conservative answer
    for an unknown is the pool, which bounds it, never `none`, which leaves it
    unbounded beside three other scripts. Only a table that cannot be read at
    all -- a corrupted tree, where no name at all can be classified -- takes
    the exclusive lease.
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
    for name in names:
        seconds = _recorded_seconds(name)
        if seconds is None or seconds >= SLOT_MIN_SECONDS:
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
    held = []
    for i, owner in enumerate(info["holders"]):
        if owner is None:
            continue
        # "expired" is a claim that a taker may take it; a live-pid holder past
        # its lease still holds, so the status must not read as free.
        if owner.expired:
            state = ("live-past-lease" if owner.pid is not None and _pid_alive(owner.pid)
                     else "expired")
        else:
            state = "live"
        held.append(f"{i}:{owner.label}({state})")
    past = info["past_lease"]
    unleased = info["unleased"]
    print(
        f"{info['pool_dir']}: {len(held)}/{info['slots']} slots held "
        f"[{', '.join(held) or '-'}] queue={','.join(info['queue']) or '-'} "
        f"past-lease={len(past)}{'(' + ','.join(past) + ')' if past else ''} "
        f"unleased={len(unleased)}"
        f"{'(' + ','.join(unleased) + ')' if unleased else ''}"
    )
    return 0


def _cmd_slot_unleased(args: argparse.Namespace) -> int:
    mark_unleased(args.label, lock_dir=args.lock_dir, pid=args.pid)
    return 0


def _cmd_slot_leased(args: argparse.Namespace) -> int:
    clear_unleased(args.label, lock_dir=args.lock_dir)
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

    slot_un_p = sub.add_parser(
        "slot-unleased", help="count a run that could not take a slot"
    )
    slot_un_p.add_argument("--label", required=True)
    slot_un_p.add_argument("--pid", type=int, default=None,
                           help="the running process (default: this one)")
    slot_un_p.set_defaults(func=_cmd_slot_unleased)

    slot_cl_p = sub.add_parser(
        "slot-leased", help="remove a label's unleased marker"
    )
    slot_cl_p.add_argument("--label", required=True)
    slot_cl_p.set_defaults(func=_cmd_slot_leased)

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


def _priority_cases(g) -> list[tuple[str, bool, str]]:
    """The priority channel's cases, against module ``g`` -- this one, or
    origin/main's copy loaded beside it, where the ordering arms fail because
    the base lease ignores both the environment and a ticket's priority, and
    the concurrency control holds either way.

    Every arm states the property rather than an instance. The ordering arms
    set ``HPO_GATE_PRIORITY`` in the process while a waiter ENTERS ``take``
    (its priority is read once, at entry), and read the order the waiters were
    released in. The aging arm drives ``_queue(now=...)`` with a stated clock,
    so no arm sleeps a window. The concurrency arm counts holders inside the
    pool, so two grants in one poll show up as a count, not an argument.
    """
    import tempfile
    import threading

    env_name = "HPO_GATE_PRIORITY"
    poll = g.WAIT_POLL_SECS

    class _Env:
        def __init__(self, value: str | None):
            self.value = value

        def __enter__(self):
            self.saved = os.environ.get(env_name)
            if self.value is None:
                os.environ.pop(env_name, None)
            else:
                os.environ[env_name] = self.value

        def __exit__(self, *exc):
            os.environ.pop(env_name, None)
            if self.saved is not None:
                os.environ[env_name] = self.saved

    def ticket_text(d: Path, who: str, limit: float = 8.0) -> str:
        """The ticket ``who`` waits on, read back; "" when it never queues."""
        end = time.monotonic() + limit
        while time.monotonic() < end:
            for p in d.glob(g.TICKET_PREFIX + "*"):
                try:
                    text = p.read_text()
                except OSError:
                    continue
                if f"label={who}\n" in text:
                    return text
            time.sleep(0.02)
        return ""

    def rewritten(d: Path, who: str, first: str, limit: float = 8.0) -> str:
        """The ticket after at least one poll rewrote it: its expiry moved.

        An instrument for the rewrite property rather than a sleep: a ticket
        only counts as rewritten once ``expires_at`` has advanced past the
        stamp read when it first queued.
        """
        seen = _fields(first).get("expires_at")
        end = time.monotonic() + limit
        while time.monotonic() < end:
            for p in d.glob(g.TICKET_PREFIX + "*"):
                try:
                    text = p.read_text()
                except OSError:
                    continue
                if f"label={who}\n" in text and _fields(text).get("expires_at") != seen:
                    return text
            time.sleep(0.02)
        return ""

    def priority_first(d: Path, got: list[str]) -> tuple[bool, str]:
        g.WAIT_POLL_SECS = 0.1
        g.take("h", lock_dir=d, lease_seconds=60, wait=False)

        def one(who: str) -> None:
            g.take(who, lock_dir=d, lease_seconds=60)
            got.append(who)
            time.sleep(0.15)
            g.release(who, lock_dir=d)

        normal = threading.Thread(target=one, args=("normal",), daemon=True)
        normal.start()
        normal_queued = bool(ticket_text(d, "normal"))
        with _Env("2"):
            urgent = threading.Thread(target=one, args=("urgent",), daemon=True)
            urgent.start()
            urgent_queued = ticket_text(d, "urgent")
        # Wait for an actual rewrite, not a sleep: the priority must survive
        # the poll that refreshes the ticket the queue will read next.
        after_rewrite = rewritten(d, "urgent", urgent_queued) if urgent_queued else ""
        g.release("h", lock_dir=d)
        normal.join(20)
        urgent.join(20)
        ok = (normal_queued and bool(urgent_queued) and "priority=2" in urgent_queued
              and "priority=2" in after_rewrite and got == ["urgent", "normal"])
        return ok, (f"queued={normal_queued}/{bool(urgent_queued)} "
                    f"rewrite={'priority=2' in after_rewrite} order={got}")

    def rewrite_keeps(d: Path, got: list[str]) -> tuple[bool, str]:
        g._ensure_lock_dir(d)
        path = g._enqueue(d, "w", None, priority=2)
        first = _fields(path.read_text())
        time.sleep(0.05)
        again = g._enqueue(d, "w", path, priority=2)
        second = _fields(again.read_text())
        ok = (again == path and first.get("priority") == "2"
              and second.get("priority") == "2"
              and first.get("queued_at") and first.get("queued_at") == second.get("queued_at"))
        return ok, (f"same_path={again == path} priority={first.get('priority')}/"
                    f"{second.get('priority')} queued_at_kept="
                    f"{first.get('queued_at') == second.get('queued_at')}")

    def aging(d: Path, got: list[str]) -> tuple[bool, str]:
        window = g.PRIORITY_AGING_SECONDS
        now = datetime.now(UTC)

        def ticket(where: Path, n: int, who: str, prio: int, age: int) -> None:
            g._ensure_lock_dir(where)
            (where / f"{g.TICKET_PREFIX}{n:012d}").write_text(
                f"label={who}\npid={os.getpid()}\n"
                f"expires_at={(now + timedelta(seconds=window + 900)).isoformat()}\n"
                f"priority={prio}\nqueued_at={(now - timedelta(seconds=age)).isoformat()}\n")

        old, young = d / "old", d / "young"
        ticket(old, 1, "normal", g.PRIORITY_NORMAL, window + 1)
        ticket(old, 2, "urgent", g.PRIORITY_MAX, 60)
        aged = [w.label for w in g._queue(old, now=now)]
        # Null control: one second short of the window the same pair is FIFO by
        # priority, so this arm binds on the threshold, not on age alone.
        ticket(young, 1, "normal", g.PRIORITY_NORMAL, window - 1)
        ticket(young, 2, "urgent", g.PRIORITY_MAX, 60)
        below = [w.label for w in g._queue(young, now=now)]
        return aged == ["normal", "urgent"] and below == ["urgent", "normal"], \
            f"aged={aged} below={below}"

    def malformed(d: Path, got: list[str]) -> tuple[bool, str]:
        now = datetime.now(UTC)
        g._ensure_lock_dir(d)

        def ticket(n: int, who: str, extra: str) -> None:
            (d / f"{g.TICKET_PREFIX}{n:012d}").write_text(
                f"label={who}\npid={os.getpid()}\n"
                f"expires_at={(now + timedelta(seconds=600)).isoformat()}\n" + extra)

        ticket(1, "absent", "")                                    # no fields at all
        ticket(2, "junk", "priority=junk\n")                       # unparseable
        ticket(3, "over", "priority=9\n")                          # clamps to the top
        ticket(4, "negative", "priority=-4\n")                     # clamps to normal
        ticket(5, "float", "priority=2.5\nqueued_at=not-a-time\n")  # both unreadable
        order = [w.label for w in g._queue(d, now=now)]
        parsed = [g._read_priority(v) for v in
                  (None, "", "junk", "9", "-4", "2.5", " 1 ")]
        ok = (order == ["over", "absent", "junk", "negative", "float"]
              and parsed == [0, 0, 0, 2, 0, 0, 1])
        return ok, f"order={order} parsed={parsed}"

    def renew_refused(d: Path, got: list[str]) -> tuple[bool, str]:
        g.WAIT_POLL_SECS = 0.1
        g.take("h", lock_dir=d, lease_seconds=60, wait=False)

        def one() -> None:
            g.take("urgent", lock_dir=d, lease_seconds=60)
            got.append("urgent")
            time.sleep(0.1)
            g.release("urgent", lock_dir=d)

        with _Env("2"):
            thread = threading.Thread(target=one, daemon=True)
            thread.start()
            queued = bool(ticket_text(d, "urgent"))
        try:
            g.renew("h", lock_dir=d, lease_seconds=60)
            refused = False
        except RuntimeError:
            refused = True
        g.release("h", lock_dir=d)
        thread.join(20)
        return refused and queued and got == ["urgent"], f"refused={refused} order={got}"

    def slot_priority(d: Path, got: list[str]) -> tuple[bool, str]:
        g.WAIT_POLL_SECS = 0.1
        pool = g.pool_dir(d)
        g.take_slot("h", lock_dir=d, slots=1, lease_seconds=60, wait=False)

        def one(who: str) -> None:
            g.take_slot(who, lock_dir=d, slots=1, lease_seconds=60)
            got.append(who)
            time.sleep(0.1)
            g.release_slot(who, lock_dir=d, slots=1)

        normal = threading.Thread(target=one, args=("normal",), daemon=True)
        normal.start()
        normal_queued = bool(ticket_text(pool, "normal"))
        with _Env("2"):
            urgent = threading.Thread(target=one, args=("urgent",), daemon=True)
            urgent.start()
            urgent_queued = ticket_text(pool, "urgent")
        g.release_slot("h", lock_dir=d, slots=1)
        normal.join(20)
        urgent.join(20)
        ok = (normal_queued and bool(urgent_queued)
              and "priority=2" in urgent_queued and got == ["urgent", "normal"])
        return ok, f"queued={normal_queued}/{bool(urgent_queued)} order={got}"

    def one_winner(d: Path, got: list[str]) -> tuple[bool, str]:
        g.WAIT_POLL_SECS = 0.05
        pool = g.pool_dir(d)
        g.take_slot("holder", lock_dir=d, slots=1, lease_seconds=60, wait=False)
        inside, overlaps, guard = [0], [0], threading.Lock()

        def one(who: str) -> None:
            g.take_slot(who, lock_dir=d, slots=1, lease_seconds=60)
            with guard:
                if inside[0]:
                    overlaps[0] += 1
                inside[0] += 1
            time.sleep(0.15)
            with guard:
                inside[0] -= 1
            got.append(who)
            g.release_slot(who, lock_dir=d, slots=1)

        threads = [threading.Thread(target=one, args=(w,), daemon=True) for w in ("a", "b")]
        [t.start() for t in threads]
        queued = bool(ticket_text(pool, "a")) and bool(ticket_text(pool, "b"))
        g.release_slot("holder", lock_dir=d, slots=1)
        [t.join(20) for t in threads]
        ok = queued and sorted(got) == ["a", "b"] and overlaps[0] == 0
        return ok, f"queued={queued} overlaps={overlaps[0]} order={got}"

    cases = [
        ("priority: an urgent waiter takes before an older normal one, after its ticket rewrite",
         priority_first),
        ("priority: a ticket rewrite keeps its priority and its arrival stamp", rewrite_keeps),
        ("priority: aging promotes a normal waiter past a later urgent one, and only past the window",
         aging),
        ("priority: malformed, absent and out-of-range values are 0 or clamped, never a crash",
         malformed),
        ("priority: a waiting tenant still refuses renew, and queues ahead after the release",
         renew_refused),
        ("priority: the heavy-slot pool orders by the same rule", slot_priority),
        ("concurrency control: two waiters released in one poll, exactly one holds the slot",
         one_winner),
    ]
    out: list[tuple[str, bool, str]] = []
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


def _slot_hold_cases(g) -> list[tuple[str, bool, str]]:
    """The pool's liveness rule and its two witnesses, against module ``g``.

    A slot is held for the life of its run: a holder whose named process is
    alive keeps it past ``expires_at``, a dead or absent one is stolen at once,
    and only a legacy slot with no pid is freed by expiry alone. Every arm
    PLANTS the lease state it measures -- a past ``expires_at`` -- so none
    sleeps a lease, and the live-pid arms use this process, which cannot die
    mid-case.
    """
    import tempfile
    import threading

    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    poll = g.WAIT_POLL_SECS

    def pool(d: Path) -> Path:
        return g.pool_dir(d)

    def plant(d: Path, pid: int | None) -> None:
        g._ensure_lock_dir(pool(d))
        past = datetime.now(UTC) - timedelta(seconds=60)
        g.Owner("holder", past, past - timedelta(seconds=600), pid).write(
            g._slot_path(pool(d), 0))

    def take_taker(d: Path, who: str, slots: int = 1) -> bool:
        try:
            g.take_slot(who, lock_dir=d, slots=slots, lease_seconds=60, wait=False)
            return True
        except BlockingIOError:
            return False

    def take_fifth(d: Path, slots: int = 1) -> bool:
        return take_taker(d, "fifth", slots)

    def live_holds(d: Path, got: list[str]) -> tuple[bool, str]:
        plant(d, os.getpid())
        blocked = not take_fifth(d)
        status = g.slots_status(lock_dir=d, slots=1)
        # A real take records a pid even when the caller names none: without it
        # the liveness rule above would free the slot at expiry.
        g.take_slot("recording", lock_dir=d, slots=2, lease_seconds=60, wait=False)
        recorded = g._read_at(g._slot_path(pool(d), 1))
        names_pid = recorded is not None and recorded.pid == os.getpid()
        ok = (blocked and names_pid and status["past_lease"] == ["0:holder"]
              and status["unleased"] == [])
        return ok, (f"blocked={blocked} names_pid={names_pid} "
                    f"past_lease={status['past_lease']}")

    def dead_stolen(d: Path, got: list[str]) -> tuple[bool, str]:
        # The control the liveness rule binds on: the SAME past expiry, with the
        # named process gone, must free the slot at once.
        plant(d, dead.pid)
        took = take_fifth(d)
        return took, f"stolen={took}"

    def no_pid_freed(d: Path, got: list[str]) -> tuple[bool, str]:
        # A legacy slot names no process, so nothing proves its run is alive:
        # expiry frees it. A fresh one is still respected (the other arm), so
        # the rule binds on expiry and not on the absence of a pid alone.
        plant(d, None)
        expired_taken = take_fifth(d)
        g._ensure_lock_dir(pool(d))
        now = datetime.now(UTC)
        g.Owner("holder", now + timedelta(seconds=600), now, None).write(
            g._slot_path(pool(d), 1))
        fresh_blocked = not take_taker(d, "sixth", slots=2)
        return expired_taken and fresh_blocked, \
            f"expired_taken={expired_taken} fresh_blocked={fresh_blocked}"

    def queues_then_takes(d: Path, got: list[str]) -> tuple[bool, str]:
        plant(d, os.getpid())
        g.WAIT_POLL_SECS = 0.05

        def one() -> None:
            index, _owner = g.take_slot("fifth", lock_dir=d, slots=1, lease_seconds=60)
            got.append(f"fifth:{index}")

        thread = threading.Thread(target=one, daemon=True)
        thread.start()
        queued, end = False, time.monotonic() + 8
        while time.monotonic() < end and not queued:
            queued = any(w.label == "fifth" for w in g._queue(pool(d)))
            time.sleep(0.02)
        # The holder finishes: its slot file goes, exactly as release_slot does.
        g._slot_path(pool(d), 0).unlink(missing_ok=True)
        thread.join(20)
        held = g._slot_of(pool(d), 1, "fifth") is not None
        return queued and got == ["fifth:0"] and held, \
            f"queued={queued} order={got} holds={held}"

    def witnesses(d: Path, got: list[str]) -> tuple[bool, str]:
        plant(d, os.getpid())
        marker = g.mark_unleased("prepr-x", lock_dir=d, pid=os.getpid())
        counted = g.slots_status(lock_dir=d, slots=1)
        before = (counted["past_lease"] == ["0:holder"]
                  and counted["unleased"] == ["prepr-x"])
        g.clear_unleased("prepr-x", lock_dir=d)
        after = g.slots_status(lock_dir=d, slots=1)["unleased"]
        cleared = after == [] and not marker.exists()
        g.mark_unleased("prepr-dead", lock_dir=d, pid=dead.pid)
        pruned = g.slots_status(lock_dir=d, slots=1)["unleased"] == []
        return before and cleared and pruned, \
            f"counted={before} cleared={cleared} dead_pruned={pruned}"

    cases = [
        ("a live holder keeps its slot past its lease, and a fifth taker is blocked",
         live_holds),
        ("a slot whose named process is gone is stolen at once (null control)",
         dead_stolen),
        ("a legacy slot with no pid is freed on expiry; a fresh one is respected",
         no_pid_freed),
        ("a taker queues behind a live past-lease holder and takes the slot when it frees",
         queues_then_takes),
        ("slot-status counts past-lease holders and unleased runs, and prunes a dead marker",
         witnesses),
    ]
    out: list[tuple[str, bool, str]] = []
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

    R.section("priority")
    for name, ok, detail in _priority_cases(sys.modules[__name__]):
        R.check(name, ok, detail)

    R.section("heavy-slot holds")
    for name, ok, detail in _slot_hold_cases(sys.modules[__name__]):
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
