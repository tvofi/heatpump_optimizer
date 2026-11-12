Question: body_push.sh refused with CARRY-LANDED. The three future-work carries now go to R10-ROUND-PLAYBOOK-FINAL per the orchestrator ruling, but they are not yet in that group's brief or carries on the roster branch; the relay should land them (carry_audit.py land-ops) and re-run body_push.sh. Item ce279d5a is dismissed (built in this pull request) and the friction lines are unchanged. Repaired body kept at handoff-wip/r10-ci-priority-pause-body b80d34b6cbfa422f647a27ade229dd0cf3ef44cc.

body_push output, verbatim:
```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-CI-PRIORITY-PAUSE at ec3c6b8b29f1, 9 live, 9 dispatched carries, 0 refused
CARRY-MISSING R10-ROUND-PLAYBOOK-FINAL body item 6614d45d: not in its brief or carries: '- Backfill of `source`/`hotfix`/`savings_source` on the live roster groups (carry 3 item 4: R10-UX-H'
CARRY-MISSING R10-ROUND-PLAYBOOK-FINAL body item ebd4600d: not in its brief or carries: '- Enabling `priority_cancel` needs the after measure above. (into the round-11 opening list held by '
CARRY-MISSING R10-ROUND-PLAYBOOK-FINAL body item 1655cf71: not in its brief or carries: '- `roster_lib.is_hotfix` still treats `kind == "bug"` as a hotfix beside `hotfix: true` and the name'
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-ci-priority-pause-body b80d34b6cbfa422f647a27ade229dd0cf3ef44cc
```
