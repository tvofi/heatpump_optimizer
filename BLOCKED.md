# BLOCKED: r10-process-slim-p2 body push refused (review packet, hot-file)

The code head 25bc7471a0386ad028b02db9feb0b6c89f80210d merges origin/main 7bdc8aa2 into e24d9e40. There is one hand-resolved hunk, the carry-missing sentence in `dev/governance/roles/fix-review.md` step 10, and BODY.md `## Head` lists it. The head is pushed, fast-forward, to `handoff/r10-process-slim-p2`. `tools/pr/prepr.sh` passes at it (`PRE-PR: 25bc7471... rc=0`, receipt written). `git merge-tree --write-tree origin/main HEAD` exits 0 at the main fetched after prepr.

`bash tools/audit/seat/body_push.sh r10-process-slim-p2 BODY.md` exited 1. Its lines, verbatim:
```
review_packet: REFUSE hot-file: #3245 holds an unboarded merge verdict and shares dev/audit/harnesses/r10_seat_selftests_mutants.py
review-packet handoff: R10-PROCESS-SLIM at 25bc7471a038, 2 carries, 1 refused
body_push: the review packet refuses this head at the handoff (above); answer each, push the code, then the body
body_push: REFUSED REVIEW-PACKET
body_push: refused body kept at handoff-wip/r10-process-slim-p2-body 8108b6c3438447d67b11345b2e66123979e570f6
```

Cause: #3245 is the PR this head supersedes, and it carries the same patch. Its merge verdict is still unboarded, so the packet treats every file the two share as hot. The brief forbids touching #3245, so this seat cannot answer the refusal. The orchestrator must board or close #3245's verdict, then re-run `body_push.sh`. BODY.md on this ref is the body that prepr passed.

The step ref is not deleted, because the body push did not succeed.
