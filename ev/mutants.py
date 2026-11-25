import subprocess, sys, shutil, os
wt = sys.argv[1]; src = os.path.join(wt, "tools/ci/sweep.py"); orig = open(src).read()
M = {
 "A pinned exemption off": ("and not n.startswith(pinned)", "and True"),
 "B fail-open on unreadable": ("        if pinned is None:\n            return []\n", "        if pinned is None:\n            pinned = ()\n"),
 "C PIN_MARK test dropped": ('"PINNED:" in line and PIN_MARK in line', '"PINNED:" in line'),
 "D no split at expression": ("(name or job).split('${{')[0]", "(name or job)"),
 "E key instead of name": ("(name or job).split('${{')[0]", "job"),
 "F name-is-None guard off": ('line.startswith("    name:") and name is None', 'line.startswith("    name:")'),
 "G any indented key is a job": ('line[2:3] not in (" ", "#", "")', 'True'),
 "H pinned_graders returns None": ("    return tuple(sorted(out))", "    return None"),
 "I pinned_graders returns ()": ("    return tuple(sorted(out))", "    return ()"),
 "M6 status ignored": ('j.get("status", "completed") == "completed"', "True"),
 "M7 key order swapped": ('k = (j.get("started_at") or "", r["id"])', 'k = (r["id"], j.get("started_at") or "")'),
 "M2 conclusion !=success": ('if c == "failure")', 'if c != "success")'),
 "M3 first wins": ('if j["name"] not in newest or k > newest[j["name"]][0]:', 'if j["name"] not in newest:'),
 "M5 code_red empty": ("        from gate import REQUIRED        # the gate's own list, never restated here\n", "        return []\n"),
 "J PIN_MARK wrong": ('PIN_MARK = "github.event.pull_request.base.sha"', 'PIN_MARK = "github.sha"'),
 "K in_jobs never set": ("                    in_jobs = True", "                    in_jobs = False"),
}
for k,(a,b) in M.items():
    n = orig.count(a)
    if n != 1: print(f"{k}: SKIP anchor count {n}"); continue
    open(src,"w").write(orig.replace(a,b))
    p = subprocess.run([sys.executable, "tools/ci/sweep.py", "--self-test"], cwd=wt, capture_output=True, text=True)
    out = p.stdout + p.stderr
    fails = [l for l in out.splitlines() if "FAIL" in l][:3]
    print(f"{k}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} | {out.strip().splitlines()[-1] if out.strip() else ''}")
    for l in fails: print("    ", l[:200])
open(src,"w").write(orig)
p = subprocess.run([sys.executable, "tools/ci/sweep.py", "--self-test"], cwd=wt, capture_output=True, text=True)
print("unmutated:", p.returncode, p.stdout.strip().splitlines()[-1])
