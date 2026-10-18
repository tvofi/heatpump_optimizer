"""Plant dropped steps into a U5-style AFTER and run phase 2's unitcheck.py on it.
BEFORE = Tests dispatch run 39158300302 (phase 1 raw). AFTER = the same jobs, each
name prefixed `tests / `, with these planted defects:
  P1: job `closures-autofix` deleted entirely (it skipped in BEFORE);
  P2: every step of `fast` that BEFORE skipped is deleted;
  P3: `closures`' step "Re-record the closures" kept by name (a gutted body
      keeps its name; unitcheck compares names only).
Prints unitcheck's verdict on each. A detector that detects prints rc 1."""
import copy, json, subprocess, sys
from pathlib import Path
raw = Path(sys.argv[1]); uc = sys.argv[2]
B = json.loads((raw / "jobs_39158300302.json").read_text())
def write(i, jobs):
    (raw / f"jobs_{i}.json").write_text(json.dumps({"jobs": jobs}))
def pref(jobs):
    out = copy.deepcopy(jobs)
    for j in out: j["name"] = "tests / " + j["name"]
    return out
plants = {}
a = pref(B["jobs"]); a = [j for j in a if j["name"] != "tests / closures-autofix"]; plants[1] = a
a = pref(B["jobs"])
for j in a:
    if j["name"] == "tests / fast (3.14)":
        n0 = len(j["steps"]); j["steps"] = [s for s in j["steps"] if s["conclusion"] != "skipped"]
        print(f"P2: fast (3.14) steps {n0} -> {len(j['steps'])} (deleted every step BEFORE skipped)")
plants[2] = a
plants[3] = pref(B["jobs"])
for k, jobs in plants.items():
    write(900000 + k, jobs)
    r = subprocess.run([sys.executable, "-I", uc, str(raw), "--before", "39158300302", "--after", str(900000 + k)], capture_output=True, text=True)
    print(f"P{k}: unitcheck rc {r.returncode}: {r.stdout.strip().splitlines()[-1]}")
