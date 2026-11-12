Adds the report-only convergence scorecard as a beat row (R10-MACH-SCORECARD): `tools/audit/seat/scorecard.py` computes A_gate, A_run, Y_rev, M_first, Y_train, H, S, E, C and K by the study's section-7 rules; the `scorecard` row of `beatd.jobs.json` runs it daily into `S/beatd/scorecard.txt`. No gate, exit code or digest wake changes. An input the row cannot read prints `unread`, never a number. The rules live in the code and in `instruments/scorecard.py.md`. Repair round 2: the sweep template declared the `sweep_record` overlay row without rendering it; it is now an optional `--sweep-record` flag, rendered in the sweep's step (4b) beside the `scorecard` row, with a self-test case.

## Head

`d322a7b693b759d8d3efe48ddac639d243b8eada` merges `origin/main` at `2b4515dc52821ad721225090d329c224dbddafae` (2026-11-12T13:02:21Z) into `1965559c0ce814ee36c37fce9b5d41f55ec3e5ef`, itself the merge of the authored code head `c77c5a836b396b67beddad333234fe5f7071494c`.

## Mutation proof

Scorecard mutants: one per predicate of `scorecard.py`, planted by `python3 -I tools/audit/seat/scorecard.py --self-test`, each killed by a named case (round 1's six survivors stay killed; the self-test ends "ok (with mutants)" at this head). For the repair: the new `sweep_render.py` case "sweep_record renders as one --sweep-record FILE, and none leaves the flag out" fails if the `OPTIONAL_FLAGS` entry is dropped (the render then refuses `unused: sweep_record`, the red the reviewer measured).

Unpinned survivor carried: `scorecard.py:127` mf_first_any_blocked, dismissed by the round 2 review as equivalent on the two-kind verdict grammar; not pinned.

## Null control

Red at the old head, run first: `python3 -I tools/audit/seat/sweep_render.py --self-test` died with `Refused: unused: sweep_record declared and never used by the sweep`. Green after the fix: `sweep_render self-test: 36 checks, 0 failed`. Scorecard lines keep their round 1 null controls.

## Figures

none

## Red checks

- `governance / instrument-self-tests`, step "Render the sweep template, and the policy re-read predicate": red at `1965559c0c`, green at the merge base. Cause: `sweep_template.md` declared `sweep_record` and the sweep body never used it, so `sweep_render.py --self-test` refused. Cheaper detector: that same `--self-test` (about one second), already the step's own command; the first round's scope selection omitted the step, though the PR touches `sweep_template.md`, its scope trigger. Repaired here and run green. The other self-test steps this diff reaches were run on this head: `beat_jobs.py`, `scorecard.py`, `policy_reread_check.py`, `selftest_wiring.py --check`, `selftest_scope.py --self-test`, all 0 failed.
- `tests / closures`: the `tests/entities.py` record moved rc 1 to rc 0; not re-derived here (no full derive off Linux); CI's closures job at this head is the check.

## Forward-carry

none

## Friction

scorecard: stale: the refresh scripts of the study, the FAMILY map (`yield.py`) and the sweep record that K counts are not in the tree, so the row reads `unread` until the orchestrator provisions them. Carry: dismissed: out-of-tree session inputs, named in instruments/scorecard.py.md
