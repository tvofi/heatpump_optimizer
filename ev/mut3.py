"""Reviewer round 3: finder's mut2.py mutants (verdict/3090) plus the start-path mutant M42 and variants; reports the start-path arms' state."""
import subprocess, pathlib, runpy, sys
F = "tools/audit/seat/merge_train.py"
CMD = "python3 -I tools/audit/seat/merge_train.py --self-test"
ns = {}
src2 = pathlib.Path(sys.argv[1]).read_text().split("for name, a, b in M:")[0]
exec(src2, ns)
M = list(ns["M"])
START = "queue = t.drain_order([entry] + spooled if front else spooled + [entry])  # mut:start"
M += [
 ("S1 start path back to spooled+[entry] (round-2 code)", START, "queue = [entry] + spooled if front else spooled + [entry]  # mut:start"),
 ("S2 start path ignores front", START, "queue = t.drain_order(spooled + [entry])  # mut:start"),
 ("S3 start path drain_order on spool only", START, "queue = (t.drain_order(spooled) + [entry]) if not front else [entry] + t.drain_order(spooled)  # mut:start"),
]
def run():
    r = subprocess.run(CMD.split(), capture_output=True, text=True, timeout=600)
    last = [l for l in r.stdout.splitlines() if "self-test:" in l][-1:] or [""]
    fails = [l for l in r.stdout.splitlines() if "start path" in l]
    return r.returncode, last[0], fails
rc, last, sp = run(); print(f"== UNMUTATED rc={rc} | {last}", flush=True)
for l in sp: print("   ", l[:200])
for name, a, b in M:
    p = pathlib.Path(F); src = p.read_text(); n = src.count(a)
    if n != 1: print(f"== {name}: NOT PLANTED (anchor count {n})", flush=True); continue
    p.write_text(src.replace(a, b))
    try:
        rc, last, sp = run()
        print(f"== {name}: {'KILLED' if rc else 'SURVIVED'} rc={rc} | {last}", flush=True)
        for l in sp: print("   ", l[:200])
    finally:
        p.write_text(src)
