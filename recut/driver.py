import json,subprocess,sys,re,os
GC='/Users/timmalmstrom/hpo-seats/r10s4/gc-main'; W='/Users/timmalmstrom/hpo-seats/r10s4/roster-edit-wt'
D='/Users/timmalmstrom/hpo-seats/r10s4/roster/recut'
env=dict(os.environ)
def sh(*a,**k): return subprocess.run(a,capture_output=True,text=True,cwd=GC,**k)
ops=[]
for n in ['R10-ORCH-DISPATCH-REG','R10-ORCH-BEATD','R10-ORCH-PLANPAGE','R10-ORCH-ROSTER-SCHEMA','R10-FLY-WORKTREE-GC','R10-FLY-DAEMONIZE-ARGV','R10-FLY-CIPREDICT-LAYOUT','R10-FLY-CLOUD-SETUP-TOOLCHAIN','R10-FLY-YIELD-GUARD','R10-FLY-ENVMATRIX-NOREMOTE']:
    ops.append((f'append-group {n}',['append-group','x',f'{D}/groups/{n}.json']))
for g,f in [('R10-FLY-CARRY-DISPOSITION','cd-1'),('R10-FLY-CARRY-DISPOSITION','cd-38'),('R10-UPDATE-PR-SIGNALS','ups-9'),('R10-FLY-CAP-LINE','cap-27')]:
    ops.append((f'append-carry {g} {f}',['append-carry',g,f'@{D}/carries/{f}.txt']))
for i,s in enumerate(json.load(open(f'{D}/drops.json'))):
    ops.append((f'drop-carry MACHINERY #{i}',['drop-carry','R10-ORCH-MACHINERY',f'--match={s}']))
ops.append(('machinery note',['set-resume','R10-ORCH-MACHINERY','--field','note','--value','Closed, superseded by the re-cut (orchestrator decision under mandate 6329234399, 2026-10-23; designer note on design/R10-ORCH-MACHINERY at 2fc665c61, sections 3 and 4): the concerns now sit in R10-ORCH-LEDGER, R10-ORCH-DISPATCH-REG, R10-ORCH-BEATD, R10-ORCH-PLANPAGE and R10-ORCH-ROSTER-SCHEMA, with single-file defects in R10-FLY groups. This group keeps only the no-build records and residuals as carries.']))
ops.append(('machinery stage',['set-stage','R10-ORCH-MACHINERY','absorbed']))
ops.append(('toolkit-model after',['set-after','R10-FLOW-TOOLKIT-MODEL','R10-ORCH-PLANPAGE,R10-FLOW-TOOLKIT-MEASURE']))
ops.append(('playbook after',['set-after','R10-ROUND-PLAYBOOK','R10-FLOW-ARCH-PLANNER,R10-FLOW-AUDIT-PLAN,R10-ORCH-LEDGER,R10-ORCH-DISPATCH-REG,R10-ORCH-BEATD,R10-ORCH-PLANPAGE,R10-HANDOVER-REFRESH,R10-FLOW-AUTOTRAIN,R10-FLOW-MAIN-GATE,R10-FLOW-DISPATCH,R10-CI-LAYOUT-P2']))
for g,f in [('R10-FLOW-DESIGN-STAGES','t-designstages'),('R10-FLY-PRUNE-REFS','t-prune'),('R10-FLY-RELAY-REVIEW-FF','t-reviewff'),('R10-ORCH-BEATD','t-beatd')]:
    ops.append((f'append-carry {g} {f}',['append-carry',g,f'@{D}/carries/{f}.txt']))
ops.append(('rca-body-lint done',['set-stage','R10-RCA-BODY-LINT','done','--at-sha','cf01e82eec281c0d4e4141beb8fd5a8834cf99de']))
start=int(sys.argv[1]) if len(sys.argv)>1 else 0
log=open(f'{D}/driver.log','a')
for k,(label,args) in enumerate(ops):
    if k<start: continue
    sh('git','fetch','-q','origin','main','handoff/audit-r10-roster'); sh('git','checkout','-q','--detach','origin/main')
    subprocess.run(['git','-C',W,'checkout','-q','--detach','origin/handoff/audit-r10-roster'])
    r=sh('python3','tools/audit/seat/roster_edit.py','--worktree',W,'--lint-cwd',GC,'--push',*args)
    out=r.stdout+r.stderr
    m=re.search(r'pushed handoff/audit-r10-roster at (\w{40})',out)
    ok=bool(m) and 'TOTAL: 0 error(s)' in out
    log.write(f'{k} {label} rc={r.returncode} {"OK "+m.group(1) if ok else "FAIL "+out[-600:]}\n'); log.flush()
    if not ok: sys.exit(1)
log.write('ALL DONE\n')
