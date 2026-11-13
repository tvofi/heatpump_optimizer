import sys, subprocess, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("ss", sys.argv[1]); ss = importlib.util.module_from_spec(spec); spec.loader.exec_module(ss)
root = Path(sys.argv[2])
for m in open(sys.argv[3]).read().split():
    subprocess.run(["git", "checkout", "-q", "--detach", m], cwd=root, check=True)
    p = subprocess.run(["git", "rev-parse", m + "^1"], cwd=root, capture_output=True, text=True).stdout.strip()
    subj = subprocess.run(["git", "log", "-1", "--format=%s", m], cwd=root, capture_output=True, text=True).stdout.strip()[:60]
    g = ss.shrink_gaps(root, p)
    print(f"{m} {len(g)} {subj}")
