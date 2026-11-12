"""seat_gen.py's self-test: the generation comparison, the wired writers' refusal, the session lock."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import seat_gen as sg

HERE = Path(__file__).resolve().parent


def run(target: Path = HERE / "seat_gen.py", mutants: bool = True) -> int:
    n = bad = 0

    def check(name, ok):
        nonlocal n, bad
        n += 1
        if not ok:
            bad += 1
            print(f"FAIL {name}")

    cases(check)
    if mutants:
        src = target.read_text()
        for name, (old, new, case) in MUTANTS.items():
            n += 1
            if src.count(old) != 1:
                print(f"FAIL mutant {name}: its site appears {src.count(old)} times")
                bad += 1
                continue
            with tempfile.TemporaryDirectory() as d:
                shutil_copy = Path(d)
                for f in HERE.glob("seat_gen*.py"):
                    (shutil_copy / f.name).write_text(f.read_text())
                (shutil_copy / "seat_gen.py").write_text(src.replace(old, new))
                r = subprocess.run([sys.executable, "-I", str(shutil_copy / "seat_gen.py"), "--self" "-test", "--no-mutants"],
                                   capture_output=True, text=True)
            killed = case in r.stdout
            print(f"{'ok  ' if killed else 'FAIL'} mutant {name} killed by: {case}")
            bad += not killed
    print(f"seat_gen self-test: {n} checks, {bad} failed")
    return 1 if bad else 0


def cases(check) -> None:
    with tempfile.TemporaryDirectory() as d:
        sd = Path(d)
        check("bump: the first generation is 1, the next 2", [sg.bump(sd, "merge", 1000.0), sg.bump(sd, "merge", 1001.0)] == [1, 2])
        check("bump: the file holds the number and the epoch", (sd / "merge.gen").read_text() == "2 1001\n")
        check("check null: the current generation passes", sg.check(sd, "merge", 2) == (0, ""))
        check("check null: a generation ahead of the file passes", sg.check(sd, "merge", 3) == (0, ""))
        check("check: a lower generation is SUPERSEDED, exit 1", sg.check(sd, "merge", 1) == (1, "SUPERSEDED merge gen=1 held=2"))
        check("check null: a seat with no file passes", sg.check(sd, "dispatch", 1) == (0, ""))
        (sd / "bad.gen").write_text("x\n")
        check("check: a garbage file is UNREADABLE, never a pass", sg.check(sd, "bad", 1)[0] == 2)
        env = {"HPO_STATE_DIR": str(sd), "HPO_SEAT_GEN": "merge=1"}
        check("check-env: a superseded seat is refused", sg.check_env(env)[0] == 1)
        check("check-env null: unset passes", sg.check_env({"HPO_STATE_DIR": str(sd)}) == (0, ""))
        check("check-env: a malformed spec is UNREADABLE", sg.check_env({**env, "HPO_SEAT_GEN": "merge"})[0] == 2)
        r = subprocess.run([sys.executable, "-I", str(HERE / "seat_gen.py"), "check", "merge", "1"],
                           env={"HPO_STATE_DIR": str(sd)}, capture_output=True, text=True)
        check("the CLI exits 1 and prints SUPERSEDED for a lower generation",
              r.returncode == 1 and r.stdout.startswith("SUPERSEDED"))

    cmds = {100: "/usr/bin/claude --resume", 200: "claude", 300: "vim notes.txt"}
    ps = lambda pid: cmds.get(pid, "")
    with tempfile.TemporaryDirectory() as d:
        sd = Path(d)
        check("lock: a free lock is taken", sg.lock(sd, 100, 50.0, ps, lambda pid, now: 7)[0] == 0 and (sd / "session.lock").read_text() == "100 7\n")
        check("lock null: the session's own pid is not a duplicate", sg.lock(sd, 100, 6.0, ps, lambda pid, now: 7)[0] == 0)
        rc, msg = sg.lock(sd, 200, 7.0, ps)
        check("lock: a live other holder whose command is the session binary refuses, naming both pids",
              rc == 1 and "100" in msg and "200" in msg and (sd / "session.lock").read_text() == "100 7\n")
        (sd / "session.lock").write_text("999 1\n")
        check("lock null: a dead holder pid is taken over", sg.lock(sd, 200, 8.0, ps)[0] == 0)
        (sd / "session.lock").write_text("300 1\n")
        check("lock null: a reused pid naming another command is taken over", sg.lock(sd, 200, 9.0, ps)[0] == 0)
    t0 = time.time()
    st = sg.ps_start(os.getpid(), t0)
    check("ps_start: this process's start time is now less its ps etimes, never 0",
          int(t0) - 600 < st <= int(t0))
    check("ps_start null: a pid ps cannot find is 0", sg.ps_start(2 ** 22 + 1, t0) == 0)
    par = {5: 4, 4: 3, 3: 2}.get
    check("session_pid: the first ancestor running the session binary, never the shell",
          sg.session_pid(5, lambda p: {2: "claude", 4: "bash"}.get(p, "x"), lambda p: par(p, 0)) == 2)
    check("session_pid null: no ancestor is the session binary", sg.session_pid(5, lambda p: "bash", lambda p: par(p, 0)) is None)


#: one site, one mutant, the case that must fail (the comparison, the command match)
MUTANTS = {
    "gen_ge": ("    if held is not None and held > gen:", "    if held is not None and held >= gen:",
               "check null: the current generation passes"),
    "gen_le": ("    if held is not None and held > gen:", "    if held is not None and held < gen:",
               "check: a lower generation is SUPERSEDED, exit 1"),
    "lock_no_command_match": ("    if held and held != mine and SESSION_RE.search(command(held)):", "    if held and held != mine:",
                              "lock null: a reused pid naming another command is taken over"),
    "lock_own_pid": ("    if held and held != mine and SESSION_RE.search(command(held)):", "    if held and SESSION_RE.search(command(held)):",
                     "lock null: the session's own pid is not a duplicate"),
    "session_ppid": ("        if SESSION_RE.search(command(pid)):\n            return pid\n", "        if True:\n            return pid\n",
                     "session_pid: the first ancestor running the session binary, never the shell"),
}
