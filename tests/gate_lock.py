#!/usr/bin/env python3
"""Renewed-lease gate lock with flock for local stress runs (#404).

Serialises anything that runs ``tests/stress.py`` on a shared box. The owner
file carries an ``expires_at`` lease and an agent label — not a shell pid.
``flock`` is held only for the duration of a gate run; the lease covers the
window between commands when no process holds anything. An expired lease or
an abandoned hold (``holding`` marker, flock dropped) is taken without
forensics so a waiter can proceed after crash or expiry.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Above 735 s full gate / 560 s stress on the owner's box (#404).
LEASE_SECONDS = 1800
DEFAULT_LOCK_DIR = Path("/tmp/hpo-gate.lock")
OWNER_NAME = "owner"
FLOCK_NAME = "flock"
HOLDING_NAME = "holding"
WAIT_POLL_SECS = 5


@dataclass(frozen=True)
class Owner:
    label: str
    expires_at: datetime
    taken_at: datetime

    def write(self, path: Path) -> None:
        path.write_text(
            f"label={self.label}\n"
            f"expires_at={self.expires_at.isoformat()}\n"
            f"taken_at={self.taken_at.isoformat()}\n"
        )

    @property
    def expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at


def parse_owner(text: str) -> Owner:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    missing = {"label", "expires_at", "taken_at"} - fields.keys()
    if missing:
        raise ValueError(f"owner file missing {sorted(missing)}")
    return Owner(
        label=fields["label"],
        expires_at=datetime.fromisoformat(fields["expires_at"]),
        taken_at=datetime.fromisoformat(fields["taken_at"]),
    )


def read_owner(lock_dir: Path) -> Owner | None:
    owner_path = lock_dir / OWNER_NAME
    if not owner_path.is_file():
        return None
    try:
        return parse_owner(owner_path.read_text())
    except (OSError, ValueError):
        return None


def _new_owner(label: str, lease_seconds: int) -> Owner:
    now = datetime.now(UTC)
    return Owner(
        label=label,
        taken_at=now,
        expires_at=now + timedelta(seconds=lease_seconds),
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
        yield
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


def _clear_stale_holding(lock_dir: Path) -> None:
    # Same-label return after crash: leftover holding would let a waiter steal.
    if _abandoned_hold(lock_dir):
        (lock_dir / HOLDING_NAME).unlink(missing_ok=True)


def take(
    label: str,
    *,
    lock_dir: Path = DEFAULT_LOCK_DIR,
    lease_seconds: int = LEASE_SECONDS,
    wait: bool = True,
) -> Owner:
    """Acquire the gate lease for ``label``; wait while a live holder renews."""
    while True:
        owner = read_owner(lock_dir)
        if owner is None:
            if not lock_dir.exists():
                _ensure_lock_dir(lock_dir)
            fresh = _new_owner(label, lease_seconds)
            fresh.write(lock_dir / OWNER_NAME)
            return fresh
        if owner.label == label:
            _clear_stale_holding(lock_dir)
            if owner.expired:
                fresh = _new_owner(label, lease_seconds)
                fresh.write(lock_dir / OWNER_NAME)
                return fresh
            return renew(label, lock_dir=lock_dir, lease_seconds=lease_seconds)
        if owner.expired or _abandoned_hold(lock_dir):
            _clear_lock(lock_dir)
            continue
        if not wait:
            raise BlockingIOError(f"gate held by {owner.label} until {owner.expires_at}")
        time.sleep(WAIT_POLL_SECS)


def renew(
    label: str,
    *,
    lock_dir: Path = DEFAULT_LOCK_DIR,
    lease_seconds: int = LEASE_SECONDS,
) -> Owner:
    owner = read_owner(lock_dir)
    if owner is None or owner.expired:
        raise RuntimeError("no live gate lease to renew")
    if owner.label != label:
        raise RuntimeError(f"lease held by {owner.label}, not {label}")
    refreshed = Owner(
        label=label,
        taken_at=owner.taken_at,
        expires_at=datetime.now(UTC) + timedelta(seconds=lease_seconds),
    )
    refreshed.write(lock_dir / OWNER_NAME)
    _clear_stale_holding(lock_dir)
    return refreshed


def release(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR) -> bool:
    owner = read_owner(lock_dir)
    if owner is None:
        return False
    if owner.label != label:
        raise RuntimeError(f"lease held by {owner.label}, not {label}")
    _clear_lock(lock_dir)
    return True


def status(lock_dir: Path = DEFAULT_LOCK_DIR) -> dict[str, object]:
    owner = read_owner(lock_dir)
    return {
        "lock_dir": str(lock_dir),
        "owner": owner,
        "flock_available": flock_available(lock_dir) if lock_dir.exists() else True,
    }


def flock_wrap(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR) -> int:
    """Renew the lease, hold flock for ``argv``, release flock on exit."""
    renew(label, lock_dir=lock_dir)
    with flock_context(lock_dir, blocking=True):
        return subprocess.call(argv)


def _cmd_take(args: argparse.Namespace) -> int:
    owner = take(
        args.label,
        lock_dir=args.lock_dir,
        lease_seconds=args.lease_seconds,
        wait=not args.no_wait,
    )
    print(
        f"taken label={owner.label} expires_at={owner.expires_at.isoformat()}",
        file=sys.stderr,
    )
    return 0


def _cmd_renew(args: argparse.Namespace) -> int:
    owner = renew(args.label, lock_dir=args.lock_dir, lease_seconds=args.lease_seconds)
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
        print(
            f"{info['lock_dir']}: {state} label={owner.label} "
            f"expires_at={owner.expires_at.isoformat()} "
            f"flock_available={info['flock_available']}"
        )
    return 0


def _cmd_flock_wrap(args: argparse.Namespace) -> int:
    return flock_wrap(args.label, args.argv, lock_dir=args.lock_dir)


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
    take_p.set_defaults(func=_cmd_take)

    renew_p = sub.add_parser("renew", help="extend the lease for this label")
    renew_p.add_argument("--label", required=True)
    renew_p.add_argument("--lease-seconds", type=int, default=LEASE_SECONDS)
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

    return p


# --- acceptance (#404) -------------------------------------------------------


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

    for d in (d1, d2, d3, d4):
        if d.exists():
            _clear_lock(d)

    return R.close("gate lock acceptance checks")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--accept":
        sys.exit(_acceptance())
    args = _parser().parse_args()
    if args.cmd == "flock-wrap" and args.argv[:1] == ["--"]:
        args.argv = args.argv[1:]
    sys.exit(args.func(args))
