Fix review: blocked 6295f868a4314316f5e12c72fa2d16ead4895d35 doc-claim-false: two added user-doc sentences are false against executable code (lost heat is charged only hot-water-to-heating; the cold-tank exception needs a step that heats the tank) and the body's null control prints nothing for docs/how-it-works.md

bus-nonce: fd9c4779b03c45c5897554d16b10dca6

## Block

Round 1. Measured at head 6295f868a4314316f5e12c72fa2d16ead4895d35 (handoff tip; the body's `## Head` names the same SHA). Every item below is evidenced by an executable line, not by a comment or docstring (owner ruling 2026-11-13).

1. **docs/configuration.md (Pump duty control, "A switch that stops the compressor is priced") and docs/how-it-works.md (cycling-cost section) state the off time is charged as heat not delivered for any latched direction.** The configuration bullet says "Once a direction has stopped the compressor ... the plan ... expects the median measured off time as heat not delivered in the step that follows"; how-it-works says the optimizer learns "per direction" and "counts the off time as heat not delivered". Executable code charges lost heat for one direction only: `duty_legs.lost_share` returns `min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))` (custom_components/heatpump_optimizer/duty_legs.py:161), index 0 being `dhw_space` (`duty_switch.DIRECTIONS = ("dhw_space", "space_dhw")`, read in that order by `planner_pairs`). A latched heating-to-hot-water direction is priced in `switch_weights_batch` but never reduces availability. Fix: name the direction (hot water to heating) in both sentences.

2. **docs/configuration.md, Heat pump on/off switch row: "a run the plan would end within 10 minutes is not started unless the tank needs heat now (below its minimum, or a disinfection hold)".** `supply_hold._ends_soon` (supply_hold.py:156) exempts the start only when `step_duty(inp.plan, now) in ("dhw", "both") and tank_reason(inp)`: a cold tank or disinfection hold on a space-only step is still held. The page states the tank condition alone. Fix: "unless the step heats the tank and the tank needs heat now".

3. **The body's `## Null control` does not re-derive.** It claims the `git grep -c -E ...` command prints "one or more lines per page at the head"; at the head it prints README.md:1 and docs/configuration.md:3 and nothing for docs/how-it-works.md (none of the four patterns appears in the added how-it-works paragraph). Origin/main side prints nothing, as claimed. ev/checks.txt. Fix: add a pattern that occurs in the how-it-works paragraph (e.g. `min\(a, b\) / p_max`) or correct the sentence.

## Findings

none

## Evidence

- No pull request exists yet: no review packet, no CI runs to read, so no red check is owed an answer (step 11 has nothing to read). `merge_train.py owed-reds` set recorded in ev/checks.txt.
- Merge: `git merge-tree --write-tree origin/main 6295f868a4` rc=0, tree b797a2d8a3; origin/main is e23124ff6e, the head's merge base (head not behind). ev/checks.txt.
- Role contract current: `git diff <mb>...origin/main -- dev/governance/roles/` empty.
- VERSION, manifest.json, RELEASE_NOTES.md untouched; both claim files untouched; no golden fixture in the diff (docs-only), so `env_drift.py --all` has nothing to compare.
- Mutation proof: n/a, no production line changed (diff: README.md, docs/configuration.md, docs/how-it-works.md, dev/audit/rounds/round4/D6/claims.{json,md}); confirmed by `git diff --stat`.
- `python3 tests/doc_claims.py` at head: ALL 348 checks PASSED, rc 0; `--markers --user`: 0 user-doc marker(s), 0 due. Re-derived, matches the body.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` re-run at head leaves claims.json/claims.md byte-identical; C108 reads 92 links, broken=[]. Re-derived, matches the body.
- Scope line: `python3 tests/closure.py select --diff e23124ff6e --workdir $D` prints `MODE: SCOPED -- 6 script(s) run, 27 scoped out.`, matching the body's figure block.
- Enumeration rule re-run (body's first-parent loop over f44e761c19..origin/main): returns #3511, #3526, #3512, #3536, #3505, #3441, #3534, #3530, #3524 plus the two stamps and #3513 itself; every product merge is dispositioned in the body. `git merge-base --is-ancestor 3246aa389f origin/main` true. ev/enum_and_code.txt.
- Verified true against code: supply MIN_RUN/MIN_PAUSE = 10 min, `_passes` exempts modes other than auto/economy, system identification and live boosts; retry `_TICK = timedelta(minutes=1)` via `supply_tick`; age from the switch's `last_changed` (`switch_age`), restart stamp pinned by tests/ha_contract.py `_restart_stamps_last_changed`; early_cutoff's own `_cycle_guard` refuses a cut under `MIN_ON` (= MIN_RUN), so the "never switched off less than 10 minutes" claim holds for both switch writers (`switch_supply` callers: `write_supply`, early_cutoff). Duty switch: `STOP_WINDOW_S = 180.0`, `N_ON = 5.0`, `P_ON = 0.5`, `SPAN_DAYS_ON = 2`, `HALF_LIFE_DAYS = 14.0` in `Direction._latch`; published keys `duty_switch_{dhw_space,space_dhw}_{p,n,stopped,kept,void,censored,median_off_s,span_days}` on the Compressor Starts sensor; `_switch_cost_fn` and the placement candidate return nothing when `cycling_cost` is not > 0 while `_stop_availability` still applies (start cost 0 plans only lost heat: true); cost term `p * min(level_before, level_after) / p_max` matches how-it-works' formula; option label "Cost of one compressor start" is `compressor_cycling_cost`. `_lead_mode` writes the mode only under DUTY_CONTROL with the switch reading off: true.
- `BOOST_SPACE_SETTLE_TAIL_HOURS: Final = 12.0` at head (body's #3505 disposition).
- Not re-derived: the body's "re-read, no stale claim found" for #3534, #3441, #3536 and the carries it marks implemented without touching; I did not re-read those pages in full.
- Code reads for duty_switch/optimizer were extracted by a delegated read-only worker quoting file:line; the three block items were read by me directly (ev/enum_and_code.txt).
