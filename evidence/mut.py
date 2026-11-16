import subprocess,sys,pathlib
F=pathlib.Path("tools/audit/seat/roster_lib.py"); orig=F.read_text()
M=[("whole-text",'or me in rca_subjects(text)','or me in {t.strip(".-") for t in re.findall(r"[\\w.-]+", text)}'),
("all-paras",'for p in paras[:2 if title else 1]','for p in paras'),
("always-two",'for p in paras[:2 if title else 1]','for p in paras[:2]'),
("no-table-filter",'if not ln.lstrip().startswith("|")]','if True]'),
("title-multiline",'and "\\n" not in paras[0]','and True'),
("title-hash",'paras[0].startswith("# ")','paras[0].startswith("#")'),
("title-never",'title = bool(paras) and','title = False and'),
("split-strict",'re.split(r"\\n[ \\t]*\\n", text.strip())','re.split(r"\\n\\n", text.strip())'),
("table-nolstrip",'if not ln.lstrip().startswith("|")]','if not ln.startswith("|")]'),
("no-strip-text",'text.strip())','text)'),
("no-pstrip-filter",'if p.strip()]','if p]'),
("tok-nostrip",'return {t.strip(".-") for t in re.findall(r"[\\w.-]+", "\\n".join(block))}','return set(re.findall(r"[\\w.-]+", "\\n".join(block)))'),
]
for name,a,b in M:
    if orig.count(a)!=1: print(name,"NOMATCH",orig.count(a)); continue
    F.write_text(orig.replace(a,b))
    try:
        r=subprocess.run([sys.executable,"-I","tools/audit/seat/roster_lib.py","--self-test"],capture_output=True,text=True,timeout=300)
        fails=[l for l in (r.stdout+r.stderr).splitlines() if "FAIL" in l or "Error" in l]
        print(name,"KILLED" if r.returncode else "SURVIVED", "rc",r.returncode, fails[:2])
    finally:
        F.write_text(orig)
print("restored", F.read_text()==orig)
