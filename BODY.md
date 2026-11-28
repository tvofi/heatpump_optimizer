R11-PRODUCT-TEXT-PINS: two stale product docstrings corrected, the stray after-save key in the setup wizard's `device_prefill` step decided by a test, and the corrected user sentences pinned to the code that decides them, so reverting one fails `tests/entities.py`.

Per carry:

- **Carry 0 (b30f48ba), `setpoint_check.py` module docstring.** "Space set-point is never recommended" is replaced: this module only checks that the space set-point entity can be read (`_space`, issue `space_setpoint_unreadable`). Under Control, `pump_arbiter` writes the plan's own value to it each step, so no configured space value exists to compare against.
- **Carry 1 (6f36db0c), `presets.py` module docstring.** "three answerable" questions is replaced. The docstring now lists the questions `preset_from_config` reads from `answers` (structure, foundation, era, heated area, upper and lower emitter) and gives no count, so it cannot go stale on a count.
- **Carry 2 (bb5336e8), `config_flow.py` setup step `device_prefill`.** Decided: the key is not stored, and no production change is needed. Since 7b4ef782bc (R11-SEAM-config) the wizard's preview is `vol.Schema(_prefill_fields(...))`, not `_prefill_schema`, so no after-save choice renders. Its schema refuses one, so `self._data.update` cannot receive one. `tests/config_flow_steps.py` now pins both halves in one check: "the wizard's pre-fill page renders no after-save choice and its schema refuses one". The schema probe is the null control on the rendered key set, because it reads a key the rendered set does not name.
- **Carry 3, rain thresholds and "four price steps".** In `tests/entities.py`, every shipped `set_thermal_parameters.rain_heat_loss_multiplier` description (`strings.json` plus each `translations/*.json`) is parsed for its two rain rates, in order: the full-multiplier rate, then the no-multiplier rate. `ThermalModel.effective_heat_loss_coefficient` is then driven at each rate, above the full one, just above the zero one and halfway between. The `run_optimization_no_prices` message's step count is read from `strings.json`, and the coordinator's own `async_run_optimization` is driven on a horizon cut to one step short of that count and to the count itself. The check asserts its precondition: the uncut horizon is longer than the count. The pin is on the coordinator, which owns the bound (`coordinator.py`, `async_run_optimization`'s `len(prices) <` guard), not on the service handler. features.py's "run_optimization on a stale list raises the same no-prices error" already pins that the handler maps `no_prices` to this message. The stale rain comment and docstring in `effective_heat_loss_coefficient` ("Light rain (0.1-1 mm/h)", "Heavy rain (>2 mm/h)", "when precipitation > 0") now state what the code does.
- **Carry 4, `narrative.py` `dhw_window` / `dhw_preheat`.** A witness plan is run through `optimizer.classify_dhw_steps`: its dearest step is a hot-water charge outside any window, and it has a later in-window charge. The first is tagged `dhw_preheat` and the second `dhw_window`. A check then refuses any language's `dhw_preheat` sentence that claims a price (cheap / billig / günstig) and any `dhw_window` sentence that claims the present (now / nu / jetzt). Its detector is driven over the six sentences dabc6d30af replaced, which are its control corpus. A detector that missed them would read as a pass.

Alternatives considered for carries 3 and 4: a literal equality pin on each corrected sentence would also fail on a revert, but it would refuse every legitimate rewording and pin no behaviour. It lost to the property-plus-witness form above. For carry 2, the alternative was to strip `CONF_AFTER_SAVE` in the wizard's second submit as `_async_save_reconfigure` does. That adds a production line for a key the schema already refuses, so it lost.

## Head

`077b3afcf5d0b8305df699fa0f1706fc6b8f8194`, the code head `handoff/r11-product-text-pins` points at, measured on origin/main `ac9045c223721608e684c8a2213831aa34c1fa4f`, which is also the merge base (stamped 2026-11-28, `date -u`). The entity and mutant runs were taken at `6a53fe2094`; the one later commit rewords a comment in `tests/entities.py`, so they hold at the head.

## Mutation proof

Each mutant is a detached worktree at the head with one change, running the named script under `PYTHONPATH=tests/hastub`:

- m1: `git show dabc6d30af -- custom_components/heatpump_optimizer/narrative.py | git apply -R` (the six sentences reverted), then `tests/entities.py`: FAIL "no dhw_preheat sentence claims a price and no dhw_window sentence claims the present, in any language" (all six claiming); 1 of 2800 failed.
- m2: the `strings.json` rain description reverted to its pre-dabc6d30af text, then `tests/entities.py`: FAIL "every rain-multiplier description states the full and the zero rain rate effective_heat_loss_coefficient applies, in proportion between" (`strings.json: ()`) and the existing en-equals-strings leaf check; 2 of 2800 failed.
- m3: `thermal_model.py` `precipitation > 0.1` changed to `> 0.0`, then `tests/entities.py`: FAIL the rain-rate check above and "the rain-rate check refuses a text that names other rates"; 2 of 2800 failed.
- m4: `thermal_model.py` `precipitation / 2.0` changed to `/ 1.0`, then `tests/entities.py`: the same two checks fail; 2 of 2800 failed.
- m5: `coordinator.py` `async_run_optimization`'s `len(prices) < 4` changed to `< 3`, then `tests/entities.py`: FAIL "the no-prices message's step count is the run's own minimum: one step short answers no_prices, that many does not" (`runs={3: None, 4: None}`); 1 of 2800 failed.
- m6: `config_flow.py` `async_step_device_prefill`'s preview changed from `vol.Schema(_prefill_fields(suggested, suggested, self._data))` to `_prefill_schema(suggested, suggested, self._data)`, then `tests/config_flow_steps.py`: FAIL "the wizard's pre-fill page renders no after-save choice and its schema refuses one", plus the eight existing preview-label checks naming `after_save`; 9 of 731 failed.

The diff adds no executable production line: the production `.py` changes are docstrings and one comment. So `prepr.sh`'s mutant draw has no added site, and there is no `## Unpinned sites` entry.

## Null control

- The head, unmutated: `tests/entities.py` ALL 2800 ENTITY CHECKS PASSED; `tests/config_flow_steps.py` ALL 731 checks PASSED.
- The finder's harness at the base end, m0: origin/main `ac9045c223` with three changes together, then `tests/entities.py`: ALL 2794 ENTITY CHECKS PASSED. The three changes are m1's narrative revert, the rain description reverted to its pre-dabc6d30af text in all four of `strings.json` and `translations/{en,sv,de}.json`, and m5's `< 3`. A first m0 run reverted the rain text in `strings.json` alone. It failed only the existing "en.json equals strings.json leaf for leaf" parity check, 1 of 2794. So at the base, parity catches a one-file revert and nothing catches a consistent one. That is carry 4's stated defect ("reverting `narrative.py` to the merge base survives `tests/entities.py`") and carry 3's ("prose-only"), read at the base; m1, m2 and m5 read them closed at the head.
- Each pin carries its own control in-script: the claim detector over the six replaced sentences, the rain-rate checker refusing `(1.0, 0.1)`, `(2.0, 0.0)` and `()`, the uncut-horizon precondition, and the schema probe on a key the rendered set does not name.

## Figures

- Entity checks at the head: `PYTHONPATH=tests/hastub python3 tests/entities.py` (its last line).
- Config-flow checks at the head: `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` (its last line).
- Mutants m0–m6: the same two commands in each mutant worktree, as listed under `## Mutation proof`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`: `tests/doc_claims.py` failed its comment ratchet at `6a53fe2094` on one new comment sentence over 40 words. The sentence was split at the head, and `tests/doc_claims.py` then printed ALL 445 checks PASSED. Every other script the scope selected was ok.
- Structure: `python3 tests/structure.py`. `class_excess_loc` and `module_excess_loc` each moved down one (the shortened rain comment), re-recorded in commit "structure: re-record …".
- Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`, which printed `dS +0.0000 NULL`.

## Red checks

none

## Forward-carry

none

## Friction

none
