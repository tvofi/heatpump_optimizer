"""Reviewer's harness: trace chosen gated steps at the head, then run the
drift check against the head table and against copies with each added entry
removed. Usage: python3 mutate_drift.py <worktree> <step>...  """
import copy, json, os, subprocess, sys, tempfile
from pathlib import Path
root = Path(sys.argv[1]).resolve(); want = sys.argv[2:]
sys.path.insert(0, str(root / "tools/ci")); os.chdir(root)
import selftest_scope as S
steps = S.workflow_steps(root)
tmp = Path(tempfile.mkdtemp(prefix="rev-trace-"))
env = dict(os.environ, RUNNER_TEMP=str(tmp), SELFTEST_TRACE="1", HPO_JOB_GRADES="nothing"); env.pop("BASH_ENV", None)
(tmp / S.SCOPE_FILE).write_text("".join(f"{i}\n" for i in want))
for s in steps:
    if s.id in want and s.run:
        sc = tmp / f"{s.id}.sh"; sc.write_text(s.run)
        r = subprocess.run(["bash", S.WRAPPER, str(sc)], cwd=root, capture_output=True, text=True, env={**env, "GITHUB_ACTION": s.id})
        print("RUN", s.id, "rc", r.returncode)
measured, broken = S.fold(tmp / S.TRACE_DIR, steps, root)
measured = {k: v for k, v in measured.items() if k in want}
print("broken", broken)
table = S.load_table(root / S.TABLE)
base = json.loads(subprocess.check_output(["git", "show", "47f0f18a7:tools/ci/selftest_closures.json"]))
def run(t, label):
    refuse, _ = S.drift(t, measured, steps)
    refuse = [x for x in refuse if any(w in x for w in want)]
    print(f"{label}: {len(refuse)} refusal(s)"); [print("   ", x) for x in refuse]
run(table, "HEAD table")
for sid in want:
    for k in ("files", "probes", "dirs"):
        added = sorted(set(table["steps"][sid].get(k, ())) - set(base["steps"].get(sid, {}).get(k, ())))
        for p in added:
            t = copy.deepcopy(table); t["steps"][sid][k] = [x for x in t["steps"][sid][k] if x != p]
            run(t, f"MUTANT drop {sid}.{k} {p}")
