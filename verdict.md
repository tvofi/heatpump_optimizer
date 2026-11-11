Fix review: blocked 9394a6528c7683f5b8b5fb19a1d939e244c515e6 mutation-vacuous: optimizer.py:2712 GUARD_OFF, optimizer.py:2723 CLAMP_DROP, thermal_model.py:2603 hours-guard drop

bus-nonce: 523338c3a482531749a97f36da9bddee

Round 1 (first review), measured at head 9394a6528c7683f5b8b5fb19a1d939e244c515e6; the PR head was still that SHA when this verdict was written (`git ls-remote`).

## Block

The fix is not pinned on a valved install, which is the population the group's savings residual is about. `_terminal_row_cost` has two places where it applies the new law. The single-sum one (2722) is pinned. The split buffer/building one (`optimizer.py:2712`, `if refill is not None:` taken when `cop_buffer != cop_end`) is not: turn that guard off (`if False:`) and the derated terminal falls back to the linear figure, yet every check stays green.

- On the finder's own valved two-zone install (`r10_sav_wood_reference._install(False, True)`: manual valve, `buffer_is_store` True, cop_end 2.4500 against cop_buffer 1.7160), d = 0.2 gives terminal 80.267178 at the head and 64.213742 under the mutant, which is exactly the linear figure. At d = 0 both read 64.213742 (`ev/buffer_reach_finder_install.txt`, `ev/buffer_reach3.py`).
- The PR's new check passes under the mutant (`ev/mutants.txt`, M7). So does all of `tests/features.py`: `ALL 5223 FEATURE CHECKS PASSED` in 452 s (`ev/features-M7.txt`). So does the companion harness `r10_sav_valuation_residue.py`, whose terminal gap reads 0.000000 on every row (`ev/companion-M7.txt`). None of its 16 cells reaches the split branch.
- CI's own driver gives the same result over the whole closure. `tests / mutation-pins (2)` (job 130371095337) prints `UNPINNED custom_components/heatpump_optimizer/optimizer.py:2712 GUARD_OFF -- lives` and `UNPINNED ... optimizer.py:2723 CLAMP_DROP -- lives` (`ev/ci-mutation-pins-2.txt`).

The body says "The new check kills the guard, return and constant sites by the mutation proof's four arms", and it lists 2712 GUARD_OFF as "pinned by `mutation-autofix` (unmeasured)". At 2712 this is false: nothing kills that site, so autofix has nothing to pin. The body's companion figure ("terminal gap max 0.000000" at the head) covers only installs where the split branch is never taken.

Every survivor, from my driver run and from CI's:
- `optimizer.py:2712 GUARD_OFF` survives in my run (M7) and in CI. It is real and reachable (above).
- `optimizer.py:2723 CLAMP_DROP` survives in CI. The body predicted it as an equivalent survivor ("triage owed if `tests / mutation` reports it"). It has been reported, and no triage exists.
- `thermal_model.py:2603`: dropping the `hours <= 0.0` arm of the guard survives in my run (M10). It is equivalent at every reachable input, because `hours = 0.25 * n_steps * dt_hours` > 0. It still needs the body's triage line.

Remedy, sized to the defect: add a valved arm to the new check, for example `buffer_is_store` with `cop_buffer != cop_end` as on the install above. Assert its derated terminal against the law, and assert that its `_terminal_cost_batch` row equals the scalar figure. Re-run the pins lane, and triage 2723 and the 2603 hours arm in the body.

## Findings

