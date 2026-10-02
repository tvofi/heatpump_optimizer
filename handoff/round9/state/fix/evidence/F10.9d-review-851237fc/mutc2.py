import subprocess,sys,pathlib,os
wt=pathlib.Path(sys.argv[1]); f="tests/closure.py"
M={
 "C1_execrecord_empty":('"inert_reads": sorted(f for f in opened if _is_real_file(f) and is_inert(f)),','"inert_reads": [],'),
 "C2_union_drop":('    rec["inert_reads"] = sorted(set(rec.get("inert_reads", ())) | inert_seen)\n',''),
 "C3_fold_noop":('    for k, r in records.items():\n        reads = sorted(f for f in r.get("inert_reads", ()) if _is_real_file(f))','    for k, r in []:\n        reads = sorted(f for f in r.get("inert_reads", ()) if _is_real_file(f))'),
 "C5_fullmerge_nofold":('    _fold_inert_reads(payload["inert_reads"], records)\n',''),
 "C6_partialmerge_nofold":('        _fold_inert_reads(payload.setdefault("inert_reads", {}), records)\n',''),
 "C4_check_off":('    if missed:\n        print("INERT READS','    if False:\n        print("INERT READS'),
}
env=dict(os.environ)
p=wt/f; src=p.read_text()
for k,(a,b) in M.items():
    assert src.count(a)==1,k
    p.write_text(src.replace(a,b))
    out=[]
    for cmd in (["python","tests/entities.py"],["python","tests/closure.py","selftest"],["python","tools/audit/merge_fastpath.py","--self-test"]):
        r=subprocess.run(cmd,cwd=wt,capture_output=True,text=True,env=env)
        lines=(r.stdout+r.stderr).strip().splitlines()
        fails=[l.strip()[:140] for l in lines if l.strip().startswith(("FAIL","✗"))][:3]
        out.append(f"  {cmd[1]} rc={r.returncode} :: {lines[-1][:120] if lines else ''} {fails}")
    p.write_text(src)
    print(k); print("\n".join(out), flush=True)
