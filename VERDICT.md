Fix review: blocked dfb981d7a0066c472ef408467a88630e77227f70 class-open: dhw_planner._plan_dhw_cheapest_first take / (cop * dt) and its spare-heat forward, and _baseline_dhw_economics (baseline_draw + standby_loss) / cop_dhw, are heat-to-power conversions of this class in neither the diff nor the body

bus-nonce: 498e30fea17a22b203e85ba09cae1d97

## Block

Round 1: no earlier review on #3006. Reviewed from a detached worktree at `dfb981d7a0066c472ef408467a88630e77227f70`, with a second one at the merge base `cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7`. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.

The body names no enumeration rule of its own. It inherits the four-site census in `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` section 5 and states: "No fifth copy: the helper replaces the four quotients and is the only inverse in the tree." The body already shows that census is incomplete: it found a forward site the census missed (the clamp walk). So I ran my own enumeration over production: every division by a COP-named variable (`ev/class_grep.txt`, 21 hits). Two hits are heat-to-power conversions of exactly this PR's kind, and the body neither converts nor dispositions them. The census does not list them either.

1. `custom_components/heatpump_optimizer/dhw_planner.py:2174`, `plan[j] += take / (cop * dt)`, with its forward twin `:2155`, `spare_thermal_kwh = (p_dhw_max - plan[j]) * cop * dt`. These lines are in `_plan_dhw_cheapest_first`, stage 2 of every hot-water plan (`dhw_planner.py:1124`, seeded by the LP this PR fixed), and its complete fallback when the LP is unavailable. They are the same pair as M1 and M2 on the LP, but left on the plain quotient and product.
2. `custom_components/heatpump_optimizer/dhw_planner.py:393`, `baseline_dhw = np.full(n_steps, (baseline_draw + standby_loss) / cop_dhw)` in `_baseline_dhw_economics`. This is the hot-water twin of the space savings baseline this PR converted (M5). It has the same mean-draw shape as the setpoint sweep, which the PR converted and tested on a floorless band.

Measured harm, stated honestly: my probe `ev/greedy_demo.py` (reviewer-built, out of tree) runs `_plan_dhw_cheapest_first` at d=0 and d=0.2, unseeded and LP-seeded, over three cap/dt shapes. The tank floor is met in all 12 cells (`ev/greedy_demo_head.txt`), because the repair re-simulates the derated tank and buys again. So I have not shown a missed setpoint. The block is about the class: the PR presents four sites as the whole class, and that is not established. To clear it, either convert these two seams through `power_for_heat_per_cop_kw` / `heat_per_cop_kw` with a failing check and mutant each, or disposition each in the body with its reason. In both cases, name the enumeration rule and paste its output. The other hits are under Findings.

## Findings

