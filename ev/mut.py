import subprocess,tempfile,os,sys
H="c7c5cef52a49bed59ee4c8a42e495ef2dae30db5"
M=[("m1-no-owned","    if owned := _owned_lane(group):\n        return owned\n","")
,("m2-no-kindfallback",'    if k in INSTRUMENT_KINDS or group.get("class") == "instrument":\n        return "Instruments"\n',"")
,("m3-no-class",' or group.get("class") == "instrument":',':')
,("m4-any","not all(f.startswith","not any(f.startswith")
,("m5-nofiles-guard","if not files or not all","if not all")
,("m6-userdocs-tooling","\n                 and not any(f.startswith(_TOOLING_PREFIXES) for f in files))",")")
,("m7-doc-kind",'group.get("kind") == "doc" or user_docs','user_docs')
,("m8-hotfiles",' + list(group.get("hot_files") or [])',"")
,("m9-docs-prefix",', "dev/", "docs/")',', "dev/")')
,("m10-rootfiles",'_NON_PRODUCT_FILES = ("CLAUDE.md", "AGENTS.md", "README.md", "RELEASE_NOTES.md")','_NON_PRODUCT_FILES = ()')
,("m11-rca-kind",'("instrument", "policy", "rca", "tooling")','("instrument", "policy", "tooling")')
,("m12-userdocs-true","user_docs = (any(","user_docs = True or (any(")
,("m0-null",None,None)]
for n,a,b in M:
    d=tempfile.mkdtemp()
    subprocess.run(f"git archive {H} | tar -x -C {d}",shell=True,check=True)
    p=d+"/tools/plan/replan.py"; s=open(p).read()
    if a is not None:
        assert s.count(a)==1,(n,s.count(a)); open(p,"w").write(s.replace(a,b))
    r=subprocess.run(["python3","-I","tools/plan/replan.py","--self-test"],cwd=d,capture_output=True,text=True)
    print("MUTANT",n,"rc=%d"%r.returncode)
    for l in (r.stdout+r.stderr).splitlines():
        if l.startswith("FAIL") or "self-test:" in l and "failed" in l or "Traceback" in l or "Error" in l: print("  ",l[:150])
