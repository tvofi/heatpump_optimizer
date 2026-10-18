"""Owner ruling D-2 input: does each saved head's three-dot diff reach custom_components/?

    python3 -I measure/rev/reaches_cc.py measure/p2/raw > measure/rev/reaches_cc.txt   (run from a full checkout)

The base is the `pull_requests[].base.sha` the head's check runs carry; the count
is `git diff --name-only $(git merge-base BASE HEAD) HEAD -- custom_components/`.
UNKNOWN where a commit is not in the checkout or no check run names a base.
"""
import json, subprocess, sys
from pathlib import Path
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True)
print("# head  base_sha_from_check_runs  custom_components_files_in_three_dot_diff  (measure/rev/reaches_cc.py)")
for f in sorted(Path(sys.argv[1]).glob("checks_*.json")):
    head = f.stem.split("_")[1]; runs = json.loads(f.read_text())["check_runs"]
    bases = [p["base"]["sha"] for r in runs for p in r.get("pull_requests") or []]
    base = bases[0] if bases else None
    if not base or git("cat-file", "-e", head).returncode or git("cat-file", "-e", base).returncode:
        print(head, base or "-", "UNKNOWN"); continue
    mb = git("merge-base", base, head).stdout.strip()
    print(head, base, len(git("diff", "--name-only", mb, head, "--", "custom_components/").stdout.split()))
