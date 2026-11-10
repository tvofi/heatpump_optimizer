Main is red on `governance / instrument-self-tests` (run 42741176573, job
129582549659, main b076272509): `selftest_scope check: 109 gated step(s), 38 refusal(s)`
at the step `Refuse a self-test read set the committed table misses`. It has
not been green on main since #3315 (ba6fd7e8b0) introduced the check: until
#3375 (2cf0f129bc) restored tracing the job hung or was cancelled, and after
that every main push failed this step (37, 37, 37, 38 refusals at 2cf0f129bc,
9b1bb58db7, 20d96598c9, b076272509). From 8652aa65ce (#3361) a second cause
also fails the selftest_scope self-test and its mutants step (job 129633096425:
`selftest_scope self-test: 96 checks, 1 failed`, `selftest_scope check: 109 gated step(s), 39 refusal(s)`).
Not infrastructure: no rate-limit or network line; each step printed its
refusals and exited 1.

## Causes

1. **A probe no table can hold.** `ref_privacy.added_lines` ran
   `git show REV:path` on the side of the diff where the path is absent (an
   added file at the base, a deleted one at the ref). Git lstat()s the worktree
   path to word that error, so on main's push `push-names-the-host` probed
   each merge's new files: `dev/programme/delivery/3375.md`, `3396.md`,
   `3299.md` (with `heat_curve.py`, `off_restore.py`), `3399.md`, `3400.md`,
   `3361.md` in successive runs, one new path every merge. A re-recorded table
   alone would go red again at the next merge.
2. **The committed table drifted.** `tools/ci/selftest_closures.json` missed
   files, dirs and probes that merges since #3315 added (`topic_grammar.py`,
   `bottleneck_check.py`, `tools/audit/seat/hooks/`, the new
   mutation-ledger dirs, ...).
   - **2b. An ungated step.** #3361 (e79a0e78bc) added `Show the workflow read
     runner refusing its own fixtures` with an `if:` that does not read
     `steps.scope.outputs.<id>`:
     `UNGATED step 'Show the workflow read runner refusing its own fixtures': its if: does not read steps.scope.outputs.<its own id>`.

## Fixes

1. `tools/audit/seat/ref_privacy.py`: the content arm reads the diff's
   `--name-status` and shows only the present sides. Its output is unchanged,
   because an absent side was already read as no lines.
2. `tools/ci/selftest_closures.json`: re-recorded as the union of the
   committed table and main's own measurement at b076272509 (artifact
   `selftest-closures` 13730213593 of run 42741176573), less that run's one
   cause-1 probe `dev/programme/delivery/3399.md`. The union keeps the
   committed over-approximation, which drift reports and never refuses.
3. `.github/workflows/governance.yml`: the step gets `id: gh-read-run` and is
   gated on `steps.scope.outputs.gh-read-run` (precedent d9990a12f2). Its table
   entry recorded on Linux by
   `python3 -I tools/ci/selftest_scope.py record --step gh-read-run`
   (`0 failed [], 0 broken trace(s)`).
4. **A timing-dependent read set, fixed at its cause.** `beatd.py`'s self-test
   case (a)6 ran `git status --short` on `ROOT`. Status re-reads the content of
   every racily clean index entry (mtime not older than the index), so the
   files it reads follow the checkout's timing: main's measurements recorded
   80, 20 and 235 `beatd` files, mostly `dev/audit/**` logs and PNGs, for one
   unchanged step. The status now runs in the case's own throwaway repo
   (`w / "plain"`, initialised before it); the check, that a non-fetch command
   through the shim logs no retry, is unchanged. Fixed rather than narrowed:
   a narrowed recording would still need the step to read `ROOT`'s index and
   665 dirs, and any file a later checkout leaves racy would refuse again.
   The `beatd` entry is re-recorded from the fixed code.
5. Union with main's later measurements (artifacts 13735714488 and
   13737089304 of `selftest-closures`): `tools/audit/seat/gh_read_run.py`
   added to field-coverage, hooks-setup, open-pr, pr-args, selftest-wiring and
   update-pr (real drift from #3361). Not unioned: their `beatd` sets (the old
   case (a)6, fix 4) and `push-names-the-host`'s probes
   `dev/programme/delivery/3400.md`, `3361.md` and
   `dev/audit/harnesses/r10_red_list_lag.py`, each a path the measured push
   added (`git log --diff-filter=A`: 7326025c8, 5a5b2c4fc, d3deec006), i.e.
   cause 1, fixed by fix 1.

## Head

79f25fdb3bc296091a1b48d64549927f5391c262

## Mutation proof

New self-test check in `tools/audit/seat/ref_privacy.py`: a subprocess spy
over `content_check`, on a diff with an added, a modified and a deleted file,
refuses any `git show` of an absent side.

- Before fix 1 (the check added, `added_lines` unchanged):
  `FAIL the content arm never shows a side the diff says is absent ...`,
  `ref_privacy self-test: 125 checks, 1 failed`.
- Mutant `if not present:` -> `if False and not present:`: `125 checks, 1 failed`.
- Mutant ref side `status != "D"` -> `True`: `125 checks, 1 failed`.
- Fixed: `ref_privacy self-test: 125 checks, 0 failed`.
- Fix 3: before it, `FAIL the live job parses (118 steps) and its gating is consistent`
  (main's job 129633096425); after it, `selftest_scope self-test: 96 checks, 0 failed`.

- Fix 4, perturbation: two tracked files touched
  (`dev/audit/rounds/round9/D4/s1/shots/expanded_plan__1280__light__en.png`,
  `dev/audit/waves/w5-g5-195-coverage/coverage/logs/entities.log`), then
  `selftest_scope.py record --step beatd --out <scratch>`. Old case (a)6:
  the entry reads both touched files, `index: true`, 665 dirs. Fixed: neither,
  `index: false`, 1 dir. Unperturbed control, bare `git status --short` under
  `strace -e openat` on this checkout: 0 opens of `dev/audit/*.{png,log,tsv}`
  on a fresh index, 2 after touching those two files, 0 on the next run.

## Null control

On the unmodified tree the new check fails (above), and the other 124 checks
pass, so fix 1 changes no refusal `--check` makes. Table: main's own
measurement (artifact 13730213593) fed to `selftest_scope.drift` gives the
job's 38 refusals against the committed table, and none against this table
once the cause-1 probe is removed from the measurement.

## Figures

- `python3 -I tools/audit/seat/ref_privacy.py --self-test` -> `ref_privacy self-test: 125 checks, 0 failed`
- `python3 -I tools/ci/selftest_scope.py --self-test` -> `selftest_scope self-test: 103 checks, 0 failed` (at 79f25fdb3)
- `python3 -I tools/ci/selftest_scope.py static` -> `selftest_scope static: 110 gated step(s), 0 problem(s)` (at 79f25fdb3)
- `python3 -I tools/audit/seat/beatd.py --self-test` -> `beatd self-test: 119 checks, 0 failed` (at 79f25fdb3)
- Union check: each artifact's steps against this table, by `selftest_scope.covers` and the dirs rule `drift` uses, misses only in `beatd` (old code) and `push-names-the-host` (the three cause-1 probes above); every other step 0.
- Scoped gate: `tests/closure.py select` -> `MODE: FULL` (`tools/ci/selftest_closures.json changes the gate itself`); left to CI.

## Red checks

`governance / instrument-self-tests` on main (steps `Refuse a self-test read
set the committed table misses`, `Show the self-test scope
(tools/ci/selftest_scope.py) refusing its own fixtures`, `Show the self-test
scope refusing each mutant of its trace rules`). Cheaper detector:
- Cause 2 (table drift) and fix 4 (beatd's timing): none cheaper; only the
  strace measurement of the whole job sees a read set, and it runs on a push
  to main.
- Cause 2b (ungated step): `selftest_scope.py static` / `--self-test`, under a
  second each, would have refused it on #3361's own PR.
- Cause 1 (absent-side probe): a second recording at a different head diff.
Process state (a), no such process: nothing commits main's uploaded `selftest-closures`
artifact when the drift step goes red (`closures-autofix` repairs
`tests/closures.json` only), so main stayed red across merges with the repair
already uploaded. The root cause is owed in a separate seat
(`defect-root-cause.md`).

## Forward-carry

none

## Friction

none
