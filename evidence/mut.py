import subprocess, sys, pathlib
F = pathlib.Path("wt/tools/audit/seat/roster_edit.py").resolve()
orig = F.read_text()
M = {
 "M1 unwire absent-refusal deleted": ('    if n not in held:\n        raise Refuse(f"{group} does not hold #{n} in {field} "\n                     f"(holds: {held})")\n', ''),
 "M2 unwire default field -> fixes": ('op_unwire_issue(roster, a.group, value, a.field or "issues")', 'op_unwire_issue(roster, a.group, value, a.field or "fixes")'),
 "M3 wire dispatch drops --field": ('op_wire_issue(roster, a.group, value, a.field or "issues")', 'op_wire_issue(roster, a.group, value)'),
 "M4 unwire keeps the entry": ('    g[field] = [i for i in held if i != n]\n', '    g[field] = list(held)\n'),
 "M5 wire dup-refusal deleted": ('    if n in (g.get(field) or []):\n        raise Refuse(f"{group} already wires #{n} in {field}")\n', ''),
 "M6 wire writes issues regardless": ('    g.setdefault(field, []).append(n)\n    g[field].sort()\n', '    g.setdefault("issues", []).append(n)\n    g["issues"].sort()\n'),
 "M7 main --field guard for wire ops deleted": ('    if a.op in ("wire-issue", "unwire-issue") and a.field \\\n            and a.field not in WIRE_FIELDS:\n        p.error(f"{a.op} --field is one of {\', \'.join(WIRE_FIELDS)}")\n', ''),
 "M8 op-level WIRE_FIELDS guard in unwire deleted": ('    if field not in WIRE_FIELDS:\n        raise Refuse(f"--field for unwire-issue is one of "\n                     f"{\', \'.join(WIRE_FIELDS)}, not {field!r}")\n', ''),
 "M9 dispatch unwire op dropped": ('        elif a.op == "unwire-issue":\n            op_unwire_issue(roster, a.group, value, a.field or "issues")\n', ''),
 "M10 unwire removes from issues regardless": ('    held = g.get(field) or []\n', '    field = "issues"\n    held = g.get(field) or []\n'),
}
try:
  for name,(a,b) in M.items():
    assert orig.count(a)==1, name
    F.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable,str(F.resolve()),"--self-test"],capture_output=True,text=True,cwd="wt")
    last=[l for l in (r.stdout+r.stderr).splitlines() if "self-test:" in l or "FAIL" in l.upper()]
    fails=[l for l in (r.stdout+r.stderr).splitlines() if "self-test:" in l]
    print(f"RESULT mutant {name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {fails[-1] if fails else (r.stdout+r.stderr)[-200:]}")
finally:
  F.write_text(orig)