- Under a derate, `_deferred_energy_cost` applies the law to the net gap, f(D_plan − D_ref). The objective's terminal cost prices each end from its cap, so the difference it implies is f(D_plan) − f(D_ref). The two agree bit for bit at d = 0 and part at d > 0. Synthetic, `ev/gap_vs_difference.txt`: with the anchor 3 °C above the reference end, f(gap) is 5.4646 against 7.4683. On the harness's own solves the gap is small: at most 0.012743 (spread) and 0.005016 (flat) per horizon over 40 capped deferred calls each, against deferred figures up to 17.74, and exactly 0 at d = 0 (`ev/settle_vs_terminal.txt`, instrument `ev/settle_vs_terminal.py`, built by this reviewer and not the finder's). It is not material at these cells. It is the rule to keep in view if the settlement is ever required to equal the objective's terminal difference exactly. Carry: R10-SAV-VALUATION-RESIDUE

## Evidence

- Setup: `cloud-setup check: OK`. The roles diff against main is empty. `git merge-tree --write-tree origin/main <head>` exits 0, so it merges cleanly. VERSION, the manifest and RELEASE_NOTES are untouched in the three-dot diff. The body's `## Head` names 9394a652, the head reviewed.
- Mutation proof, re-created against the PR's check run standalone (`ev/svr_check.py`, driver `ev/mutants.txt`):
  - Killed: M1 (deferred return made linear), M2 (terminal law `None`), M3 (`_refill_law` always `None`), M4 (`refill_power_kwh` returns its input), M5 (quantile 0.25 to 0.5), M6 (copysign dropped), M8 (single-sum law guard off), M9 (refill hours doubled).
  - Survived: M7 (split-branch law guard off) and M10 (`hours <= 0` arm dropped).
  - NULL (docstring edit) survived, as it should.
  - The check fails at base 32aea942 (`ev/check-at-base.txt`).
- Finder's harness `r10_partload_pricing.py` re-derives the body's base figures exactly at 32aea942: flat d=0.112 lp_err 0.267290 (dhw 7.0145), terminal-at-max 4.368455, deferred-at-max 2.140129, `null rows not zero 0`. At the head, flat terminal-at-max is 3.674941 and deferred-at-max 2.179748; it still prints a bound, as the body says (`ev/partload-base.txt`, `ev/partload-head.txt`).
- Companion `r10_sav_valuation_residue.py` (`ev/companion-base.txt`, `ev/companion-head.txt`) re-derives exactly:
  - At base: spread terminal gap 3.150490 and deferred gap 0.440868; flat 2.835283 and 0.187447.
  - At the head: all four read 0.000000.
  - LP gap: spread 0.202595 and flat 0.335995 at both ends.
  - d = 0 rows read 0; `null rows not zero 0`, `failures 0`.
  - This companion compares production with the PR's own rule applied to the linear figure. It shows that the rule is implemented. It does not show that the rule is right, and it does not reach the split branch (Block).
- Residual and attribution re-derive exactly at the head (`ev/wood-valve-*-head.txt`, `ev/attribution-*-head.txt`):
  - valve-flat −3.90 %, valve-vary −8.02 %.
  - Flat: reference stored −34.85 kWh_th, non-steady +12.52, `plant steps seen 192 of 192`.
  - winter_typical: −34.85 and +11.89, 192 of 192.
  - The kWh_th residual (−22.33 flat) and the harness's kWh_e residual (−5.21) differ because the two COPs do (1.820 against 1.910). This agrees with the original carry's remark that COP pushes the other way. Carry: dismissed: evidence, not a finding
- Structure: `tests/structure.py` exit 0, `class_excess_loc 17536 <= 17536` (`ev/structure-head.txt`). `env_drift.py --all`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE` (`ev/env_drift.txt`).
- Forward-carry: both `## Forward-carry` items, and the Figures item defedabb, are in the group's `carry` on `origin/handoff/audit-r10-roster` (`wave-r10-groups.json`). Each states its control as a precondition. The own-group carries name "Pending the orchestrator's ruling on its owner", which is `fixer.md`'s exception. `carry_audit` at render: 3 routed, 0 unrouted.
- Red checks:
  - `tests / mutation` is red. It is in `merge_train.py owed-reds` (`ev/owed-reds.txt`). The body names it and answers it (prepr.sh step 6d, no further detector).
  - `gate` (required) is red on two runs, and `classify` prints `gate red: none`, so I read it as the aggregate of the above and of pending lanes.
  - `tests / nightly-status` is red. It is outside this PR's set.
- CI state: `merge_train.py classify` printed `WAIT ... pending: gate red: none` from 06:43 to 08:43 UTC (`ev/classify.log`). At 08:43, `tests / mutation-pins (1)` (job 130371095299) was still in_progress. This block does not rest on CI: the survivor was reproduced locally, and CI's completed pins shard confirms it.
