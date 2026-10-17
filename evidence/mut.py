import sys, subprocess, pathlib
TARGET = sys.argv[1]
WT = pathlib.Path("/private/tmp/rev-2344")
ent = WT / "tests/entities.py"
clo = WT / "tests/closure.py"
cjs = WT / "tests/closures.json"
PRIST = pathlib.Path("/private/tmp/rev-2344-ev")

def restore():
    (WT/"tests/entities.py").write_text((PRIST/"pristine_entities.py").read_text())
    (WT/"tests/closure.py").write_text((PRIST/"pristine_closure.py").read_text())
    (WT/"tests/closures.json").write_text((PRIST/"pristine_closures.json").read_text())

def sub(path, old, new, label):
    s = path.read_text()
    if s.count(old) != 1:
        print(f"ABORT {label}: anchor count {s.count(old)}"); sys.exit(3)
    path.write_text(s.replace(old, new))

restore()
if TARGET == "M1":
    sub(ent, "        if isinstance(n, ast.Name):\n            stack.extend(binds.get(n.id, ()))\n",
             "        if isinstance(n, ast.Name):\n            pass\n", "M1")
elif TARGET == "M2":
    sub(ent, '        elif name in _SP_READS and isinstance(n.func, ast.Attribute):\n            for cc in _sp_reach(n.func.value, binds):\n                if isinstance(cc, ast.Constant):\n                    opens.add(id(cc))\n', "", "M2")
elif TARGET == "M3":
    sub(ent, '            v = n.value[1:] if id(n) in fstr and n.value.startswith("/") else n.value\n',
             "            v = n.value\n", "M3")
elif TARGET == "M4a":
    sub(clo, "    if (is_handover(rel) or rel in INERT_EXCEPT or _is_header_corpus(rel)\n            or _is_archscore(rel) or _is_citation_source(rel)):\n",
             "    if (is_handover(rel) or rel in INERT_EXCEPT or _is_header_corpus(rel)\n            or _is_archscore(rel)):\n", "M4a")
elif TARGET == "M4b":
    subprocess.run(["git","show","92accb2cff702c910d33ee1a276d38f5b482061c:tests/closures.json"],
                   stdout=open(cjs,"wb"), cwd=WT, check=True)
print(f"MUTANT {TARGET} applied")
r = subprocess.run([sys.executable, str(PRIST/"finder_arm.py")], cwd=WT,
                   capture_output=True, text=True)
for ln in r.stdout.splitlines():
    if ln.startswith(("PASS ","FAIL ","ARM ")):
        print("  " + ln[:170])
if r.returncode != 0:
    print("  (rc %d) stderr tail: %s" % (r.returncode, r.stderr.strip().splitlines()[-3:]))
restore()
