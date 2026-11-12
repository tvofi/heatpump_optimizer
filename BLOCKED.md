# BLOCKED: body_push.sh exit 4, REFUSED CARRY-LANDED

Topic r10-outside-contributor-cycle-p2, repair of the blocked handoff 40abc1bd (verdict nonce 00b0ea32).

The code head `0d2dfd8b850441a1db42f4c88042dc5b27e88917` is on `handoff/r10-outside-contributor-cycle-p2`. `tools/pr/prepr.sh` printed `PRE-PR: 0d2dfd8b850441a1db42f4c88042dc5b27e88917 00000000000000000000000000000000 rc=0` on it with this body.

body_push.sh kept the refused body at `handoff-wip/r10-outside-contributor-cycle-p2-body` `176ba146b52ea92a2d3cd548a993bd9a2f30b181`. Its four carries name live groups on the round's roster, which this seat may not write. The relay folds them and re-runs `bash tools/audit/seat/body_push.sh r10-outside-contributor-cycle-p2 <body.md>`:
- Carry 2 to R10-CI-PRIORITY-PAUSE
- Carry 3 to R10-PROCESS-SLIM
- Carry 4 to R10-GATE-DEFER-BARRIER
- Carry 5 to R10-SEAT-SCRIPT-OUTPUT

This seat could not delete the stale step ref of the earlier round: the deletion was refused as destructive. The ref was therefore fast-forwarded, by a commit whose parents are the old ref and this head and whose tree is this head's.

`body_push.sh`'s output, verbatim to its last line (lines naming a path on this host left out: 0):

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-OUTSIDE-CONTRIBUTOR-CYCLE at 0d2dfd8b8504, 7 live, 7 dispatched carries, 0 refused
CARRY-MISSING R10-CI-PRIORITY-PAUSE body item dfa8b375: not in its brief or carries: '- Carry 2: **The live checks the design owes are not run.** This seat has no `gh`, no App key and no'
CARRY-MISSING R10-PROCESS-SLIM body item 6c28b5ad: not in its brief or carries: "- Carry 3: **The three instruments' guides and decision 0017 owe this part's surface:** remerge_main"
CARRY-MISSING R10-GATE-DEFER-BARRIER body item 283207ca: not in its brief or carries: '- Carry 4: **Carry 14, round 3:** `_post_agent_approval`\'s body under a bare `--mandate` id reads "u'
CARRY-MISSING R10-SEAT-SCRIPT-OUTPUT body item 48daf0c6: not in its brief or carries: "- prepr-ci-predict: unenforced: Carry 5: `tools/pr/ci_predict.py` runs the base's `carry_audit.py` i"
CARRY-LANDED: 4 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
fatal: expected 'acknowledgments', received 'packfile'
warning: push negotiation failed; proceeding anyway with push
remote: 
remote: Create a pull request for 'handoff-wip/r10-outside-contributor-cycle-p2-body' on GitHub by visiting:        
remote:      https://github.com/tvofi/heatpump_optimizer/pull/new/handoff-wip/r10-outside-contributor-cycle-p2-body        
remote: 
body_push: refused body kept at handoff-wip/r10-outside-contributor-cycle-p2-body 176ba146b52ea92a2d3cd548a993bd9a2f30b181
```
