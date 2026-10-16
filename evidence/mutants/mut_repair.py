"""Re-run the mutants that pin THIS round's repair (M7-M10 in the body's table),
with the mutation strings carrying real newlines. Restores after each."""
import os, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__))
WT = os.path.join(S, "wt")
C  = "tools/audit/archscore/metrics/common.py"
L  = "tools/audit/archscore/metrics/layering.py"
CASES = ("rt_21_lazy_solver_import,rt_22_private_module_attr,rt_23_layer_owner_import,"
         "rt_24_layer_guarded_else,rt_25_layer_negated_guard,rt_26_layer_import_module,"
         "rt_27_layer_absolute_self_import,a3_layer_violations_control,a3_layer_violations_fix,"
         "a3_layer_violations_null,a3_private_cross_module_control,a3_private_cross_module_fix,"
         "a3_private_cross_module_null")

GUARD_ATTR = ('    if isinstance(t, ast.Attribute) and t.attr == "TYPE_CHECKING" \\\n'
              '            and isinstance(t.value, ast.Name) and t.value.id in ("typing", "typing_extensions"):\n'
              '        return node.body\n')
GUARD_NAME = '        return node.body if t.id == "TYPE_CHECKING" else []\n'
SELF = ('    if dotted == SELF:\n        return ""\n'
        '    return dotted[len(SELF) + 1:] if dotted.startswith(SELF + ".") else None\n')
DYN = '    if not named or not node.args:\n        return None\n'

MUTS = {
 "M7_guard_is_whole_if": (C, [(GUARD_NAME, '        return [node] if t.id == "TYPE_CHECKING" else []\n'),
                              (GUARD_ATTR, '    if isinstance(t, ast.Attribute) and t.attr == "TYPE_CHECKING":\n        return [node]\n')]),
 "M8_guard_unparse_endswith": (C, [(GUARD_NAME + GUARD_ATTR,
     '    if ast.unparse(node.test).endswith("TYPE_CHECKING"):\n        return node.body\n')]),
 "M9_no_dynamic": (L, [(DYN, '    return None\n')]),
 "M10_no_self_import": (L, [(SELF, '    return None\n')]),
}

def sh(*a, **kw):
    return subprocess.run(a, cwd=os.path.join(S, "wt") if kw.pop("cwd", True) else None,
                          capture_output=True, text=True, **kw)

env = dict(os.environ, PYTHONPATH="tests/hastub",
           PATH=os.path.join(S, "bin") + ":" + os.environ["PATH"])
for name, (path, edits) in MUTS.items():
    sh("git", "checkout", "-q", "--", C, L)
    src = open(os.path.join(WT, path)).read()
    for old, new in edits:
        assert src.count(old) == 1, f"{name}: {old!r} occurs {src.count(old)}x"
        src = src.replace(old, new)
    open(os.path.join(WT, path), "w").write(src)
    r = subprocess.run([sys.executable, "tools/audit/archscore/calibrate.py", "--only", CASES, "--jobs", "4"],
                       cwd=WT, env=env, capture_output=True, text=True)
    out = os.path.join(S, "ev", "arm3_%s.txt" % name)
    open(out, "w").write(r.stdout + r.stderr)
    moved = [l.split()[1].rstrip(":") for l in r.stdout.splitlines() if l.startswith("MOVED") and "now None" not in l]
    rt = [l for l in r.stdout.splitlines() if l.strip().startswith("RED TEAM")]
    print(f"== {name} rc={r.returncode} moved={sorted(set(moved))}")
    print("   " + (rt[0].strip() if rt else "(no RED TEAM line)"))
    for l in r.stdout.splitlines():
        if l.startswith("MOVED") and "now None" not in l:
            print("   " + l[:150])
    sh("git", "checkout", "-q", "--", C, L)
print("--- git status ---")
print(sh("git", "status", "--short").stdout)
