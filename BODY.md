CI decision cards CI-4 (the reading part), CI-5 (the rule text) and CI-6, from the 2026-11-21 CI bottleneck study. Owner approval 2026-11-21 (decision cards), built as a tooling-freeze exception. This is the policy-and-instruments half. Its sibling, the workflows PR, carries CI-1, CI-2, CI-5's workflow part, CI-7's cap and CI-17. This PR changes `CLAUDE.md` and `dev/governance/rules/defect-root-cause.md`, which are policy, so it merges on the owner's approving review.

**CI-4: "introduced" is read from the diff's scope, not the merge base's job.** Before this change, `merge_train.introduced_at` and `review_packet.introduced_reading` called an `instrument-self-tests` step red at the head *introduced* only when it was not red in the merge base's own job. A base job that was cancelled or never ran therefore failed closed. The study counts 8 of 19 push runs cancelled, and in those cases the review packet waited on a job that would never conclude.

The rule now reads the three-dot diff `base...head` through `tools/ci/selftest_scope.py`'s own `select`, over the head's workflow and table, and reads no base job:
- A red on a step the diff reaches is the pull request's.
- A red on a gated step the diff cannot reach is inherited.
- A timeout is introduced unless every step it cancelled is out of scope.
- It fails closed: when git cannot read the diff, the workflow or the table, or when the selection is FULL (a gate file, an empty diff), every red counts. An ungated or unknown step name is never treated as unreached.

The one new function is `merge_train.selftest_unreached`. `review_packet` calls it through `ci_facts(..., git_read=)`, and `merge_train.Train.introduced` calls it with the merge base. The dead `_selftest_runs` base reader is deleted. The policy sentence in `defect-root-cause.md` follows; it is held at its exact per-file cap of 151 lines and 1885 tokens, and no budget is raised. The bus's REPAIR-OWED wording, the refusal text, the CLI help and both instrument pages follow it too.

**CI-5 rule text.** In `CLAUDE.md` rule 1, "within one merge" becomes "within one burst" and every other word stays. The two comments quoting it (`tests/lane_skip.py` and `tests/card_browser.mjs`) follow. Those comment edits touch gate files, so this diff's gate scope is FULL (see Figures).

**CI-6.** The overlay `proto/CI-SCOPED-RERUN` becomes tracked:
- `tools/audit/seat/ci_rerun.py` reruns only the failed jobs of a PR head's newest runs, only where a failed job is required by an active ruleset, and never past attempt 6. `--dispatch` starts `ci.yml` naming the PR and its base. Its fixture is `fixtures/ci_rerun/pr3836`. It is the overlay's `ci_rerun.sh` logic as Python; the overlay's shell shim only set machine-specific PATH entries, which `tmp_paths.py` refuses, so there is no `.sh`.
- `tools/audit/seat/ci_supersede.sh` runs this tree's `cancel_superseded.py sweep` once, or on a `--loop` that stops on `$HPO_STATE_DIR/ci-supersede.STOP`.

Each has an instrument page, an `INSTRUMENTS.md` line and a self-test, wired into `governance / instrument-self-tests` beside `cancel_superseded.py`'s. Both files sit under `tools/audit/seat/`, which `tests/closure.py` classifies INERT by prefix.

## Head

f20b2af5d18bf32b7ef4a63287e807c5915d8a62, one commit on origin/main 6fdc15354f0f6f4613370fdabe4bd82adbadc087, measured 2026-11-22T01:20Z (origin/main then 4ebd430fbf; the merge is clean). `git merge-tree --write-tree origin/main HEAD` prints one tree.

The finder's harness is the study's symptom: the INTRODUCED reading of live PR heads. It ran `merge_train.py introduced <head>` from a detached worktree at the base 6fdc15354f and from this branch, over the 13 open PRs' heads (scratch driver `harness_ci4.sh`):
- **#3824 and #3822** (the brief-lint `ENOBUFS` reds): the base and the head each read `introduced: 6`. The base read that from the head job against base job 136950904110 (resp. 136952446108). The head read it with `scope leaves 84 step(s) out` and read no base job. A `diff` of the six INTRODUCED names from the two trees for #3824 is empty.
- **The other eleven** read identically from both trees: 0 on a green or absent job, `pending` on a job still running, and REFUSE on a head job that concluded cancelled. A cancelled head job still fails closed.

## Mutation proof

Each mutant was applied in place and run against the file's own self-test arms. Scratch driver `mut_b.py`: `merge_train._introduced_self_test`, and `review_packet.py --self-test`.

