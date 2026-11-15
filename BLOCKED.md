# BLOCKED: body_push CARRY-LANDED (exit 4)

p1 (grader alone) is at refs/heads/handoff/r11-pre-finder-contract 9259c5e81b, prepr.sh clean (PRE-PR rc=0). Its body is kept at refs/heads/handoff-wip/r11-pre-finder-contract-body. p2 is this branch below this commit (cb6600d2f1); its draft body is p2-BODY.md here.

Question: none; the relay folds the carry and re-runs body_push.sh. body_push.sh output:

```
review-packet handoff: R11-PRE-FINDER-CONTRACT at 9259c5e81bdd, 3 live, 3 dispatched carries, 0 refused
CARRY-STATUS R11-PRE-FINDER-CONTRACT body item 54b6f537: a status line on its own carry, lands nothing: '- Carry 0 (D5 and D6 cover their full scope every round; the D5 and D6 finders start only after R10-'
CARRY-STATUS R11-PRE-FINDER-CONTRACT body item 04f717a6: a status line on its own carry, lands nothing: "- Carry 1 (the playbook's Round start step 3 names the paths that land instead of the group citation"
CARRY-STATUS R11-PRE-FINDER-CONTRACT body item a59e87fa: a status line on its own carry, lands nothing: "- Carry 2 (the denominator block made unconditional in p2's own copy of this grader, the dual mutant"
CARRY-MISSING R11-PRE-FINDER-CONTRACT body item afef0cef: not in its brief or carries: "- p2, the group's artifact, waits at `refs/heads/handoff-wip/r11-pre-finder-contract` (cb6600d2f1) f"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-finder-contract-body 1319d7804fd92345fa40901cb6128d846ec59ba9
```
