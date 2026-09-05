"""Renewed lease + flock for ``/tmp/hpo-gate.lock`` (#404).

The owner file carries ``label`` and ``expires_at``, not a shell pid. Every
command under the lock renews the lease. An expired lease is taken with no
process-table forensics. A crash mid-command leaves ``holding`` without a
live flock, which is also takeable immediately. A live agent between
commands has a valid lease and no ``holding`` file, so the next taker waits.
"""
from __future__ import annotations

import argparse
import fcntl
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

DEFAULT_LOCK_DIR = Path("/tmp/hpo-gate.lock")
LEASE_SECONDS = 30 * 60

_OWNER = "owner"
_FLOCK = "flock"
_HOLDING = "holding"


@dataclass(frozen=True)
class Status:
    label: str
    expires_at: datetime
    expired: bool
    flock_held: bool


class _Held(Exception):
    def __init__(self, owner: Status, flock_held: bool) -> None:
        self.owner = owner
        self.flock_held = flock_held


def _when(now: datetime | None) -> datetime:
    return now if now is not None else datetime.now(UTC)


def _root(lock_dir: Path | str | None) -> Path:
    return Path(lock_dir) if lock_dir is not None else DEFAULT_LOCK_DIR


def _parse_owner(text: str) -> tuple[str, datetime] | None:
    label = None
    expires = None
    for line in text.splitlines():
        if line.startswith("label="):
            label = line[6:]
        elif line.startswith("expires_at="):
            expires = datetime.fromisoformat(line[11:])
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=UTC)
    if not label or expires is None:
        return None
    return label, expires


def _write_owner(lock_dir: Path, label: str, expires_at: datetime) -> None:
    lock_dir.mkdir(parents=True, exist_ok=True)
    (lock_dir / _OWNER).write_text(
        f"label={label}\nexpires_at={expires_at.isoformat()}\n"
    )


def _read_owner(lock_dir: Path) -> tuple[str, datetime] | None:
    path = lock_dir / _OWNER
    if not path.is_file():
        return None
    return _parse_owner(path.read_text())


def _flock_is_held(lock_dir: Path) -> bool:
    path = lock_dir / _FLOCK
    if not path.exists():
        return False
    fd = os.open(path, os.O_RDWR)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    finally:
        os.close(fd)


def _abandoned_hold(lock_dir: Path) -> bool:
    # Crash mid-hold: marker remains, kernel dropped flock.
    return (lock_dir / _HOLDING).exists() and not _flock_is_held(lock_dir)


def _refuse(owner: Status) -> None:
    print(
        f"gate lock: held by {owner.label} until {owner.expires_at.isoformat()} "
        "(renewed lease; do not forensic pids). "
        "Wait, pass --wait, or take it when the lease expires.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def _block_flock(lock_dir: Path) -> None:
    lock_dir.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_dir / _FLOCK, os.O_RDWR | os.O_CREAT)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _take_once(label: str, lock_dir: Path, now: datetime, lease_s: int) -> None:
    expires = now + timedelta(seconds=lease_s)
    parsed = _read_owner(lock_dir) if lock_dir.exists() else None
    if parsed is None:
        _write_owner(lock_dir, label, expires)
        return
    cur_label, cur_exp = parsed
    if cur_label == label:
        _write_owner(lock_dir, label, expires)
        return
    if cur_exp <= now or _abandoned_hold(lock_dir):
        _write_owner(lock_dir, label, expires)
        (lock_dir / _HOLDING).unlink(missing_ok=True)
        return
    flock_held = _flock_is_held(lock_dir)
    raise _Held(
        Status(cur_label, cur_exp, expired=False, flock_held=flock_held),
        flock_held,
    )


def take(
    label: str,
    *,
    lock_dir: Path | str | None = None,
    now: datetime | None = None,
    lease_s: int = LEASE_SECONDS,
    wait: bool = False,
    poll_s: float = 0.25,
) -> None:
    root = _root(lock_dir)
    if not wait:
        try:
            _take_once(label, root, _when(now), lease_s)
        except _Held as exc:
            _refuse(exc.owner)
        return
    while True:
        try:
            _take_once(label, root, _when(now), lease_s)
            return
        except _Held as exc:
            if exc.flock_held:
                _block_flock(root)
            else:
                time.sleep(poll_s)