| mutant | killed by (first failing check) |
|---|---|
| M1 `introduced_at` ignores the scope (`unreached = None`) | `null: a head red only on steps the diff cannot reach (inherited) is GREEN under classify --pr, introduced rc 0` (5 arms) |
| M2 `introduced_reds` stops subtracting the unreached steps | `introduced: a head red the scope reaches is the PR's; one on an unreached step is inherited` (5 arms) |
| M3 ungated steps counted as unreached | `selftest_unreached: the gated steps the diff's read sets miss, by selftest_scope's select` (3 arms) |
| M4 a FULL selection read as scoped | `selftest_unreached: a gate file in the diff (FULL) is None, every red counts` (2 arms) |
| M6 a timeout always counted | `null: a timeout on a step the diff cannot reach is inherited (GREEN, introduced rc 0)` |
| M7 the diff read two-dot | `an explicit base is the diff's left side, with no merge-base read` (2 arms) |
| R1 `introduced_reading` passes no scope | `introduced: the head's red the scope reaches is INTRODUCED, the unreached one is not, by 1 job-step read` (3 checks) |
| R2 `ci_facts` drops `git_read` | `gather's ci_facts carries the INTRODUCED reading build refuses (M9: its wiring)` |

M5 reads an unreadable diff as empty. It survives as an equivalent mutant: `select` treats an empty diff as FULL (`selftest_unreached: an empty diff (FULL) is None` pins that), so it returns None, and every red counts, either way.

The instrument self-tests carry their own null controls:
- `ci_rerun`:
  - a run whose failed jobs are all non-required is SKIP, never RERUN;
  - one attempt below the cap still reruns (`null: one attempt below the cap still reruns`);
  - `--dry-run` posts nothing;
  - an unreadable ruleset reruns and dispatches nothing.
- `ci_supersede`: without the stub, it runs this tree's `cancel_superseded.py`; `--loop` without `HPO_STATE_DIR` refuses.

## Null control

- On the unmodified tree, the reading needed the base job. The base-tree harness rows above read `base job <id>` for #3824 and #3822.
- At the head, the same two PRs give the same six names without that read. The eleven heads that are not red read identically from both trees, so the change does not move a clean, pending or cancelled reading.
- Synthetic arms:
  - A head red only on an unreached step refuses nothing: `null: a head red only on unreached steps (inherited) refuses nothing` in review_packet, and the GREEN `classify --pr` arm in merge_train.
  - An unread scope counts every red: `an unread scope (git unable to diff): every head red but the push-only drift step counts`.

## Figures

The scope-line figure block is omitted. The gate's MODE line, from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`, is `MODE: FULL`, because `tests/lane_skip.py` changes the gate itself. Those are the CI-5 quote edits; CI runs the full suite.

- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 843 checks, 0 failed`.
- `python3 tools/audit/seat/review_packet.py --self-test`: `review_packet self-test: 131 checks, 0 failed`.
- `python3 tools/audit/seat/ci_rerun.py --self-test`: `ci_rerun self-test: 16 checks, 0 failed`.
- `bash tools/audit/seat/ci_supersede.sh --self-test`: `ci_supersede self-test: 6 checks, 0 failed`.
- `bash tools/audit/seat/bus.sh --self-test`: `bus self-test: 240 checks, 28 failed`. The arms this diff touches pass: `an INTRODUCED red (classify --pr RED, the required set green) owes REPAIR-OWED naming each INTRODUCED line, never a required context`. The 28 failures are host failures: the `adopt` arms find no pinned interpreter under their temporary HOME (`no pinned interpreter at .../.local/state/hpo/venv-ci/bin/python3`), the case-only evidence names meet a case-insensitive filesystem, and two `HPO_SEAT_GEN` arms fail. The base 6fdc15354f, run from a detached worktree on the same host, prints the same `bus self-test: 240 checks, 28 failed`. Its list of FAIL lines is identical: `diff <(grep FAIL base.log) <(grep FAIL head.log)` is empty.
- `python3 tools/audit/seat/selftest_wiring.py --check`: `153 self-testing, 153 wired, 0 unwired` and `0 index gap(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `node tools/policy/policy_lint.mjs --budgets`: `defect-root-cause.md` at its per-file cap and no cap raised.
- `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- The `governance.yml` step change moves `superseded-run-canceller`'s `run_sha`, so `tools/ci/selftest_closures.json`'s entry is re-recorded by its own `write_table` (scratch driver `rec_step.py`). The entry takes the new `run_sha` and adds the two self-tests' reads, over-approximated: the two programs, `fixtures/ci_rerun/**`, and the directories on their paths. `record` needs Linux `strace`, which this host lacks. Main's drift check and the bot's `absorb` add any read a trace finds that this misses. `python3 -I tools/ci/selftest_scope.py static`: `127 gated step(s), 0 problem(s)` (at the first prepr it was `1 problem(s)`, the stale `run_sha`).
- `tests/closures.json` gains the INERT READS pair `tests/entities.py` -> `tools/audit/seat/ci_rerun.py` that `ci_predict.py` predicted. It is written by `ci_predict.apply_inert`, the `--apply-inert` writer, called for that one pair.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`: rc 0

## Approval

This diff changes policy: `CLAUDE.md` rule 1 and `dev/governance/rules/defect-root-cause.md`, with its generated `.claude/rules` and `.cursor/rules` copies. The owner approved decision cards CI-4 (reading, including this sentence), CI-5 ("within one merge" becomes "within one burst") and CI-6 on 2026-11-21. That approval covers the change, not this text: the text merges only on the owner's approving review at this head (the code-owner rule).

## Red checks

none

## Forward-carry

none

## Friction

none
