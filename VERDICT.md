Fix review: merge ba4d4d2359a7e15add72e3fa836aa0f11081ca61

bus-nonce: 5ac864a6133bcdd428a563bab1008a45

Round 4. The dispatch scoped this round to `git diff df4ecb11ac ba4d4d2359` (the merge of `origin/main` `7ae05284d5`) and asked that prior findings stay resolved. No verdict ever named `df4ecb11ac`: the last one is round 3, `blocked bef58ed281 harness: design-trace-missing`. So "prior findings stay resolved" also covers the branch's own change since `bef58ed281`, which is the four commits `a486e51b62`..`6ff83a2feb` (the `absorb` step). I reviewed that as well (`ev/delta_r4.diff`, 6 files, +102/-6). No `custom_components/` file is touched.

## Findings

- `trace_steps` in `tools/ci/selftest_scope.py` skips the new `absorb` step for `record` and `precheck` (`s.id in ("scope", "strace", "drift", "absorb")`), and no check pins that skip. If `"absorb"` is taken out of the tuple, `python3 -I tools/ci/selftest_scope.py --self-test` still reads 0 failed (`ev/own_mutants.txt`). Without the skip, the step's run text would run in the scratch clone with no `$RUNNER_TEMP/selftest_closures.json`. `absorb` would then be refused as UNREADABLE, and the step would be listed in `failed`. As a result, every `record` would return 1 and every `precheck` would return the skip code. The failure is loud (the step is printed as `FAIL`), not a wrong table. The same mutant on the older `"drift"` member also survives, so the gap is older than this diff, which copied the pattern. The body's `## Unpinned sites` does not list it. A fixture job in `--self-test` that contains a `drift` and an `absorb` step, driven through `record`'s scripted-strace arm, would pin both. Carry: R11-PRE-SHARED-FILES (part 3)

## Notes

- Note: stale-figure: `## Head` says the merged file is "written in `fold_ledger.py`'s own format". That is true, but the format has no final newline, so `tools/merge/ledger_merge.py` `_format` returns `None` for main's file and for this head's file alike (`ev/ledger_format.txt`). Every later branch that touches `dev/audit/config/bugclasses.json` will meet the same driver refusal this merge met. That is main's own state from `e597cc96ae`, not this diff. Carry: dismissed: main's own state, not this pull request's diff

## Evidence

The prior block (round 3, `harness: design-trace-missing`) is resolved:

- The owner ruled on D1/D2. `dev/programme/RULINGS.md` at `origin/main` has the entry "2026-11-18, #3708 design decision D1/D2 (as recorded): option (b)", committed by tvofi in `e4fbf16e79`. It puts the part-1 job in `governance.yml` with the read-only grant and leaves the `record-autofix` write set at delivery rows only. Under that ruling the body's departure (a seat commits the `selftest-absorbed` artifact) follows the ruling and does not depart from it.
- The design demonstration ran on real CI, and I read the cited jobs back through the API (`ev/ci_jobs.txt`):
  - Job 135045572288, at scratch `964901436f` (this branch plus one planted `open("VERSION").read()` in `tests/lane_skip.py`, and tracing switched on for a dispatched run): the job is `failure`, step 131 (drift) is `failure`, step 133 (`absorb`) is `success`, and step 134 (upload) is `success`.
  - Job 135103173468, at scratch `c96dac8741` (+133 lines in `tools/ci/selftest_closures.json` only): the job is `success`, step 131 is `success`, and steps 133 and 134 are `skipped`. That is the null: a green push writes nothing.
  - `git diff --stat` confirms the shapes of both scratch commits.
- My own mutants of the delta, each run with `python3 -I tools/ci/selftest_scope.py --self-test` in a detached worktree and restored afterwards (`ev/own_mutants.txt`, `ev/own_mutants2.txt`). Unmutated, the self-test exits rc 0 with 0 FAIL lines (`ev/sscope_selftest.txt`), and its three `the bot's step:` checks read `ok`.

  | Mutant | Result |
  |---|---|
  | `absorb` `if:` changed to `steps.drift.outcome != 'skipped'` | killed (the gating check) |
  | `--out` pointed at the drift artifact instead of `absorbed/` | killed (the red-table check) |
  | upload `if:` changed to `always()` | killed (the gating check) |
  | `exit 1` changed to `exit 0` when nothing is added | killed (the null-control check) |
  | the result grep accepts `0 read(s) ... 0 step(s)` | killed (the null-control check) |
  | `absorb` removed from `UNTRACED` in `selftest_step.sh` | killed (2 wrapper checks) |
  | `absorb` removed from `UNGATED` | killed (2 checks) |
  | `absorb` removed from `trace_steps`' skip | survives (see Findings) |
  | `drift` removed from the same skip (an older line) | survives |
- `tools/pr/ci_predict.py`: the replay skip for a failure-conditioned step has a check of its own with a null (a success-conditioned step stays replayed). I ran one mutant of my own (`continue` changed to `pass`). The full `--self-test` hit my 600 s bound before it printed anything (rc 124, `ev/cip_mutant.txt`), so that mutant is not counted either way. The check reads `instrument_steps`' output directly, so it fails by construction if the skip is removed.

The merge `df4ecb11ac` to `ba4d4d2359`:

- The head's tree equals `4f49139099`'s, which is `df4ecb11ac` merged with `origin/main` `7ae05284d5` (merge base `5e2ef89b4e`).
- Three files differ from both parents: `.github/workflows/governance.yml`, `tools/ci/selftest_closures.json` and `dev/audit/config/bugclasses.json` (`ev/both.txt`). The first two equal git's own automatic merge (`git merge-tree --write-tree`, tree `9c40b65ebc`: empty diff over the whole tree outside `bugclasses.json`).
- `dev/audit/config/bugclasses.json`, the one conflict, was refused by the ledger driver. `git diff 7ae05284d5 ba4d4d2359` over that file is exactly the branch's four values (`_rca.R10-RCA-SELFTEST-SCOPE-DRIFT` `countermeasure` and `doc`, and the `R10-SELFTEST-TABLE-SHRINK` `detector` and `barrier`), byte-equal to `git diff 5e2ef89b4e df4ecb11ac` over the same file. Main changed none of those four values. Every main addition (the R11 instances and the 27 R11 `_rca` records) is kept.
- The file parses as JSON. `python3 -I tools/audit/fold_ledger.py check` reports `0 violation(s)` (83 classes, 179 rca entries).

Head and CI:

- Head reviewed: `ba4d4d2359a7e15add72e3fa836aa0f11081ca61` (`ev/HEAD.txt`). It is the PR's `headRefOid`, and the author is `app/hpo-author`.
- `VERSION`, `custom_components/`, `RELEASE_NOTES.md` and `tests/golden/` are untouched by the branch.
- CI: `merge_train.py classify ba4d4d2359 --pr 3708` printed `WAIT ... pending: gate red: none`. The check runs at the head are completed-success, skipped or queued, and none is red, so no owed red is unanswered.
- carry_audit at the head (from the packet): `10 finding item(s): 10 routed, 0 unrouted, 0 bad destination(s)`.
- Not re-taken: the body's `precheck --base origin/main` (22 min 39 s under strace, Linux only) and its `prepr: passed rc=0 at 6ff83a2feb`.
