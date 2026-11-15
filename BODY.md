R11-PRE-SHARED-FILES part 1, union half (`dev/programme/triage/r10-round-end.md` P748, P762; tvofi card C6, 2026-11-15). `record` in `tools/ci/selftest_scope.py` unions every measurement over the committed entry (`union_record` over `union_entry`, the same union `check --write` writes for main's artifact), so a re-record at a stale base no longer drops reads main measures (#3409, #3419, #3506). A read leaves the table only by `prune --step ID --drop KIND:ITEM`. The table `tools/ci/selftest_closures.json` is recorded here as that union over main's own measurement, which turns main's red drift step green.

## Re-cut

Fifth-round body, replaced. Round history is dropped; every figure below is taken at the head named. The re-cut follows P762 and roster carry 9: the table-shrink guard is dropped (`shrink_drops`, `table_base`, `shrink_gaps`, its `static` hook, its fixtures and mutants). The self-test's environment hold and the `main` return-type wrapper go too, because only the guard's base selectors needed them. The union record, `prune` and their tests stay.

Blocking verdict at `00a470f7b7` (`mutation-vacuous`), each finding answered:

- **M3**: `shrink_gaps`'s deletion exemption widened from status D to every touched path survived. Answer: `shrink_gaps` is deleted with the guard (P762), so the predicate no longer exists. `git grep -n 'shrink_gaps\|shrink_drops' -- tools/` prints nothing at this head.
- **M1**: `table_base`'s merge-base replaced by a bare `rev-parse` survived. Answer: `table_base` is deleted with the guard. `git grep -n table_base -- tools/` prints nothing at this head.

The verdict also lists the reviewer's own killed mutants. Two of their predicates stay: the gated-step filter of `union_record` and `prune`'s held-item checks. Both are now pinned by in-tree mutants (below). The third, the probe-is-a-file filter in `union_entry`, is removed as a defect (next paragraph).

Found in this pass and fixed here: `union_entry` dropped a probe that the union also held as a file. `drift` answers a measured probe from `probes` alone, so that union made the next drift run refuse it. Replaying main's measurement against a table written with the filter refused `tools/audit/round4/**` in `open-pr`, `pr-args` and `update-pr`, 3 refusals. Without the filter there are 0. The union is now pure. The `union_record` check expects the probe kept, and it fails on the filtered copy (`FAIL union_record: recording one step over an entry holding reads the trace lacks keeps them`).

## Head

`8ccc59556f257b52e65c0e364957cf86c9d018c7`, measured 2026-11-15 between 13:30Z and 13:50Z against `origin/main` `b3831ff64eca1936f0b618193ee86c3e337b51a9`. `git merge-tree --write-tree origin/main HEAD` conflicted in `tools/ci/selftest_closures.json` after the table union was committed on the old head. So `origin/main` was merged in (`5dccb958d6`), and the table was resolved as `union_record` over main's table of the branch's table and main's artifact.

## Mutation proof

`sh tools/ci/selftest_scope_mutants.sh` at this head: 27 mutants, ends `SELFTEST-SCOPE MUTANTS: every mutant refused`, no `NOT REFUSED`, `MUTANT NOT APPLIED` or `BASELINE RED` line. The union-half mutants and the check each one fails:

- "record replaces the committed entry again" (`entries[sid] = m`): FAIL `union_record: recording one step over an entry holding reads the trace lacks keeps them`. This is the failing test first: the replace semantics `record` had at the merge base.
- "record keeps a step the workflow no longer gates": FAIL `union_record: a step not re-measured is kept, a step the workflow no longer gates is not`.
- "the union drops a committed list entry", "the union drops a committed flag": FAIL `check --write: a planted committed read and flag the run did not measure survive the write`.
- "prune clears a flag the entry does not set", "prune drops a list item the entry does not hold": FAIL `prune_entries: a read the entry does not hold is reported, not ignored`.
- "prune writes nothing", "prune accepts an unknown drop", "prune goes on over an unreadable table": each fails its `prune:` CLI check.

## Null control

- Drift replay with main's own table at this head's tree: the same 4 refusals main's CI printed (below), so the replay reads what CI reads. Replaying with the artifact itself as the table gives 0 refusals.
- Dropped reads: comparing every step of `origin/main`'s table with this head's, item by item and flag by flag, gives `117 step(s) compared, 0 dropped read(s)`. Of the 17 `-` lines of `git diff origin/main -- tools/ci/selftest_closures.json`, 13 are duplicate `D/**` items that `union_entry`'s set removes (main's table holds 13 duplicates, counted per step and kind as list length less set size). The other 4 are values that grew: `[]` now filled, `false` now `true`. The same comparison against a copy with one `open-pr` file removed prints `DROP open-pr files tools/site/day_chart.mjs`, `1 dropped read(s)`.
- `python3 -I tools/ci/selftest_scope.py --self-test` prints `118 checks, 0 failed` both unset and with `GITHUB_BASE_REF=main` exported.

## Figures

