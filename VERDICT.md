Fix review: merge 4a07b1eca5cfd6c507ad7bdcd29e38af6e46f3de

bus-nonce: 92fef8dda7b41ea375ac5fc1a2b15f25
pending-ci: gate

Round 1 (first review of #3923; scope full). Head reviewed: 4a07b1eca5cfd6c507ad7bdcd29e38af6e46f3de, the body's stated head (step 7).

Note: figure-unverified: the body's per-job timings for runs 45907700288 and 45891233921 (refresh 75 s / 49 s, cancel-superseded 13 s / 12 s) were not re-derived; the census-arm figure is quoted by the body as not re-run. Neither is load-bearing for the change.
Note: design-trace: the design's L5 test ("a run that shows both steps' lines") is met by this head's own CI run 45912714635 (ev/ci-run-45912714635-cancel-superseded.txt), which the body does not cite.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 4a07b1ec` exits 0 (tree 5ff61e43b2); merges cleanly. Role files unchanged between merge base and origin/main.
- RESULT head suite: `PYTHONPATH=tests/hastub python3 tests/entities.py` in a detached worktree at the head: ALL 2788 ENTITY CHECKS PASSED, rc=0 (ev/entities-head.log).
- RESULT mutation proof (step 1), six ci.yml mutants of my own at the head, each killed by a top-level check (ev/mutants-summary.txt, ev/entities-M*.log; indented FAIL lines are the suite's planted negatives and timing self-tests, present at the head too):
  - M2 refresh step `if:` deleted: FAIL `#3885 L5: the same job re-runs the stale green gates ...`
  - M3 cancel step `if:` deleted: FAIL `ci.yml's cancel-superseded cancels a superseded older SHA ... on a non-bot same-repo pull_request run only`
  - M4 restore guard dropped from the refresh `if:` (`!cancelled()` only): FAIL the #3885 L5 row and the CI umbrella row
  - M5 restore no longer restores `tools/ci/*.py`: FAIL the #3885 L5 row, D11-s1-03 (`ci.yml:cancel-superseded runs tools/ci/gate.py unrestored`) and the codeql D-5 null control
  - M6 job `if:` no longer admits `pull_request_review`: FAIL the #3885 L5 row
  - M7 refresh made dependent on the cancel step (`success()` for `!cancelled()`): FAIL the #3885 L5 row
  No survivor. The fixer's M1-M3 are a subset of the same shape; M2 and M3 reproduce their quoted failing rows.
- RESULT figure (step 8): job list at base 7194ff84 includes `refresh` and `cancel-superseded`; at the head only `cancel-superseded` (ev/jobs-figure.txt, the body's own rule). Housekeeping jobs per pull_request event 2 -> 1: re-derived.
- RESULT live trace: CI run 45912714635 at this head ran job cancel-superseded (13 s) with steps restore (success, 0 s: base already in the depth-2 clone), cancel (`cancel_superseded: 0 superseded run(s) ...`) and refresh (`NOTICE no green gate to refresh`); no `refresh` job in the run.
- RESULT name dependence: no program under `tools/` or `.github/` keys on a job named `refresh` (only recorded fixtures and merge_train.py's self-test listing, which are historical data); `gate.py --refresh` skips its own run by run id, not job name, and refuses fork heads itself.
- RESULT steps 4-5: the diff touches only `.github/workflows/ci.yml`, `tests/entities.py`, `dev/programme/delivery/3923.md`; no claim file, golden fixture, VERSION, manifest or notes heading. Step 14: no budget, closure, INERT or ledger moves; the new delivery file passes the head's classification checks (entities rc=0).
- RESULT step 6 (other configurations): fork head (job admitted, cancel step false, refresh a notice), review event (cancel false, refresh runs), bot sender (cancel false), push / workflow_dispatch (job false) are each evaluated by the L5 and cancel rows; M3/M6 show they bind. One-seam class (one job fold); no enumeration rule owed.
- RESULT permissions: the folded job keeps `contents: read`, `pull-requests: read`, `actions: write`, the grant both old jobs held; `persist-credentials: false`; restore precedes every token-holding step.
- RESULT step 16: no actuator path; not applicable. Step 15: matches the approved design's L5 (same grant, order and conditions kept, review events kept).
- CI: `merge_train.py classify 4a07b1ec --pr 3923` polled ~30 min, last line `WAIT 4a07b1eca5cfd6c507ad7bdcd29e38af6e46f3de pending: gate red: none`; no red at the head, so no `## Red checks` answer owed.

## Findings

- Follow-up: the L5 saving (one allocation and checkout fewer per PR event, design ~150-200 runner-min/day) is measured only after the merge, by the design harness `census` arm on the first busy day; the body states it owed. Carry: #3885
