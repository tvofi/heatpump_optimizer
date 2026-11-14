import subprocess, sys, pathlib, shutil
SRC = pathlib.Path("/root/wt2/tools/audit/seat/merge_train.py")
orig = SRC.read_text()
M = {
 "M4 record_drafts call in _batch -> pass": ("self.record_drafts(queue)", "pass"),
 "M7 pending.add -> pass": ("            pending.add(name)\n", "            pass\n"),
 "M8 zero-time filter dropped": ('if x and not x.startswith("0001")]', 'if x]'),
 "M9 startedAt fallback dropped": ('(c.get("completedAt"), c.get("startedAt")) if x', '(c.get("completedAt"),) if x'),
 "X10 >= -> >": ("(stamp, i) >= best[name][0]", "(stamp, i) > best[name][0]"),
 "X14 stamps[0] -> stamps[-1]": ("stamp = stamps[0] if stamps", "stamp = stamps[-1] if stamps"),
 "X16 drop context fallback": ('c.get("name") or c.get("context") or "?"', 'c.get("name") or "?"'),
 "X17 drop real guard in record_drafts": ('        if not self.real:\n            return\n        for item in queue:\n            if "draft" not in item:', '        for item in queue:\n            if "draft" not in item:'),
}
for name, sub in M.items():
    if sub is None: continue
    a, b = sub
    if orig.count(a) != 1:
        print(f"{name}: NOT-APPLIED (count {orig.count(a)})"); continue
    SRC.write_text(orig.replace(a, b))
    try:
        p = subprocess.run([sys.executable, str(SRC), "--self-test"], cwd="/root/wt2", capture_output=True, text=True, timeout=400)
        fails = [l.strip() for l in (p.stdout + p.stderr).splitlines() if l.strip().startswith("FAIL")]
        tail = (p.stdout + p.stderr).strip().splitlines()[-1:] 
        verdict = "KILLED" if p.returncode != 0 else "SURVIVED"
        print(f"{name}: {verdict} rc={p.returncode} {tail} {fails[:4]}")
    except subprocess.TimeoutExpired:
        print(f"{name}: KILLED-by-timeout (hang)")
    finally:
        SRC.write_text(orig)
