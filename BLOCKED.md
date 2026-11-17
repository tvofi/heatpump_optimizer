# BLOCKED: body_push.sh exit 4 (REFUSED CARRY-LANDED)

Topic r11-outside-honest-starts-runs-p2. Code head dbc806ce5f14fdee9c18587da32d5a1045c3b234 is on refs/heads/handoff/r11-outside-honest-starts-runs-p2; tools/pr/prepr.sh is clean at that head (PRE-PR rc=0, PREPR_SKIP_CLOSURES=1) and the body check is clean. The refused body is kept at refs/heads/handoff-wip/r11-outside-honest-starts-runs-p2-body (34ecbe5552). The carries land on the round's roster, which this seat may not write; per the brief the relay folds them and re-runs body_push.sh.

body_push.sh output:

```
fill-red: the diff adds no unpinned mutation site; nothing written
figure_block: refreshed 1 block(s) at dbc806ce5f14
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-OUTSIDE-HONEST-STARTS-RUNS-P2 at dbc806ce5f14, 3 live, 3 dispatched carries, 0 refused
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P3 body item 1d1c10a9: not in its brief or carries: '- Carry 2 (the `median_off_s` headroom cut after a duty change is not built): not this seam (the can'
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P3 body item 2e78177c: not in its brief or carries: '- Carry 1 of the brief (three live checks on a test fork: update-branch identity, `app_approve` end '
CARRY-MISSING R11-OUTSIDE-HONEST-STARTS-RUNS-P3 body item ad4f75a0: not in its brief or carries: '- Carry 2 of the brief (the `median_off_s` headroom cut after a duty change is not built) is outside'
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-outside-honest-starts-runs-p2-body 34ecbe5552f0534e9d2d15a6b5367b4f26f78bd1
```
