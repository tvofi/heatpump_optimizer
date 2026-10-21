Part of #2238 (D7-s2-01, round 10 D7/s2). The finding: `_observe_frequency` folded every defrost interval into the
kW-per-Hz map while every other learner refused the same interval. Defrost was decided by two divergent predicates:
`_freq_fold_blocked` refuses cooling, distorted draw and pinned-input reasons and never `defrosting`, so the map learned
8 folds over 8 defrost intervals; and `FrequencyWatchdog`'s own contract calls a pump pausing for a defrost "an operating
point at rest", while the caller computed `active` without asking.

The fix gives the fact one owner. `freq_control.defrost_interval` is the predicate, in the module the map and the
watchdog live in, and `_observe_frequency` consults it for both readings: the map's fold and the watchdog's `active`.
A defrost interval is now neither evidence for kW-per-Hz nor evidence about the write path.

Scope note, stated plainly: D7-s2-01's report also names `pump_offline` as a contaminant of the same map. This group's
brief scopes the pull request to defrost, so the offline arm is measured (Figures) and carried, not closed here. It is
the same seam, not a new one.

Two in-seam cleanups pay the coordinator class span. The watchdog's mode guard was a second copy of `_freq_mode`'s
predicate: `source == FREQ_SOURCE_NUMBER and configured == FREQ_MODE_CONTROL and not self._freq_fallback` is exactly
`_freq_mode() == FREQ_MODE_CONTROL`. And `_freq_view` asked "is this install configured" in two spellings
(`mode != "unconfigured"` and `source is not None`, the same fact) while wrapping both ternary values across four lines;
one spelling now answers, and the view no longer re-derives it.

## Head

`fd9bcf6f1210e5fb52ec2c90f18f431e3fc5c652`: the PR head `3ce0b78f8`, a merge of `origin/main` `df6ca4bc6858` (delivery
rows only), and `fd9bcf6f1` recording the structure budgets this branch earned. Every figure below is taken at this head
(2026-10-21, `date -u` 08:34Z) unless a line names another one. `git diff --quiet 3ce0b78f8 HEAD -- custom_components
tests/features.py tests/entities.py tests/mutation_ledger` exits 0, so CI's `mutation` run at `3ce0b78f8`, cited below,
measured the same production code, checks and ledger.

## Mutation proof

The mutant deletes the two production terms the fix adds — `not defrosting` from `watch_active` and `or defrosting` from
the map's fold guard — in a scratch worktree at this head, runs `PYTHONPATH=tests/hastub python3 tests/features.py`, and
restores. The run ends `EXIT=1`:

```
  FAIL a defrost interval never teaches the frequency map  [the fold would learn a ratio that is not a kW-per-Hz point, and the decile-keyed map is inherited when the user later switches to control]
  FAIL defrost ticks never stand control down  [a defrost is not a write path that stopped listening]
2 of 4271 FEATURE CHECKS FAILED
```

The third added check is the null control and stays green under the mutant: `null control: a non-defrost interval still
folds`. After the last restore, `git status --short` in the scratch worktree prints nothing (0 lines).

### The two bound variants

