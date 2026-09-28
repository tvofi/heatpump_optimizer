import csv
R='5a2a62ff:docs/audit-2026-09.md'
X=[]
def x(rnd,fid,iss,status,reason,src,in_rows='no'):
    X.append([rnd,fid,iss,status,reason,src,in_rows])
# R1
x('R1','D1-02','','refuted','REFUTED, judge ruling on reachability (setup/unload serialised; stub divergence); hygiene residue shipped in #144',R+':60,243-253')
x('R1','D3-01','','refuted','REFUTED 2-0: CI env_drift --all catches the mutant (finder ran default 5-fixture mode)',R+':201,239-242','YES - rows_v2 line 28 carries it as a survivor (I1); should be removed')
x('R1','D1-03','','duplicate of R1 D9-02 (M1)','merged into M1 := D1-03 + D9-02; counted once, rows_v2 keeps D9-02',R+':61,219-221')
x('R1','D8-02','','duplicate of R1 D1-04 (M2)','merged into M2 := D1-04 + D8-02; counted once under D1-04',R+':152,222-224','YES - rows_v2 lines 3 and 43 carry both D1-04 and D8-02 (P6); one is a double count')
x('R1','D7-06 (CONF-keys half)','#178','refuted (partial)','4 dead CONF keys refuted by judge runtime sentinel; the 5-dead-symbols half survives and is in missing_rows as D7-06',R+':251-256')
x('R1','round-1 deferred hacs.json floor','#227','not a finding','carry-over task from tracker #200 (floor bump precondition), no finder/panel; closed by #235 as already correct','gh:#227')
# R2
x('R2','D10-16','#216','duplicate of R2 D10-03','zcode session\'s parallel round-2 D10 run (baseline b39fc6f, branch claude/audit-r2-d10): same Tibber per-poll ERROR phenomenon; PR #312 fixes "D10-16 + D10-03" together; judge verified','gh:#216')
x('R2','D10-17','#217','duplicate of R2 D10-09','same zcode run; #299 (R2 D10-09) closed with comment "Duplicate of #217 (same rule, same sites)"; counted once under D10-09 (in rows_v2)','gh:#217, gh:#299 comment 5517438711')
x('R2','D10-18','#218','duplicate of R2 D10-12 (blueprint arm)','same zcode run; no automation example/blueprint = the blueprints arm of D10-12 (#302, added in missing_rows); fixed separately by #313','gh:#218')
x('R2','D9-02 remainder','#346','residual of R2 D9-02','the single-scenario 2x arm split out of #287 after its fix; same finding, rows_v2 keeps D9-02','gh:#346')
x('R2','[gate] golden fixtures never bit-compared','#347','not a round finding (fix-wave discovery)','found by the #341 fixer, no panel/judge verdict; round-2 label only. Could be counted as a fixer-found instance of I1 under the register counting rule (low confidence)','gh:#347')
x('R2','basin coverage floor red','#387','not a finding','defect introduced by #346\'s fix; incident, not an audit finding','gh:#387')
x('R2','[wave5] #195 tranches','#505','not a finding','wave-5 programme follow-up carrying the round-2 label','gh:#505')
x('R2','D10-15 (ENERGY half)','#305','refuted (partial)','ENERGY half refuted by panel; entry_type/manufacturer half survives (already in rows_v2)',R+':948')
x('R2','D4-11 (duplicate-copy guard half)','#265','refuted (partial)','guard half refuted per #265 title; version half survives (in missing_rows)','gh:#265')
x('R2','D0/D1/D4 panel verdicts','','not recorded','register L896: panels D0, D1, D4 still to run; no later refutation found in tree or issues; all 20 rows filed (#232-#240, #256-#266) and treated as survivors','%s:896'%R)
# R3
x('R3','D9-01','','refuted','verdicts.tsv:11 refuted (multi-start redundancy within its own permutation null); filed.tsv:44 REFUTED-no-issue','5a2a62ff:tools/audit/round3/ledger/verdicts.tsv:11')
x('R3','D0-01/02','#826','one defect, filed once','judge: "ONE DEFECT WITH D0-02"; one issue #826. rows_v2 carries D0-01 and D0-02 as two rows (lines 139-140); D0-01 verdict "not actionable" -- possible double count','5a2a62ff:tools/audit/round3/ledger/verdicts.tsv:38-39','YES - both in rows_v2 (flag only)')
# R4
x('R4','D4-02','','refuted','3-of-3 + judge: premise (HA stock dark theme #212121) false at every supported version','5a2a62ff:tools/audit/round4/judge-verdicts.md:340')
x('R4','D1-INST..D12-01 first filing','#909-#919','duplicate filings','11 issues filed without the [R4-] prefix, re-filed as #920-#961; counted once under the R4- issues','gh:#909-#919')
x('R4','valve_storage_small_tank drift','#996','not a finding','BLAS-conditional golden drift incident (round-4 label)','gh:#996')
x('R4','tracking','#962','not a finding','round-4 tracking issue','gh:#962')
# R5
x('R5','D0-01 (run 1cc89e0)','#1293','refuted after filing','owner/fixer comment 2026-09-22: ftol tightening is net-negative (+6.4 % money on the shoulder cell), "closed as refuted"','gh:#1293 comment 5771279915','YES - rows_v2 line 178 (P4); reconsider')
x('R5','D0-02, D1-01..D1-04, D9-01..D9-04 (run 1cc89e0)','','unknown','numbering gaps in the 48 filed #1293-#1340; no round-5 register or JUDGE file exists in any commit (register L1440: "There is no Round 5 section"); cannot tell refuted from renumbered','%s:1440'%R)
x('R5','run eaa2a06 refuted/unfiled','','unknown','only the 35 filed (#1207-#1241) are visible; the run\'s verdict record is not in the tree','gh:#1207-#1241')
# R6
x('R6','R6-CLASS x7','#1408-#1414','not findings','class-fix work items derived from findings, not findings','gh:#1408-#1414')
x('R6','R6-user','#1416','not a finding','owner feature request','gh:#1416')
# R7: none refuted
x('R7','(none)','','-','round 7: 30 findings, 0 refuted, 0 unreproduced (register L1737); nothing excluded',R+':1737')
with open('/tmp/claude-0/-home-user-heatpump-optimizer/1b5fa08f-9bd8-59e8-b197-ffb291fc579e/scratchpad/phaseA/a1b/excluded.tsv','w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n')
    w.writerow(['round','finding_id','issue','status','reason','source','in_rows_v2'])
    w.writerows(X)
print(len(X))
