Hotfix (triage seat triage-1113, proposal T4): `update_pr.sh` never re-rendered a body's generated figure blocks, so the body it handed on named a head the pull request no longer had and the pre-PR body check refused "figure-block scope-line names another head" (pull requests 3512, 3531, 3534; earlier 3510, 3511). Two paths carried it: the moved-head path (merge of the code sha, of main and the own-row commit move the head, the body is pushed as written) and the body-only path (`HPO_UPDATE_BODY_ONLY`, the relay's handoff arm: the block names the authored code head, the live head is a merge of main, `body_patch.sh` refuses every pass).

Fix: `update_pr.sh` gains `upd_figures`, which runs the existing `tools/pr/figure_block.py refresh` (no second renderer, as `open_pr.sh`'s `op_figures`) at the head the run will push or patch: before `app_push.sh` on the moved-head path, before `body_patch.sh` on the body-only path. A failed refresh calls `pr_refuse` and pushes or patches nothing; a body with no figure block never reaches it. The alternative of patching only the moved-head path lost: the relay's body-only path is the one that recurred on every pass.

Repair round (review blocked 5d2c0a30, introduced-red on the instrument-self-tests step "Show the PR updater (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures"): `pr_args.sh`'s self-test copied each program under test from the live checkout (`$src`) at every arm. In that job `update_pr.sh --self-test` runs in the background while the tick-loop step's `tick_loop.sh --self-test` moves the job's checkout onto origin/main, so every arm after the move copied main's `update_pr.sh`, which has no `upd_figures`: exactly the five arms that need it failed, while the mutant arm and the two null controls (which main's copy also satisfies) passed. The fix: the self-test now copies its programs from a snapshot taken once at fixture time, holding exactly the files its copy-in loops name plus `roster_lib.py` (which `pr_cap.py` loads from beside itself); all ten are already in the update-pr step's recorded closure, so its read set does not grow. The underlying trap (a step that moves the job's checkout) is PR #3520's to cure; this change makes this suite's verdict independent of it.

## Head

`b161a5553f540a7cc561640d91b7b05a4457387e`: the code head all figures below were measured at. It carries the previous code head `80efc75a32c24956ba2598c4a7d936f6832e2abf` plus three commits, all to `tools/audit/seat/pr_args.sh`'s self-test (the snapshot, narrowed to the programs under test, and `roster_lib.py` in it). No history was rewritten.

## Mutation proof

`pr_args.sh --self-test` arms, each new predicate line tagged: deleting the `# mut:updfig1` line (moved-head refresh) turns the arm "mutant mut:updfig1" into a push refused with "figure-block scope-line names another head"; deleting the `# mut:updfig2` line (body-only refresh) turns "mutant mut:updfig2" into a `body_patch.sh` refusal naming another head. Each mutant line removed is exactly the merge-base behaviour, so these two arms are also the refusal reproduced at the merge base on a fixture body, gone at the head (arms "a moved head with a figure block pushes a body whose block names the new head" and "a body-only run over a block naming the code head patches a body naming the live head" pass).

The snapshot's own mutant is the previous code head, which is this head with the snapshot removed: `bash tools/audit/seat/update_pr.sh --self-test` from a clean clone, its checkout moved (`git checkout --detach`) to origin/main `cfa868394685dbb2360844aec43d7a8cac4736ab` once pr_args' arms start, as the tick-loop step moves it in CI, gives at `80efc75a32` "pr_args self-test: 251 checks, 5 failed", the five FAIL rows identical to CI job 131858573499's; at `b161a5553f` the same run gives "pr_args self-test: 251 checks, 0 failed". `mutant_run.py --diff` reads only added Python lines; this diff adds none, so it has no mutant to apply (rc 0, empty).

## Null control

An update of a pull request whose body has no figure block runs as before: the arms "null control: a body with no figure block never reaches the refresh and is pushed as before" and "…a body-only run over a body with no figure block never reaches the refresh" pass (the refresh stub records every call; none occurs). A failing refresh refuses on both paths and pushes or patches nothing (two arms). For the snapshot: with the checkout left in place, the suite's verdict is unchanged: `bash tools/audit/seat/pr_args.sh --self-test` from a clean clone of `b161a5553f` gives "pr_args self-test: 251 checks, 0 failed".

## Figures

- `bash tools/audit/seat/update_pr.sh --self-test` from a clean clone of `b161a5553f`, checkout moved to origin/main `cfa8683946` mid-run: "delivery_row self-test: 6 checks, 0 failed", "pr_args self-test: 251 checks, 0 failed"; the same at `80efc75a32`: "pr_args self-test: 251 checks, 5 failed" (the five rows of the blocked CI step).
- The rest of that background chain from a clean clone of `b161a5553f`, in the job's order: `open_pr.sh --self-test` (its tally lines "delivery_row self-test: 6 checks, 0 failed" and "pr_args self-test: 251 checks, 0 failed", rc 0), then `pr_args.sh --self-test` ("251 checks, 0 failed", rc 0).
- `python3 -I tools/ci/selftest_scope.py record --step update-pr` on Linux at the merge base f9a19d7bd4, written by union: every file, probe, dir and git entry of the committed update-pr step is still covered by the recorded one; the only addition is the probe dev/programme/delivery/5.md. The snapshot's ten files are each listed in that step's `files`.

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

## Red checks

- instrument-self-tests, step "Show the PR updater (delivery_row.sh's and pr_args.sh's self-tests) refusing its own fixtures", red at `5d2c0a30ec65f2d4d4f5976ee50937737e19c089` (job 131858573499, "pr_args self-test: 251 checks, 5 failed"). Cause: the self-test copied the programs under test from the live checkout at every arm, and the job's tick-loop step moves that checkout onto origin/main while this background self-test runs, so the five arms that pin `upd_figures` ran main's `update_pr.sh`. Process state: the cheaper detector existed and was run, but not in the job's shape: the fixer's and reviewer's local `pr_args.sh --self-test` runs (251 checks, 0 failed, about 5 minutes) left the checkout still, so the gap was host parity with the job's step order, not a missing check. Countermeasure: the snapshot in this change makes the suite immune to a moved checkout, and the same suite run locally with the checkout moved mid-run (the reproduction in Figures, about 6 minutes) is the detector that would have caught it before push; the general cure for every step after the tick-loop step is PR #3520.

## Forward-carry

none

## Friction

none
