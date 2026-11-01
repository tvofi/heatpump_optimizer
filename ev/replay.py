# Reviewer's own harness: a claim conflict both sides rewrote, resolved by the real
# tests/env_drift.py driver, plus a ledger refusal, an empty driver, multi-line, long, non-UTF8.
import importlib.util, os, subprocess, sys, tempfile, shlex
from pathlib import Path
ROOT = Path(sys.argv[1]); W = Path(sys.argv[2])
def load(n):
    s = importlib.util.spec_from_file_location(n, W/f"{n}.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
base, head = load("bot_base"), load("bot_head")
td = tempfile.mkdtemp(); r = os.path.join(td, "r")
g = lambda *a: subprocess.run(["git","-C",r,*a],capture_output=True,text=True,check=True).stdout.strip()
os.makedirs(r); g("init","-q","-b","main"); g("config","user.name","x"); g("config","user.email","x@x")
cf="tests/golden/claimed_drift.txt"
g("config","merge.claimnotes.driver",f"{shlex.quote(sys.executable)} {shlex.quote(str(ROOT/'tests/env_drift.py'))} --merge-claim-file %O %A %B %L %P")
Path(r,".gitattributes").write_text(f"{cf} merge=claimnotes\n"); os.makedirs(os.path.join(r,"tests/golden"))
Path(r,cf).write_text("# claims-for: 1.0.0\n"); g("add","-A"); g("commit","-qm","c0"); c0=g("rev-parse","HEAD")
def side(b,t):
    g("checkout","-q","-b",b,c0); Path(r,cf).write_text(t); g("commit","-qam",b); return g("rev-parse","HEAD")
a=side("fix","# claims-for: 1.0.0\nscen_x # ours: lower cost\n"); m=side("mn","# claims-for: 1.0.0\nscen_x # main: higher cost\n")
for name,mod in (("base",base),("head",head)):
    st,_=mod.plan_one(r,a,m,mergeable=False,same_repo=True)
    print(f"RESULT replay-2872-shape at={name} lines={len(st.splitlines())} carries_decision={'scen_x' in st}")
    print("  " + st.replace("\n","\n  "))
# null control: non-refusal statuses byte-identical
kw=dict(mergeable=False,same_repo=True,contains_main=False,text_conflicts=["led.json"],drivers={"led.json":"f"},driver_rc=0,driver_conflicts=[],driver_err="")
cases=[{},{"mergeable":True},{"same_repo":False},{"text_conflicts":[]},{"text_conflicts":["led.json","a.py"],"driver_err":"MERGE-CLAIM: refused x\nfoo"},
       {"driver_rc":1,"driver_err":"LEDGER-MERGE: refused led.json: why"},{"driver_rc":1,"driver_err":""},{"driver_conflicts":["led.json"]}]
same=all(base.decide(**{**kw,**c})==head.decide(**{**kw,**c}) for c in cases)
same2=all(base.decide(**{**kw,**c},pins=p)==head.decide(**{**kw,**c},pins=p) for c in cases for p in (None,["x"]))
print(f"RESULT null-control non-claim-refusal statuses byte-identical base==head: {same and same2} ({len(cases)*3} cases)")
cr=head.claim_refusal
print("RESULT empty stderr ->", repr(cr("")))
print("RESULT multi-line ->", repr(cr("LEDGER-MERGE: resolved l.json\nMERGE-CLAIM: refused c.txt\n  a\n\n  b\n")))
long_="MERGE-CLAIM: refused c\n"+"x"*100+"\n"*0
big="MERGE-CLAIM: refused c\n"+"\n".join("line%d"%i for i in range(100000))
print("RESULT very long stderr (100001 lines) relayed length chars:", len(cr(big)), "(no cap)")
print("RESULT CRLF ->", repr(cr("MERGE-CLAIM: refused c\r\nz\r\n")))
# non-UTF8: the git() helper decodes text=True strict; does it raise?
try:
    subprocess.run([sys.executable,"-c","import sys;sys.stderr.buffer.write(b'MERGE-CLAIM: refused c\\n\\xff\\xfe\\n')"],capture_output=True,text=True,encoding="utf-8")
    print("RESULT non-UTF8 stderr decode: no error")
except UnicodeDecodeError as e:
    print("RESULT non-UTF8 stderr decode: UnicodeDecodeError (raised in subprocess.run, before claim_refusal; identical at base:", "text=True" in (W/"bot_base.py").read_text(), ")")
