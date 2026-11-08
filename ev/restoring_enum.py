import sys, importlib.util, re
from pathlib import Path
spec = importlib.util.spec_from_file_location("cp", sys.argv[1]); cp = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(sys.argv[1]).parent)); spec.loader.exec_module(cp)
root = Path(sys.argv[2])
jobs = cp.restoring_jobs(root)
for k,(w,j,_) in sorted(jobs.items()): print("JOB", k, w, j)
print("RESULT restoring_jobs", len(jobs))
# null control: every job in every workflow that lacks the step is not listed
allj = 0; bad = []
for wf in sorted((root/".github/workflows").glob("*.y*ml")):
    t = wf.read_text()
    for j in re.findall(r"^  ([a-z][\w-]*):\n", t, re.M):
        allj += 1
        has = cp.RESTORE_STEP in cp.job_text(t, j)
        listed = any(v[0]==wf.relative_to(root).as_posix() and v[1]==j for v in jobs.values())
        if has != listed: bad.append((wf.name, j, has, listed))
print("RESULT null-control jobs scanned", allj, "mismatches", bad)
