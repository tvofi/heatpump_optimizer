R10-HOTFIX-SWEEP-TOKEN-ACTOR. `gate-sweep.yml` triggers on `workflow_run` of CI, and GitHub starts no workflow from an event its `GITHUB_TOKEN` caused: a ci.yml run whose `actor` is `github-actions[bot]` (a token push's `pull_request` run that `hpo-runs` approves, a `github.token` dispatch) never fires a sweep, on any attempt. An edit run's gate that deferred to such a run (`gate.py` `deferral`) stays red until a person re-runs it. Fix: ci.yml's `sweep-self` job (`needs: gate`, `if: ${{ !cancelled() && github.actor == 'github-actions[bot]' }}`, `actions: write`) runs `gate.py --sweep --run ${{ github.run_id }}` from the base's restored `tools/ci/*.py`; `tools/ci/sweep.py` gains the self-call arm (caller = `GITHUB_RUN_ID`): settle never waits on the calling run (still `in_progress`) or on another gate still judging, a `sweep-self` job is never a source, and a red gate whose run is busy past its gate is polled to the run's completion, because GitHub refuses a re-run inside a running run. The RCA lands in `dev/audit/rca/R10-RCA-SWEEP-TOKEN-ACTOR.md` (cause, process state (c), cost table).

Alternatives: dispatching ci.yml with an App token covers the dispatched runs only; the approved `pull_request` runs of token pushes keep the bot as actor whatever approves them. Rejected. An earlier cut of the self-call arm counted a run concluded once its gate and every job but `sweep-self` completed; its mutant survived the self-test and, read in workflow_run mode, it stopped polling a run busy only with its own `sweep-self`, which `judge` then leaves: replaced by the caller-only exclusion above, whose every predicate is killed below.

Departure from the brief, raised: the brief says `sweep-self` restores "the same programs as `refresh`" (`github.event.pull_request.base.sha`). `refresh` never runs on `workflow_dispatch`, and a bot dispatch is one of the two token-actor shapes, so `sweep-self` restores as `gate` does: `base.sha`, else `origin/<inputs.base>`; with neither (a bot push to main, a merge group) it runs nothing rather than the head's own programs under `actions: write`. Consequence of the pinned copy: a PR whose base predates this merge runs the old `sweep.py`, whose settle waits the 600 s bound on the calling run and then re-runs the same deferral (`settle`'s loop ends at the bound and judges): late, not wrong.

## Head

26ebdd09dde9ad3d459ae73361e4c2f6d5d4746a, cut from `origin/main` at 9b1bb58db713a8a13148f98148fa8eb4fd796980.

## Mutation proof

Each production predicate of the self-call arm deleted or inverted in `tools/ci/sweep.py`, `python3 -I tools/ci/sweep.py --self-test` run, file restored (`cmp` against the saved copy):

- `r["id"] != self.caller` dropped from settle's `finishing` -> `FAIL sweep-self: called from inside V (in_progress, gate green), it re-runs the edit gate that deferred to V, without polling`; `FAIL sweep-self null: a red gate judged after V's gate concluded is final; V's running sweep-self is no source`; `FAIL sweep-self: an edit run busy only past its gate is polled from inside V, then its deferral re-run` (3 failed).
- `judging` dropped from settle's break -> `FAIL sweep-self: a gate still running elsewhere is not waited on from inside V (its completion sweeps)` (1 failed).
- `judging = self.caller == run_id and any(` to `or any(` -> `FAIL sweep-self null: the workflow_run sweep polls that gate as before`; `FAIL sweep-self: an edit run busy only past its gate is polled from inside V, then its deferral re-run`; `FAIL settle: a gate still running is polled, then the deferral it leaves red is re-judged` (3 failed).
- `SELF_JOB` dropped from `sources` -> `FAIL sweep-self null: a red gate judged after V's gate concluded is final; V's running sweep-self is no source` (1 failed).
- the green branch's busy-run poll arm made `elif False` -> `FAIL a red gate in a still-running run is not re-run while it runs (GitHub refuses it): polled, left at the bound`; `FAIL a red gate whose run was still running (its own sweep-self) is re-run once the run completes` (2 failed).
- caller detection made `caller=None` -> 4 failed (the three self-call arms and the gate-still-judging arm).

