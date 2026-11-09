Fix review: blocked ab236e012dedd0c24039a4b530dcc83ebd20d3b3 root-cause-unrecorded: required check codeql / Analyze (actions) concluded failure at this head and ## Red checks does not name it; pr-contract refuses the body

bus-nonce: 41920e27aabfd0d98f620634394f2fb7

## Block

- `codeql / Analyze (actions)` (job 129049215302, run 42583904042) concluded `failure` at `ab236e012dedd0c24039a4b530dcc83ebd20d3b3`. It is in `merge_train.py owed-reds`, so it is a required check that owes an answer (`defect-root-cause.md` Enforcement). Its log shows the CodeQL CLI download failing in the init step: `Unable to download and extract CodeQL CLI: Unexpected HTTP response: 504`. That is an infrastructure failure, not this diff's code. But the body's `## Red checks` does not name the check. Every workflow at the head concluded, and the `pr-contract` run that started after the last red concluded (job 129063994594, 08:47:25Z) refused the body: `ERROR [pr-body] ... check \`codeql / Analyze (actions)\` is red and \`## Red checks\` does not name it`, `PR-BODY: 1 error(s)`. `gate` code run 42583904042 is red on exactly that pair (`FAIL codeql / Analyze (actions): failure (this run)`, `pr-contract / pr-contract: failure (this run)`). `merge_train.py classify` exits 1: `RED ... pending: none red: gate`.
- Class: this check is the cheapest detector of its own failure, since no earlier detector predicts a CDN 504. The answer owed is therefore the recorded finding that none exists, so the class is `root-cause-unrecorded`, not `-detectable`.
- Remedy, with no code change: add a `## Red checks` line at `ab236e01` naming `codeql / Analyze (actions)` with the 504 log line and "cheaper detector: none exists; an infrastructure download failure". Or re-run the job: if it concludes `success`, the red is still in the range's history, which `pr-contract`'s `red-history` records, so the line is owed either way. Then let `pr-contract` and `gate` re-run. The patch carries this review: `review_carry.py 50d4c7e0 ab236e01` prints `CARRY`, so a body-only repair at this head needs no re-review of the code. Everything under Evidence stands at this head.

## Findings

none

## Evidence

- Head: `ab236e012dedd0c24039a4b530dcc83ebd20d3b3`. It is still the PR head at verdict time (`ev/HEAD.txt`). The body's `## Head` names it as a merge of the authored code head `50d4c7e0`. `review_carry.py 50d4c7e0e2c6 ab236e012ded` prints `review_carry: CARRY`.
- Round: the body records reviews 3350r3 and 3350r4, plus a round-5 repair. This review is at least the fifth round, so `fix-review.md` says `fixer.md` owes a re-cut from the fourth. This block is a body-only repair and asks for no code re-cut.
- Role currency: `git diff merge-base...origin/main -- dev/governance/roles/` is not empty (`fix-review.md` +4/-4). I read the role from origin/main `ba6fd7e8b` through `role_pack.py render fix-review`.
- Mutation proof (step 1): I ran the in-tree harness `python3 -I dev/audit/harnesses/r10_outside_intake_p2_mutants.py` at the head (`ev/harness_full.txt`). It printed `RESULT mutant=M0 rc=0 fails=0 verdict=null`, every other mutant line `verdict=killed` (27 rows, including `state-of-kind-only rc=1 fails=4` and `mark-legacy-dropped rc=1 fails=1`), and `RESULT survived=0`, rc=0.
- My own mutants, outside the harness (`ev/reviewer_mutants.txt`), each applied as one exact replacement and restored with `git checkout`:
  - `memory-dropped`: `old.get(state_of(ln), ln)` becomes `ln`. Result: rc=1, 3 FAIL lines, including "a still-tripped metric re-prints its first line verbatim".
  - `memory-key-whole-line`: `state_of` returns `line`. Result: rc=1, 5 FAIL lines, including two behaviour cases beyond the anchor guards.
  - `make-edit-no-mark`: `"mark-carry"` dropped from `make_edit`'s tuple at `roster_edit.py:1324`. Result: rc=1, 1 FAIL line, `mark-carry whose only unmarked carry left is legacy writes done`. This confirms the body's claim.
  - Unmutated `bottleneck_check.py --self-test`: `ok: bottleneck_check self-test`.
- Body figures re-derived at this head (`ev/cheap_checks.txt`):
  - `roster_edit self-test: 261 checks, 0 failed` (matches the body).
  - `selftest_wiring: 0 index gap(s)`.
  - `STRUCTURE RATCHET PASSED`.
  - `claims hygiene: origin/main ok`.
  - `Architecture score: dS +0.0000 NULL`.
- The three-dot diff touches none of `VERSION`, `RELEASE_NOTES.md`, the manifest, `tests/golden/` or any `*budgets.json`. `pr-contract` agrees: "no version edit".
- Figures not re-derived: the replan both-arms figures at `78d409286` (closure date, batches, CI minutes, `groups_discharged` 3) are a function of a roster tip that has since moved (roster now `1e6a84b72`). I did not re-run them. The gate-scope `MODE: SCOPED -- 2 script(s)` line was not re-run either; I cite CI's heavy runs instead: `tests / closures`, `tests / fast (3.14)`, `tests / coverage` and `tests / mutation` are all `success` at this head.
- Merge with main: `git merge-tree --write-tree origin/main ab236e01` exits 0. Its stderr reads `LEDGER-MERGE: resolved tests/closures.json`, and no claim file conflicts (`ev/merge_tree.txt`).
- Forward-carry: the body says `## Forward-carry: none`. Carry 2 (pluralising the plan-page note) is still on `origin/handoff/audit-r10-roster` in `dev/programme/rosters/wave-r10-groups.json`, as the body states. `carry_audit` in `pr-contract`: `2 routed, 0 unrouted, 0 bad destination(s)`.
- Other reds: `governance / delivery-status` (job 129049215315) is not in `owed-reds`, and the body answers it anyway. The other `gate` jobs (129049711327, 129064781854) are deferrals to code run 42583904042. Full listing: `ev/ci_reds.txt`, `ev/owed_reds.txt`, `ev/classify.log`.