def renew(
    label: str,
    *,
    lock_dir: Path | str | None = None,
    now: datetime | None = None,
    lease_s: int = LEASE_SECONDS,
) -> None:
    root = _root(lock_dir)
    parsed = _read_owner(root) if root.exists() else None
    if parsed is None or parsed[0] != label:
        print("gate lock: renew refused (not the holder)", file=sys.stderr)
        raise SystemExit(1)
    _write_owner(root, label, _when(now) + timedelta(seconds=lease_s))


def release(label: str, *, lock_dir: Path | str | None = None) -> None:
    root = _root(lock_dir)
    parsed = _read_owner(root) if root.exists() else None
    if parsed is None:
        return
    if parsed[0] != label:
        print(f"gate lock: release refused (held by {parsed[0]})", file=sys.stderr)
        raise SystemExit(1)
    shutil.rmtree(root)


def status(
    *,
    lock_dir: Path | str | None = None,
    now: datetime | None = None,
) -> Status | None:
    root = _root(lock_dir)
    parsed = _read_owner(root) if root.exists() else None
    if parsed is None:
        return None
    label, expires = parsed
    return Status(
        label,
        expires,
        expired=expires <= _when(now),
        flock_held=_flock_is_held(root),
    )


class hold:
    """Hold flock for one command; leave the lease in place on the way out."""

    def __init__(
        self,
        label: str,
        *,
        lock_dir: Path | str | None = None,
        now: datetime | None = None,
        lease_s: int = LEASE_SECONDS,
    ) -> None:
        self.label = label
        self.lock_dir = _root(lock_dir)
        self.now = now
        self.lease_s = lease_s
        self._fd: int | None = None

    def __enter__(self) -> hold:
        take(self.label, lock_dir=self.lock_dir, now=self.now, lease_s=self.lease_s)
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self._fd = os.open(self.lock_dir / _FLOCK, os.O_RDWR | os.O_CREAT)
        (self.lock_dir / _HOLDING).write_text(self.label + "\n")
        fcntl.flock(self._fd, fcntl.LOCK_EX)
        renew(self.label, lock_dir=self.lock_dir, now=self.now, lease_s=self.lease_s)
        return self

    def __exit__(self, *exc: object) -> None:
        holding = self.lock_dir / _HOLDING
        holding.unlink(missing_ok=True)
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
            finally:
                os.close(self._fd)
                self._fd = None
        if self.lock_dir.exists() and _read_owner(self.lock_dir):
            try:
                renew(
                    self.label,
                    lock_dir=self.lock_dir,
                    now=self.now,
                    lease_s=self.lease_s,
                )
            except SystemExit:
                pass


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd: list[str] = []
    if "--" in argv:
        split = argv.index("--")
        cmd = argv[split + 1 :]
        argv = argv[:split]
    parser = argparse.ArgumentParser(
        description="Gate lock: renewed lease + flock (#404).",
    )
    parser.add_argument(
        "command", choices=["take", "renew", "release", "status", "hold"],
    )
    parser.add_argument("--label", default="")
    parser.add_argument("--lock-dir", default=str(DEFAULT_LOCK_DIR))
    parser.add_argument("--lease-s", type=int, default=LEASE_SECONDS)
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.lock_dir)
    if args.command == "status":
        st = status(lock_dir=root)
        if st is None:
            print("free")
            return 0
        state = "expired" if st.expired else "held"
        print(
            f"{state} label={st.label} expires_at={st.expires_at.isoformat()} "
            f"flock_held={int(st.flock_held)}"
        )
        return 0
    if not args.label:
        print("gate lock: --label is required", file=sys.stderr)
        return 2
    if args.command == "take":
        take(args.label, lock_dir=root, lease_s=args.lease_s, wait=args.wait)
        return 0
    if args.command == "renew":
        renew(args.label, lock_dir=root, lease_s=args.lease_s)
        return 0
    if args.command == "release":
        release(args.label, lock_dir=root)
        return 0
    if not cmd:
        print("gate lock: hold requires a command after --", file=sys.stderr)
        return 2
    take(args.label, lock_dir=root, lease_s=args.lease_s, wait=args.wait)
    with hold(args.label, lock_dir=root, lease_s=args.lease_s):
        return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