ci.yml's job, by `tests/entities.py`'s CI umbrella plants (each a mutant of ci.yml the reader must name): `sweep-self on every actor`, `sweep-self on the triggering actor`, `sweep-self skipped on a red gate`, `sweep-self before the gate`, `sweep-self on another run's id`, `sweep-self keyed on the exit code`; `plants the reader missed=[]` at the head. The first run at the head missed `sweep-self on another run's id`: its replace matched `cancel-superseded`'s identical `RUN_ID` line first, so the plant left `sweep-self` untouched; re-anchored on `sweep-self`'s step.

## Null control

- Failing test first: with only the interface added (`SELF_JOB`, `main(..., env=)`), the new arms at the merge base's behaviour: `sweep self-test: 77 checks, 5 failed` (the two busy-run arms, the self-call re-run, the self-call no-source null, the gate-still-judging arm). The sixth arm, `an edit run busy only past its gate is polled from inside V`, was added with the final rule.
- Null arms that pass at both ends: `sweep-self null: the workflow_run sweep of the same head (V completed, sweep-self skipped) re-runs alike`; `sweep-self null: the workflow_run sweep polls that gate as before`; every pre-existing arm (`sweep self-test: 78 checks, 0 failed` at the head; `gate self-test: 81 checks, 0 failed`, which drives `sweep.main` over the #3282 recording).
- `sweep-self`'s `if:` is read per modelled event (`_CI_EVENTS`) and per actor: true only for `github-actions[bot]`, false for `hpo-author[bot]`, `hpo-runs[bot]` and `tvofi`, so an App- or human-actor run skips it and `workflow_run` alone sweeps it: no double sweep (and one would be harmless: `judge` skips green gates, `settled` bounds re-runs).
- `tests/entities.py` at the merge base's checks with this ci.yml: `2 of 2707 ENTITY CHECKS FAILED`, the edited-jobs listing and the D11-s1-03 null control, each naming the unlisted `sweep-self`; at the head `0 of` the same count.

## Figures

- Finder harness, before (the merge base: no `sweep-self` exists, so coverage is gate-sweep's alone): `python3 -I dev/audit/harnesses/r10_sweep_token_actor.py census --since 2026-11-09T22:21:00Z --until 2026-11-10T01:19:00Z` -> `RESULT census other=37/37 token=0/2 gate_sweep_runs=184 unread_logs=0`, uncovered 42711494947 and 42711632468 (#3351). Rule: ci.yml runs created in the window, completed, with a pull request; covered when a gate-sweep run's `sweep` job log carries `RUN_ID: <id>` or the run's own `sweep-self` ran. The root-cause seat's 61 and 3 count completions in the window; this census counts creations, so its totals are smaller and its split is the same.
- `python3 -I dev/audit/harnesses/r10_sweep_token_actor.py census --since 2026-11-09T14:36:00Z --until 2026-11-09T14:37:00Z --slack-min 660` -> `RESULT census other=0/0 token=0/1 gate_sweep_runs=371 unread_logs=0`: #3358's 42636336860 uncovered across every gate-sweep run of the next 11 h, tvofi's re-run (attempt 2) included.
- Harness null control: `python3 -I dev/audit/harnesses/r10_sweep_token_actor.py --self-test` -> `RESULT self-test checks=5 failed=0` (a log naming another run, a skipped `sweep-self` and another job that ran each read uncovered).
- After: owed once this merges and a token-actor run completes at a live head; the same census over a window after the merge reads `token=<n>/<n>`. The head cannot read it: `workflow_run` and `sweep-self` run main's and the pinned base's copies, never this branch's.
- Cost table (31 deferral reds to token-actor deciders, 15 with the decider green at a live head, 0 re-run by the bot, 13 by a person, 2 stood until the head moved, 9 heads on 6 PRs, about 1,088 head-minutes): the root-cause seat's measurement with its rule in the RCA; its working directory is host-local and is not re-derived here.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> `MODE: FULL` (`.github/workflows/ci.yml changes the gate itself`): CI runs every script; run here: `tests/entities.py`, `tools/ci/sweep.py --self-test`, `tools/ci/gate.py --self-test`.

## Red checks

none

## Forward-carry

none

## Friction

none
