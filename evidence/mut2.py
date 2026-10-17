import sys, subprocess, pathlib
WT = pathlib.Path("/private/tmp/rev-2344-r2"); PRIST = pathlib.Path("/private/tmp/rev-2344-r2-ev")
ent = WT/"tests/entities.py"
PRIST.joinpath("pristine2_entities.py").write_text(ent.read_text()) if not (PRIST/"pristine2_entities.py").exists() else None
P = (PRIST/"pristine2_entities.py")
def restore(): ent.write_text(P.read_text())
def sub(old, new, label):
    s = ent.read_text(); n = s.count(old)
    if n != 1: print(f"ABORT {label}: anchor count {n}"); sys.exit(3)
    ent.write_text(s.replace(old, new))
def run(label):
    r = subprocess.run([sys.executable, str(PRIST/"finder_arm.py")], cwd=WT, capture_output=True, text=True)
    print(f"===== {label}")
    for ln in r.stdout.splitlines():
        if ln.startswith(("PASS ","FAIL ","ARM ")): print("  "+ln[:190])
restore(); run("M0 null run (unmodified round-2 head)")
restore(); sub("        key = n.id if isinstance(n, ast.Name) else (n.attr if isinstance(n, ast.Attribute) else None)\n",
               "        key = None\n", "M1"); run("M1 _sp_reach stops following a bound name")
restore(); sub("        if (name in _SP_OPENS or name in _SP_READS\n", "        if (name in _SP_OPENS\n", "M2"); run("M2 _SP_READS dropped from the open-site test")
restore(); sub('        v = n.value[1:] if id(n) in fstr and n.value.startswith("/") else n.value\n', "        v = n.value\n", "M3"); run("M3 f-string strip removed")
restore(); sub("            if isinstance(n.func, ast.Attribute):\n                for cc in _sp_reach(n.func.value, scopes, parent, scope):\n                    if isinstance(cc, ast.Constant):\n                        opens.add(id(cc))\n", "", "M4"); run("M4 receiver branch removed")
restore(); sub("        elif isinstance(node, (ast.For, ast.AsyncFor)):\n            if isinstance(node.iter, (ast.Tuple, ast.List, ast.Set)):\n                bind(scope, [node.target], node.iter)\n", "", "M5"); run("M5 for-target binding removed")
restore(); sub("        inner = node if isinstance(node, _SP_SCOPE_NODES) else scope\n", "        inner = scope\n", "M6"); run("M6 scope chain replaced by one flat map")
restore(); print("restored; git status:", subprocess.run(["git","status","--porcelain"],cwd=WT,capture_output=True,text=True).stdout.strip() or "(clean)")
