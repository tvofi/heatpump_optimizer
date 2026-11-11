# BLOCKED: body_push.sh exited 4 (REFUSED CARRY-LANDED)

Code head handed off: handoff/r10-rca-restore-base-skew = 30b143922cdc5ed869fe32150ecb20cc8202727b (prepr.sh rc=0). Refused body kept at handoff-wip/r10-rca-restore-base-skew-body 02c2fcfb8709d93b4f1a01abd6e8e1c641135d66.

Question: the relay folds the two R10-HOTFIX-RESTORE-BASE-SKEW carries below into the round roster and re-runs body_push.sh; this seat may not write the roster.

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-RCA-RESTORE-BASE-SKEW at 30b143922cdc, 0 carries, 0 refused
CARRY-MISSING R10-HOTFIX-RESTORE-BASE-SKEW body item e41acc16: not in its brief or carries: "- Open seam `tests.yml:1180` (`mutation-pins`). The payload base's `tests/mutation_table.py` is writ"
CARRY-MISSING R10-HOTFIX-RESTORE-BASE-SKEW body item 530feedf: not in its brief or carries: '- Census arm cost. `_rbs_defects` as written spends a median 1.98 s per `tests/entities.py` run, mos'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
fatal: expected 'acknowledgments', received 'packfile'
warning: push negotiation failed; proceeding anyway with push
body_push: refused body kept at handoff-wip/r10-rca-restore-base-skew-body 02c2fcfb8709d93b4f1a01abd6e8e1c641135d66
```