`_observe_frequency`'s `CMP_BOUND` site has two variants. One check in `tests/features.py`, `the watchdog's two bounds:
the floor is exclusive, the minimum inclusive`, feeds each bound its exact input (0.05 kW, and a reading exactly at the
entity's minimum). Applied alone at this head and restored, each variant fails it:

| Variant | Edit | Result |
|---|---|---|
| `CMP_BOUND` a | `self._commanded_power() > 0.05` -> `>= 0.05` | `1 of 4271 FEATURE CHECKS FAILED`, that check (`floor -> [True], minimum -> [True]`) |
| `CMP_BOUND` b | `reported >= hz_min` -> `>` | `1 of 4271 FEATURE CHECKS FAILED`, that check (`floor -> [False], minimum -> [False]`) |

## Null control

The finder's harness on the unmodified merge base `df6ca4bc6858` reads `freq_map_clean_folds=8`,
`freq_map_defrost_folds=8`. At this head the clean arm still reads 8 and the defrost arm reads 0, so the harness
separates the two arms only where the fix is. `tests/features.py` carries the same arms as checks: a `defrosting=False`
interval folds (green under the mutant above), and without the fix the divergent defrost arm trips the watchdog.

The harness's `--perturb` arm (patch `_freq_fold_blocked` to refuse defrost) is vacuous at the head: the fold reads the
predicate before the gate. The harness's learner table's `freq_map` column still reads INGEST on the defrost row for the
same reason: the column asks `_freq_fold_blocked` alone, which this diff deliberately leaves unchanged. The finding stays
measurable at the head through the mutation proof: deleting the fix's terms takes the defrost arm back to folding.

## Figures

- Merge base `df6ca4bc6858`: `freq_map_clean_folds=8`, `freq_map_defrost_folds=8`, `cop_gate_on_defrost='defrosting'`,
  `pump_offline.learners_ingesting=1`. Head: `freq_map_clean_folds=8`, `freq_map_defrost_folds=0`,
  `cop_gate_on_defrost='defrosting'`, `pump_offline.learners_ingesting=1` (`freq_map` = INGEST). Command at both ends:
  `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s2/learner_gates.py`; `shasum` of the harness =
  `5b77f8743adbc990a2277046e9cdbb83c4d3a537` at both ends.
- `python3 tests/structure.py` at the merge base `df6ca4bc6858`: `class_excess_loc=18299`, `max_class_loc=8541`,
  `seam_cut_total=718`, `STRUCTURE RATCHET PASSED` with no improvement line (the control: the gain is not main's). At
  this head before `fd9bcf6f1`: `18297`, `8539`, `717`, `3 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`, exit 2.
  `python3 tests/structure.py --record` re-recorded them (reason in the commit message), and the ratchet then reads
  `STRUCTURE RATCHET PASSED`.
- `Architecture score: dS +0.0000 NULL`: `python3 tools/audit/archscore/score.py --diff origin/main`.
- `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`: `python3 tests/closure.py select --diff $(git merge-base origin/main
  HEAD) --workdir "$D"` (keyed on the mode line, not the count). Locally run from `scope.run`: `tests/features.py`,
  `tests/entities.py`, `tests/structure.py` (below); the heavy scripts are CI's.
- `ALL 4271 FEATURE CHECKS PASSED`: `PYTHONPATH=tests/hastub python3 tests/features.py` at this head.
- `ALL 2361 ENTITY CHECKS PASSED`: `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head.
- `CI PREDICT: no closures or fast red predicted against df6ca4bc6858`: `python3 tools/pr/ci_predict.py --base
  origin/main` at this head.
