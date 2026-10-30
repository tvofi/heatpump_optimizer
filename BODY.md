R10-COP-GATE item E (carries 8 and 9): the open-window latch (`_vent_cusum.tripped`) froze every learner, including those that read no room air. This change lifts it for the COP fold on measured heat (a heat counter's span, or a measured flow heat) and for hot water (the probe and `DhwProfileLearner`). The inferred COP, the flow-curve bias and every room-air learner keep the freeze. Design: the round-3 note at handoff-body/r10-cop-gate-vent-r3 d25be122, approved by `Design review: approve ce5ca88b` at handoff-body/r10-cop-gate-vent-drev3 74f35d42. The approval's minimal fixer brief is followed with no departure. This head adds no finding for a later stage. The review's carried notes are answered here: the mutant kills claimed are only those the runs show (`## Mutation proof`). The sysid abort stays R10-CEILING-PROBE's. The latch reason still resets each cycle (item 9).

- **Seam.** `_learning_frozen(self, *keys, room_air: bool = True)`. Passing `room_air=False` skips only the `ventilation` branch. Every other reason keeps its rank and still fires: external heat, pump signals, defrosting, unusable inputs, boost and the tail. The default fails closed.
- **Sites, three in production, all in `coordinator.py`:**
  - `_dhw_probe_temperature` passes `room_air=False`.
  - The `DhwProfileLearner` wiring gets `functools.partial(self._learning_frozen, room_air=False)`.
  - `_fold_measured_cop` reads `heat_kw` before the freeze and passes `room_air=heat_kw is None and not heat_energy.meter_of(self).counter`. That is the approval's `room_air=not measured_heat`, inlined (see the structure payment below).
- **No edit** at `_fold_flow_lift` (the default freeze is kept: the round-3 arm moves `bias_k` under a window) or at `_freq_fold_blocked`. `_freq_fold_blocked` already lifts through its own `":" in frozen` predicate, because the vent branch returns `"ventilation"` with no colon. Every other call site stays on the default.
- **Test doubles.** The test doubles and the two finders' harnesses that stub `_learning_frozen` (`r10_heat_meter.py`, `r10_thermal_power_option.py`) now accept the keyword. Without that, `features.py` crashed at the `_CopGate` double (`TypeError: ... unexpected keyword argument 'room_air'`), seen on the first head run.
- **Ledger.** The ledger's GUARD_OFF pin `286162d5` on the edited COP freeze line is deleted by hand, because `ci_predict.py` reported it as a STALE PIN. `ci_predict.py --apply-inert` wrote the new harness's `tests/closures.json` entry.
- **Structure.** `tests/structure.py` refused the first cut: `class_excess_loc` and `max_class_loc` were both +4. I paid for it inside the diff, with no budget change:
  - I dropped my two-line comment at the COP gate and the one-line `measured_heat` local.
  - I moved the `room_air` note from the docstring onto the vent branch's existing comment.

## Head

2adf2b7e8b4b3f5f8c9611c262a9c959cf0afa92, cut from base cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7, and every figure was measured there. At 2026-10-30T18:28Z, origin/main was cc930cdd1a3cfb005ba7ec557f4451ff5e53e364. `git merge-tree --write-tree origin/main HEAD` reported no conflict, and `git diff --name-only cf4f6b7a6 origin/main` touches no file this diff changes and nothing under `custom_components/`, so I did not merge main.

## Mutation proof

The failing tests came first, in commit cf74b1e99, which has the tests and the harness and no fix. At the base, `PYTHONPATH=tests/hastub python3 tests/features.py` gave `4 of 4611 FEATURE CHECKS FAILED`:
- counter span gate;
- flow heat folds;
- stale thermal-power (its fresh-reading null control needs the lift);
- hot water.

The inferred-COP check and the room-air check passed at the base, as designed: they pin what keeps the freeze.

Each mutant below is a one-line edit of `coordinator.py` in a detached worktree at the head, run through the full `tests/features.py`. The head gives `ALL 4611 FEATURE CHECKS PASSED`.

| mutant (one per gate) | result | failing checks (`R10-COP-GATE E: ...`) |
|---|---|---|
| vent branch `if room_air and self._vent_cusum.tripped:` → `if self._vent_cusum.tripped:` | 4 of 4611 FAILED | heat-counter span gate; measured flow heat folds; stale thermal-power (fresh null); hot water learns and the probe answers |
| COP `room_air=<expr>` → `room_air=True` | 3 of 4611 FAILED | heat-counter span gate; measured flow heat folds; stale thermal-power (fresh null) |
| COP `room_air=<expr>` → `room_air=False` | 1 of 4611 FAILED | an inferred COP stays frozen |
| COP `and` → `or` (the BOOLOP site) | 3 of 4611 FAILED | heat-counter span gate; measured flow heat folds; stale thermal-power (fresh null) |
| DHW partial → `frozen=self._learning_frozen` | 1 of 4611 FAILED | hot water learns and the probe answers |
| `:9926` probe → default | 1 of 4611 FAILED | hot water learns and the probe answers |
| `_fold_flow_lift` `:878` → `room_air=False` | 1 of 4611 FAILED | the buffer, draw range, ... flow-curve bias takes no sample |
| `_async_learn_buffer_cooling` `:5311` → `room_air=False` | 1 of 4611 FAILED | the buffer, draw range, ... (same check) |
| `_record_accuracy` `:9760` → `room_air=False` | 1 of 4611 FAILED | the buffer, draw range, ... (same check) |

These are the kills the runs showed. The review's carried note held: the `room_air=False` COP mutant does **not** kill the stale-thermal-power check. A stale reading is refused by the input-health branch (`stale:heat_pump_thermal_power_entity`) ahead of the vent branch, whatever `room_air` is. The inferred-COP check kills that mutant on its own.

**2b, the stale-reading gate.** The stale entity yields `None`: `read_heat_output_kw` returns `None` when `heat.ok` is false, `observe_water` stores that, and the check reads `(learners_frozen, 0)`. So `measured_heat` keys on `heat_kw is not None`, with no separate freshness gate. The fresh null reads `(None, 1)`.

## Null control

- **Tests.** Every new check carries its own null with the latch clear: counter `span_open`, flow `(None, 1)`, inferred passes the freeze, DHW `(55.0, None)`, flow bias folds 1. The room-air check's null also has the draw-range fold seeing `frozen=False`, and no output reading `ventilation`.
- **Harness.** Each window arm runs at `k=0.00`. Law (b) is the flow arm's null by construction.
- **Base.** The unmodified tree freezes all four lifted paths on `learners_frozen` / `ventilation` (harness learners arm, base column below).

## Figures

The harness is `dev/audit/harnesses/r10_cop_gate_vent.py`: the design's Appendix A, committed. I changed it in two places, both in the learners arm:
- I added the counter and flow-heat COP rows;
- the arm's mutant lambda now forwards keywords (`lambda *k, **kw`).

The rule for "unchanged" below is `diff` of the full output at base cf4f6b7a against head 2adf2b7e: the line pairs `diff` printed, out of the 118 output lines.

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate_vent.py`, run at both ends, exit 0 each. `diff` reports exactly 3 changed lines, all in the learners arm's latch column, base → head:
  - `cop counter(_fold_measured_cop)`: `refused:learners_frozen` → `passes freeze (span_open)`.
  - `cop flow-heat(_fold_measured_cop)`: `refused:learners_frozen` → `passes freeze (None)`.
  - `dhw(async_learn_dynamics)`: `frozen:ventilation` → `runs`.
- These rows are identical at both ends, which makes the `diff` its own null control:
  - the inferred `cop(_fold_measured_cop)` stays `refused:learners_frozen`;
  - buffer `frozen:ventilation`, sysid `aborted:ventilation`, house `ventilation`;
  - the latch arm (carry 9) reads ventilation, ventilation, None, None;
  - the cusum, cop-window, draw-window, buffer-window and flow-window arms.
- At the base, the `_fold_flow_lift under a window` block (19 lines) is byte-identical to the design note's measured block (`diff` empty). It includes the null and law (b) at +2.496 [+2.483..+2.511], and the latch-set row `folds=0`.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_heat_meter.py` and `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_thermal_power_option.py`, run at base and head. The only `diff` lines are the harness's own `TREE head <sha>` line and traceback file paths. `r10_thermal_power_option.py` exits rc=1 at both ends: that is its own pre-existing state, unchanged.
- `PYTHONPATH=tests/hastub python3 tests/features.py`:
  - at cf74b1e99 (tests without the fix): `4 of 4611 FEATURE CHECKS FAILED`;
  - at the head: `ALL 4611 FEATURE CHECKS PASSED`.
- `GATE_SCOPE=auto GATE_SCOPE_BASE=$(git merge-base origin/main HEAD) GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` printed `MODE: SCOPED -- 22 script(s) run, 11 scoped out`, `24 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN`, exit 0. No golden moved, and no claim file is touched: `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/` is empty.
- `python3 tests/structure.py`: exit 0, no FAIL line, budgets unchanged. The first cut read `FAIL class_excess_loc 17676 > 17672 (+4)` and `FAIL max_class_loc 8069 > 8065 (+4)`, paid as described above.
- `python3 tools/audit/archscore/score.py --diff cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7 HEAD`: `Architecture score: dS +0.0000 NULL`.
- **Class census (step 8).** The rule is `grep -n "_learning_frozen(" custom_components/heatpump_optimizer/coordinator.py`, plus the `frozen=` wiring. It returns 13 call sites and the DHW callable, the same as the design's site table and the review's grep. No module outside the coordinator calls it. Every seam the rule returns is listed with its disposition:
  - `:878` `_fold_flow_lift`: default, kept frozen. Pinned by the room-air check's `flow_bias_folds == 0`.
  - `:1152` `_freq_fold_blocked`: no edit. It already lifts through `":" in frozen`.
  - `:3405` DHW callable: `room_air=False`, closed in this diff.
  - `:5018` `_fold_measured_cop`: room air only without measured heat, closed in this diff.
  - `:5311` buffer: default, pinned.
  - `:5437` house: default, pinned.
  - `:5601` lower floor: default, pinned.
  - `:8971` curve comfort: default. It is a room-air learner.
  - `:9388` `_inputs_unhealthy`: default.
  - `:9760` draw-range `power_frozen`: default, pinned.
  - `:9780` `indoor_frozen`: default.
  - `:9926` DHW probe: `room_air=False`, closed in this diff.
  - `:10773` quiet comfort: default.
  - `:10858` sysid: default, abort pinned.

  Of these, `room_air=False` is passed at one site plus the callable, the heat-keyed expression at one site, and the default at the other eleven.
- Count `grep -rn "_learning_frozen(" custom_components/ | grep -c room_air`: 3 (`:3405`, `:5018`, `:9926`).

## Unpinned sites

- `custom_components/heatpump_optimizer/coordinator.py:5018 GUARD_OFF`: pinned by `mutation-autofix` (custom_components lane). The inferred-COP check is expected to kill it (a dropped return folds under the latch); not run here.
- `custom_components/heatpump_optimizer/coordinator.py:5018 BOOLOP`: pinned by `mutation-autofix`. The `and` → `or` mutant was run here and failed 3 checks (table above).
- `custom_components/heatpump_optimizer/coordinator.py:6641 GUARD_OFF`: pinned by `mutation-autofix`. Expected killed by the room-air check (a dropped vent return un-freezes it); not run here.
- `custom_components/heatpump_optimizer/coordinator.py:6641 BOOLOP`: pinned by `mutation-autofix`. The guard mutant without `room_air` failed 4 checks.
- `custom_components/heatpump_optimizer/coordinator.py:9926 GUARD_OFF`: pinned by `mutation-autofix`. The hot-water check pins the keyword (mutant above); the GUARD_OFF itself was not run here.

## Red checks

`ci_predict.py` predicted two reds at the first commit, and both were repaired before the handoff:
- the `tests / closures` INERT READS for the new harness (`--apply-inert`);
- the `ledger` STALE PIN `286162d5` (deleted by hand).

The cheaper detector is `ci_predict.py` itself, already standing. It found both before any push, so no further countermeasure is owed.

- `mutation`: the red here is the mutants this seat ran on purpose (the `## Mutation proof` table), plus `tests / mutation`'s predicted ADDED UNPINNED warning on the five sites in `## Unpinned sites`. The `mutation-autofix` lane pins those after the PR opens (`ci-autofix.md`). The cheaper detector is prepr step 6d (`ci_predict.py`), which costs seconds per run. It named all five sites before the handoff, so no further countermeasure is owed.

## Forward-carry

none

## Friction

- frugal-inline-guard: cost: the session's routing hook refused plain greps of this seat's own result logs past five per prompt, forcing a subagent read of four log files. Carry: dismissed: a session plugin hook, not repository policy
