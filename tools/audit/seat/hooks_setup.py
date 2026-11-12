#!/usr/bin/env python3
"""Report and install the user-level Claude Code hooks the orchestrator's host depends on.

    python3 -I tools/audit/seat/hooks_setup.py --check   [--settings FILE]
    python3 -I tools/audit/seat/hooks_setup.py --install [--settings FILE]
    python3 -I tools/audit/seat/hooks_setup.py --self-test

WHY THIS EXISTS. The orchestrator's sessions leaned on four hooks that lived
only in one user's settings, with no description and no way to rebuild them on
a new host (R10-FLY-STANDING-CONTRACTS, carry 19 part 2). The scripts are
tracked under tools/audit/seat/hooks/ and described in
instruments/hooks_setup.py.md; this is the one installer, and a later group's
user-level hook adds a row to HOOKS here rather than shipping its own.

USER LEVEL, per hook (project-level hooks bind every session through
.claude/settings.json and need no installer):
  liveness          SessionStart, PostCompact   hooks/liveness.py
  seat-interpreter  SessionStart                hooks/seat_interpreter.py
  git-identity      SessionStart                hooks/git_identity.py
PROJECT LEVEL, reported by --check and never installed: the Bash PreToolUse
guard of the orchestrator's checkout, the second arm of .claude/hooks/pre-bash.sh.

--check changes nothing and prints one line per hook and event: `ok`,
`missing` or `differs` (an entry for the script whose command is not the
one this tree would write). Exit 0 when none is missing or differing, else 1.
--install adds a missing entry and corrects a differing command in place, prints
each change, and backs the settings file up first (settings.json.bak-<ns>), only
when it changes something; a second run changes nothing and writes no byte. It
never touches an entry of another script, and keeps every unrelated key.
Settings default to $HOME/.claude/settings.json.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SEAT = Path(__file__).resolve().parent
ROOT = SEAT.parents[2]
HOOKS = [  # (id, script, events)
    ("liveness", "liveness.py", ("SessionStart", "PostCompact", "UserPromptSubmit")),
    ("seat-interpreter", "seat_interpreter.py", ("SessionStart",)),
    ("git-identity", "git_identity.py", ("SessionStart",)),
]
PROJECT_GUARD = ("pre-bash guard", ".claude/hooks/pre-bash.sh", "HPO_PRE_BASH_GUARD_PY")


def expected(script: str, root: Path = ROOT) -> str:
    return f'python3 -I "{root}/tools/audit/seat/hooks/{script}"'


def find(settings: dict, event: str, script: str) -> list[dict]:
    """Every command entry under `event` whose command names this script."""
    out = []
    groups = (settings.get("hooks") or {}).get(event) or []
    for g in groups if isinstance(groups, list) else []:
        for h in (g.get("hooks") or []) if isinstance(g, dict) else []:
            if isinstance(h, dict) and f"hooks/{script}" in str(h.get("command", "")):
                out.append(h)
    return out


def state_of(settings: dict, event: str, script: str, root: Path = ROOT) -> str:
    hs = find(settings, event, script)
    if not hs:
        return "missing"
    return "ok" if all(h.get("command") == expected(script, root) for h in hs) else "differs"


def check(settings: dict, root: Path = ROOT) -> tuple[int, list[str]]:
    out, bad = [], 0
    for hid, script, events in HOOKS:
        for ev in events:
            st = state_of(settings, ev, script, root)
            bad += st != "ok"
            out.append(f"{st} {hid} {ev}")
    name, rel, marker = PROJECT_GUARD
    try:
        proj = json.loads((root / ".claude/settings.json").read_text())
        wired = any("pre-bash.sh" in h.get("command", "")
                    for g in proj["hooks"]["PreToolUse"] if g.get("matcher") == "Bash" for h in g["hooks"])
        armed = marker in (root / rel).read_text()
    except (OSError, ValueError, KeyError, TypeError):
        wired = armed = False
    st = "ok" if wired and armed else "missing"
    bad += st != "ok"
    out.append(f"{st} {name} PreToolUse project-level (tree: .claude/settings.json, installs nothing)")
    return (1 if bad else 0), out


def install(settings: dict, root: Path = ROOT) -> list[str]:
    """Mutate `settings` in place; return one line per change."""
    changes = []
    hooks = settings.setdefault("hooks", {})
    for hid, script, events in HOOKS:
        for ev in events:
            st = state_of(settings, ev, script, root)
            if st == "ok":
                continue
            if st == "differs":
                for h in find(settings, ev, script):
                    h["command"] = expected(script, root)
            else:
                hooks.setdefault(ev, []).append(
                    {"hooks": [{"type": "command", "command": expected(script, root)}]})
            changes.append(f"{'corrected' if st == 'differs' else 'added'} {hid} {ev}")
    return changes


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def cmd_install(path: Path, root: Path = ROOT) -> int:
    settings = load(path)
    changes = install(settings, root)
    if not changes:
        print("hooks_setup: nothing to change")
        return 0
    if path.exists():
        bak = path.with_name(f"{path.name}.bak-{time.time_ns()}")
        shutil.copy2(path, bak)
        print(f"hooks_setup: backed up to {bak.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n")
    for c in changes:
        print(f"hooks_setup: {c}")
    return 0


# ---------------------------------------------------------------- self-test

def _fixture_state(base: Path, *, dead: bool = False, stale: bool = False, down: bool = False):
    """A healthy beat state under `base` (lock held by the caller), or one planted fault."""
    import fcntl
    s = base / "state"
    (s / "beatd").mkdir(parents=True)
    (s / "digest").mkdir()
    (s / "alive").mkdir()
    repo = base / "orch"
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_init
    throwaway_git_init(repo, "-q")
    (s / "orch-checkout").write_text(f"{repo}\n")
    now = time.time()
    stamp = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))  # noqa: E731
    rows = json.loads((SEAT / "beatd.jobs.json").read_text())["jobs"]
    lines = [f"START {stamp(now - 100000)} beatd pid=1 code=unknown supervisor=none"]
    for j in rows:
        if j["kind"] == "watch" or (dead and j["name"] == "pulse"):
            continue
        lines.append(f"PASS {stamp(now - 30)} {j['name']} start={stamp(now - 31)} dur=1 rc=0 outcome=ok")
    (s / "beatd" / "journal.log").write_text("\n".join(lines) + "\n")
    (s / "digest" / "digest.txt").write_text("OWED reviewer-fire 1\n")
    (s / "alive" / "merge").write_text("")
    (base / "transcript.jsonl").write_text("")
    subprocess.run([sys.executable, "-I", str(SEAT / "policy_reread_check.py"), "--stamp",
                    str(s / "policy-reread.stamp"), "--write-stamp"], check=True, capture_output=True)
    if stale:
        old = now - 86400
        for p in (s / "digest" / "digest.txt", s / "beatd" / "journal.log", s / "alive" / "merge"):
            os.utime(p, (old, old))
    fd = os.open(s / "beatd" / "beatd.lock", os.O_RDWR | os.O_CREAT, 0o600)
    if not down:  # a free lock is a dead beatd
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, b"1\n")
    return s, fd


def _run_hook(script: str, state: Path, payload: dict | None = None, *, env: dict | None = None,
              seat: Path = SEAT, args: list[str] | None = None) -> str:
    """The hook's stdout, plus an `EXIT <rc>` line when it exits non-zero (a hook must not)."""
    tr = state.parent / "transcript.jsonl"
    payload = dict({"hook_event_name": "SessionStart", "transcript_path": str(tr)}, **(payload or {}))
    r = subprocess.run([sys.executable, "-I", str(seat / "hooks" / script),
                        *(["--state", str(state)] if args is None else args)],
                       input=json.dumps(payload), env=dict(os.environ, **(env or {})),
                       capture_output=True, text=True)
    return r.stdout + (f"EXIT {r.returncode}\n" if r.returncode else "")


