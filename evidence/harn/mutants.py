import sys, shutil, subprocess, os
tree=sys.argv[1]; py=sys.argv[2:]
src=open(f"{tree}/tests/mutation_table.py").read()
M={
 "M1":('or rel in reach["reads"]','or False'),
 "M2":('    if foreign:\n        out.append','    if False:\n        out.append'),
 "M3":('    if reach["untraced"]:','    if False:'),
 "M4":('if p["recorded"] < p["started"]:','if False:'),
 "M5":('if reach.get("rc") != 0:\n        out.append(f"the traced','if False:\n        out.append(f"the traced'),
 "M6":('            or line not in executable):','            or False):'),
 "M7":('    def _importing():\n        try:','    def _importing():\n        return True\n        try:'),
 "M8":('after_in_child=_start)','after_in_child=lambda: None)'),
 "M9":('        return run(script, tree, timeout, extra_args, extra_env), None\n    reach["rc"]','        reach["rc"] = got.rc\n        return got, reach\n    reach["rc"]'),
 "N1":('    def _popen_spawn():\n','    def _popen_spawn():\n        return True\n'),
 "N2":('if event != "os.posix_spawn" or not _popen_spawn():','if True:'),
 "X1":('    _mon.set_events(_mon.COVERAGE_ID, _mon.events.LINE)','    pass'),
 "X3":('elif _hookless(argv) or','elif'),
 "X4":('            if set(a[1:]) & set("IES"):\n                return True','            if False:\n                return True'),
}
work=os.path.join(os.path.dirname(tree),"mtests")
for k,(a,b) in M.items():
    n=src.count(a)
    if n!=1: print(k,"ANCHOR COUNT",n); continue
    work=f"{tree}/tests"
    open(f"{work}/mutation_table.py","w").write(src.replace(a,b))
    for p in py:
        r=subprocess.run([p,os.path.join(os.path.dirname(tree),"harn/rch.py"),work],cwd=tree,capture_output=True,text=True)
        fails=[l[5:60] for l in r.stdout.splitlines() if l.startswith("FAIL")]
        print(k,os.path.basename(p),"RED" if (fails or r.returncode) else "GREEN",fails or r.stderr[-200:])
open(f"{tree}/tests/mutation_table.py","w").write(src)
