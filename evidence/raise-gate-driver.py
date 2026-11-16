import subprocess,sys,json
sys.path.insert(0,'tools/policy')
import budget_raise_gate as g
MB='6f422812d5d8b918beace0283419c153f6df66ce'; H='724ee26de5ee639ab76f3bb33ee534a18da30211'
def ls(s): return subprocess.run(['git','ls-tree','-r','--name-only',s],capture_output=True,text=True).stdout.splitlines()
def show(s,p):
    if p is None: return None
    r=subprocess.run(['git','show',f'{s}:{p}'],capture_output=True,text=True); return r.stdout if r.returncode==0 else None
paths,r=g.raises_between(MB,H,ls,show); print('raises_between ->',r)
P='dev/governance/config/policy_budgets.json'; old=show(MB,P); d=json.loads(old); del d['files_tokens']['CLAUDE.md']
print('grader control ->', g.file_raises(P, old, json.dumps(d,indent=2), set(ls(H)).__contains__))
