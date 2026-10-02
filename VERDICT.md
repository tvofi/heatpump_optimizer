Fix review: merge 25f434a65c7c4096c2da5f2bb2565d767c9f4dca

bus-nonce: 6b532161f3afbd3069d048856625162f

Round 4, the main-merge delta. PR #1851 (R9-EG-A1), head 25f434a65c7c4096c2da5f2bb2565d767c9f4dca (live head re-read 2026-10-02T20:39:59Z, unchanged). Evidence: evidence/ (HEAD.txt names the head). Every finding on the round-4 head d5830a13 (verdict 3f76a1d4) carries: the round-3 owed list is closed, and its only block was a missing body answer.

## The delta is a main merge with no hand resolution

- RESULT HEAD's parents: d5830a13 (the reviewed head) and 51ce8f2a7 (an ancestor of origin/main).
- RESULT `git merge-tree --write-tree d5830a13 51ce8f2a7` gives 93ccc4a5, which equals HEAD^{tree}. There is no hand resolution.
- RESULT the PR's own diff is unchanged. The patch-id of (merge-base..head) is 3e4b95c3 at both d5830a13 and 25f434a6.
- The merge brings in #1856/#1857. They touch tests/entities.py, tests/closure.py and tests.yml, so I re-ran what they reach:
  - RESULT the #1218 probe (d308_probe.py, mine) at head: both checks ok. With a third full-coverage closure injected, it FAILs, so a third is still refused.
  - RESULT the full `tests/entities.py` at head under the seat venv: ALL 2074 ENTITY CHECKS PASSED, rc=0.
- merge-tree against origin/main exits 0. `tools/audit/briefs/` shows no diff between the merge base and origin/main, so this contract is current.

## CI at this head

RESULT check-runs at 25f434a6: every check is success, skipped or neutral except nightly-status.
- fast (3.14): success (job 111002211505).
- mutation: success.
- closures: success.
- budget-raise-gate: success.
- pr-contract: success (111020543180, 20:39:45Z, on the edited body).

nightly-status is a failure (111002210757): NIGHTLY ABSENT for mutation-ledger and mutation-ledger-push. The diff touches the plan, so the exemption is void, and `## Red checks` now names this red and answers it. The cause is main's: the last scheduled nightly predates #1848, which added the jobs. There is no cheaper detector. The orchestrator owns the proof, dispatch 37050037132 (tests.yml, main at aa7a8119, workflow_dispatch, still in progress at review time). Step 11 checks that the trigger is answered, not the answer, and pr-contract accepts it.

Not re-taken at this head: tests/arch_score.py. Its inputs are unchanged by this merge, and CI's FULL fast (3.14) is green here. The round-3 run passed 139 checks.
