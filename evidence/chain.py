import sys,json,copy; sys.path.insert(0,'dev/audit/harnesses/r10_hotfix_ci_critpath_3')
import replay as R
from tests import ci_ratchet as cr
runs=sorted(json.loads((R.HERE/'runs.json').read_text())['workflow_runs'],key=lambda r:r['created_at'],reverse=True)
W=16; new=cr.window_work_minutes; base=new(runs[:W])
cq=sorted(int(R.work_s(r,'codeql / Analyze (python)') or 0) for r in runs[:W]); print('codeql/python success work newest16:',cq)
from collections import Counter
print('chains over 40:',Counter(tuple(cr.run_chain(r) or ()) [2:3] for r in runs))
r0=R.with_work(runs[0],'tests / fast (3.14)',lambda x:1100)
print('newest run fast drawn quick (1100 s, success): chain',cr.run_chain(r0),'grade delta',round(new([r0]+runs[1:W])-base,3),'retired delta',round(R.retired([r0]+runs[1:W])-R.retired(runs[:W]),3))
