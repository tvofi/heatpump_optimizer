import importlib.util, json, subprocess, sys
from pathlib import Path
ROOT = Path("/home/user/heatpump_optimizer")
sys.path.insert(0, str(ROOT/"tools/ci"))
spec = importlib.util.spec_from_file_location("prelude", ROOT/"tools/ci/prelude.py")
pre = importlib.util.module_from_spec(spec); spec.loader.exec_module(pre)
runs = json.loads((ROOT/"dev/audit/harnesses/r10_ci_slim/sample.json").read_text())["runs"]
def git(*a):
    p = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None
def diff(b, h):
    o = git("diff", "--name-only", "--no-renames", f"{b}...{h}")
    if o is None:
        subprocess.run(["git","fetch","-q","origin",b],cwd=ROOT,capture_output=True)
        subprocess.run(["git","fetch","-q","origin",h],cwd=ROOT,capture_output=True)
        o = git("diff", "--name-only", "--no-renames", f"{b}...{h}")
    return None if o is None else [x for x in o.splitlines() if x]
def conc(r, pred):
    return {j["conclusion"] for j in r["jobs"] if pred(j["name"])}
mut = lambda r: ",".join(sorted(map(str, conc(r, lambda n: n == "tests / mutation")))) or "missing"
pins = lambda r: conc(r, lambda n: n.startswith("tests / mutation-pins"))
auto = lambda r: conc(r, lambda n: n == "tests / mutation-autofix")
canc = lambda r: any(j["conclusion"] == "cancelled" for j in r["jobs"])
code = sorted((r for r in runs if r["event"] == "pull_request"
               and (pre.parse_title(r["title"]) or ("",))[0] == "code"), key=lambda r: r["created_at"])
byp = {}
for r in code: byp.setdefault(pre.parse_title(r["title"])[1], []).append(r)
print("== pins_due False runs")
nf = nfail = nnotsucc = nunread = 0
for pr, rs in byp.items():
    for i, r in enumerate(rs):
        if i == 0 or rs[i-1]["head_sha"] == r["head_sha"]: continue
        p = rs[i-1]; d = diff(p["head_sha"], r["head_sha"])
        if d is None:
            print(f"PR {pr} run {r['id']} {r['head_sha'][:9]}: git cannot read diff vs {p['head_sha'][:9]}"); nunread += 1; continue
        if pre.pins_due(d): continue
        nf += 1; nfail += mut(r) == "failure"
        ps = pins(p); ok = ps == {"success"}; nnotsucc += not ok
        print(f"PR {pr} R={r['id']} H={r['head_sha'][:9]} prev={p['id']} P={p['head_sha'][:9]} Rmut={mut(r)} "
              f"prevmut={mut(p)} prevpins={sorted(map(str,ps)) or 'missing'} prevautofix={sorted(map(str,auto(p))) or 'missing'} "
              f"prev_status={p['status']} prev_cancelled={'yes' if canc(p) else 'no'}")
print("== per-PR code runs: (id, head, mutation, pins set, any cancelled)")
for pr, rs in byp.items():
    print(f"PR {pr}: " + "; ".join(f"({r['id']}, {r['head_sha'][:9]}, {mut(r)}, {sorted(map(str,pins(r))) or 'missing'}, {'yes' if canc(r) else 'no'})" for r in rs))
hole = 0
for pr, rs in byp.items():
    for i in range(len(rs)-1):
        r, n = rs[i], rs[i+1]
        if not canc(r) or mut(r) not in ("failure", "cancelled") or r["head_sha"] == n["head_sha"]: continue
        d = diff(r["head_sha"], n["head_sha"])
        if d is not None and not pre.pins_due(d): hole += 1
print("== summary")
print(f"code runs total: {len(code)}; PRs: {len(byp)}; unreadable diffs: {nunread}")
print(f"pins_due False runs: {nf}")
print(f"  of those R mutation == failure: {nfail}")
print(f"  of those previous run's mutation-pins not all success: {nnotsucc}")
print(f"code runs with any cancelled job: {sum(canc(r) for r in code)}")
print(f"hole scenario (cancelled run, mutation failure/cancelled, next run pins_due False): {hole}")
