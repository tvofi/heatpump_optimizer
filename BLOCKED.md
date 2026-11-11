body_push.sh exited 4 at handoff 09a166660de9528e4bec9ee030320ad161e4bfae (pushed to handoff/r10-mutant-run-forkcap; prepr.sh rc 0, MODE: SCOPED; body check 0 errors). Its output:

review-packet handoff: R10-MUTANT-RUN-FORKCAP at 09a166660de9, 1 carries, 0 refused
CARRY-MISSING R10-MUTANT-RUN-FORKCAP body item 803fdcf8: not in its brief or carries: "- Residual: MUTVAC-STMT-DEL's acceptance (the 23 reviewer-named Python sites reach >= 14 STMT_DEL-vi"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-mutant-run-forkcap-body 431f2ab7d066460bae69ef0dabaebe9d7189529a

Question: the relay folds the MUTVAC-STMT-DEL acceptance carry (heads.tsv for the 23 sites is not reachable from this seat; #3394 has no owner) into R10-MUTANT-RUN-FORKCAP's carries and re-runs body_push.sh with the kept body.
