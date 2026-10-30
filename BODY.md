R10-COP-PARTLOAD part 2, the residual carries after #2872. Issue #2501 is met by #2872 and needs only its close, which is the orchestrator's: it is a roster issue no group lists under `fixes`, so this body names it without a closing keyword.

**Inverse conversions (built).** The four sites that closed the loop with `heat / cop` -- `DhwPlanner._plan_dhw_min_cost` and `DhwPlanner._clamp_dhw_to_capacity`, `HeatPumpOptimizer._compute_baseline_power`, and the coordinator's `_dhw_setpoint_sweep` -- understated the draw a heat needs once `cop_partload_derate` is set, because the forward relation `h = P * (1 - d * (P - p_min) / band)` is quadratic in power. They now take `power_for_heat_per_cop_kw`, one helper beside `heat_per_cop_kw` in `thermal_model.py`: the smaller root on the rising branch, `2h / (b + sqrt(b^2 - 4ah))`, `h` below the floor, `h / (1 - d)` past max power. It returns its input object unchanged at a zero derate, so each replaced `heat / cop` is the same float. Two forward sites rode along because the inverse is only exact against a forward that prices the derate: the LP's energy ceiling (`cop * heat_per_cop_kw(p_dhw_max) * dt`, where it read `p_dhw_max * cop * dt`) and the clamp's own walk (`delivered_heat_kw`, where it stepped `cop * plan[i]` -- a forward site #2872's census did not list, since the clamp reaches `simulate_dhw_step` with a precomputed thermal power). The sweep converts a day's energy through `hours=24.0`, which scales the band instead of dividing and re-multiplying, so its zero-derate answer stays the quotient bit for bit. No fifth copy: the helper replaces the four quotients and is the only inverse in the tree.

Alternatives: a per-site closed form (four copies of the root -- refused, the brief prices that against the ratchet); linearising the LP's objective by the convex electrical cost (piecewise segments per step) -- not taken, see Forward-carry: the LP still prices `price * E / cop`, a secant under-estimate of a convex cost, while its back-conversion and ceiling are now exact.

**Small-buffer fallback (built, carry 2a).** The two-zone scalar step and `simulate_trajectory_batch` each carried an inline `0.04` fallback for a vanishing buffer mass; both now call `_buffer_capacity`, the helper every other step already used. The fallback lived in `thermal_model.py`, not `optimizer.py` as the carry named it. Measured against the call allowance below: inside it.

**Live buffer store CPU (carry 2b): measured, not built.** At the merge base the owner-shaped buffer arm costs 2.44x the flat no-buffer null (Figures). This seat built no bound or warm start; the carry stays open with the measurement attached (Forward-carry). This is not the brief's call-channel refusal -- the channel has headroom -- it is unbuilt work, said plainly.

**Policy (carry 3): one sentence in `dev/governance/dimensions/D2.md` item 2**, the countermeasure `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` section 3 priced: before sweeping, derive the priced formula's inputs from the device's own control surface and mark each a modelled term, a documented constant, or out of scope. Policy: it needs the owner's approving review before merge (see Approval).

## Head

b3e835ffd52de02d2c780a5c4bac414007659b9d, cut from origin/main 507a9ec264eb373b132248d752259254d8a9fa4d (behind 0; `date -u` 2026-10-30). Six commits: the change (production, the feature block, D2), the structure record (68f4e6591), the D2 brief's cap raise (f57d2fd21), the helper's edge/guard/clamp pins in the feature block (7a1abd6a5), and two mutation-ledger commits (0e7b72ebd, the tip). The scoped gate, `prepr.sh`, policy lint and the ledger were re-taken at the tip; the harness both-ends run, the bench and M0's full-suite run were taken at 68f4e6591, and nothing after it touches production code (`git diff --stat 68f4e6591 HEAD -- custom_components` is empty).

## Mutation proof

Seven mutants against the new `tests/features.py` block (`R10-COP-PARTLOAD part 2`, six checks over five `R.check` calls; the clamp and LP checks each carry two arms). Each mutant reverts one production line; every one turns at least one check red, and each per-site mutant turns exactly its own site's check:

- Recorded pins: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main` pinned all 7 helper and baseline sites the diff adds as killed by `tests/features.py` (two runs; the first left three for its budget), and two survivors on base clamps whose line text this diff changed are triaged `equivalent` under `tests/mutation_ledger/survivor_triage/` with their reasons (the sweep's 0.5 COP floor under `_cop_law`'s 1.0 floor; the LP's 1e-9 energy floor, which only differs at `p_dhw_max == 0`). The baseline's old CLAMP_DROP pin anchored the replaced line and is removed; its new line is one of the 7.
- M0 `power_for_heat_per_cop_kw` returns its input (the root deleted): 5 of 5 checks red -- the round trip, baseline, clamp, LP and sweep. Re-run against the whole of `tests/features.py` in a worktree at 68f4e6591 with only that line added: `5 of 4610 FEATURE CHECKS FAILED`, exactly those five, so the root is load-bearing and nothing else leans on it.
- M1 LP back-conversion `energy / (cop * dt)`: the LP check red.
- M2 LP energy ceiling `p_dhw_max * cop * dt`: the LP check red (its capped arm, 2.0 kW at dt 0.5 h; the first draft's 1.2 kW cap sat next to the floor where the derate barely bites, and M2 survived it -- the arm was moved onto the band).
- M3 clamp allowance plain quotient: the clamp check red.
- M4 clamp walk `cop * plan[i]`: the clamp check red (its second step reads its room off the clamp's own walk of the first; the first draft was one step and M4 survived it).
- M5 baseline `required_thermal / cop`: the baseline check red.
- M6 sweep `(standby_kwh + draw_day_kwh) / cop * mean_price`: the sweep check red.

M1-M6 were run by a reviewer's driver that execs the block alone with its prelude (fixer step 18: a one-off driver stays out of the tree); each restores the file afterwards.

The `_buffer_capacity` routing is behaviour-identical by construction (the same `0.04` under the same `< 1e-6` predicate); its pin is the existing buffer checks, unchanged and green.

## Null control

- Zero derate, byte-identical plans: the finder's harness `dev/audit/harnesses/r10_cop_partload.py` (sha1 0b2f5ce911c0), run at the base and at the head, prints 32 `d=0.0` plan hashes; all 32 are identical. The hash is live: 26 of the 32 `d=0.112` plans move, which they must, since the hot-water and baseline conversions now price the derate.
- Flat price: the harness's flat-price `d=0.112` summary line is identical at both ends (16 cells, heat short max 0.0977, flat wins 14 of 16); the term-vs-none cost line moves in the fourth decimal only (max +0.1065 -> +0.1064).
- In the new checks: a zero derate hands `heat / cop` back as the same object (`is`); the baseline below the floor, the clamp and the LP at `d = 0` land where they did.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- Scoped gate at the tip: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out`, rc 0: ALL 4610 FEATURE CHECKS, ALL 2484 ENTITY CHECKS, ALL 113 STRESS CHECKS and every other scoped script passed. On the first commit's tree the same command had reddened `tests/entities.py` (1 of 2484, Red checks) and `tests/structure.py` (2 rows improved and unrecorded, recorded in 68f4e6591).
- Policy lint: `node tools/policy/policy_lint.mjs` at f57d2fd21 -> `TOTAL: 0 error(s) across 50 policy file(s)`; at 68f4e6591 it printed the two D2 cap errors (54 lines > 51, about 706 tokens > 644) that turned `tests/entities.py` red. `node tools/policy/rules_sync.mjs --check` -> `RULES-SYNC ok`.
- Production-call channel: `tests/stress.py` inside that gate -- 20 of 20 families judged against origin/main (507a9ec264eb), none past the `1.0 + SCENARIO_CALLS_GROWTH` (1.05x) allowance its work counts vouch for; ALL 113 STRESS CHECKS PASSED.
- Structure: `python3 tests/structure.py --record` -> `class_excess_loc` 17672 -> 17671, `max_class_loc` 8065 -> 8064. Paid by joining the sweep's wrapped COP call onto one line against the conversion's added line: formatting, not simplification, and said so in the commit.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 507a9ec264eb373b132248d752259254d8a9fa4d HEAD` -> `Architecture score: dS +0.0000 NULL`.
- Buffer store CPU at the merge base: `python3 dev/audit/harnesses/r10_buffer_store.py bench 3` (PYTHONPATH=tests/hastub:custom_components:tests, worktree at 507a9ec26) -> `owner_buffer_spread` median 2.405 s, `null_flat_nobuffer` median 0.985 s: 2.44x, over 3 runs each.
- Inverse round trip: the new block's first check, forward of inverse of forward over 0-6.5 kW at d=0.15 on a 1.5-5 kW band, max error 8.88e-16 (tolerance 1e-12).
- M0 full suite: `PYTHONPATH=tests/hastub:custom_components:tests python3 -u tests/features.py` with the root deleted -> `5 of 4610 FEATURE CHECKS FAILED`; unmutated head: rc 0, no FAIL line.
- Finder's harness both ends: `PYTHONPATH=tests/hastub:custom_components:tests python3 -u dev/audit/harnesses/r10_cop_partload.py` -> the Null control's 32/32 and 26/32.

## Red checks

- `tests/entities.py` (local, at 68f4e6591; this branch's own): "the template arm turns the acceptance red on a template that fails its own contract (and the real template keeps it green)" -- its live arm runs the whole `policy_lint.mjs` acceptance, which refused the D2 brief past its caps. At the base the same script passes all 2484. Repaired in f57d2fd21 by the cap raise below; re-run at f57d2fd21: `ALL 2484 ENTITY CHECKS PASSED`. The cheaper detector already exists and is the one that named it: `node tools/policy/policy_lint.mjs`, under a second, which a seat editing a policy file should run before the gate; no new detector is owed.
- `mutation`: none predicted at the tip -- every site `prepr.sh` step 6d listed is pinned or triaged (Mutation proof).
- `budget-raise-gate`: expected red until the approving review at the head -- `dev/governance/config/policy_budgets.json` raises the D2 brief's caps (Raise justification).

## Forward-carry

- The 2.44x CPU of the live buffer store (carry 2b) is unbuilt: a bound or warm start on the planner must still earn it, against the flat no-buffer null, with the call channel inside its allowance. The group's roster carry already states it; this pull request discharges none of it. Carry: R10-COP-PARTLOAD
- The hot-water LP's objective prices `price * E / cop`, linear in heat, while the electrical cost is now convex in it under a derate: the LP's back-conversion and ceiling are exact, its cost ranking is a secant under-estimate. A later D0 pass on `_plan_dhw_min_cost` owns whether to segment it; the roster's carry list for the group is the standing-roster seat's to append (`roster_edit.py`), which this seat does not run. Carry: R10-COP-PARTLOAD

## Friction

- frugal-routing: cost: the session's inline-read guard (five searches per prompt) blocked plain `Read`s of files this seat had to edit; reads went through delegated workers and edits through scripted replacements. Carry: dismissed: a session-local plugin, not repository policy

## Raise justification

`dev/governance/config/policy_budgets.json`: `tools/audit/briefs/D2.md` (the key the cap table still uses for `dev/governance/dimensions/D2.md`) 51 -> 53 lines and 644 -> 683 tokens. The two lines and 39 tokens are the policy sentence the dispatch asks for, and nothing else.

Payments tried: (1) cutting spent prose elsewhere in the brief -- every `## Reuse` citation still resolves (`thermal_model.py`, `tariff.py`, `grid_fee.py`, `price_model.py`, `tests/golden.py` with `SCENARIOS`, `tests/dst_checks.py`, `tests/profiles.py` all present) and no item restates another, so nothing was spent; (2) tightening the sentence itself -- from four lines and the parenthetical list of inputs (54 lines, about 706 tokens) to three (53, 683); the list moved out because the RCA it comes from names the inputs; (3) reflowing lines to fit 51 -- refused, it moves the metric without improving the text. Code architecture is untouched by the raise.
Architecture score: dS +0.0000 NULL

## Approval

`dev/governance/dimensions/D2.md` is policy: this pull request changes what a D2 seat must do in item 2. It needs the owner's approving review at its head before merging (the orchestrator approves under mandate 6329234399, per the dispatch).