- CI's `mutation` at `3ce0b78f8` (job 119088425250): `MUTATION TABLE PASSED`, `PIN RE-VERIFICATION: 4 reproduced, 0 not
  reproduced, 0 not re-verified`, `0 survivor(s) of 4 evaluated = 0.0%, cap 20.0%`, each of the four sites `killed by
  tests/features.py`, and the comment-only null control `coordinator.py:507 NULL_COMMENT survived every driver`. Its log
  prints no `INCONCLUSIVE` or `REFUSED` verdict: every driver line reads `LAZY AND NEVER RUN` or `DEFERRED AND NEVER RUN`
  because no mutant survived the drivers that ran (`grep -E 'INCONCLUSIVE|REFUSED'` on the log returns only those
  explanatory lines). The production code, checks and ledger are identical at this head (Head).
- The registry row for `defrost_standoff` passes in `tests/entities.py` (above). Its shape pins a decision-context read
  of `*.defrosting`: direct, `bool(...)`, `not` and walrus, as the reviewer planted each at `de28f656`. A copy to a local
  first (`d = signals.defrosting; if d:`) is **not** matched, so the barrier pins the flag's read, not a local derived
  from it. The one other read the rule returns is dispositioned at
  `coordinator.py::HeatPumpOptimizerCoordinator._learning_frozen`, the plant-wide gate that owns the reason string every
  learner is frozen with and which the map deliberately ignores for external heat (#781).

## Architecture score

`dS +0.0000 NULL`, no gate metric rose: `python3 tools/audit/archscore/score.py --diff origin/main` at this head.

## Unpinned sites

None added: `tools/pr/ci_predict.py --base origin/main` predicts no red, and CI's `mutation` at `3ce0b78f8` re-verified
all four of the diff's sites pinned. Each is killed by `tests/features.py`:

- `coordinator.py` `_observe_frequency` `CMP_BOUND` (both variants): the bound check above; ledger row
  `tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._observe_frequency.CMP_BOUND.e2a6e890.json`.
- `coordinator.py` `_observe_frequency` `GUARD_OFF`, the mode guard: with it off the watchdog never runs and `persistent
  divergence stands control down to latch` fails.
- `coordinator.py` `_freq_view` `GUARD_OFF`, the view's configured guard: with it off a configured view loses `source`
  and the configured-view checks fail.
- `freq_control.py` `defrost_interval` `RETURN_DEL`: the predicate returns None, which is not a defrost, and `a defrost
  interval never teaches the frequency map` fails.

## Red checks

Every check that concluded `failure` on this pull request's heads (`check-runs` API per commit; `cancelled` runs were
superseded by a newer push and are not reds):

- `fast (3.14)` (required), red at `3ce0b78f8`: `tests/structure.py` printed `3 STRUCTURE BUDGET(S) IMPROVED AND NOT YET
  RECORDED` and exited 2. Main's own ratchet passes with no improvement line (Figures), so the gain is this branch's:
  the recarry onto `main` stacked main's re-recorded table under this branch's payment and left three rows below the
  table. Repaired at `fd9bcf6f1` by `--record`, reason in the commit. Cheaper detector: `python3 tests/structure.py`,
  seconds, already owed before every push by fixer.md step 5; the miss was running it before the recarry and not after.
  No new countermeasure is owed: the detector exists and costs seconds; it was not re-run on the recarried head.
- `pr-contract`, red at `3ce0b78f8`: the body did not name `fast (3.14)` under `## Red checks`. This section answers it.
  Cheaper detector: `tools/pr/prepr.sh` on the body, which runs the same check locally and was run before this handoff.
- `mutation` (required), red at `4f2ac0cac`, `de28f656b`, `f157063b2` and `f8c523f09`: `2 of them added by this diff`
  unpinned (the two `CMP_BOUND` variants), with the survivor rate over its 20% cap. `mutation_table --pin-killed`
  measured both surviving every driver in play, so this branch added their killer (the bound check, Mutation proof)
  rather than a triage. CI's `mutation` is green at `3ce0b78f8` with 0 survivors of 4 (Figures). Cheaper detector:
  `tools/pr/ci_predict.py --base origin/main`, source-only and seconds, which prepr step 6d runs; it predicts no red at
  this head.
- `nightly-status`, red at every head: it grades `main`, not this branch — the nightly `slow` lane's `loop_cpu_ratio`
  over budget, fixed by the separate `r10-replay-cap` work. This diff touches nothing it reads. Cheaper detector: none
  owed here; the red is main's.

## Forward-carry

- The `pump_offline` arm of D7-s2-01: `_freq_fold_blocked` does not refuse a freeze reason of `pump_offline`, so an
  install whose online flag reads False while its frequency entity still reports a number folds that interval. Same
  seam and same class as this fix, outside this group's stated scope (defrost), measured at both ends by the harness's
  `pump_offline` row (`freq_map` = INGEST). A later group's carry lands in
  `dev/programme/rosters/wave-r10-groups.json`; the orchestrator assigns that group, and `#2238` stays the open record on
  the Delivery-status table until it does. Carry: #2238

## Friction

`none`
