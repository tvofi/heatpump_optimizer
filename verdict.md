Fix review: merge a720d3ed6381bbf7f5771d33b000a2cf02fa84d4

bus-nonce: cefbb97647b65e53c02b3ca8a419a22d
pending-ci: gate

## Scope

Round 6, a delta round over the reviewed head 34dae66f17d5b511646ff51f3607d0fa6110bbfe (merge verdict, round 5). The delta `git diff 34dae66f a720d3ed` holds no non-merge commit of the PR's own (`git log --no-merges a720d3ed ^origin/main ^34dae66f` is empty, `ev/own_commits_since_reviewed.txt`). It is made up of merges of origin/main, the handoff bc06133f (origin/main 237fad44 merged into 09fac908), and an automatic merge of origin/main 6858b4abc1. The PR's own patch does not touch `custom_components/` (0 paths against its merge base). The 34 `custom_components/` paths in the delta all come from main, so nothing widens the scope (fix-review.md step 12). From round 4 on, `fixer.md` owes a re-cut; the body's `## Re-cut` is present.

## Findings

None new. The previous verdict's one item, a Follow-up about the `ps_start` sign mutant, was dismissed (no in-tree reader of the start field). Nothing in this delta touches `seat_gen.py`'s `ps_start`, so it stands as dismissed.

## Evidence

- The PR's own patch is unchanged: `git diff <merge-base> <head>` at 34dae66f (base d1def1ea) and at a720d3ed (base 6858b4ab) cover the same 19 files. The changed lines are identical in 18 of them (`ev/patch_compare.txt`). The one difference, `beat_jobs.py`, is only the `ROWS`/`RUN` union with main's `darwin-selftest` (`ev/beat_jobs_patchdiff.txt`): 518 insertions both times, deletions 13 -> 14 for that one rewritten line.
- bc06133f matches the body. Re-creating its merge (`git merge-tree --write-tree 09fac908 237fad44`) conflicts only in `tools/audit/seat/beat_jobs.py` (rc 1, `LEDGER-MERGE: resolved tests/closures.json`, `ev/bc06_recreate.txt`). Diffing that conflicted tree against bc06133f gives one file, `beat_jobs.py`: the ROWS and RUN conflict hunks resolved as a union of `loop-cwd` and `darwin-selftest`, with no other edit (`ev/bc06_resolution.txt`). This matches the body's Head and Resolution note: "no other file touched by hand".
- The later merges e6b98dd5 (bc06133f into 09fac908) and a720d3ed (origin/main 6858b4ab) are each tree-identical to `git merge-tree` of their parents (`ev/bc06_recreate.txt`, empty diffstats), so they add nothing beyond the automatic merge.
- Mutants at the head (`mutant_run.py --spec`, copy-tree, `ev/spec.json`, `ev/cmd.sh` = the body's cmd.sh; output in `ev/mutants.txt`, rc 0): `SURVIVED NULL`, then `KILLED` for each of `pulse_gen_read_off`, `ps_start_zero` and `loopcwd_path_only`. My resolution mutants are also all KILLED: `resolution_drop_loopcwd_row`, `resolution_drop_darwin_row`, `resolution_drop_loopcwd_run` and `resolution_drop_darwin_run`. The `beat_jobs` self-test therefore pins both halves of the union in ROWS and in RUN.
- Self-tests at the head (`ev/selftests.txt`): pulse 70 checks, 0 failed; seat_gen 25 checks, 0 failed; beat_jobs 250 checks, 0 failed (matches the body's Resolution note "250 checks 0 failed"); open_driver 93 checks, 0 failed.
- `git merge-tree --write-tree origin/main a720d3ed` at origin/main ebff4c1b5aac: rc 0, no conflict (`ev/merge_tree.txt`).
- VERSION, `custom_components/` and RELEASE_NOTES.md are untouched by the PR's own patch against its merge base (count 0).
- The body's `## Head` names a720d3ed6381bbf7f5771d33b000a2cf02fa84d4, the head I measured.
- Not re-derived in this round (outside the delta's scope): `r10_open_driver_mutants.py` `RESULT mutants=24 survived=0` and `prepr.sh rc=0`.
- `merge_train.py owed-reds` set: `ev/owed_reds.txt`.
- CI: `merge_train.py classify a720d3ed --pr 3491` printed `WAIT a720d3ed6381bbf7f5771d33b000a2cf02fa84d4 pending: gate red: none` on every run from 18:08 to 18:38 UTC (~30 min, `ev/classify.log`), so no red at this head and `gate` still pending: hence `pending-ci: gate`. The packet's `introduced-red` refusal was an in-progress `instrument-self-tests`, not a red; classify decides. The PR head is still a720d3ed at 18:38 UTC.
