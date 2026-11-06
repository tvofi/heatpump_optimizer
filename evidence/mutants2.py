"""Reviewer's round-2 mutants (own driver): the three round-1 findings' fixes. Apply, run self-test with a 120 s group-killed bound, restore."""
import subprocess, sys, pathlib, os, signal, time
F = pathlib.Path("tools/release/stamp.py"); Y = pathlib.Path(".github/workflows/release.yml")
orig = {F: F.read_text(), Y: Y.read_text()}
def rep(p, *pairs):
    s = orig[p]
    for a, b in pairs:
        assert s.count(a) >= 1, (p, a); s = s.replace(a, b, 1)
    return p, s
UNB = (Y, [('for attempt in $(seq 1 "${attempts}"); do', 'attempt=0; while attempt=$((attempt+1)); do')])
TREE_LOOP = (Y, [('          set -euo pipefail\n          problems=0\n', '          set -euo pipefail\n          while :; do :; done\n          problems=0\n')])
def multi(*edits):
    d = {}
    for p, pairs in edits:
        s = d.get(p, orig[p])
        for a, b in pairs:
            assert s.count(a) >= 1, (p, a); s = s.replace(a, b, 1)
        d[p] = s
    return d
FL = "    head, deferred = flush_before_tag(args, last_tag, nxt, head)\n"
AN = "    last_tag = last_stamped_tag(tags, tag_version)\n"
M = {
 "flush call moved above the last_stamped_tag anchor": multi((F, [(FL, ""), (AN, FL + AN)])),
 "flush pin: anchor replaced by old newest-tag form": multi((F, [(AN, '    last_tag = "v" + ".".join(map(str, top)) if top != (0, 0, 0) else None\n')])),
 "release.yml: unbounded readback": multi(UNB),
 "release.yml: tree step never ends": multi(TREE_LOOP),
 "_run_step: no timeout + unbounded readback": multi((F, [("return proc.wait(timeout=RELEASE_STEP_TIMEOUT_S)", "return proc.wait()")]), UNB),
 "_run_step: kill only bash (proc.kill, not killpg) + unbounded readback": multi((F, [("os.killpg(proc.pid, signal.SIGKILL)", "proc.kill()")]), UNB),
 "_run_step: timeout returns 1 (not None) + unbounded readback": multi((F, [("            proc.wait()\n            return None", "            proc.wait()\n            return 1")]), UNB),
 "RELEASE_READBACK_ATTEMPTS=4 (constant disagrees with yml)": multi((F, [("RELEASE_READBACK_ATTEMPTS = 5", "RELEASE_READBACK_ATTEMPTS = 4")])),
}
def run():
    t = time.time()
    p = subprocess.Popen([sys.executable, "-I", "tools/release/stamp.py", "--self-test"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=120)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL); p.communicate(); return "HUNG", [], [], time.time()-t
    fails = [l for l in out.splitlines() if "FAIL" in l]
    tb = [l for l in out.splitlines() if "Error" in l][-1:]
    return p.returncode, fails, tb, time.time()-t
try:
    rc, f, tb, dt = run(); print(f"NULL unmutated: exit {rc}, {len(f)} FAIL, {dt:.1f}s")
    for name, edits in M.items():
        for p, s in edits.items(): p.write_text(s)
        try: rc, f, tb, dt = run()
        finally:
            for p in edits: p.write_text(orig[p])
        print(f"MUTANT {name}: exit {rc}, {len(f)} FAIL, {dt:.1f}s {'SURVIVED' if rc == 0 else 'KILLED'}")
        for l in f[:5]: print("   ", l.strip()[:200])
        for l in tb: print("    tb:", l.strip()[:200])
    rc, f, tb, dt = run(); print(f"NULL restored: exit {rc}, {len(f)} FAIL")
finally:
    for p, s in orig.items(): p.write_text(s)
