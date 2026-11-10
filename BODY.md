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
   gated on `steps.scope.outputs.gh-read-run` (precedent d9990a12f2). **Owed
   before handoff:** its table entry, recorded on Linux with
   `python3 -I tools/ci/selftest_scope.py record --step gh-read-run`; until
   then `static` prints `STALE ... missing ['gh-read-run']`.

**Open for the cloud round:** main's later measurements (artifacts
13735714488 and 13737089304) show further drift against this table:
`tools/audit/seat/gh_read_run.py` is missing from field-coverage,
selftest-wiring, hooks-setup, open-pr, pr-args and update-pr (real drift from
#3361, so union it in). `beatd`'s files also swing from run to run (80, 20
and
235 files across the three runs, mostly `dev/audit/**` logs and PNGs), a
timing-dependent read set that may be a third non-reproducible source.

## Head

d2f3db226841114198ec126f3ec8148559435e82

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

## Null control

On the unmodified tree the new check fails (above), and the other 124 checks
pass, so fix 1 changes no refusal `--check` makes. Table: main's own
measurement (artifact 13730213593) fed to `selftest_scope.drift` gives the
job's 38 refusals against the committed table, and none against this table
once the cause-1 probe is removed from the measurement.

## Figures

- `python3 -I tools/audit/seat/ref_privacy.py --self-test` -> `ref_privacy self-test: 125 checks, 0 failed`
- `python3 -I tools/ci/selftest_scope.py --self-test` -> `selftest_scope self-test: 96 checks, 0 failed`

## Red checks

TO FILL from the cloud run. The red check is
`governance / instrument-self-tests` on main (steps `Refuse a self-test read
set the committed table misses`, `Show the self-test scope
(tools/ci/selftest_scope.py) refusing its own fixtures`, `Show the self-test
scope refusing each mutant of its trace rules`). Draft root-cause answer:
the drift is visible only to the strace measurement of the whole job, which
runs only on a push to main, so no cheaper detector reaches cause 2. Cause 2b
was reachable on #3361's own PR: `selftest_scope.py --self-test` and
`static` refuse it in under a second. Cause 1 was reachable with a second
recording at a different head diff. The process state: nothing repairs the
table when main goes red. `closures-autofix` repairs `tests/closures.json`,
but nothing commits the `selftest-closures` artifact, and main stayed red over
several merges with the repair already uploaded. The root cause is owed in a
separate seat (`defect-root-cause.md`).

## Forward-carry

none

## Friction

none
