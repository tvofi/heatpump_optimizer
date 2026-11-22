import sys, subprocess, pathlib
p = pathlib.Path("tests/structure.py"); orig = p.read_text()
M = {
 "A_binding_off": ("    if bindings:\n        names |=", "    if False:\n        names |="),
 "B_module_zero": ("    return sum(max(0, (tree.body[-1].end_lineno", "    return 0 * sum(max(0, (tree.body[-1].end_lineno"),
 "C_alias_ignored": ("bindings |= {a.asname or a.name for a", "bindings |= {a.name for a"),
 "D_const_filter_off": ("for a in node.names if a.name == \"const\"}", "for a in node.names}"),
 "E_lineno_not_end": ("(tree.body[-1].end_lineno if tree.body", "(tree.body[-1].lineno if tree.body"),
 "F_names_list_dup": ("        fanout = len(const_names_read(tree))", "        fanout = len(const_names_read(tree)) if False else 0"),
 "G_attr_any_name": ("and isinstance(n.value, ast.Name) and n.value.id in bindings}", "and isinstance(n.value, ast.Name)}"),
 "H_limit_off_by": ("- MODULE_LOC_LIMIT)\n", "- MODULE_LOC_LIMIT - 1)\n"),
}
for k,(a,b) in M.items():
    assert orig.count(a)==1, k
    p.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable,"tests/structure.py"],env={"PYTHONPATH":"tests/hastub","PATH":"/opt/hpo/venv-ci/bin:/usr/bin:/bin"},capture_output=True,text=True)
    fails=[l for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL") or "BROKEN" in l or "BREACHED" in l]
    print(f"MUTANT {k}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}"); [print("   ",l) for l in fails[:6]]
p.write_text(orig); print("restored", subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout or "clean")
