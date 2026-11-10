Fix review: merge 64e6ff57bbd6008f221ec1c39335ba8599be407d

bus-nonce: 7e2e19f18e1e6f4033b6e35f0f32ad3a

## Findings

- The re-recorded table carries tracer-shaped probes such as `-c` (open-pr, pr-args, update-pr) and `.gitattributes` under paths ending `.py`; they only over-approximate, which drift reports as notes and never refuses. Carry: dismissed: over-approximation only, drift never refuses it and no gate selection depends on it

## Evidence

Round 1 of review for #3409. Measured head 64e6ff57bbd6008f221ec1c39335ba8599be407d (the head the body names; 64e6ff57 adds only `dev/programme/delivery/3409.md` over the code head 79f25fdb3), re-read as the PR head before return. Role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` empty.

- RESULT ref_privacy self-test at head: `ref_privacy self-test: 125 checks, 0 failed` (matches body).
- RESULT selftest_scope self-test at head: `selftest_scope self-test: 103 checks, 0 failed` (matches body).
- RESULT selftest_scope static at head: `selftest_scope static: 110 gated step(s), 0 problem(s)` (matches body).
- RESULT beatd self-test at head: `beatd self-test: 119 checks, 0 failed`, `ok (6) git status through the shim logs no retry` (ev/beatd-selftest.txt).
- Mutation, fix 1 (`ref_privacy.added_lines`), each run alone and restored: `if not present:` -> `if False and not present:`; ref side `status != "D"` -> `True`; base side `status != "A"` -> `True` (a mutant the body did not run); whole `added_lines` reverted to origin/main's. Each: `ref_privacy self-test: 125 checks, 1 failed`, the failing check `the content arm never shows a side the diff says is absent ...`. Not vacuous.
- Mutation, fix 3 (governance.yml gating): `if:` reverted to `${{ !cancelled() }}` -> static prints `UNGATED step 'Show the workflow read runner refusing its own fixtures'` and `109 gated step(s), 2 problem(s)`. Deleting the `gh-read-run` table entry -> `STALE ... missing ['gh-read-run']`, `110 gated step(s), 1 problem(s)`.
- Mutation, fix 4 (beatd case (a)6), the body's perturbation reproduced with my own recording: touched `dev/audit/rounds/round9/D4/s1/shots/expanded_plan__1280__light__en.png` and `dev/audit/waves/w5-g5-195-coverage/coverage/logs/entities.log`, then `selftest_scope.py record --step beatd --out <scratch>` on Linux/strace. Fixed code: files 3, index false, dirs 1, neither touched file read; covered by the head table (no missing files, dirs or index, run_sha equal). Mutant (status back on `ROOT`): files 7 incl. both touched files, index true, dirs 665; against the head table it misses 4 files, 664 dirs and the index, i.e. drift would refuse. Matches the body's 665 dirs / index figures (ev/fixed.json, ev/mutant.json).
- Table re-record (fix 2/5): my own semantic diff of `tools/ci/selftest_closures.json` origin/main vs head, using `selftest_scope.covers` and drift's dirs/ancestor rule with main's committed table as the measurement: every step of main's table is covered by the head table except `beatd` (`.gitignore`, 656 dirs, index), the read set fix 4 removes. All other changes are additions (the textual 1610-line diff is mostly key reordering). The body's union check against main's uploaded artifacts 13730213593, 13735714488, 13737089304 was not re-derived: those artifacts are not reachable from this seat; the CI `governance / instrument-self-tests` run at this head (job 129677221345) concluded success.
- Class (step 6): the body's cause 1 is the one absent-side `git show` in `added_lines`; the fix routes both sides through `--name-status` with `--no-renames`, so no R/C two-path record can misalign the `zip(fields[0::2], fields[1::2])` pairing. No enumeration rule named; the class is one seam.
- Claims/version (steps 4, 5): diff touches no `tests/golden/`, claim file, `VERSION`, manifest or `RELEASE_NOTES.md`; no fixture can move.
- Metrics (step 14): no `*_budgets.json`, `tests/closures.json`, mutation ledger or archscore file in the diff.
- Merge: `git merge-tree --write-tree origin/main 64e6ff57...` exit 0 at origin/main 699f4d9ef4 (ev/merge-tree.txt).
- CI: `merge_train.py classify 64e6ff57bbd6008f221ec1c39335ba8599be407d --pr 3409` -> `GREEN 64e6ff57bbd6008f221ec1c39335ba8599be407d pending: none red: none` (ev/classify.txt). The digest's early `gate` failure (job 129677715544, 06:47) is superseded; classify reads no red. No owed red (`merge_train.py owed-reds` set) is red at this head, so no `## Red checks` answer is owed by this PR's runs; the body answers main's `instrument-self-tests` red anyway, naming process state (a) and a separate RCA seat (roster item r10-rca-main-selftests-red).
- Forward-carry: body states none; its roster carries (22f9186f) are consumed by fixes 1 and 4.