- Main's red step: `governance / instrument-self-tests`, step `selftest_scope.py check --traces ... --write` (the drift step, run only on a push to main). Main CI run 43705258717 at `26dbf7c43e` and run 43716462808 at `b3831ff64e` both print `selftest_scope check: 117 gated step(s), 4 refusal(s)`, from `UNDER-SCOPED step verdict-bus: files misses ['.github/workflows/ci.yml']`, `orchestrator-tick: probes misses ['.gitmodules']`, `orchestrator-tick: it read the index`, `merge-train: files misses ['tools/policy/policy_lint.mjs', 'tools/pr/outside.py']`.
- That step's predicate, replayed offline. The trace needs Linux strace, so the measurement is each run's `selftest-closures` artifact, which is `union_entries(main's table, measured)` and so holds every read main measured. Command, with `A` the downloaded artifact and `T` the table: `python3 -I -c 'import json,sys; sys.path.insert(0,"tools/ci"); import selftest_scope as s; r,_=s.drift(json.load(open(sys.argv[2])), json.load(open(sys.argv[1]))["steps"], s.workflow_steps(s.ROOT)); print(*r, sep="\n"); print(len(r), "refusal(s)")' A T`. At `origin/main`'s table: `4 refusal(s)`, the four lines above, for both artifacts. At this head's table: `0 refusal(s)` for both artifacts. So the merge turns the drift step green on main's current measurement.
- Limit: the replay uses main's measurement and does not trace this head. This head changes the reads of one gated step only, `selftest-scope` (its self-test). Its new fixtures run in a scratch repository outside the checkout, and its table entry keeps every read the branch recorded. A new in-tree read would show as UNDER-SCOPED in the first main run after the merge.
- `python3 -I tools/ci/selftest_scope.py static`: `117 gated step(s), 0 problem(s)`.
- `python3 -I tools/ci/selftest_scope.py --self-test`: `118 checks, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

<!-- figure-block: scope-line mb=b3831ff64eca1936f0b618193ee86c3e337b51a9 head=8ccc59556f257b52e65c0e364957cf86c9d018c7 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Brief carries

The group's ten roster carries (`git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`, group R10-SELFTEST-SCOPE-UNION-GUARD, by array position):

- Carry 0 (beatd and review-packet hold unions of two recordings, so a retiring group re-records twice): superseded.
- Carry 2 (the same instruction, as carried a second time): superseded, like Carry 0. `record` unions, and a read leaves by `prune`. The correction to R10-NUDGE-RETIRE's landed instruction is under Forward-carry.
- Carry 1 (`record` replaces): built (`union_record`), pinned by "record replaces the committed entry again".
- Carry 3 (`git` item `?` dropped from three steps): a union never drops it.
- Carry 4 (`tests/entities.py` not runnable on the reviewer's seat): an environment fault, with no finding on the head and nothing to build.
- Carry 5 (the guard should treat a `compact_probes` fold as no drop): void, because the guard is dropped (P762).
- Carry 6 (the same, as carried a second time): void, like Carry 5.
- Carry 7 (shrink guard plus union `record`): the union is built here. The guard is dropped by P762 and replaced by part A, which is carried to R11-PRE-SHARED-FILES below.
- Carry 8 (the same, as carried a second time): answered like Carry 7.
- Carry 9 (the re-cut): done. The guard, its fixtures and its mutants are dropped, and the union record is kept with its failing test and mutant. Roster stage `absorbed` into R11-PRE-SHARED-FILES once this merges (the orchestrator's op).

## Red checks

Ancestry reds on earlier commits of this branch, each answered:

- `tests / fast (3.14)` was red at `0f191f49a8` (job 132252007494). Cause: `tests/features.py` `_chg_seq` starts its default arm from the real clock, so the block is red on every Saturday and Sunday from 2026-11-14T00:00Z, on main and on every head. This diff does not touch `tests/features.py`. Fixed on main by #3578 (R10-HOTFIX-FEATURES-WEEKEND-CLOCK), which is in this head's ancestry. The cheaper detector and its cost test are recorded in `dev/audit/rca/R10-RCA-FEATURES-WEEKEND-CLOCK.md`: state (c), a nightly faketime step on the other day type at an estimated 10-20 s a night.
- `governance / instrument-self-tests` was red at `ef7e3373e7` (job 131898295736). Cause: the shrink guard read `GITHUB_BASE_REF=main` inside a fixture that has no `origin/main`. The guard is deleted in this re-cut, so the arm that went red no longer exists.
- `tests / nightly-status` is red at `00a470f7b7` (job 132594690855). It is outside `merge_train.py owed-reds` and reads the nightly's state, not this diff.

At this head, before CI: none. Main's inherited red, `governance / instrument-self-tests` (the drift step, on push to main only), is the step this merge turns green (Figures). Its cause is the drift family recorded in `dev/audit/rca/R10-RCA-SELFTEST-SCOPE-DRIFT.md`, and its countermeasure is part A, carried below.

## Forward-carry

- dev/programme/rosters/wave-r10-groups.json, group R11-PRE-SHARED-FILES (part 1b, countermeasure A): the bot that commits a refused drift step's `selftest-closures` artifact from main's run is not built here. Until it lands, a red drift step on main is repaired as this pull request did it: the artifact is unioned over the table by `union_record`, and the replay above shows 0 refusals for that artifact. The artifact is already a union (`union_entries`), so the bot needs no merge logic of its own, only `union_record` over the live table at its own head. Carry: R11-PRE-SHARED-FILES
- dev/programme/rosters/wave-r10-groups.json, group R11-PRE-SHARED-FILES: `write_table`'s `compact_probes` appends every `D/**` probe after `collapse`, so an item can be listed twice (main's table held 13 such duplicates, removed here by the union's set). The generator the design registers for this table should write each item once. Carry: R11-PRE-SHARED-FILES
- dev/programme/rosters/wave-r10-groups.json, group R10-NUDGE-RETIRE: the carry landed from this pull request's earlier body says "the shrink guard accepts the removal only for a path the same diff deletes". No shrink guard exists after this re-cut. A group that retires or moves a file the table names (beatd and review-packet read it) removes each such read with `python3 -I tools/ci/selftest_scope.py prune --step ID --drop files:PATH`. Nothing refuses a prune of a path that still exists, so prune only the retired path, and the next main drift run is the check. Carry: R10-NUDGE-RETIRE (supersedes item e4179dbc)

## Friction

none
