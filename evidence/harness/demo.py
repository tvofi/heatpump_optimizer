import shutil, subprocess, tempfile, json, random
from pathlib import Path
src=Path("/root/wt/tools/audit/seat")
M={
 "gate_name_any":('if j["name"] == "gate":','if True:'),
 "report_record_dropped":("out.append(line_ck(runs, rd(record) if record else None))","out.append(line_ck(runs, None))"),
 "first_by_input_not_t":("last = sorted(by.values(), key=lambda vs: vs[0][\"t\"])[-WINDOW_PRS:]","last = list(by.values())[-WINDOW_PRS:]"),
 "named_regex_no_merged":('r"(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)"','r"(BATCH|SKIP|PARK|ADMIT|ALREADY)"'),
}
S=Path("/root/h/st7"); U=Path("/root/h/st7u"); shutil.rmtree(U,ignore_errors=True); shutil.copytree(S,U)
v=json.load(open(U/"scorecard/verdicts.json")); random.seed(3); random.shuffle(v["verdicts"]); json.dump(v,open(U/"scorecard/verdicts.json","w"))
def run(sc,st):
    return subprocess.run(["python3","-I",str(sc),"report","--dir",str(st/"scorecard"),"--train-log",str(st/"train.log"),"--sweep-record",str(st/"sweep.rec")],capture_output=True,text=True).stdout.splitlines()
for name,(a,b) in M.items():
    t=Path(tempfile.mkdtemp()); shutil.copy(src/"scorecard.py",t); s=(t/"scorecard.py").read_text(); (t/"scorecard.py").write_text(s.replace(a,b))
    st=U if name=="first_by_input_not_t" else S
    base=run(src/"scorecard.py",st); mut=run(t/"scorecard.py",st)
    print(f"## {name} on {st.name}")
    for x,y in zip(base,mut):
        if x!=y: print("  head:  ",x); print("  mutant:",y)
