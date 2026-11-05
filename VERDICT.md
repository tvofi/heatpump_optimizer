Fix review: blocked 2cfa51a43dea225ad55adf1ac3826f58da613655 pr-contract-red: pr-contract / pr-contract failed at this head (run 41981691725, job 127094257612) because the body's ## Red checks does not name red check `tests / mutation-autofix`

bus-nonce: 5e6e995a5fb3bceebfef469ad06f5908

## Block

CI-only re-check of 2cfa51a43dea225ad55adf1ac3826f58da613655 (code not re-reviewed, per brief).

Step 3 fails. The pr-contract job at this head (06:42 UTC) ran policy_lint and exited 1:
`[pr-body] check `tests / mutation-autofix` is red and `## Red checks` does not name it. Name the failure and answer it: the cheaper detector and its standing cost, or the finding that none exists.`
Red history across the 17 commits: governance / delivery-status, tests / mutation, tests / mutation-autofix, tests / nightly-status. The body names the other three but not mutation-autofix. Fix: add a `tests / mutation-autofix` bullet to ## Red checks (the red was the bot run that pinned replay_doc.py:535; cheaper detector = prepr step 6d, or none). Edit the body only; the head does not move.

Step 2 is not settled either: classify reads WAIT (gate still in progress at the time of review; two gate runs in_progress). Step 1 holds: review_carry prints CARRY.

## Findings

- Defect: body `## Red checks` omits `tests / mutation-autofix`; pr-contract red until the body names and answers it. Carry: R10-FLY-REPLAY-MASK | #3219 | O1 | dismissed: fixed by a body edit on this PR, not a separate issue

## Evidence

- ev/HEAD.txt: head reviewed.
- ev/review_carry.txt: CARRY.
- ev/classify.txt: classify output at review time (WAIT; gate pending).
- Inherited reporters failing: tests / nightly-status, governance / delivery-status (as the body says).
- ## Head names one head, 2cfa51a4...; figures: 3 resolved, 1 inline-script figure unverified (the python3 -c one), not a refusal.
