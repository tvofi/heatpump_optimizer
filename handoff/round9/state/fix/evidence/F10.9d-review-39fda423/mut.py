import subprocess,sys,pathlib
wt=pathlib.Path(sys.argv[1])
M={
 "P1_reads_none":("tools/audit/merge_fastpath.py","    if any(\"inert_reads\" not in t for t in tables.values()):\n        return None","    return None"),
 "P2_no_sibling":("tools/audit/merge_fastpath.py","                or f in reads[0] or str(Path(f).parent) in reads[1]):","                or f in reads[0]):"),
 "P3_no_file":("tools/audit/merge_fastpath.py","                or f in reads[0] or str(Path(f).parent) in reads[1]):","                or str(Path(f).parent) in reads[1]):"),
 "P4_no_isinert":("tools/audit/merge_fastpath.py","reads is None or not closure.is_inert(f)\n","reads is None\n"),
 "P5_any_all":("tools/audit/merge_fastpath.py","if any(\"inert_reads\" not in t","if all(\"inert_reads\" not in t"),
 "P6_always_ignored":("tools/audit/merge_fastpath.py","for t in tables.values() for s in always for f in t[\"inert_reads\"].get(s, ())}","for t in tables.values() for s in [] for f in t[\"inert_reads\"].get(s, ())}"),
}
for k,(f,a,b) in M.items():
    p=wt/f; src=p.read_text(); assert src.count(a)==1,(k,src.count(a))
    p.write_text(src.replace(a,b))
    r=subprocess.run([sys.executable,f,"--self-test"],cwd=wt,capture_output=True,text=True)
    p.write_text(src)
    fails=[l for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(k,"rc",r.returncode,r.stdout.strip().splitlines()[-1]); [print("   ",l[:150]) for l in fails]
