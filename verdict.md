Fix review: merge 17b2f1561770b4e1f928e5c253d9ae668d5acdd5

bus-nonce: 18a76097c21bc652248415c46837a3a9

## Evidence

CI re-check at the same head; the review itself stands from the prior verdict (probe/rev-3216-4604d562), whose ev/ found the RCA and harness sound and blocked for CI only.

- RESULT head unchanged: refs/pull/3216/head is still 17b2f1561770b4e1f928e5c253d9ae668d5acdd5 (ev/pull-head.txt), the SHA the prior review measured. Same SHA, so the code diff against the reviewed head is empty.
- RESULT classify: `GREEN 17b2f1561770b4e1f928e5c253d9ae668d5acdd5 pending: none red: none`, rc 0 (ev/classify.out).
- RESULT check runs, all pages (ev/check-runs.txt, 68 distinct rows): gate success (3 runs, last 02:06:02Z), prelude success, pr-contract success, budget-raise-gate success. The earlier cancelled gates are superseded by these concluded successes.
- The one other concluded red is `tests / nightly-status` (failure, 01:21:08Z). As the prior verdict found, this diff touches no workflow, nightly record or production file, so it is not this PR's (fix-review.md step 11). I did not re-trace its origin on main's ancestry beyond that.

## Findings

- Follow-up: the census's pass at the fix's head (`handoff/r10-hotfix-sav-estimate`) and its wiring as a `tests/` script are owed after this merge. Until then the class stays `detector`, and the only demonstrated pass is the planted one, which holds by construction. Carry: #2492
- Residual: the record's parenthetical "3.6 to 3.8 times v7.1.1's mean in a scratch probe of these shapes" did not re-derive. My own probe on the census's valve cells (`ev/probe-*.out`) gives v7.0.4 / v7.1.1 horizon means of 5.802/1.118 = 5.2 and 5.805/0.885 = 6.6, so the factor is larger than claimed. The direction the record draws from it (v7.0.4's valved ratio is low because the mean is inflated) holds, and the record labels the probe as uncommitted scratch. Carry: dismissed: a scratch-labelled parenthetical whose direction holds; no conclusion of the record rests on its magnitude
