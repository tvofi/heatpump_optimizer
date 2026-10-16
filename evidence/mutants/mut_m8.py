import os, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__)); WT = os.path.join(S, "wt")
C = "tools/audit/archscore/metrics/common.py"
CASES = ("rt_21_lazy_solver_import,rt_22_private_module_attr,rt_23_layer_owner_import,"
         "rt_24_layer_guarded_else,rt_25_layer_negated_guard,rt_26_layer_import_module,"
         "rt_27_layer_absolute_self_import,a3_layer_violations_control,a3_layer_violations_fix,"
         "a3_layer_violations_null,a3_private_cross_module_control,a3_private_cross_module_fix,"
         "a3_private_cross_module_null")
old = ('    t = node.test\n'
       '    if isinstance(t, ast.Name):\n'
       '        return node.body if t.id == "TYPE_CHECKING" else []\n'
       '    if isinstance(t, ast.Attribute) and t.attr == "TYPE_CHECKING" \\\n'
       '            and isinstance(t.value, ast.Name) and t.value.id in ("typing", "typing_extensions"):\n'
       '        return node.body\n'
       '    return []\n')
new = ('    if ast.unparse(node.test).endswith("TYPE_CHECKING"):\n'
       '        return node.body\n'
       '    return []\n')
src = open(os.path.join(WT, C)).read()
assert src.count(old) == 1, src.count(old)
open(os.path.join(WT, C), "w").write(src.replace(old, new))
env = dict(os.environ, PYTHONPATH="tests/hastub", PATH=os.path.join(S,"bin")+":"+os.environ["PATH"])
r = subprocess.run([sys.executable, "tools/audit/archscore/calibrate.py", "--only", CASES, "--jobs", "4"],
                   cwd=WT, env=env, capture_output=True, text=True)
open(os.path.join(S,"ev","arm3_M8_guard_unparse_endswith.txt"),"w").write(r.stdout + r.stderr)
print("rc", r.returncode)
for l in r.stdout.splitlines():
    if l.startswith("MOVED") and "now None" not in l: print(l[:150])
    if "RED TEAM" in l: print(l.strip())
subprocess.run(["git","checkout","-q","--",C], cwd=WT)
print(subprocess.run(["git","status","--short"], cwd=WT, capture_output=True, text=True).stdout)
