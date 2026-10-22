Fix review: merge e817bb123b46b6ecee2e2516966dcb48d6061e27

bus-nonce: ba02500d49395877f462af385bec246c

This review covers PR #2585 (R10-CI-LAYOUT-P1) at fixer round 3 (fix2585y). The code head is `188c5728b` and the PR head is `e817bb123b46b6ecee2e2516966dcb48d6061e27` (it adds the automatic origin/main `3976515a0` merge). I measured from detached worktrees at that head on a Linux cloud seat under `/opt/hpo/venv-ci` (CPython 3.14.7). `dev/governance/roles/` is identical on main and at the merge base. Evidence is in `ev/`, and `ev/HEAD.txt` names the head.

## Open blocks from earlier rounds

- `review/2585:VERDICT.md` is round 2's `merge` at `0644c36d`, so no block is open. Its three carries are still routed in this body. The round-2 `1001`/`1002` line-count note does not apply here: `ref_privacy --check` reads `1019 line(s) added since 3976515a0822 judged, 0 refused` (ev/ref_privacy_check.txt), the body's own figure.
- Since `e93de866` the head has changed by `adc94f5eb` (a main merge whose only conflict was HANDOVER.md, where main's text was taken), `188c5728b` (the predictor fix), `b138c5f3a` and `e817bb123` (merges). The main merge `93e6a63d2..3976515a0` touches none of this PR's 39 files (ev/merge_tree.txt: 0 shared paths). So the only authored change I judge this round is `188c5728b`.

## Findings

- **A surviving mutant: `nightly.yml`'s concurrency is unpinned since the move.** I changed `nightly.yml`'s `concurrency.group` from `${{ github.workflow }}-${{ github.run_id }}` to `${{ github.workflow }}`. That gives every schedule, dispatch and push run one shared group, so a newer pending run cancels an older pending one (ev/mutant_R3.diff). Results:
  - `tests/entities.py` reads `ALL 2388 ENTITY CHECKS PASSED`, rc 0 (ev/entities_mo3.txt), and unitcheck is unchanged (ev/mutant_R3_unitcheck.txt).
  - The cause: `_cc_problems` returns `[]` for any workflow without a `pull_request` trigger. Before this PR the nightly lived in `tests.yml`, whose `schedule`, `push` and `workflow_dispatch` arms that check iterates. After the move it reaches no check.
  - Control (ev/mutant_R3_cc_probe.txt, the committed `_cc_*` functions exec'd verbatim): give the same mutant a `pull_request` trigger and the predicate returns 6 problems on its `push`, `schedule` and `workflow_dispatch` pairs ("two schedule runs ... get groups 'Nightly' and 'Nightly'"). The unmutated head file gets distinct per-run groups.
  - The shipped config is correct (`group: ...-${{ github.run_id }}`, `cancel-in-progress: false`), so this is a lost guard, not a live defect.
  - The body's enumeration rule (`git grep -l workflows/tests\.yml`) is path-keyed and does not return this event-keyed filter, so this is not `class-open` under step 6.
  - To settle it: `_cc_problems` covers every workflow (or `nightly.yml` explicitly) for its non-PR events. Mutant: the group above, which must turn entities red. Carry: R10-CI-LAYOUT-P2
- **`nightly-status` at this head names a newer red than the one the body answers.** The body's `## Red checks` answers run 39563978649 (`mutation-nightly`, `slow`) and calls 39681119764 "in flight". At this head, check-run 119599436141 grades the concluded dispatch 39681119764 (head `1ebc737`): `NIGHTLY FAILED: nightly-ha (stable), record-autofix`.
  - `record-autofix` (job 119503547092) failed on `record_row.py --enumerate` with `HTTPError: HTTP Error 503: Service Unavailable`. The guard step then printed "the record step did not run".
  - `nightly-ha (stable)` (job 119503698667) printed `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`.
  - Both are main's lanes on main's head, and this PR moves both jobs verbatim, so neither red is this diff's. The check is not a required context and does not block. `pr-contract` passed at this head (119599434224 and 119599587417), so the trigger is answered by name.
  - The body's Forward-carry already says to dispatch `nightly.yml` right after the merge. That dispatch is the first run of both moved jobs under the new file, so it must be read for these two lanes, not only for `mutation-nightly`. Carry: R10-CI-LAYOUT-P2
- The body routes main's `slow` red (`loop_cpu_ratio 0.1138 over its budget 0.111`) to `R10-REPLAY-CAP`. On roster `306a96d5f` that group is at `resume.stage: done` (ev/roster_stages.txt), so it is not a live destination. The newest concluded dispatch (39681119764) does not list `slow` among its failing jobs, so nothing is left to carry. Carry: dismissed: the newest nightly dispatch no longer fails `slow`, and the destination group is done, so nothing is owed

## Evidence

### Round 3's fix (`188c5728b`, `ci_predict.inert_siblings` counts only INERT siblings)

- RESULT ci_predict head `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against 3976515a0822 (a data-file read is not seen)`, rc 0 (ev/ci_predict_head.txt).
- RESULT M8 (mine) restores the old predicate, `1 file changed, 1 insertion(+), 2 deletions(-)` (ev/m8.diff). `ci_predict` prints `PREDICT closures INERT READS tests/entities.py: tools/audit/seat/orchestrator_tick.py (a new file beside 6 it lists)`, `1 predicted red(s)`, rc 1 (ev/m8_ci_predict.txt). So the mutant changes the prediction.
- RESULT M8 `bash tools/pr/prepr.sh --self-test`: `310 passed, 1 failed`, rc 2. The one failure is `6d reads no glob from three listed siblings that left INERT ... (got 0, wanted 1)` (ev/m8_prepr_selftest.txt). At the head it reads `311 passed, 0 failed`, rc 0 (ev/prepr_selftest.txt). The fix is not vacuous.
- RESULT the premise, checked with the committed recorder. I ran `tests/entities.py` under the recorder's own argv (`strace -f -qq -y -e trace=openat,execve,clone,clone3,fork,vfork`, tests/closure.py:1350) and passed the log to `closure.strace_files` itself, not a scratch re-implementation (ev/strace_probe.txt).
  - `orchestrator_tick.py` is in neither the non-INERT set nor the INERT set.
  - No INERT `tools/audit/seat/` file is read by any Python process.
  - 480 trace lines name the file, all from non-Python processes.
  - Positive control: `record_row.py`, `merge_train.py` and `roster_lib.py` are in the non-INERT set. The traced run read `ALL 2388 ENTITY CHECKS PASSED`, rc 0.
  - CI agrees: `closures` 119599561207 (FULL) concluded `success` at this head.
- RESULT the listed siblings (ev/remaining_figures.txt). `inert_reads["tests/entities.py"]` lists 6 seat files, and `is_inert` is true for `selftest_wiring.py` alone. `tools/audit/seat/` has 55 tracked files, 45 of them INERT. `orchestrator_tick.py` is INERT and unlisted. Re-derived.
  - The body's "44 of the 45 are listed in neither table" was not re-counted in full: I checked only `orchestrator_tick.py`.
- Null control: the self-test's `pglobsib` arm (three INERT siblings) still predicts at the head (`311 passed`), and so does the existing `pinert` arm. So the narrowing does not silence a true glob.
- RESULT prepr `env PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body> 2495` at the head: `PRE-PR: e817bb123b46...`, rc 0, `PR-BODY: 0 error(s)`, `FIGURES: 32 resolved, 11 not verified, 0 refused` (ev/prepr_body.txt).

### The PR's original change: mutation proof (my own mutants)

| Mutant | Change | Result |
|---|---|---|
| R1 | `mutation-pins` `needs: [mutation, mutation-pin-plan]` (ev/mutant_R1.diff) | `1 of 2388 ENTITY CHECKS FAILED`: `the pin shard count scales ... plan wiring=False` (ev/entities_mo.txt). Killed. |
| R2 | `nightly.yml` loses its `schedule:` cron (ev/mutant_R2.diff) | `3 of 2388` failed: `one schedule cron, nightly.yml's ... crons=[]`, the ledger-reach check and the nightly-ha events check (ev/entities_mo2.txt). Killed. |
| R4 (B9) | `briefs` given `needs: [recheck-gate]` (ev/mutant_R4.diff) | `1 of 2388` failed: `every required context tests.yml produces runs on an autofix or batch-proof dispatch (B9) [... 'briefs: briefs needs recheck-gate, which tests.yml has no job for']` (ev/entities_R4.txt). Killed, through the needs arm that the fixer's M1 did not exercise. |
| M7 variant | `PUSHERS` key renamed to `nightly.yaml` (ev/m7.diff) | `ref_privacy --check`: `REFUSE .github/workflows/nightly.yml:381 ...`, `2 refused`, rc 1 (ev/m7_ref_privacy.txt). Killed. |
| R3 | `nightly.yml`'s concurrency group shared across runs | Survives. Under `## Findings`. |

- The diff of each mutant's entities FAIL lines against the head run differs only in the planted-negative `a8:register_once` sample line, as the body says.
- I did not re-run the self-test mutants for `PIN_CHAIN` and the `record-autofix` rename. Those figures are the fixer's.

### The finder's harness at both ends

The design's own `measure/rev/unitcheck2.py static` was read from `archive/probe/design-ci-rev4` (ev/finder_unitcheck_both_ends.txt).

- Base end (before = after = main `3976515a0` `tests.yml`, no map): `STATIC rows 249->249 lost 0 gained 0 changed 0 rc 0`.
- Head without the fixer's map: `lost 30 gained 13 changed 24 (mapped 0) rc 1`. Every LOST row is one of the design's deletions: `recheck-gate`, `composed-proof`, `mutation-pin-plan` folded, the C1 steps of `closures` and `coverage`, and `nightly-ha` steps moved into the action. Every GAINED row is the action, the folded plan step, or the `nightly.yml` `nightly-ha` arm.
- Head with the committed map: `STATIC rows 225->232 lost 0 gained 0 changed 29 (mapped 29) misplaced 0 rc 0`. The plant gives `rc 1 (1 LOST row(s))` (ev/unitcheck.txt).
- `c1_consumers.sh HEAD` lists the body's 8 files, and at origin/main it lists 14. Re-derived.

### Figures re-measured at this head

RESULT entities `ALL 2388 ENTITY CHECKS PASSED` rc 0 (445 s)
RESULT structure `STRUCTURE RATCHET PASSED` rc 0
RESULT archscore `score.py --diff 3976515a0 HEAD`: `Architecture score: dS +0.0000 NULL` (the body ran it against `93e6a63d2`; main's later merge moved none of this PR's files)
RESULT closure selftest `ALL 112 closure shrink pins PASSED`
RESULT select `MODE: FULL -- every test script runs, nothing is scoped out.`, reason `.github/actions/nightly-ha/action.yml changes the gate itself`
RESULT ref_privacy `--check` `20 file(s) with a push site, 9 guarded, 1019 line(s) added since 3976515a0822 judged, 0 refused` in 0.78 s; `--self-test` `66 checks, 0 failed`
RESULT self-tests:
  - merge_main_bot 40/0, merge_train 198/0, orchestrator_tick 176/0, ci_ratchet 15/0;
  - record_row `all checks passed`, ci-watch 8/0;
  - selftest_wiring `73 self-testing, 73 wired, 0 unwired`; tmp_paths `0 refused`; harness_headers `ALL 109`
RESULT policy_lint `TOTAL: 0 error(s) across 41 policy file(s)`; rules_sync `RULES-SYNC ok`; codeowners_gap `RESULT uncovered_files=0 count`
RESULT jobs: tests.yml 19, nightly.yml 6. Carry 1's `GITHUB_TOKEN push ...` grep reads `0`. diffstat `39 files changed, 1941 insertions(+), 2125 deletions(-)`
RESULT critpath self-test `edge+tail gain 330 s (want 330) ok; null control 0 s (want 0) ok`
RESULT carry_audit `--roster-ref origin/handoff/audit-r10-roster check --body`: `11 finding item(s): 11 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt)
RESULT carry_audit over the body plus this verdict (passed as a verdict comment): `12 finding item(s): 12 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_verdict.txt). R10-CI-LAYOUT-P2 is `not-started` on roster `306a96d5f`, so it is live.
RESULT env_drift `env_drift.py 3976515a0 --all`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, rc 0. No claim file is touched.

- `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are not in the diff.
- `budget_raises=1`: `script_runs_per_push 53 -> 54`. Entities' every-script-once pin passes at 54 (`_cir_once_count`), so the row equals the derived count. The payments were judged in round 2, and nothing in round 3 moves them.
- Not re-derived:
  - the critical-path medians (8.8 / 18.1 min) and the coverage-step count (53 executed / 31 skipped), which are round 1's CI-run figures from a host this seat's proxy refuses;
  - `queue_pre_flight` 41/0, `sweep_render` 21/0, `policy_reread_check` 15/0, `throwaway_git` and `train.sh`. My `-I` invocation of `queue_pre_flight` failed on import path. Governance's `instrument-self-tests` (119599436398) ran them all and concluded `success` at this head.

### Red checks (check-runs API, this head; ev/check_runs_final.txt)

All workflows at this head have concluded. Three are red. `closures`, `coverage`, `fast (3.14)`, `instrument-self-tests`, `pr-contract` (×2), `mutation`, CodeQL and `graders-head-copy` concluded success or skipped. The intermediate commits `188c5728b`, `adc94f5eb` and `b138c5f3a` carry no check runs.

- `budget-raise-gate` (119599434022, 119599436099): `RAISE tests/ci_budgets.json: script_runs_per_push: 53 -> 54`, `REFUSED: tvofi's approval is on e93de8667eaf, not this head`. The body names it, and a mandated approval at this head (mandate 6329234399) is the orchestrator's. Answered.
- `nightly-status` (119599436141) grades main. See `## Findings` for the run it now names. It is not a required context.
- Main's `ci-ratchet` red is runner-speed variance owned by R10-CI-LAYOUT. It is not read at this head.

### Merge

- `git merge-tree --write-tree origin/main e817bb123b46...`: rc 0 against origin/main `3976515a0` (tree `f1911fd2`, equal to the head's own tree).
- Origin/main has since moved to `07fcbee2e`. Against it, merge-tree is still rc 0 (tree `c0e9e37f`). The one shared path is `tests/closures.json`, resolved by the ledger driver (`LEDGER-MERGE: resolved tests/closures.json`); `policy_lint.mjs` merges textually clean (ev/merge_tree.txt, ev/main_since_overlap.txt).
- The head is clean, so no absorb is asked. The PR head was still `e817bb123b46...` when I last read it.
