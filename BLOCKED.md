# BLOCKED: r11-pre-machinery-limiter (repair round 2, PR #3627)

Question: #3566 holds a merge verdict that is not on the train and shares the hot file tools/audit/seat/orchestrator_tick.py with this diff, so review_packet refuses the handoff (hot-file). Should the relay board or merge #3566 first and then re-run body_push.sh for this topic, or is there a different route for this PR?

State at the stop:
- Code head 2986495e9cc46e911d37945166c18dd13c60d89a is on refs/heads/handoff/r11-pre-machinery-limiter. It adds one commit over the reviewed 3ad61a1f6e: tests that kill the six survivors the review named. The review's driver (evidence/mut.py on review/3627), re-run at this head, kills 19 of 19 mutants.
- tools/pr/prepr.sh (PREPR_SKIP_CLOSURES=1, MUTANT_CMD set to the two self-tests) at 2986495e: rc=0. Its 6 diff-mutant survivors are the fixture lines 749, 753, 764, 770, 775 and 777, and the body answers them under ## Unpinned sites.
- `git merge-tree --write-tree origin/main HEAD` reports no conflict against origin/main 5825e1346c.
- The full body is the one body_push.sh kept at refs/heads/handoff-wip/r11-pre-machinery-limiter-body (07026ad0ca).

body_push.sh output (tail):
review_packet: REFUSE hot-file: #3566 holds an unboarded merge verdict and shares tools/audit/seat/orchestrator_tick.py
review-packet handoff: R11-PRE-MACHINERY-LIMITER at 2986495e9cc4, 14 live, 14 dispatched carries, 1 refused
body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body
body_push: REFUSED REVIEW-PACKET
