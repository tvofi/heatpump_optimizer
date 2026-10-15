import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[1])
L="tools/audit/seat/roster_lib.py"; T="tools/audit/seat/orchestrator_tick.py"; D="tools/audit/seat/state_docs.py"
E="tools/audit/seat/roster_edit.py"; Z="tools/audit/seat/daemonize.py"
M = {
 "M1": (L, "found = [(int(m.group(1)), m.group(0))", "found = [(m.group(1), m.group(0))", ["roster_lib","roster_edit","orchestrator_tick"]),
 "M2": (L, "    if override:\n        there", "    if False:\n        there", ["roster_lib","roster_edit"]),
 "M3": (L, "    if path is None:\n        raise RosterNotFound(f\"no {ROSTERS_DIR}", "    if path is None:\n        return f\"{ROSTERS_DIR}/wave-r9-groups.json\"\n    if path is None:\n        raise RosterNotFound(f\"no {ROSTERS_DIR}", ["roster_lib","roster_edit"]),
 "M4": (D, '    d = f"handoff/round{round_n}/state"', '    round_n = 9\n    d = f"handoff/round{round_n}/state"', ["state_docs"]),
 "M4b": (D, "    is none, rather than defaulting to some round.\"\"\"\n", "    is none, rather than defaulting to some round.\"\"\"\n    return 9\n", ["state_docs"]),
 "M5": (Z, '    if "--" in argv:', '    if False:', ["daemonize"]),
 "M6": (T, "            path = self.roster_path\n", "            path = \"dev/programme/rosters/wave-r9-groups.json\"\n", ["orchestrator_tick"]),
 "M7": (T, "            path = self.roster_path\n", "            path = None\n", ["orchestrator_tick"]),
 "M8": (E, "        return ref, roster_lib.round_branch(path)", "        return ref, ref", ["roster_edit"]),
 "M9-own": (L, '    return subprocess.run(["git", "-C", repo, *args]', '    return subprocess.run(["git", *args]', ["roster_lib"]),
}
for name,(f,old,new,tools) in M.items():
    p = W/f; src = p.read_text()
    assert src.count(old)==1, (name, src.count(old))
    p.write_text(src.replace(old,new,1))
    res=[]
    for t in tools:
        r = subprocess.run([sys.executable, f"tools/audit/seat/{t}.py","--self-test"], cwd=W, capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith(("FAIL","fail")) or "failed:" in l or "check(s) failed" in l][:6]
        res.append(f"{t} rc={r.returncode} {fails}")
    subprocess.run(["git","checkout","--",f], cwd=W, check=True)
    print(f"RESULT mutant {name}: " + " | ".join(res), flush=True)
print("clean:", subprocess.run(["git","status","--porcelain"],cwd=W,capture_output=True,text=True).stdout or "yes")
