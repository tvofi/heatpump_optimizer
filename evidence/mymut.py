import subprocess, sys, pathlib, os
W = pathlib.Path(os.environ["HOME"]) / "wt-mut"
MUT = [
 ("A1-rc-distinction", "tools/pr/app_approve.sh", '    if [ "$anc" -eq 1 ]; then echo "$v is not an ancestor of $h"', '    if true; then echo "$v is not an ancestor of $h"', "bash tools/pr/app_approve.sh --self-test"),
 ("A2-no-fetch", "tools/pr/app_approve.sh", 'git cat-file -e "$ob^{commit}" 2>/dev/null || git fetch -q --no-tags origin "$ob" >/dev/null 2>&1 || :', ':', "bash tools/pr/app_approve.sh --self-test"),
 ("B1-post-red-pass", "tools/audit/seat/bus.sh", "        0|3|4) ;;\n", "        0|1|3|4) ;;\n", "bash tools/audit/seat/bus.sh --self-test"),
 ("B2-post-unreadable-pass", "tools/audit/seat/bus.sh", "        0|3|4) ;;\n", "        *) ;;\n", "bash tools/audit/seat/bus.sh --self-test"),
 ("B3-c4-derive-off", "tools/audit/seat/bus.sh", '  if [ -z "$rh" ] && [ -z "$n" ]; then', '  if false; then', "bash tools/audit/seat/bus.sh --self-test"),
]
sel = sys.argv[1:]
for name, f, old, new, cmd in MUT:
    if sel and name not in sel: continue
    p = W / f; src = p.read_text()
    n = src.count(old)
    if n != 1:
        print(f"RESULT {name}: NOT-BUILT (anchor count {n})", flush=True); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(cmd, shell=True, cwd=W, capture_output=True, text=True, timeout=3000)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if l.startswith(("FAIL", "not ok", "FAILED")) or " FAIL " in l][:6]
        tail = out.strip().splitlines()[-1:] 
        print(f"RESULT {name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {tail} | {fails}", flush=True)
    finally:
        p.write_text(src)
