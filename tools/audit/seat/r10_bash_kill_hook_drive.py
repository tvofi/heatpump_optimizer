#!/usr/bin/env python3
"""R10-BASH-KILL-HOOK: drive the pre-bash hook as the harness would, and plant a mutant per arm.

The command is read out of the REAL .claude/settings.json (the PreToolUse entry
whose matcher is Bash), run with CLAUDE_PROJECT_DIR set, and given the payload
on stdin: exit 2 is a refusal, exit 0 an allow. A mutant runs the same
registered command against a scratch project dir that holds a byte copy of the
real settings.json and a hook with one plant applied; the real hook is never
edited.

Metric, one line per case: `CASE <want> got=<rc> <label>`; one per plant:
`MUTANT <name> killed=<yes|no>`. Expected: every CASE rc matches, every MUTANT
killed=yes, `--null` (no plant) all CASE ok. Exit 1 on any miss.

Plants, one per arm of the refusal predicate:
  M-pkill     `pkill` is no longer a refused command word
  M-killall   `killall` is no longer a refused command word
  M-pgrepkill a `kill` in the statement of a `pgrep` is no longer refused

    python3 tools/audit/seat/r10_bash_kill_hook_drive.py [--null]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOK = ".claude/hooks/pre-bash.sh"
SETTINGS = ".claude/settings.json"

CASES = (  # (want rc, command, label)
    (2, 'pkill -f tests/entities.py', "pkill at command position"),
    (2, 'killall python3', "killall at command position"),
    (2, 'kill $(pgrep -f x)', "kill fed by pgrep"),
    (2, 'pgrep -f x | xargs kill', "pgrep piped to xargs kill"),
    (0, 'kill 1234', "NULL kill of an owned pid"),
    (0, 'git status', "NULL a non-kill command"),
    (0, 'echo "never pkill"', "NULL pkill inside quoted text"),
)
PLANTS = {  # name -> (anchor, replacement), each anchor occurs once in the hook
    "M-pkill": ('if b in ("pkill", "killall") or', 'if b in ("killall",) or'),
    "M-killall": ('if b in ("pkill", "killall") or', 'if b in ("pkill",) or'),
    "M-pgrepkill": ('or (b == "kill" and s in feeds)', ''),
}


def registered_command():
    for entry in json.loads((ROOT / SETTINGS).read_text())["hooks"]["PreToolUse"]:
        if entry.get("matcher") == "Bash":
            return entry["hooks"][0]["command"]
    sys.exit("no Bash entry in PreToolUse of " + SETTINGS)


def rc_of(project, command):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
    return subprocess.run(["bash", "-c", registered_command()], input=payload, text=True,
                          capture_output=True, env=env).returncode


def run_cases(project):
    bad = 0
    for want, command, label in CASES:
        got = rc_of(project, command)
        bad += got != want
        print(f"CASE {'ok' if got == want else 'MISS'} want={want} got={got} {label}")
    return bad


def main():
    bad = run_cases(ROOT)
    if "--null" in sys.argv:
        return 1 if bad else 0
    src = (ROOT / HOOK).read_text()
    for name, (anchor, repl) in PLANTS.items():
        if src.count(anchor) != 1:
            sys.exit(f"{name}: anchor occurs {src.count(anchor)} times, wanted 1")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".claude/hooks").mkdir(parents=True)
            shutil.copy(ROOT / SETTINGS, Path(d) / SETTINGS)
            (Path(d) / HOOK).write_text(src.replace(anchor, repl))
            killed = any(rc_of(d, c) != w for w, c, _ in CASES)
        print(f"MUTANT {name} killed={'yes' if killed else 'no'}")
        bad += not killed
    return 1 if bad else 0


sys.exit(main())
