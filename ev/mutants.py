# Reviewer's mutation driver: each mutant is a literal (file, old, new) applied to the worktree,
# owning self-tests run, restored by git checkout.
import subprocess, sys, pathlib
T = pathlib.Path(sys.argv[1])
MT, RP, BUS = "tools/audit/seat/merge_train.py", "tools/audit/seat/review_packet.py", "tools/audit/seat/bus.sh"
M = [
 ("R1 RED_CONCLUSIONS failure only", MT, 'RED_CONCLUSIONS = frozenset({"failure", "cancelled", "timed_out", "action_required", "startup_failure"})', 'RED_CONCLUSIONS = frozenset({"failure"})', "mr"),
 ("R2 STEP_READ without timed_out", MT, 'SELFTESTS_STEP_READ = frozenset({"failure", "timed_out"})', 'SELFTESTS_STEP_READ = frozenset({"failure"})', "mr"),
 ("R3 JOB_TIMED_OUT never added", MT, '        names.insert(0, JOB_TIMED_OUT)', '        pass', "mr"),
 ("R4 timeout not subtracted by base timeout", MT, 'if hc == "timed_out" and bc != "timed_out":', 'if hc == "timed_out":', "m"),
 ("R5 running head job reads clean", MT, '        return None, f"head {SELFTESTS} job {hj[\'id\']}: {hc}"', '        return [], f"head {SELFTESTS} job {hj[\'id\']}: {hc}"', "mr"),
 ("R6 selftest_job max->min", MT, '    return max(mine, key=lambda r: int(r["id"])) if mine else None', '    return min(mine, key=lambda r: int(r["id"])) if mine else None', "m"),
 ("R7 job-level cancelled read clean", MT, 'SELFTESTS_CLEAN = frozenset({"success", "skipped", "neutral"})', 'SELFTESTS_CLEAN = frozenset({"success", "skipped", "neutral", "cancelled", "startup_failure", "action_required"})', "mr"),
 ("R8 red job with no red step not refused", MT, '    if not _red_steps(hs):\n', '    if False:\n', "m"),
 ("R9 classify WAIT branch dropped", MT, '        if intro is None and state == "green":', '        if False:', "m"),
 ("R10 base non-readable conclusion accepted", MT, '        if bc not in SELFTESTS_CLEAN | SELFTESTS_STEP_READ:', '        if False:', "m"),
 ("R11 ci_facts introduced dropped", RP, '            "introduced": introduced_reading(head, base, read)}', '            "introduced": ([], "")}', "r"),
 ("R12 packet running-job reads clean", RP, '    if names is None:\n        return [], f"unreadable:', '    if names is None:\n        return [], f"pending:', "r"),
 ("R13 introduced_cmd pending dropped", MT, '    if intro is None:\n        return 3, f"introduced: pending', '    if False:\n        return 3, f"introduced: pending', "m"),
]
only = sys.argv[2:] or None
for name, f, old, new, who in M:
    if only and name.split()[0] not in only: continue
    p = T / f; s = p.read_text()
    if s.count(old) != 1:
        print(f"{name}: ANCHOR {s.count(old)} matches -- not applied", flush=True); continue
    p.write_text(s.replace(old, new))
    fails = []
    if "m" in who:
        o = subprocess.run([sys.executable, f"{T}/{MT}", "--self-test"], cwd=T, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
        fails += [l.strip() for l in o.splitlines() if l.lstrip().startswith("FAIL")]
        fails.append(o.strip().splitlines()[-1] if o.strip() else "no output")
    if "r" in who:
        o = subprocess.run([sys.executable, f"{T}/{RP}", "--self-test"], cwd=T, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
        fails += [l.strip() for l in o.splitlines() if l.lstrip().startswith("FAIL")]
        fails.append(o.strip().splitlines()[-1] if o.strip() else "no output")
    subprocess.run(["git", "checkout", "--", f], cwd=T, check=True)
    killed = any(" 0 failed" not in x for x in fails if "self-test:" in x)
    print(f"{name}: {'KILLED' if killed else 'SURVIVED'}", flush=True)
    for x in fails: print("   ", x[:200], flush=True)
print("tree clean:", subprocess.run(["git","status","--porcelain"],cwd=T,capture_output=True,text=True).stdout == "", flush=True)
