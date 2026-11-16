# R11-OUTSIDE-SELF-SETTING-PUMP: body_push.sh refused CARRY-LANDED (exit 4)

Code head pushed: refs/heads/handoff/r11-outside-self-setting-pump at 1787779ba56897cbafacb7194a6bf3b5f073cfa3; prepr.sh rc 0 at that head with the body below. The body is kept at handoff-wip/r11-outside-self-setting-pump-body 85114c13446ec64e61dce760b337794d9264e540. The relay folds the carry and re-runs body_push.sh.

~~~text
review-packet handoff: R11-OUTSIDE-SELF-SETTING-PUMP at 1787779ba568, 5 live, 5 dispatched carries, 0 refused
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item 0116e1a6: not in its brief or carries: "- Verdict item e98d0ab9: the defrost derate's inferred estimator (`coordinator._settle_defrost` with"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-outside-self-setting-pump-body 85114c13446ec64e61dce760b337794d9264e540
~~~
