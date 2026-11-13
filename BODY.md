Hotfix (triage seat triage-1113, proposal T4): `update_pr.sh` never re-rendered a body's generated figure blocks, so the body it handed on named a head the pull request no longer had and the pre-PR body check refused "figure-block scope-line names another head" (pull requests 3512, 3531, 3534; earlier 3510, 3511). Two paths carried it: the moved-head path (merge of the code sha, of main and the own-row commit move the head, the body is pushed as written) and the body-only path (`HPO_UPDATE_BODY_ONLY`, the relay's handoff arm: the block names the authored code head, the live head is a merge of main, `body_patch.sh` refuses every pass).

Fix: `update_pr.sh` gains `upd_figures`, which runs the existing `tools/pr/figure_block.py refresh` (no second renderer, as `open_pr.sh`'s `op_figures`) at the head the run will push or patch: before `app_push.sh` on the moved-head path, before `body_patch.sh` on the body-only path. A failed refresh calls `pr_refuse` and pushes or patches nothing; a body with no figure block never reaches it. The alternative of patching only the moved-head path lost: the relay's body-only path is the one that recurred on every pass.

## Head

`80efc75a32c24956ba2598c4a7d936f6832e2abf`: the code head all figures below were measured at.

## Mutation proof

`pr_args.sh --self-test` arms, each new predicate line tagged: deleting the `# mut:updfig1` line (moved-head refresh) turns the arm "mutant mut:updfig1" into a push refused with "figure-block scope-line names another head"; deleting the `# mut:updfig2` line (body-only refresh) turns "mutant mut:updfig2" into a `body_patch.sh` refusal naming another head. Each mutant line removed is exactly the merge-base behaviour, so these two arms are also the refusal reproduced at the merge base on a fixture body, gone at the head (arms "a moved head with a figure block pushes a body whose block names the new head" and "a body-only run over a block naming the code head patches a body naming the live head" pass).

## Null control

An update of a pull request whose body has no figure block runs as before: the arms "null control: a body with no figure block never reaches the refresh and is pushed as before" and "…a body-only run over a body with no figure block never reaches the refresh" pass (the refresh stub records every call; none occurs). A failing refresh refuses on both paths and pushes or patches nothing (two arms).

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test` at the head: last line "pr_args self-test: 251 checks, 0 failed"; the same command at the merge base (f9a19d7bd4): 243 checks, 0 failed (the 8 added are the new arms).
- `python3 -I tools/ci/selftest_scope.py record --step update-pr` on Linux at that merge base, written by union: every file, probe, dir and git entry of the committed update-pr step is still covered by the recorded one (checked by script against `git show HEAD:tools/ci/selftest_closures.json`); the only addition is the probe dev/programme/delivery/5.md. The scope check's full-job summary line (`selftest_scope.py check --traces`) was not produced: it needs a traced run of every step, which this container did not run; CI's drift step prints it.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py`: ALL ENTITY CHECKS PASSED.

<!-- figure-block: scope-line mb=f9a19d7bd4016ad34dee4c170c31da8f8ea27921 head=80efc75a32c24956ba2598c4a7d936f6832e2abf -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
