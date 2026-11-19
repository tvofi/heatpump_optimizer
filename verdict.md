Fix review: merge 5e10f99bc84d7ecef0d5dbdc4e3451ed27cc2c4c

bus-nonce: 6e2b52d1bfaeca831ed06cd383a34b38
pending-ci: gate

Round 1 (first review of #3801).

## Evidence

- Head: 5e10f99bc84d7ecef0d5dbdc4e3451ed27cc2c4c, still the PR head when this verdict was written (ev/HEAD.txt). The diff is tools/ci/selftest_closures.json, 4 lines added, plus the delivery row dev/programme/delivery/3801.md. VERSION, the manifest version and RELEASE_NOTES.md are untouched.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 with no conflict (ev/merge-tree.txt). origin/main is 1723f9fdc9, which is also the merge base.
- Finder's harness, re-derived independently: `selftest_scope.py record` under strace, run for the four steps (dependency-graph-census, temp-or-machine-path, self-tests-outside-seat, prepr) in a worktree at origin/main 1723f9fdc9. Result: rc=0, 0 failed, 0 broken traces (ev/record.log). Against main's table my record adds exactly the four survivor_triage/currency.py items the PR adds, and also a repeated `tools/audit/round4/**` probe glob (ev/main-vs-rec.diff). Against the head's table that glob is the only difference (ev/rec-vs-head.diff). This matches the body's statement that the duplicates are left out.
- Null control: `drift(table, my measured steps, workflow_steps())` gives the four UNDER-SCOPED refusals with main's table, the same set CI printed. With the head's table it gives 0 refusals and 0 notes (ev/drift.txt).
- Mutation proof (my own targeted mutants): removing any one of the four added items from the head's table brings back exactly its own single UNDER-SCOPED refusal. 4 mutants, 4 killed, 0 survivors (ev/drift.txt).
- Class: one seam. The class is a new directory under a listed survivor_triage/ path. The four gated steps that walk that path are exactly the ones my record and CI's drift name. Its process countermeasure belongs to R11-RCA-SELFTEST-TABLE-DRIFT, as the body's Red checks section routes it.
- At the head, `selftest_scope.py static` reports 127 gated steps and 0 problems.
- CI: `merge_train.py classify` printed `WAIT 5e10f99bc84d7ecef0d5dbdc4e3451ed27cc2c4c pending: gate red: none` on every run from 00:08 to 00:31 UTC (ev/classify.log). No red check at this head, so no red is owed an answer.

## Notes

- Note: figure: the body says `selftest_scope.py --self-test` runs 118 checks. I measure 128 checks, 0 failed, at both the head and the merge base, so the instrument did not change and the body's figure is stale. Carry: dismissed: a body figure, paperwork with no code effect
