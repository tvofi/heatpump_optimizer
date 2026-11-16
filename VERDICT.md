Fix review: merge 3350d749566385bcb0a897256544b40cbc3c46af

bus-nonce: c5070e4ff484f710f15473c8c32842bc

## Review

Round 1 (first round: no prior verdict). Head 3350d749566385bcb0a897256544b40cbc3c46af, base 47f0f18a7ecebaa0f6ff0e4948b4f8d82e616e1a. The diff touches `tools/ci/selftest_closures.json` and `dev/programme/delivery/3652.md` only. No `custom_components/` line, no `VERSION`, manifest, notes heading or claim file.

## Evidence

- RESULT mutation: the reviewer's harness `ev/mutate_drift.py` (the reviewer's own, not the finder's: a data re-record names no finder harness) traced `push-names-the-host` and `self-tests-outside-seat` under strace at the head and ran `selftest_scope.drift`. HEAD table: 0 refusals. Dropping the added `tools/audit/seat/pr_args.sh` gives 1 refusal, and dropping the added `dev/programme/RULINGS.md` gives 1 refusal. Each is the refusal main printed. The null control is the head table's 0 (`ev/mutation_drift.txt`).
- RESULT refusal-coverage: every one of the 16 UNDER-SCOPED refusals that main's push run 43774717279 (job 132998621519) printed is present at the head and absent at the base: 24 (step, kind, path) items covered, 0 missing (`ev/main_refusals_run43774717279.txt`, `ev/refusal_coverage.txt`). This confirms the body's "16 UNDER-SCOPED refusals".
- RESULT per-step delta: the PR adds reads only, with none removed (`ev/added_by_step.txt`). That confirms the body's "42 added lines, no removals" for the json; the 43rd line is the delivery row. The adds beyond main's refusals are post-merge-bookkeeping's 2 role files and sweep-template's 3 extra probes. They only widen scope, under the union rule.
- RESULT static: `selftest_scope.py static` gives 119 gated steps, 0 problems. `selftest_scope.py --self-test` gives 128 checks, 0 failed (`ev/selftest_scope_static.txt`).
- RESULT merge: `git merge-tree --write-tree origin/main 3350d749` rc=0, no conflict (`ev/merge-tree.txt`).
- RESULT version/claims: 0 of VERSION, manifest, RELEASE_NOTES.md and tests/golden/ touched (`ev/version_claims_untouched.txt`).
- Not re-derived: the body's "119 steps, 0 failed, 0 broken traces" record run. I did not re-run the full record and cite CI instead (fix-review step 11). The 119 gated-step count matches `static`.
- Red checks: no red at this head (classify GREEN), so no `## Red checks` answer is owed; `ev/owed-reds.txt` is the owed set.
- Body head: the body names 3350d749 as the head, which is the head measured (step 7).

## Findings

- The re-recorded table has 13 duplicated `/**` probe entries across 6 steps (`ev/duplicates.txt`); main's base had none. The cause is the instrument, not this diff: `write_table` calls `compact_probes`, and that function concatenates `collapse(keep, tracked)` with the existing `/**` probes without deduplicating. So a collapse that produces a glob already listed writes it twice. Every reader of the table converts the list with `set()` (`selftest_scope.py` select/drift/union paths), so scoping and drift do not change. Carry: dismissed: no behavioural effect, every reader is set-based; cosmetic duplication in a generated file
- CI: `merge_train.py classify 3350d749 --pr 3652` printed `GREEN 3350d749566385bcb0a897256544b40cbc3c46af pending: none red: none` (rc 0).
