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
  RESTARTED      beatd, the one supervisor, was DEAD: it is relaunched through
                 daemonize.py from the cwd, HPO_* environment and argv beatd.py
                 recorded in beatd/launch.json, the seat venv's bin first on PATH
                 (else `auto-restart FAILED`); no other loop is ever relaunched;
  DEAD relay     cloud_relay.sh's log (cloud-relay.log) older than
                 HPO_RELAY_STALE_MIN (default 15, three tick passes): the relay
                 runs inside tick_loop.sh's pass, so no standalone process is sought;
  MISSING        a checkout the state names (orch-checkout and the *checkout* keys
                 of sweep-overlay.json) that is not a directory;
  READ-PROOF     the policy corpus at origin/main is written to policy-corpus.txt,
                 its last line a `--prove <sha256>` command; a compact-owed marker
                 stands, and the UserPromptSubmit event re-raises the obligation
                 every prompt until `liveness.py --state S --prove <sha256>` clears it;
  the digest     digest/digest.txt, verbatim;
  ARM            the one instruction line: restart what is reported dead, check the
                 standing seats, re-arm the wake loop (exit on a new
                 digest/new.stamp or digest/events.txt line) this turn.
INERT unless $HPO_STATE_DIR/orch-checkout names a directory: on any other host
it prints nothing and exits 0, so it can sit in a user's settings everywhere.
It never fails the session: an unreadable input prints UNREADABLE for that part.
"""
from __future__ import annotations

import hashlib
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


CORPUS = ("CLAUDE.md", "dev/governance/roles/orchestrator.md", "tools/audit/seat/INSTRUMENTS.md")


def _git(repo: str, *args: str) -> str | None:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def write_corpus(state: Path, repo: str) -> str | None:
    """The policy corpus at origin/main in one file; returns the sha256 of its body, or None."""
    names = list(CORPUS)
    rules = _git(repo, "ls-tree", "-r", "--name-only", "origin/main", ".claude/rules/")
    if rules is None:
        return None
    names += rules.split()
    body = ""
    for n in names:
        t = _git(repo, "show", f"origin/main:{n}")
        if t is None:
            return None
        body += f"=== {n} ===\n{t}\n"
    sha = hashlib.sha256(body.encode()).hexdigest()
    (state / "policy-corpus.txt").write_text(
        body + f"PROOF: python3 -I {Path(__file__).resolve()} --state {state} --prove {sha}\n")
    (state / "compact-owed").write_text(sha + "\n")
    return sha


def prove(state: Path, sha: str) -> int:
    try:
        want = (state / "compact-owed").read_text().strip()
    except OSError:
        print("no read-proof owed")
        return 0
    if sha.strip() != want:
        print("READ-PROOF refused: the sha256 is not the corpus file's; read policy-corpus.txt to its last line")
        return 1
    (state / "compact-owed").unlink()
    print("read-proof accepted")
    return 0


def restart_beatd(state: Path, repo: str) -> str:
    """Relaunch beatd from its recorded launch; never any other loop."""
    try:
        rec = json.loads((state / "beatd" / "launch.json").read_text())
        argv, cwd, env = rec["argv"], rec["cwd"], rec["env"]
        assert isinstance(argv, list) and argv and Path(cwd).is_dir()
        cmd = [sys.executable, "-I", str(SEAT / "daemonize.py"), "--log", str(state / "beatd" / "restart.log"), "--cwd", cwd]
        for k, v in env.items():
            cmd += ["--env", f"{k}={v}"]
        venv = state / "venv-ci" / "bin"
        if venv.is_dir():
            cmd += ["--path-prepend", str(venv)]
        r = subprocess.run([*cmd, "--", *argv], capture_output=True, text=True)
        return "RESTARTED beatd" if r.returncode == 0 else "auto-restart FAILED beatd: daemonize refused"
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as e:
        return f"auto-restart FAILED beatd: {type(e).__name__}"


def report(state: Path, event: str, transcript: str, now: float) -> list[str]:
    marker = state / "orch-checkout"
    try:
        repo = marker.read_text().strip()
    except OSError:
        return []
    if not repo or not Path(repo).is_dir():
        return []
    out: list[str] = []
    if event == "UserPromptSubmit":
        if (state / "compact-owed").exists():
            out.append(f"READ-PROOF owed: read {state / 'policy-corpus.txt'} to its last line and run the PROOF command there")
        return out
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
    owed = event == "PostCompact" or any(ln.startswith("POLICY-REREAD") for ln in out)
    if owed and write_corpus(state, repo):
        out.append(f"READ-PROOF owed: read {state / 'policy-corpus.txt'} to its last line and run the PROOF command there")
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
            if ln.startswith("DOWN "):
                out.append(restart_beatd(state, repo))
    relay = state / "cloud-relay.log"
    age = _age_min(relay, now)
    if age is not None and age > _env_min("HPO_RELAY_STALE_MIN", 15):
        out.append(f"DEAD relay {relay.name} age_min={int(age)}")
    names = {"orch-checkout": repo}
    try:
        ov = json.loads((state / "sweep-overlay.json").read_text())
        names.update({k: v for k, v in ov.items() if "checkout" in k and isinstance(v, str)})
    except (OSError, ValueError, AttributeError):
        pass
    out += [f"MISSING checkout {k} {v}" for k, v in sorted(names.items()) if not Path(v).is_dir()]
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
        state, argv = argv[1], argv[2:]
    if not state:
        return 0
    if argv[:1] == ["--prove"] and len(argv) > 1:
        return prove(Path(state), argv[1])
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
