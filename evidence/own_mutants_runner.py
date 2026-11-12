"""Reviewer's own mutants: replace the FIRST occurrence (production code precedes the self-test table)."""
import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2])
F = "tools/audit/seat/beatd.py"; O = "tools/audit/seat/open_driver.py"
B9 = ["python3", "-I", F, "--self-test", "9"]; OD = ["python3", "-I", O, "--self-test"]
M = [
    ("stale_first", F, "            if self.stale_n >= 2:", "            if self.stale_n >= 1:", B9),
    ("untracked_counted", F, '"status", "--porcelain", "--untracked-files=no"', '"status", "--porcelain"', B9),
    ("detach_always", F, '*(["-B", br] if br else ["--detach"])', '"--detach"', B9),
    ("no_stop", F, "                    self.stop.set()\n", "", B9),
    ("no_guard_env", F, "{**os.environ, RESTARTED_ENV: beat.restart}", "dict(os.environ)", B9),
    ("retip_noswap", O, "            sha = live_tip\n", "", OD),
    ("retip_nolog", O, '            log(f"RETIP {topic} {sha[:8]} -> {live_tip[:8]}")\n', "", OD),
]
with OUT.open("w") as out:
    for name, f, old, new, cmd in M:
        p = W / f; t = p.read_text(); i = t.find(old)
        if i < 0:
            print(f"RESULT own-mutant={name} NOT-APPLIED", file=out, flush=True); continue
        p.write_text(t[:i] + new + t[i + len(old):])
        try:
            r = subprocess.run(cmd, cwd=W, capture_output=True, text=True, timeout=400)
            o = r.stdout + r.stderr; rc = r.returncode
        except subprocess.TimeoutExpired:
            o, rc = "TIMEOUT", "timeout"
        finally:
            p.write_text(t)
        summ = [l for l in o.splitlines() if "self-test:" in l][-1:]
        fails = [l for l in o.splitlines() if l.startswith("FAIL")][:3]
        tb = [l for l in o.splitlines() if "Error" in l][-1:]
        v = "killed" if rc != 0 else "SURVIVED"
        print(f"RESULT own-mutant={name} rc={rc} verdict={v} {summ} fails={fails} err={tb}", file=out, flush=True)
    print("ALL-DONE", file=out, flush=True)
