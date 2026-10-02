import os, sys, subprocess as sp, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(sys.argv[1], "tests"))
import env_drift as E
root = tempfile.mkdtemp()
def g(*a): return sp.run(["git",*a],cwd=root,check=True,capture_output=True,text=True).stdout.strip()
def put(r,t):
    p=Path(root,r); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(t)
hdr="# claims-for: 6.7.12\n"
put("VERSION","6.7.12\n"); put(E.CLAIM_FILE,hdr); put(E.CARD_CLAIM_FILE,hdr)
put("custom_components/heatpump_optimizer/optimizer.py","x=1\n"); put(E.CARD_JS,"//c\n")
g("init","-q"); g("config","user.email","t@t"); g("config","user.name","t"); g("add","-A"); g("commit","-qm","base"); g("branch","-M","main")
# claiming PR merged to main (--no-ff merge commit)
g("checkout","-qb","claimer"); put("custom_components/heatpump_optimizer/optimizer.py","x=2\n"); put(E.CLAIM_FILE,hdr+"wood_coil  # claimer moves it\n"); g("commit","-qam","claim")
g("checkout","-q","main"); g("merge","-q","--no-ff","--no-edit","claimer")
os.environ.pop("CLAIM_HEAD",None)
print("main push after claiming merge, claims-only HEAD^1:", E.check_claims_hygiene(root,"HEAD^1"))
cl=E._claimed(root)[1]
j=E.judge_drift(root,"HEAD^1",{"wood_coil":{"v":2}},{"wood_coil":{"v":1}},cl,{})
print("  judge_drift:", j)
# a non-claiming PR merges next, moves wood_coil again
g("checkout","-qb","other"); put("custom_components/heatpump_optimizer/optimizer.py","x=3\n"); g("commit","-qam","other")
g("checkout","-q","main"); g("merge","-q","--no-ff","--no-edit","other")
print("main push after non-claiming merge, claims-only HEAD^1:", E.check_claims_hygiene(root,"HEAD^1"))
j=E.judge_drift(root,"HEAD^1",{"wood_coil":{"v":3}},{"wood_coil":{"v":2}},E._claimed(root)[1],{})
print("  judge_drift (carried line must NOT excuse):", j)
# squash variant
g("checkout","-qb","sq"); put("custom_components/heatpump_optimizer/optimizer.py","x=4\n"); put(E.CLAIM_FILE,Path(root,E.CLAIM_FILE).read_text()+"dhw_only  # sq\n"); g("commit","-qam","sq")
g("checkout","-q","main"); g("merge","-q","--squash","sq"); g("commit","-qm","squash sq")
print("squash claiming merge, claims-only HEAD^1:", E.check_claims_hygiene(root,"HEAD^1"))
print("  judge_drift:", E.judge_drift(root,"HEAD^1",{"wood_coil":{"v":4},"dhw_only":{"v":2}},{"wood_coil":{"v":3},"dhw_only":{"v":1}},E._claimed(root)[1],{}))
