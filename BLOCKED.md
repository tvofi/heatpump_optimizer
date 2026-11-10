Question: carry for item 17762ad2 must land on the round's roster branch before the body can be pushed.

Receipt: prepr.sh rc=0 at head 6671786843048c52ea7c11373c1e074e4aa8f187 (no code change; body edited: Head section, carry marker routed to R10-TRAIN-RESIDUE because R10-CLOSEOUT-INSTRUMENTS is resume.stage done at handoff/audit-r10-roster f16bbac22). Refused body kept at handoff-wip/r10-process-slim-p2-body cc2e011e4d7364914f25adfb6cb9d93ae816afa9.

```
CARRY-MISSING R10-TRAIN-RESIDUE body item 17762ad2: not in its brief or carries: "- Delete Nightly's `record-autofix` beat once no stamp rule reads it. That deletion covers: - its `p"
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-process-slim-p2-body cc2e011e4d7364914f25adfb6cb9d93ae816afa9
```
