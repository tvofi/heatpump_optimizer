"""Per-unit null control: executed steps AND token permissions, before vs after.

    python3 -I measure/unitcheck.py RAW --before ID[,ID] --after ID[,ID] [--ignore JOB,..]
    python3 -I measure/unitcheck.py RAW --self-test BEFORE_ID

BEFORE = a run of the unit's own workflow today (e.g. hassfest.yml dispatched at
main). AFTER = the ci.yml run on probe/ci-layout-<unit>, where the unit is called as
`<unit> / <job>`. The `<caller> / ` prefix is stripped; --ignore drops the umbrella's
own jobs (prelude, gate, cancel-superseded). A step counts when it concluded
success/failure (phase 1's stepset.py rule); the permission set is read from each
job's saved 'Set up job' log header (raw/logs/head_<job id>.txt, fetch2.sh). Exit 0
only if both sets are equal. --self-test fabricates an AFTER from BEFORE (prefixed)
and shows: null passes, a dropped step fails, a widened grant fails.
"""
import argparse, copy, json, re, sys
from pathlib import Path

RUNNER = {"Set up job", "Complete job"}
SHA = re.compile(r"\b[0-9a-f]{40}\b")

def jobs(raw, ids):
    out = []
    for i in str(ids).split(","):
        out += json.loads((raw / f"jobs_{i}.json").read_text())["jobs"]
    return out

def perms(raw, j, logs=None):
    if logs is not None: return logs.get(j["id"], "UNREAD")
    f = raw / "logs" / f"head_{j['id']}.txt"
    if not f.exists() or not f.stat().st_size: return "UNREAD"
    m = re.search(r"##\[group\]GITHUB_TOKEN Permissions\n(.*?)##\[endgroup\]", f.read_text(errors="replace"), re.S)
    return ",".join(sorted(x for x in (re.sub(r"^\S+Z ", "", l).strip() for l in m.group(1).splitlines()) if x)) if m else "NO-BLOCK"

def sets(raw, js, ignore, logs=None):
    st, pm = set(), set()
    for j in js:
        name = j["name"].split(" / ", 1)[-1]
        if name in ignore or j["conclusion"] == "skipped": continue
        pm.add((name, perms(raw, j, logs)))
        for s in j.get("steps") or []:
            if s["conclusion"] in ("success", "failure") and s["name"] not in RUNNER and not s["name"].startswith("Post "):
                st.add((name, SHA.sub("<sha>", s["name"])))
    return st, pm

def compare(b, a):
    rc = 0
    for label, x, y in (("step", b[0], a[0]), ("perm", b[1], a[1])):
        for k in sorted(x - y): print(f"  LOST   {label}  {' | '.join(k)}"); rc = 1
        for k in sorted(y - x): print(f"  GAINED {label}  {' | '.join(k)}"); rc = 1
    print(f"  UNITCHECK steps {len(b[0])}->{len(a[0])} perms {len(b[1])}->{len(a[1])} rc {rc}")
    return rc

ap = argparse.ArgumentParser(); ap.add_argument("raw", type=Path)
ap.add_argument("--before"); ap.add_argument("--after"); ap.add_argument("--ignore", default="prelude,gate,cancel-superseded")
ap.add_argument("--self-test")
a = ap.parse_args(); ign = set(a.ignore.split(","))
if a.self_test:
    B = jobs(a.raw, a.self_test); logs = {j["id"]: perms(a.raw, j) for j in B}
    base = sets(a.raw, B, ign)
    def after(mut):
        A = copy.deepcopy(B)
        for j in A: j["name"] = "unit / " + j["name"]
        L = dict(logs); mut(A, L); return sets(a.raw, A, ign, L)
    print("null (prefixed copy):"); r1 = compare(base, after(lambda A, L: None))
    def drop(A, L):
        for j in A:
            if j["conclusion"] != "skipped" and j.get("steps"): j["steps"] = [s for s in j["steps"] if s["name"] not in RUNNER][1:] + [s for s in j["steps"] if s["name"] in RUNNER]; return
    print("perturbation, one step dropped:"); r2 = compare(base, after(drop))
    def widen(A, L):
        for j in A:
            if j["conclusion"] != "skipped": L[j["id"]] = L[j["id"]] + ",Contents: write"; return
    print("perturbation, one grant widened:"); r3 = compare(base, after(widen))
    ok = (r1, r2, r3) == (0, 1, 1); print(f"SELF-TEST {'ok' if ok else 'BAD'}"); sys.exit(0 if ok else 1)
sys.exit(compare(sets(a.raw, jobs(a.raw, a.before), ign), sets(a.raw, jobs(a.raw, a.after), ign)))
