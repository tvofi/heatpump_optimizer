Question: body_push.sh refuses the handoff of r10-process-slim-p2 at 9da744f716f5b3a2999e961f6ec61f3bc7dfc398 with REVIEW-PACKET hot-file. PR #3384 holds an unboarded merge verdict and shares dev/audit/harnesses/r10_seat_selftests_mutants.py, which this branch also changes (27 insertions, 12 deletions three-dot from d08ed310). Board or land #3384 first, or rule the order, then re-run body_push.sh.

State:
- Code head 9da744f716f5b3a2999e961f6ec61f3bc7dfc398 is pushed to refs/heads/handoff/r10-process-slim-p2 (fast-forward from 66717868). It merges origin/main d08ed310: nine conflicts unioned, generated rules regenerated. A second commit pays a 2-token fix-review.md cap overrun inside the file, with no budget change.
- prepr.sh at that head: PRE-PR 9da744f716f5... rc=0. It needs a local handoff/audit-r10-roster branch; without one, ci_predict's carry_audit reads 1 bad destination, the false red that Friction r10-process-slim-4 records.
- origin/main 444cf62f (2026-11-11T03:08:11Z): git merge-tree --write-tree origin/main HEAD exits 0.
- The updated body is kept at handoff-wip/r10-process-slim-p2-body 67bca9c075bc56d39fee64abbf8f09036609842a. It is ready for body_push.sh as-is once the hot-file clears.

body_push output:
```
ref_privacy (body) ok: no host identity in the body
review_packet: REFUSE hot-file: #3384 holds an unboarded merge verdict and shares dev/audit/harnesses/r10_seat_selftests_mutants.py
review-packet handoff: R10-PROCESS-SLIM at 9da744f716f5, 2 carries, 1 refused
body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body
body_push: REFUSED REVIEW-PACKET
body_push: refused body kept at handoff-wip/r10-process-slim-p2-body 67bca9c075bc56d39fee64abbf8f09036609842a
```
