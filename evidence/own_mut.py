import subprocess, sys, pathlib, shutil
wt = pathlib.Path(sys.argv[1]); f = wt/"tools/audit/seat/roster_edit.py"
orig = f.read_text()
M = {
 "M1 finished node never marked done": ("                state[node] = 2\n", "                pass\n"),
 "M2 drop pops last not i": ("    del carry[i]\n", "    carry.pop()\n"),
 "M3 cycle test inverted to finished": ("elif state.get(nxt) == 1:", "elif state.get(nxt) == 2:"),
 "M4 match is prefix not substring": ("if match in c]", "if c.startswith(match)]"),
 "M5 after stored sorted": ('    g["after"] = after\n', '    g["after"] = sorted(after)\n'),
 "M6 strip removed": ("[a.strip() for a in spec.split(\",\")]", "spec.split(\",\")"),
 "M7 dash not special": ('after = [] if spec == "-" else', 'after = [] if spec == "--" else'),
 "M8 dup check removed": ("    if dup:\n        raise Refuse(f\"set-after: duplicate", "    if False:\n        raise Refuse(f\"set-after: duplicate"),
}
for name,(a,b) in M.items():
    assert orig.count(a)==1, name
    f.write_text(orig.replace(a,b))
    try:
        r = subprocess.run([sys.executable,"tools/audit/seat/roster_edit.py","--self-test"],cwd=wt,capture_output=True,text=True,timeout=900)
        out = r.stdout+r.stderr
        fails=[l for l in out.splitlines() if l.strip().startswith("FAIL")]
        summ=[l for l in out.splitlines() if "self-test:" in l]
        tb = "Traceback" in out
        print(f"RESULT own-mutant={name!r} rc={r.returncode} fails={len(fails)} traceback={tb} {summ[-1:]} {fails[:3]}", flush=True)
    finally:
        f.write_text(orig)
assert f.read_text()==orig
print("restored")
