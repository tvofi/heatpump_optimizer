Root-cause record for the third `GREW critical_path_minutes` on `main` (`8f286293b`, run 41397326281), extended to the fourth (`8e90d8144`, run 41818271680). It is the product of the root-cause seat, run beside the hotfix fixers and not inside them (`dev/governance/roles/root-cause.md`). The record is `dev/audit/rca/r10-ci-critpath-3.md`. Its replay is `dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py`, which runs over three Actions-API fixtures beside it: `runs.json`, `runs_red4.json` and `ci_logs.json`. No production code, budget, claim file or ratchet changes. Both countermeasures are drafts for the owner and land nowhere until the owner decides; red 4's hotfix, `r10-hotfix-ci-critpath-4`, is the orchestrator's and is not touched.

This head repairs review round 1 (verdict/3189, blocked: replay.py exited 1 because #3180 replaced the `critical_path_minutes` it imported):

1. **The replay is pinned.** Each red is graded with `tests/ci_ratchet.py` as of the red commit (`git show <sha>:tests/ci_ratchet.py`, imported by spec). Red 3 reads 36.5 GREW at this head. With the live file in its place, step 1 reads 21.967 and the replay exits 1. That is the reviewer's own control, re-run as `## Null control` shows.
2. **The record now relates its countermeasure 1 to #3180: complementary, not superseded.** #3180 prices each job at its fastest of 16 runs, so it goes red only when a heavy job draws no fast host in 16 runs. Red 4 is that case. The planned path read 1345.7 s at red 3 and at red 4, so as a gate it would have kept red 4 off `main`. It would not have caught growth in the fast lane, which it does not grade. The table row for red 3 now names `#3180`, merged 11-04 09:26, 51.4 h.
3. **The calibration rule is cited at the red commit's tree**, `8f286293b:tests/ci_ratchet.py`, lines 41–52 and 106–111.
4. **Run counts are corrected.** `runs.json` holds 31 runs, 3775..4056, and `run_minutes` grades 29 of them. The cost test's run rate is re-derived: 281 run numbers in 28.6 h.
5. **Step 3's repeat is stated as a determinism check only.** The two closures jobs' `lane plan:` lines are committed in `ci_logs.json`, and the replay checks their totals equal the tree's. The job durations are corrected to the fixture: 38.2 min (run 3870) and 20.6 min (run 4055). The per-script figures 97.7/52.7 could not be re-derived, because the closures logs print no per-script seconds. They are replaced by the fast lane's per-script seconds, which are in the fixture: 1824 s against 3137 s over the same 33 scripts.
6. **New: the fourth red.** The record names its process state, (c): #3180 followed the calibration rule, but its 40-run sample never held 16 runs without a fast fast-lane draw. The fast lane ran under 26 min in 14 of 28 runs up to 4009 and in 0 of 16 after. The red came one push after run 4009 left the window. The runner image does not separate fast from slow runs. The cost test is re-taken at four occurrences: P = 0.42 a day, mean red ≥ 21.7 h, about 9.0 h of red main a day against about 90 s a day for the countermeasure. Section 7 states what the record does not cover.

Also corrected, as a disclosed self-correction: the first three onsets were 7.40 days apart, not 8.4, with gaps of 5.6 and 1.8 days, not 6.6 and 1.8. Two git-history counts in section 5 are corrected under the rule now written there: `roster_edit` is 31, not 32, and state-doc regenerations are 108, not 106. The 108 dispatch commits and 19 merges re-derive unchanged.

## Head

f6507bae2b86c1cd947e491e194f6f74970770e6

`origin/main` was at `8e90d81443317f76f22602a89651f7ca17c633f9` at 2026-11-04 14:20 UTC, unmoved since the base this was given and since the `prepr.sh` run. No merge was needed.

## Mutation proof

n/a: no production line changes; this is a root-cause record and its replay. The replay's own mutant is the pin. With `_ratchet_at("HEAD", …)` in place of `_ratchet_at(RED3_SHA, …)`, step 1 reads `21.967 … ok`, and the output is `RESULT: does NOT hold [False, True, True, True, True, True]`, rc=1. Restored, it reads `RESULT: holds`, rc=0.

## Null control

- The pin: see `## Mutation proof`. The unpinned replay at this tree exits 1, and the pinned one exits 0.
- Red 4's window carries its own control. The window one push earlier (`616868bdc`, runs 4009..4116) grades 22.367 ok under the same ratchet, which matches what CI printed there. Only the window that lost run 4009 grades 29.067.
- Step 3's repeat is a determinism check and controls nothing about hosts. That the planned path is unaffected by host speed rests on its reading no clock, and the CI lane totals in `ci_logs.json` are shown equal to the tree's.

## Figures

- `python3 dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py` (rc 0, 0.31 s) prints every replay figure in the record: step 1 36.5 GREW; step 2's 3 and 6 windows and the 31/29 run count; step 3's 1345.7 → 1445.7 and the CI lane totals; step 4's 22.367 ok / 29.067 GREW, the fast-lane prices 20.38 / 27.33 / 17.73, and the 7.084 excess; step 5's 1824 s / 3137 s, the ratios 1.26..3.09, the image table and the counts 14 of 28, 0 of 16 and 7 of 16; step 6's 1345.7 at both reds.
- `python3 tests/closure.py lane-plan --all-scripts --lanes 3 --out-dir "$(mktemp -d)"` prints the longest lane, 1345.7 s.
- `git log --remotes --since=2026-11-02T06:40:00Z --until=2026-11-02T21:06:00Z --format='%H %s' | sort -u | grep -c ' dispatch:'` prints 108. The same with `grep -ci roster_edit` prints 31.
- `git log --remotes --since=2026-11-01T18:00:00Z --until=2026-11-04T07:00:00Z --format='%H %s' | sort -u | grep -ci 'state_docs'` prints 108.
- `git log origin/main --first-parent --since=2026-11-02T06:40:00Z --until=2026-11-02T21:06:00Z --format=%s | grep -c '^Merge pull request'` prints 19.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`.

## Red checks

none: no check run has concluded red at `00f1d0eca` (the PR head before this push) or at this head. `main`'s own reds at `8e90d8144` are `tests / ci-ratchet`, `gate` and `record-autofix`. They are main-inherited, and `tests / ci-ratchet` is the fourth red this record names. It is push-only (`tests.yml:2265-2267`), so it cannot run on this branch. The record's countermeasure 1 is the cheaper PR-time detector for it, with a standing cost of about 90 s a day.

## Forward-carry

none

## Friction

none
