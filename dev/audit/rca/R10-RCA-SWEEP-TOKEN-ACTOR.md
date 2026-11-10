# R10-RCA-SWEEP-TOKEN-ACTOR: a deferral red at a live head that no sweep re-judges, because its decider's run was the token's

**Defect.** An edit run's `gate` defers at once to a busy run at its head
(`tools/ci/gate.py` `deferral`) and leaves itself red; `gate-sweep.yml`
re-judges it when the deciding run completes. When the decider's `actor` is
`github-actions[bot]`, no sweep ever fires, and the red stands at the head
until a person re-runs it or the head moves.

**Cause.** `gate-sweep.yml` triggers on `workflow_run: workflows [CI] types
[completed]`. GitHub starts no workflow from an event its `GITHUB_TOKEN`
caused, and a `workflow_run` event's actor is the completed run's `actor`
(the account that caused the run), not a re-run's `triggering_actor`. So
these ci.yml runs never fire a sweep, on any attempt:

- the `pull_request` runs a token push leaves `action_required` (the
  merge-main bot, the autofix jobs), which `hpo-runs` approves: approval
  changes the triggering actor, not the run's actor;
- the ci.yml dispatches made with `github.token`: `merge-main.yml`'s
  dispatch, the three in `tests.yml`, and `tools/ci/sweep.py`'s own `fresh`.

**Evidence** (the root-cause seat rca-edit-gate, orchestrator s13,
2026-11-10; re-measured in the fix's pull request by
`dev/audit/harnesses/r10_sweep_token_actor.py census`, which classes each
ci.yml completion by actor and checks if a gate-sweep run's `sweep` job
log names it with `RUN_ID: <id>`, or a `sweep-self` job of its own ran):

| window (UTC) | other-actor completions covered | token-actor completions covered |
|---|---|---|
| 2026-11-09 22:21 to 2026-11-10 01:19 | 61 of 61 | 0 of 3 (#3351's 42711494947 and 42711632468; #3358's 42636336860, which tvofi re-ran: still no sweep) |

**The same cause one hop removed: #3400 at 7326025c.** The edit run
42735879081's gate deferred at 01:38:20Z to the code run 42734628856, whose
actor is the App. That run's completion did fire a sweep (gate-sweep run
42738574607, its log naming `RUN_ID: 42734628856`), which took the stale-pin
arm: it dispatched a fresh ci.yml run with `github.token` and printed `run
42735879081 left to this sweep's dispatched run`. The dispatched run,
42738604293, has the bot as actor: its gate went green at 02:33:04Z, its
completion fired no sweep, and its green `gate` check, in a check suite of
its own, replaced no other run's red. The red stood until a person re-ran it
(gate green 02:52:55Z). So the stale-pin arm's premise, that the dispatched
run re-judges the head, held for the gate it ran and not for the red it was
left. The countermeasure covers it: the dispatched run's own `sweep-self`
re-runs each stale red it was left, once (`sweep.py` `fresh`).

**Control.** A deferral red whose decider is an App-actor run is re-run by
the sweep within a minute of the decider's gate going green: #3399 at
70461316, decider gate green 01:25:24Z, edit gate re-run 01:26:10Z.

## Cost

Rule: over 2026-11-08 06:23Z to 2026-11-10 01:30Z, every gate red whose
annotation is the deferral and whose deferred-to runs were all token-actor
runs; of those, the ones whose decider went green while the head was still
live; per such head, the minutes from the decider's gate going green until
the red was re-run or the head moved.

| measure | value |
|---|---|
| deferral reds deferring only to token-actor runs | 31 |
| of them, decider green while the head was live | 15 |
| re-run by the bot | 0 |
| re-run by a person (tvofi identity) | 13 |
| stood until the head moved | 2 |
| heads / pull requests | 9 / 6 |
| head-minutes of false red | about 1,088 |

The cost table is the root-cause seat's measurement; its working directory
is host-local, so this record carries the rule and the figures, and the
coverage half is the half re-derivable from the tree's harness.

## Process state: (c)

The process existed and was followed: a gate defers at once and holds no
runner, and the sweep re-judges it on its decider's completion. It did not
produce the intended result, because the trigger it rested on is not
delivered for one class of run (`actor` = the token). Not (d): the
GITHUB_TOKEN rule predates the sweep; the design never held for these runs.
Not (b): no seat skipped a step: the deferral and the sweep both ran as
written for every other actor.

## Countermeasure

ci.yml's `sweep-self` job: `needs: gate`, `if: ${{ !cancelled() &&
github.actor == 'github-actions[bot]' }}`, `actions: write`, running
`gate.py --sweep --run ${{ github.run_id }}` on the base's programs.
`tools/ci/sweep.py` learns the self-call (the caller's `GITHUB_RUN_ID` is
the swept run): settle never waits on the caller, which is still
`in_progress`, nor on another gate still judging (that run's completion
sweeps); a `sweep-self` job is never a source; and a red gate whose run is
still busy past its gate is polled to the run's completion, because GitHub
refuses a re-run inside a running run. Where V is the stale-pin arm's fresh
dispatched run and green, each stale red left to it is re-run once instead of
left: the re-run's own completion settles, where no green fresh judge is V,
so it is left there and the arm cannot loop.

Rejected: dispatching ci.yml with an App token. That covers the dispatched
runs, not the approved `pull_request` runs of token pushes, which carry the
bot as actor whatever approves them.

**Cost test** (wall-clock, per occurrence). Standing cost: on every run
whose actor is not the bot the job is skipped by its `if:` and takes no
runner; on a token-actor run, one job of a checkout, a restore and the
sweep's API reads (no poll from settle; a poll only for a red gate whose
run is still finishing, bounded at 600 s as gate-sweep's). Defect cost:
about 1,088 head-minutes over the 43-hour window above, 15 occurrences, each
a person's re-run or a head left red. The standing cost is below one
occurrence's mean (about 72 head-minutes) at any recurrence rate the window
shows, so the countermeasure is built.

**Detector shown to detect.** `tools/ci/sweep_selftest.py`'s sweep-self
arms fail at the merge base (the settle poll waits on the calling run to the
600 s bound; a running `sweep-self` reads as a source) and pass at the fix;
`tests/entities.py`'s CI umbrella check reads `sweep-self`'s `if:` per event
and per actor, with plants for each property.
