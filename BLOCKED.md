Question: the body's Forward-carry lines (3) are not in the group's brief or carries; carry_audit.py land-ops must land them on the roster branch, which this seat may not write. Relay: fold the carries and re-run body_push.sh with the body at handoff-wip/r10-train-residue-body. Code head d36a52f9 is pushed to handoff/r10-train-residue.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-TRAIN-RESIDUE at d36a52f94097, 15 carries, 0 refused
CARRY-MISSING R10-TRAIN-RESIDUE body item e3fd6216: not in its brief or carries: "Carry 1 (undraft after a train-recarry draft) and Carry 6 (BOT_HEAD count) need the orchestrator's l"
CARRY-MISSING R10-TRAIN-RESIDUE body item e3fd6216: not in its brief or carries: "Carry 1 (undraft after a train-recarry draft) and Carry 6 (BOT_HEAD count) need the orchestrator's l"
CARRY-MISSING R10-TRAIN-RESIDUE body item e3fd6216: not in its brief or carries: "Carry 1 (undraft after a train-recarry draft) and Carry 6 (BOT_HEAD count) need the orchestrator's l"
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-train-residue-body df043d39c39279770d68bd2a492db8f763c1b55c
```
