import subprocess, sys, pathlib
p = pathlib.Path("tests/closure.py"); orig = p.read_text()
muts = {
 "Mc1 check reads closures only": ('        for table_key in ("closures", "inert_reads")\n        for script, files in table.get(table_key, {}).items()', '        for table_key in ("closures",)\n        for script, files in table.get(table_key, {}).items()'),
 "Mc2 prune reads closures only": ('    for table_key in ("closures", "inert_reads"):\n        table = payload.get', '    for table_key in ("closures",):\n        table = payload.get'),
 "Mc3 prune keeps empty key": ('            if real or table_key == "closures":', '            if True:'),
 "Mc4 prune drops empty closures key too": ('            if real or table_key == "closures":', '            if real:'),
}
for name,(a,b) in muts.items():
    assert orig.count(a)==1, name
    p.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable,"tests/closure.py","selftest"],capture_output=True,text=True)
    reds=[l for l in (r.stdout+r.stderr).splitlines() if l.strip().startswith(("FAIL","not ok","XX","✗")) or " FAIL" in l[:8]]
    print(f"RESULT {name}: rc={r.returncode} red={len(reds)}", reds[:3])
p.write_text(orig)
