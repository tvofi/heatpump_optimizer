import sys, subprocess, pathlib
root = pathlib.Path.cwd()
sys.path[:0] = [str(root/"tools/pr"), str(root/"tests"), str(root/"tools/policy")]
import ci_predict, agreement_py
lane = ci_predict.lane_files(root)
specs = agreement_py.restore_specs((root/agreement_py.WORKFLOW).read_text())
g = lambda *a: subprocess.run(["git",*a],capture_output=True,text=True).stdout
ms = g("log","--first-parent","--merges","--since=2026-10-09T00:00","--until=2026-10-24T00:00","--format=%H","origin/main").split()
# pin origin/main to the body's merge base window: use e97f5749b
nl=nr=0
for m in ms:
    ch = set(g("diff","--name-only",f"{m}^1",m).split())
    if ch & lane: nl+=1
    if any(agreement_py.covers(s, f) if True else 0 for s in specs for f in ch): nr+=1
print(f"lane files {len(lane)} merges {len(ms)} lane {nl} restore {nr}")