- Other heat-to-power quotients from the same enumeration are not dispositioned in the body: `coordinator.py:9092` (`cap_i = entry[0] / cop_i`, a measured heat envelope turned into an electrical cap, in a different function from the census's `_fold_capacity_envelope`), and `optimizer.py:5185` and `:5218` (the terminal stored-gap refill, `stored_gap / cop`). They may legitimately be out of the class (a measurement; energy at an unstated rate), but the body owes a line each. `sysid.py:1476` and `:1492` look like the census's `sysid._size_step_power` bound; confirm in the same line. Carry: R10-COP-PARTLOAD
- The setpoint sweep's `hours=24.0` prices a day's hot water as 24 h of steady mean draw. That draw is normally below the modulation floor, where the factor is 1, so on a real install (`min_electrical_power` > 0) the derate almost never reaches the sweep. The new check needed `min_electrical_power = 0.0` to see any effect. Hot water actually runs in bursts near `p_dhw_max`, so the sweep still underprices the derate. Say so in the body, or price the day at the planned run power. Carry: R10-COP-PARTLOAD
- Carry 2b (live buffer-store CPU) is honestly left open. The body measures 2.44x at the merge base and does not build it, and the roster already carries it: `wave-r10-groups.json` `$.groups[88].carry[2]`, "The 2.5x CPU cost of the live buffer store ... a bound or warm start on the planner must earn it". I did not re-run `r10_buffer_store.py bench 3`, so 2.44x is not re-derived. Carry: R10-COP-PARTLOAD
- The LP-objective secant carry (`price * E / cop` under a convex cost) is written only in this body. It is not in the group's roster carry list yet; the body routes it to the standing-roster seat. `carry_audit` routes it (`CARRY-AUDIT: 3 routed, 0 unrouted`), so I am not blocking `carry-missing`. The append is still owed after the merge. Carry: R10-COP-PARTLOAD
- Policy: the D2.md item-2 sentence changes what a D2 seat must do. It merges only on tvofi's approving review at the head (or the mandate the body cites). That review is owed, not a defect, and I am not blocking on it. `budget-raise-gate` stays red until then. Carry: R10-COP-PARTLOAD
- The cap table keys `dev/governance/dimensions/D2.md` as `tools/audit/briefs/D2.md`, which does not exist in the tree. `policy_lint.mjs` reports the stale path in its error. This predates this PR; it is an instrument naming defect. Carry: dismissed: pre-existing in the budget file, not introduced or worsened by this diff

## Evidence

- RESULT head unmoved: `git ls-remote` reads `refs/pull/3006/head` = `dfb981d7a0066c472ef408467a88630e77227f70` just before writing (`ev/HEAD.txt`). The body's head line matches.
- RESULT merge: `git merge-tree --write-tree origin/main dfb981d7a` exits 0 (tree `980436615d4e`), with no conflict and no claim-driver line.
- RESULT unmodified suite at head: `PYTHONPATH=tests/hastub:custom_components:tests python3 -u tests/features.py` reads `ALL 4610 FEATURE CHECKS PASSED`, rc 0 (`ev/features_head.txt`).
- RESULT mutation proof, full `tests/features.py` per mutant (`ev/mutate.py`, `ev/lane.sh`, `ev/mutants_summary.txt`):
  - M0 (helper returns its input): 5 of 4610 failed, exactly the five new checks.
  - M1 (LP back-conversion), M2 (LP energy ceiling): 1 each, the LP check.
  - M3 (clamp allowance), M4 (clamp walk): 1 each, the clamp check.
  - M5 (space baseline): 1, the baseline check.
  - M6 (sweep): 1, the sweep check.
  - All seven match the body. Each mutant kills only its own site's check.
- The ledger pins (CLAMP_DROP, CMP_BOUND x2, GUARD_OFF and RETURN_DEL on the helper, plus the baseline's CLAMP_DROP) were recorded by the fixer's `--pin-killed`. I did not re-run them; the CI `tests / mutation` lane is the authority. I read both `equivalent` triages: the sweep's 0.5 floor sits under `_cop_law`'s `max(cop, 1.0)`, and the LP's 1e-9 floor differs only at `p_dhw_max == 0`. Both arguments hold on the code.
- RESULT inverse exactness (`ev/inv_check.py`, `ev/inv_check_head.txt`): 138 configs, covering bands 0-3, 1.5-5, 2-6, 0.5-12, 1-1.2 and fixed 3-3 kW; d from 0 to just under `partload_derate_limit`; hours 1, 0.25 and 24; P over 0-1.6 x max, plus the floor, max and adjacent ulps. Worst heat-space residual of forward(inverse(forward)) is 1.1e-13. Scalar and array paths agree, and a scalar returns a float. The inverse is monotone non-decreasing over 0-10 kW at d=0.2, so the floor and max-power edges are continuous. I raised under `np.errstate(all="raise")` and nothing tripped.
- RESULT null control (`ev/inv_check_head.txt`): 20 000 random draws, 0 mismatches. At zero derate the helper returns the same object for `heat / cop`, including at `hours=24`. The LP back-conversion array is bit-identical. The ceiling `cop * heat_per_cop_kw(p, p_dhw_max) * dt` equals `p_dhw_max * cop * dt` bit for bit. The sweep `mean_price * (x / cop)` and the clamp walk `delivered_heat_kw(p, cop, P)` reduce to the old two-operand products.
- RESULT finder's harness `dev/audit/harnesses/r10_cop_partload.py` (sha1 `0b2f5ce911c0`, unchanged by the diff), base `cf4f6b7a6` vs head (`ev/harness_base.txt`, `ev/harness_rev.txt`, `ev/harness_compare.txt`):
  - d=0.0 plan hashes identical 32/32; d=0.112 hashes moved 26/32. Matches the body.
  - Flat d=0.112 summary identical; flat term-vs-none max +0.1065 -> +0.1064. Matches the body.
  - Not in the body: the spread term-vs-none line moved from "cheaper 14 dearer 2" to "cheaper 13 dearer 3", min -0.0598 -> -0.0599. Both ends report `failures 0`.
- `_buffer_capacity` routing: `0.04 if c_buf < 1e-6 else c_buf` is the same predicate and value as the removed inline `if C_buf < 1e-6: C_buf = 0.04`, NaN included. Behaviour-identical, as the body says.
- Claims and versions: `tests/env_drift.py --all` reads `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE` (`ev/env_drift.txt`). No golden or claim file is touched. VERSION, the manifest and RELEASE_NOTES.md are untouched (`ev/untouched.txt`).
- Structure and policy:
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - `rules_sync.mjs --check`: ok.
  - Earned-raise test: with the D2 caps reverted to 51/644, lint reads exactly two errors, 53 lines > 51 and about 683 tokens > 644. The raise is the two added D2 lines and nothing else (D2.md is 51 lines at the base and 53 at the head).
  - The `class_excess_loc` and `max_class_loc` -1 is paid by joining a wrapped call onto one line. The body itself calls that formatting, not simplification. It is a move down, not a raise, so not `metric-gamed`.
- Architecture score: CI `arch-score` succeeded. I did not re-run the body's `dS +0.0000 NULL`, so that figure is not re-derived.
- CI on this head, read live:
  - Success: arch-score, briefs, closure-scope, browser, replay, typing, arch-instrument, policy-docs, delivery-status, nightly-status, wave-script, env-matrix, hassfest, validate-hacs, CodeQL actions/js.
  - Red: `budget-raise-gate`. The body answers it under Red checks, as expected until the approving review.
  - Red: `prelude` in run 41100571708. Its log ends `FAIL repos/tvofi/heatpump_optimizer/actions/runs/41100571817/jobs: HTTP 502 Server Error`. That is a GitHub API 502 in CI's own polling, not this diff. It is not a required check and it does not block this verdict.
  - Still in progress at writing: `tests / mutation`, `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `governance / instrument-self-tests`, `codeql / Analyze (python)`, `pr-contract`. The step-11 root-cause read cannot be completed until those conclude and a `pr-contract` run checks the body. It does not change this block.
- The `frugal` routing hook refused a few of my inline reads; I delegated them as it asks and did not work around it. My helper scripts in `ev/` are reviewer-built and out of tree (`fixer.md` 18).
