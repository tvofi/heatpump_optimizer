Fix review: blocked 8978e0437c46a10207dd682057665a214453e083 ci-red: merge_train classify exits 1 (RED: gate); two sibling gate runs concluded failure at this head

bus-nonce: 71e2f9b14f3c13f6e0b573481e573da5

Round 1. Measured head 8978e0437c46a10207dd682057665a214453e083 (ev/HEAD.txt).

## Block
`merge_train.py classify 8978e0437c46a10207dd682057665a214453e083 --pr 3339` exits 1: `RED ... red: gate`. Two of three required gate runs concluded failure: job 128993012544 (run 42563803195) and job 128992978359 (run 42563112808), both at 05:16Z with `FAIL run(s) [42563111803] at this head are still being judged; their gate decides`. The deciding gate (run 42563111803, job 128998720318) and `pr-contract / pr-contract` (128998465151) are success, and every other check is success or skipped. The red looks like a transient ordering failure of the sibling suites (arch-score, budget-raise-gate) gating before the main run finished, not a defect in the diff. I cannot judge it GREEN under the brief; re-running those two gate jobs (an orchestrator action) should flip classify to 0, after which the code review below stands as merge. The PR body names neither gate failure, so rule 11's answer is also owed if they stay red.

## Findings
- Residual: `governance / delivery-status` (job 128987283937) is red with DELIVERY STATUS OVERDUE (4 overdue rows: #3340, #3333, #3316, #3318). It grades main and is not a required context; this diff adds only its own row dev/programme/delivery/3339.md. Carry: dismissed: main's own overdue rows, not this PR's.

## Evidence
- Code review is otherwise clean. Three-dot diff, 8 files; VERSION, RELEASE_NOTES.md untouched (empty diff). `git merge-tree --write-tree origin/main 8978e0437c46a10207dd682057665a214453e083` clean, rc 0 (ev/merge-tree.txt). dev/governance/roles/ changes on main touch only proposal-triage.md, not this contract.
- RESULT ref_privacy self-test at head: 124 checks, 0 failed (matches body). Mutant 1 (email_shape returns []): 7 failed (matches). Mutant 2 (digits optional in _NUMBERED): 5 failed (body says 5). Restored with git checkout.
- RESULT plan_audit self-test 27 checks, 0 failed; delivery_row self-test 6 checks, 0 failed; app_push self-test 227 checks, 0 failed (body: same).
- Census figure re-derived: the body's t@t git grep prints 47 lines at head, as stated.
- Not re-run: the body's mutants 3 and 4 (committer-only noreply, PIN_HINT) and the 513/1 prepr line (macOS host). Not re-derived by me; the self-test arms they cite exist in the diff.
- Body head matches measured head. Red-check answers: instrument-self-tests (two jobs) and pr-contract are named and answered in the body; both are green at this head (job 128987283886 success).
