#!/usr/bin/env python3
"""SessionStart and PostCompact hook: say what the orchestrator must restart or re-read.

    python3 -I tools/audit/seat/hooks/liveness.py [--state DIR]      (payload JSON on stdin)

WHY. After a compaction or a resume nobody re-armed the wake loop, and owed lines
stood unread for hours while every instrument had flagged them (2026-11-01).
This hook runs at both events and prints, on stdout (which the session reads):
  POLICY-REREAD  the session owes a fresh read of the policy corpus from
                 origin/main (policy_reread_check.py says OWED, or the event is
                 PostCompact, which has just replaced the corpus with a summary);
  DEAD / ALARM   one line per beat job that is late, per beatd alarm, and for
                 beatd itself when its lock is free -- beatd.py status over the
                 job table, so a new row is checked the day it lands;
  STALE          an alive file under $HPO_STATE_DIR/alive/ older than
                 HPO_ALIVE_STALE_MIN (default 120) minutes, and the digest when
                 neither digest/digest.txt nor beatd/journal.log moved within
                 HPO_DIGEST_STALE_MIN (default 30): digest.txt is rewritten only on
                 a change, so a quiet board is judged by the beat's own journal;
  the digest     digest/digest.txt, verbatim;
  ARM            the one instruction line: restart what is reported dead, check the
                 standing seats, re-arm the wake loop (exit on a new
                 digest/new.stamp or digest/events.txt line) this turn.
INERT unless $HPO_STATE_DIR/orch-checkout names a directory: on any other host
it prints nothing and exits 0, so it can sit in a user's settings everywhere.
It never fails the session: an unreadable input prints UNREADABLE for that part.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SEAT = Path(__file__).resolve().parents[1]


def _age_min(p: Path, now: float) -> float | None:
    try:
        return (now - p.stat().st_mtime) / 60
    except OSError:
        return None


def _env_min(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def report(state: Path, event: str, transcript: str, now: float) -> list[str]:
    marker = state / "orch-checkout"
    try:
        repo = marker.read_text().strip()
    except OSError:
        return []
    if not repo or not Path(repo).is_dir():
        return []
    out: list[str] = []
    py = sys.executable
    stamp = state / "policy-reread.stamp"
    if event == "PostCompact":
        out.append("POLICY-REREAD owed: this session was compacted; re-read CLAUDE.md, the rules and the role "
                   f"contracts from fresh origin/main, then python3 -I tools/audit/seat/policy_reread_check.py --stamp {stamp} --write-stamp")
    else:
        cmd = [py, "-I", str(SEAT / "policy_reread_check.py"), "--stamp", str(stamp),
               "--transcript", transcript or os.devnull + ".none"]  # no transcript: unreadable, so OWED
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 2:
            out.append(f"UNREADABLE policy_reread_check: {(r.stderr or r.stdout).strip()[-80:]}")
        elif r.returncode != 0 or not r.stdout.strip().startswith("OK"):
            out.append("POLICY-REREAD owed: re-read CLAUDE.md, the rules and the role contracts from fresh origin/main, "
                       f"then policy_reread_check.py --stamp {stamp} --write-stamp")
    b = subprocess.run([py, "-I", str(SEAT / "beatd.py"), "status", "--state", str(state), "--repo", repo],
                       capture_output=True, text=True)
    if b.returncode == 2 or not b.stdout.strip():
        out.append(f"UNREADABLE beatd status: {(b.stderr or b.stdout).strip()[-80:]}")
    for ln in b.stdout.splitlines():
        f = ln.split()
        if ln.startswith("JOB ") and len(f) > 2:
            if f[2] == "late":
                out.append(f"DEAD loop {f[1]} {' '.join(f[3:])}")
            elif f[2] not in ("ok", "running", "idle"):
                out.append(f"ALARM job {f[1]} {f[2]}")
        elif ln.startswith(("DOWN ", "ALERT ", "STALE-CODE", "UNREADABLE")):
            out.append(("DEAD beatd " + ln[5:]) if ln.startswith("DOWN ") else f"ALARM {ln}")
    alive_stale = _env_min("HPO_ALIVE_STALE_MIN", 120)
    ad = state / "alive"
    for p in sorted(ad.iterdir()) if ad.is_dir() else []:
        if p.is_file():
            age = _age_min(p, now)
            if age is None or age > alive_stale:
                out.append(f"STALE alive {p.name} age_min={'?' if age is None else int(age)}")
    dig = state / "digest" / "digest.txt"
    ages = [a for a in (_age_min(dig, now), _age_min(state / "beatd" / "journal.log", now)) if a is not None]
    if not ages or min(ages) > _env_min("HPO_DIGEST_STALE_MIN", 30):
        out.append("STALE digest: neither digest.txt nor the beat journal moved in time")
    try:
        text = dig.read_text()
    except OSError:
        text = ""
    out += [ln for ln in text.splitlines() if ln.strip()]
    out.append("ARM: restart any loop reported dead above, check the standing seats, and re-arm the wake loop this turn "
               "(it exits on a new digest/new.stamp or digest/events.txt line)")
    return out


def main(argv: list[str]) -> int:
    state = os.environ.get("HPO_STATE_DIR", "")
    if argv[:1] == ["--state"] and len(argv) > 1:
        state = argv[1]
    if not state:
        return 0
    event, transcript = "", ""
    try:
        if not sys.stdin.isatty():
            p = json.loads(sys.stdin.read() or "{}")
            if isinstance(p, dict):
                event = str(p.get("hook_event_name") or "")
                transcript = str(p.get("transcript_path") or "")
    except (ValueError, OSError):
        pass
    try:
        lines = report(Path(state), event, transcript, time.time())
    except Exception as e:  # a hook never fails the session
        lines = [f"UNREADABLE liveness hook: {type(e).__name__}"]
    if lines:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