def cases() -> dict[str, bool]:
    res: dict[str, bool] = {}
    tmp = Path(tempfile.mkdtemp(prefix="hooks-setup-"))
    try:
        home = tmp / "home"
        sf = home / ".claude" / "settings.json"
        # --check on a fresh HOME lists every user-level hook as missing
        rc, out = check({})
        res["fresh settings: every user-level hook is missing"] = (
            rc == 1 and sum(ln.startswith("missing") and "project-level" not in ln for ln in out)
            == sum(len(e) for _, _, e in HOOKS))
        res["the project-level guard is reported present in the tree"] = any(
            ln.startswith("ok pre-bash guard") for ln in out)
        # --install, then --check lists none; a second --install writes no byte
        unrelated = {"permissions": {"allow": ["Read"]}, "hooks": {"Stop": [{"hooks": [
            {"type": "command", "command": "echo mine"}]}], "SessionStart": [{"hooks": [
                {"type": "command", "command": "echo other"}]}]}}
        sf.parent.mkdir(parents=True)
        sf.write_text(json.dumps(unrelated, indent=2) + "\n")
        cmd_install(sf)
        got = load(sf)
        res["install then check lists none missing"] = check(got)[0] == 0
        res["install keeps unrelated entries"] = (
            got["permissions"] == unrelated["permissions"] and got["hooks"]["Stop"] == unrelated["hooks"]["Stop"]
            and got["hooks"]["SessionStart"][0] == unrelated["hooks"]["SessionStart"][0])
        baks = list(sf.parent.glob("settings.json.bak-*"))
        res["install backs the file up first, holding the old bytes"] = (
            len(baks) == 1 and json.loads(baks[0].read_text()) == unrelated)
        before = sf.read_bytes()
        cmd_install(sf)
        res["a second install changes nothing (byte-identical, no new backup)"] = (
            sf.read_bytes() == before and len(list(sf.parent.glob("settings.json.bak-*"))) == 1)
        # a differing command is corrected in place, nothing else is
        got["hooks"]["SessionStart"][1]["hooks"][0]["command"] = "python3 old.py hooks/liveness.py"
        sf.write_text(json.dumps(got))
        res["a differing command is reported differs"] = "differs liveness SessionStart" in check(load(sf))[1]
        cmd_install(sf)
        res["install corrects the differing command only"] = (
            check(load(sf))[0] == 0 and load(sf)["hooks"]["Stop"] == unrelated["hooks"]["Stop"])
        # the hooks themselves
        s, fd = _fixture_state(tmp / "healthy")
        out = _run_hook("liveness.py", s)
        res["liveness: a healthy table prints nothing actionable"] = (
            not any(w in out for w in ("DEAD", "STALE", "ALARM", "UNREADABLE")) and "ARM:" in out
            and "OWED reviewer-fire 1" in out)
        res["liveness: a healthy table with a fresh stamp owes no policy re-read"] = "POLICY-REREAD" not in out
        res["liveness: PostCompact demands the policy re-read"] = (
            "POLICY-REREAD" in _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"}))
        res["liveness: an unparseable HPO_ALIVE_STALE_MIN falls back to its default"] = (
            "ARM:" in (o := _run_hook("liveness.py", s, env={"HPO_ALIVE_STALE_MIN": "x"})) and "UNREADABLE" not in o)
        past = time.time() - 120.5 * 60  # half a minute past the 120-minute default
        os.utime(s / "alive" / "merge", (past, past))
        res["liveness: an alive file half a minute past HPO_ALIVE_STALE_MIN is STALE"] = (
            "STALE alive merge age_min=120" in _run_hook("liveness.py", s))
        (s / "policy-reread.stamp").unlink()
        res["liveness: SessionStart with no re-read stamp owes the policy re-read"] = (
            "POLICY-REREAD owed" in _run_hook("liveness.py", s))
        # a seat copy holding the hook but not policy_reread_check.py: the check cannot run
        cp = tmp / "seatcopy"
        (cp / "hooks").mkdir(parents=True)
        shutil.copy2(SEAT / "hooks" / "liveness.py", cp / "hooks" / "liveness.py")
        o = _run_hook("liveness.py", s, seat=cp)
        res["liveness: a policy_reread_check that cannot run is UNREADABLE, not owed"] = (
            "UNREADABLE policy_reread_check" in o and "POLICY-REREAD" not in o)
        # the same copy with a stub beatd.py: each status line shape it reads
        shutil.copy2(SEAT / "policy_reread_check.py", cp / "policy_reread_check.py")
        (cp / "beatd.py").write_text(
            "import os, sys\nprint('JOB pulse failed\\nJOB tick ok\\nJOB x\\nDOWN no pid\\nALERT disk\\nSTALE-CODE b')\n"
            "sys.exit(2 if os.environ.get('STUB_RC') == '2' else 0)\n")
        o = _run_hook("liveness.py", s, seat=cp)
        res["liveness: beatd's failed job, DOWN, ALERT and STALE-CODE lines are reported, ok and short lines not"] = (
            "ALARM job pulse failed" in o and "DEAD beatd no pid" in o and "ALARM ALERT disk" in o
            and "ALARM STALE-CODE b" in o and "job tick" not in o and "UNREADABLE" not in o)
        res["liveness: beatd status exiting 2 is UNREADABLE"] = (
            "UNREADABLE beatd status" in _run_hook("liveness.py", s, seat=cp, env={"STUB_RC": "2"}))
        res["liveness: a --state with no value, and no HPO_STATE_DIR, is inert"] = (
            _run_hook("liveness.py", s, args=["--state"], env={"HPO_STATE_DIR": ""}) == ""
            and _run_hook("liveness.py", s, args=[], env={"HPO_STATE_DIR": ""}) == "")
        past = time.time() - 30.5 * 60  # half a minute past the 30-minute default
        for p in (s / "digest" / "digest.txt", s / "beatd" / "journal.log"):
            os.utime(p, (past, past))
        res["liveness: a digest and journal half a minute past HPO_DIGEST_STALE_MIN are STALE"] = (
            "STALE digest" in _run_hook("liveness.py", s))
        # seat_interpreter against a stub seat_venv.sh: silent when it passes, its last line when not
        (cp / "hooks" / "seat_interpreter.py").write_bytes((SEAT / "hooks" / "seat_interpreter.py").read_bytes())
        (cp / "seat_venv.sh").write_text('[ "${STUB_VENV:-}" = ok ] && exit 0\necho first >&2\necho last >&2\nexit 1\n')
        res["seat-interpreter: a passing seat_venv.sh --check prints nothing"] = (
            _run_hook("seat_interpreter.py", s, seat=cp, env={"STUB_VENV": "ok"}) == "")
        res["seat-interpreter: the refusal quotes the check's last line"] = (
            _run_hook("seat_interpreter.py", s, seat=cp).startswith("SEAT-INTERPRETER refused: last;")
            and _run_hook("seat_interpreter.py", s, seat=cp, args=["--state"], env={"HPO_STATE_DIR": ""}) == "")
        os.close(fd)
        gone = tmp / "gone"
        gone.mkdir()
        (gone / "orch-checkout").write_text(f"{tmp / 'no-such-checkout'}\n")
        res["liveness: an orch-checkout naming no directory is inert"] = _run_hook("liveness.py", gone) == ""
        s, fd = _fixture_state(tmp / "dead", dead=True)
        res["liveness: a planted dead loop prints DEAD"] = "DEAD loop pulse" in _run_hook("liveness.py", s)
        os.close(fd)
        s, fd = _fixture_state(tmp / "stale", stale=True)
        out = _run_hook("liveness.py", s)
        res["liveness: a planted stale digest and alive file print STALE"] = (
            "STALE digest" in out and "STALE alive merge" in out)
        os.close(fd)
        quiet = tmp / "quiet"
        quiet.mkdir()
        res["liveness, seat-interpreter and git-identity are inert without orch-checkout"] = all(
            _run_hook(h, quiet) == "" for h in ("liveness.py", "seat_interpreter.py", "git_identity.py"))
        s, fd = _fixture_state(tmp / "ident")
        os.close(fd)
        # the fixture state holds orch-checkout but no venv-ci, so seat_venv.sh --check refuses
        out = _run_hook("seat_interpreter.py", s)
        res["seat-interpreter: a refusing seat_venv.sh --check prints SEAT-INTERPRETER refused"] = (
            out.startswith("SEAT-INTERPRETER refused: seat_venv: no venv at") and "seat_venv.sh" in out)
        (s / "git-identity").write_text("Seat Name\nseat@example.invalid\n")
        first = _run_hook("git_identity.py", s)
        repo = (s / "orch-checkout").read_text().strip()
        have = subprocess.run(["git", "-C", repo, "config", "--local", "user.email"],
                              capture_output=True, text=True).stdout.strip()
        name = subprocess.run(["git", "-C", repo, "config", "--local", "user.name"],
                              capture_output=True, text=True).stdout.strip()
        res["git-identity: sets a differing identity, then prints nothing"] = (
            "GIT-IDENTITY set user.email" in first and have == "seat@example.invalid"
            and name == "Seat Name" and _run_hook("git_identity.py", s) == "")
        (s / "git-identity").write_text("Other Name\n")
        res["git-identity: a one-line identity file is ignored"] = _run_hook("git_identity.py", s) == ""
        res["git-identity: a --state with no value is ignored"] = _run_hook("git_identity.py", s, args=["--state"]) == ""
        # the installer's edges and its command line
        rc, out = check({}, tmp / "bare")
        guard_missing = rc == 1 and any(ln.startswith("missing pre-bash guard") for ln in out)
        # carries 21-22: the arms the session-local hook had
        def git(repo, *a):
            subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                           check=True, capture_output=True)
        s, fd = _fixture_state(tmp / "readproof")
        repo = Path((s / "orch-checkout").read_text().strip())
        for n in ("CLAUDE.md", "dev/governance/roles/orchestrator.md", "tools/audit/seat/INSTRUMENTS.md", ".claude/rules/r.md"):
            (repo / n).parent.mkdir(parents=True, exist_ok=True)
            (repo / n).write_text(f"policy {n}\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "corpus")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        out = _run_hook("liveness.py", s, {"hook_event_name": "PostCompact"})
        corpus = (s / "policy-corpus.txt").read_text() if (s / "policy-corpus.txt").is_file() else ""
        proof = corpus.splitlines()[-1] if corpus else ""
        sha = proof.rpartition("--prove ")[2]
        res["read-proof: PostCompact writes the corpus with a sha256 proof last line and a compact-owed marker"] = (
            "READ-PROOF owed" in out and proof.startswith("PROOF: ") and len(sha) == 64 and (s / "compact-owed").is_file()
            and "policy CLAUDE.md" in corpus and "policy .claude/rules/r.md" in corpus)
        res["read-proof: a UserPromptSubmit re-raises the obligation every prompt until the proof clears it"] = (
            all("READ-PROOF owed" in _run_hook("liveness.py", s, {"hook_event_name": "UserPromptSubmit"}) for _ in range(2)))
        res["read-proof: a wrong sha256 is refused and the marker stands"] = (
            "refused" in _run_hook("liveness.py", s, args=["--state", str(s), "--prove", "0" * 64])
            and (s / "compact-owed").is_file())
        _run_hook("liveness.py", s, args=["--state", str(s), "--prove", sha])
        res["read-proof: the right sha256 clears the marker and the next prompt is silent (null control)"] = (
            not (s / "compact-owed").exists()
            and _run_hook("liveness.py", s, {"hook_event_name": "UserPromptSubmit"}).strip() == ""
            and "session" not in proof)
        res["read-proof: a healthy SessionStart with a fresh stamp writes no marker (null control)"] = (
            (_run_hook("liveness.py", s), not (s / "compact-owed").exists())[1])
        os.close(fd)
        # checkout presence, from the state overlay
        s, fd = _fixture_state(tmp / "checkouts")
        (s / "sweep-overlay.json").write_text(json.dumps({"loop_checkout": str(tmp / "no-such-checkout"), "other": "x"}))
        out = _run_hook("liveness.py", s)
        res["checkout: a checkout the overlay names that is not a directory is MISSING"] = (
            f"MISSING checkout loop_checkout {tmp / 'no-such-checkout'}" in out and "MISSING checkout other" not in out)
        (s / "sweep-overlay.json").write_text(json.dumps({"loop_checkout": str(tmp)}))
        res["checkout: null control, a present checkout is not MISSING"] = "MISSING" not in _run_hook("liveness.py", s)
        # the relay is judged by its log's age, never a standalone process
        relay = s / "cloud-relay.log"
        relay.write_text("pass\n")
        res["relay: a fresh relay log with no standalone relay process is live (null control)"] = (
            "DEAD relay" not in _run_hook("liveness.py", s))
        os.utime(relay, (time.time() - 7200, time.time() - 7200))
        res["relay: a stale relay log is DEAD"] = "DEAD relay cloud-relay.log" in _run_hook("liveness.py", s)
        os.close(fd)
        # the one restart: beatd only, from its recorded launch, seat venv first on PATH
        s, fd = _fixture_state(tmp / "down", down=True)
        (s / "venv-ci" / "bin").mkdir(parents=True)
        mark = tmp / "down" / "restarted"
        (s / "beatd" / "launch.json").write_text(json.dumps({
            "cwd": str(tmp), "argv": [sys.executable, "-c", "import os,sys;open(sys.argv[1],'w').write(os.getcwd()+'|'+os.environ['PATH']+'|'+os.environ.get('HPO_X',''))", str(mark)],
            "env": {"HPO_X": "kept"}}))
        out = _run_hook("liveness.py", s)
        for _ in range(50):
            if mark.is_file() and mark.read_text():
                break
            time.sleep(0.1)
        got_mark = mark.read_text() if mark.is_file() else ""
        res["restart: a DEAD beatd is relaunched with its recorded cwd, HPO_* env and the seat venv first on PATH"] = (
            "DEAD beatd" in out and "RESTARTED beatd" in out and got_mark.startswith(f"{tmp.resolve()}|{s / 'venv-ci' / 'bin'}") and got_mark.endswith("|kept"))
        s2, fd2 = _fixture_state(tmp / "down2", down=True)
        out = _run_hook("liveness.py", s2)
        res["restart: a DEAD beatd with no recorded launch prints auto-restart FAILED"] = "auto-restart FAILED" in out and "RESTARTED" not in out
        s3, fd3 = _fixture_state(tmp / "down3", dead=True)
        out = _run_hook("liveness.py", s3)
        res["restart: a late job (not beatd) is DEAD and never relaunched (null control)"] = (
            "DEAD loop pulse" in out and "RESTARTED" not in out and "auto-restart" not in out)
        # beatd run, executed: the floor refusal and the recorded launch the restart above replays
        bst, jobs = tmp / "beatd-run", tmp / "empty-jobs.json"
        jobs.write_text(json.dumps({"version": 1, "jobs": []}))
        drive = lambda floor, *extra, env=None: subprocess.run(  # noqa: E731
            [sys.executable, "-I", "-c", "import sys; sys.path.insert(0, sys.argv[1]); import beatd; beatd.FLOOR = %r; "
             "sys.exit(beatd.main(['run', '--state', sys.argv[2], '--jobs', sys.argv[3], '--once', *sys.argv[4:]]))" % (floor,),
             str(SEAT), str(bst), str(jobs), *extra], capture_output=True, text=True, cwd=tmp, timeout=60,
            env={**os.environ, **(env or {})})
        r = drive((99, 0))
        res["beatd: run under an interpreter older than the floor is refused naming it, and starts nothing"] = (
            r.returncode == 2 and "REFUSE" in r.stderr and sys.executable in r.stderr and "older than the tree's floor 99.0" in r.stderr
            and not (bst / "beatd" / "launch.json").exists())
        r = drive((3, 12), env={"HPO_X": "kept", "NOT_HPO": "dropped"})
        rec = json.loads((bst / "beatd" / "launch.json").read_text()) if (bst / "beatd" / "launch.json").is_file() else {}
        res["beatd: run at the floor starts, and records its cwd, argv and HPO_* environment (null control for the refusal)"] = (
            r.returncode == 0 and "REFUSE" not in r.stderr and rec.get("cwd") == str(tmp) and rec.get("argv", [None])[0] == sys.executable
            and rec.get("env", {}).get("HPO_X") == "kept" and "NOT_HPO" not in rec.get("env", {}))
        for f in (fd, fd2, fd3):
            os.close(f)
        res["check reports the project guard missing in a tree without it"] = guard_missing
        deep = tmp / "new" / "dir" / "settings.json"
        res["install creates a settings file under a missing directory, then has nothing to change"] = (
            cmd_install(deep) == 0 and check(load(deep))[0] == 0 and cmd_install(deep) == 0)
        bad = tmp / "list.json"
        bad.write_text("[]\n")
        cli = lambda *a: subprocess.run([sys.executable, "-I", str(SEAT / "hooks_setup.py"), *a],  # noqa: E731
                                        capture_output=True, text=True)
        res["the command line: --check, --install, a non-object file refused, no mode"] = (
            cli("--check", "--settings", str(deep)).returncode == 0
            and cli("--install", "--settings", str(tmp / "cli" / "s.json")).returncode == 0
            and (tmp / "cli" / "s.json").is_file()
            and "REFUSE" in (r := cli("--check", "--settings", str(bad))).stderr and r.returncode == 2
            and cli().returncode == 2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return res


COPY_FOR_MUTANTS = (  # what cases() reads outside tools/audit/seat, copied beside each mutant
    "tests/throwaway_git.py", "tests/typing_budgets.json", ".claude/settings.json", PROJECT_GUARD[1])
MUTANTS = [  # (label, old text, new text): each must turn at least one case red
    ("install skips the backup", "        shutil.copy2(path, bak)\n", "        pass\n"),
    ("install rewrites an unrelated entry",
     "    hooks = settings.setdefault(\"hooks\", {})\n",
     "    hooks = settings.setdefault(\"hooks\", {})\n    hooks[\"Stop\"] = []\n"),
    ("install is not idempotent", "            if st == \"ok\":\n                continue\n", ""),
    ("liveness reads no dead loop", "            if f[2] == \"late\":", "            if False:"),
    ("liveness reads no stale digest", "if not ages or min(ages) > _env_min(", "if False and min(ages) > _env_min("),
    ("restart drops the seat venv from PATH", "            cmd += [\"--path-prepend\", str(venv)]\n", "            pass\n"),
    ("restart relaunches a loop whose launch is unrecorded", "        rec = json.loads((state / \"beatd\" / \"launch.json\").read_text())\n",
     "        rec = {\"argv\": [\"true\"], \"cwd\": \"/\", \"env\": {}}\n"),
    ("the relay is never judged by its log", "    if age is not None and age > _env_min(\"HPO_RELAY_STALE_MIN\", 15):", "    if False:"),
    ("a missing checkout is never reported", "sorted(names.items()) if not Path(v).is_dir()]", "sorted(names.items()) if False]"),
    ("the read-proof accepts any sha256", "    if sha.strip() != want:", "    if False:"),
    ("the prompt arm never re-raises the proof", "        if (state / \"compact-owed\").exists():", "        if False:"),
    ("beatd run never refuses an interpreter under the floor", "    if sys.version_info < FLOOR:\n", "    if False:\n"),
    ("beatd run records no launch", "(d / \"launch.json\").write_text(", "(d / \"launch.jsonX\").write_text("),
    ("seat-interpreter never reports", "    if r.returncode == 0:\n        return []\n", "    if True:\n        return []\n"),
]


def self_test(run_mutants: bool = True) -> int:
    res = cases()
    fails = [k for k, v in res.items() if not v]
    n = len(res)
    for k in fails:
        print(f"  FAIL {k}")
    if run_mutants and not fails and not os.environ.get("HPO_HOOKS_MUTANT"):
        # the null control first: the copy un-mutated must pass, or every mutant "dies" of the copy
        for label, old, new in [("null control: the copy un-mutated", None, None), *MUTANTS]:
            tgt = Path(tempfile.mkdtemp(prefix="hooks-mutant-"))
            try:
                shutil.copytree(SEAT, tgt / "tools/audit/seat", ignore=shutil.ignore_patterns("__pycache__", "fixtures"))
                for rel in COPY_FOR_MUTANTS:
                    (tgt / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / rel, tgt / rel)
                # the hooks before this file: an anchor without a newline also matches its own MUTANTS literal here
                for f in ("hooks/liveness.py", "hooks/seat_interpreter.py", "beatd.py", "hooks_setup.py"):
                    p = tgt / "tools/audit/seat" / f
                    text = p.read_text()
                    if old is None or old in text:
                        p.write_text(text if old is None else text.replace(old, new, 1))
                        break
                else:
                    print(f"  FAIL mutant '{label}': its target text is gone")
                    fails.append(label)
                    continue
                r = subprocess.run([sys.executable, "-I", str(tgt / "tools/audit/seat/hooks_setup.py"), "--self-test"],
                                   capture_output=True, text=True, env=dict(os.environ, HPO_HOOKS_MUTANT="1"))
                n += 1
                if (r.returncode == 0) != (old is None):
                    print(f"  FAIL mutant '{label}' " + ("is red: " + " | ".join(
                        ln.strip() for ln in r.stdout.splitlines() if "FAIL" in ln) if old is None else "survived"))
                    fails.append(label)
            finally:
                shutil.rmtree(tgt, ignore_errors=True)
    print(f"hooks_setup self-test: {n} checks, {len(fails)} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    path = Path(os.environ.get("HOME", "~")).expanduser() / ".claude" / "settings.json"
    if "--settings" in argv:
        path = Path(argv[argv.index("--settings") + 1])
    try:
        if "--self-test" in argv:
            return self_test("--no-mutants" not in argv)
        if "--check" in argv:
            rc, out = check(load(path))
            print("\n".join(out))
            return rc
        if "--install" in argv:
            return cmd_install(path)
    except (ValueError, OSError) as e:
        print(f"hooks_setup: REFUSE {e}", file=sys.stderr)
        return 2
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
