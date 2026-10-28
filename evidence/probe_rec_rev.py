"""Reviewer's (round 4, #2883) re-run of the fixer's probe: record roster_lib.py --self-test alone under closure._exec_record; print every repo-file read it files under dev/programme/ (inert_reads and reads)."""
import sys, json, os, tempfile, time
root = sys.argv[1]; sys.path.insert(0, os.path.join(root, "tests")); os.chdir(root)
import closure
out = tempfile.mktemp(suffix=".json"); t0 = time.time()
pid = os.fork()
if pid == 0:
    closure._exec_record("tools/audit/seat/roster_lib.py", out, ["--self-test"]); os._exit(0)
os.waitpid(pid, 0)
r = json.load(open(out))
print("RESULT", root.rsplit("/",1)[-1], "rc", r.get("rc"), "wall %.1fs" % (time.time()-t0))
print("  keys:", sorted(r.keys()))
for k in r:
    if isinstance(r[k], list):
        hits = [f for f in r[k] if isinstance(f, str) and f.startswith("dev/programme/rosters/")]
        print("  ", k, "rosters:", hits)
