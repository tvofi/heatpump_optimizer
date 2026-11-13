Question: body_push exited 4 (REFUSED CARRY-LANDED); the relay should fold the carry onto the roster and re-run body_push.sh. Code is at refs/heads/handoff/r10-hotfix-selftest-scope-rerecord (4a013ff156a4); body kept at handoff-wip/r10-hotfix-selftest-scope-rerecord-body.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-HOTFIX-SELFTEST-SCOPE-RERECORD at 4a013ff156a4, 1 live, 1 dispatched carries, 0 refused
CARRY-MISSING R10-NUDGE-RETIRE body item 81649f64: not in its brief or carries: 'Carry 0: beatd and review-packet entries in tools/ci/selftest_closures.json are unions of two differ'
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-hotfix-selftest-scope-rerecord-body 4c4865f38d3b4d3f9d0dcdfd402cb148e30b0175
```
