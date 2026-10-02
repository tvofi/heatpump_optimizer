Fix review: merge b74fc1aa21e443fef353a5bb49ea630397bf2913

bus-nonce: 6f2b5ff9c6832c791093bd754942405b

Round 4, a body-only delta. PR #1851 (R9-EG-A1), head b74fc1aa21e443fef353a5bb49ea630397bf2913 (live head re-read 2026-10-02T23:24:49Z, unchanged since verdict dd8ce6fa). Every RESULT in dd8ce6fa about the hand resolution carries, because the code head did not move:
- deployment_shape.py resolves correctly.
- arch_score_head.py's closure has 107 files, covers 87/87 and CI `closures` is green.
- the D6 claims equal main.
- arch_score.py is out of the merge's reach.
- the PR's own diff is otherwise unchanged.
- entities.py passes all 2081 checks.
The copied evidence is under evidence/.

## The one block, nightly-status unanswered, is answered

- `## Red checks` now names nightly-status as NIGHTLY FAILED: dispatch 37050037132 on main (aa7a8119) failed in mutation-nightly and mutation-ledger-push. It says the check is not exempt because the diff touches the plan, that there is no cheaper detector on the branch, and that the owner is the orchestrator's seat on main.
- I checked the claim (dispatch-37050037132-excerpt.txt):
  - RESULT mutation-nightly (110980930989): "tests/harness_headers.py: tools/audit/round4/D7/sysid_estimator_frontier.py exits 0 [rc=-24 ...]". Signal 24 is SIGXCPU, which fits the orchestrator's CPU-limit diagnosis.
  - RESULT mutation-ledger-push (111044417786): "MUTATION LEDGER: skip-head-moved -- a measured slice did not reach main".
  - RESULT neither the PR head b74fc1aa nor its authored commit 1c43a6c9d is an ancestor of aa7a8119, so the failing run cannot contain this PR's code. "Neither job runs this PR's code" holds.
  - Step 11 checks that the trigger is answered, not the answer. The answer is the root-cause seat's to judge.
- RESULT pr-contract 111065737538 (23:06:18Z, the edited body): success. The earlier 111063804675 failure is superseded.
- RESULT the other check-runs at b74fc1aa are all success, skipped or neutral: fast (3.14), mutation, closures, closure-scope and budget-raise-gate. nightly-status (111049854457) is the answered red. It is not a required context.

## Not blocking

`## Head` now carries two sentences that disagree. The first is right: it merges origin/main 03ba7f70f into the previous head. The second garbles the same merge ("merges origin/main into the authored code head 25f434a6 and then merges origin/main 03ba7f70f"). The SHA it names is the measured head, and pr-contract accepts the body. One of the two sentences should go at the next edit.
