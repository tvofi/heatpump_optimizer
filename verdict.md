Fix review: blocked 8bef9bc866a7458b19dbc00d0bf4ed07ed2f206a class-open: the wood advisor's pump-heat price (wood_fuel.py cheaper_steps and _scan_wood_night, price / COP with no draw), one of the four linear valuations carry 2 names, is neither measured nor dispositioned in the body

bus-nonce: 826c60e1923b1bd9499b480ce7129fdd

## Block

Round 1 (first-round review). Brief: dispatch/reviewer-rev-3291 at 603ce8cb5. Reviewed from a detached worktree at 8bef9bc866a7458b19dbc00d0bf4ed07ed2f206a. Its tree is identical to 306a0b76e (`git diff --stat 306a0b76e 8bef9bc86` is empty).

The roster carry this group received (R10-PARTLOAD-PRICING carry 2, re-routed to R10-PARTLOAD-RESIDUE, `origin/handoff/audit-r10-roster` at 4092d06bc) names its class itself. Quoted: "The hot-water LP's objective (price * E / cop), the terminal row_cost, _deferred_energy_cost and the wood advisor's pump-heat price all price heat linearly at a COP, with no draw rate." It then says "FIRST measure the magnitude".

The body measures and carries three of these four seams: `_plan_dhw_min_cost`, `_terminal_cost` and `_deferred_energy_cost`. Neither the body nor either harness mentions the fourth (`grep -ci wood` on the body prints 0, and prints nothing on both harnesses). The fourth seam is in the tree at this head:
- `custom_components/heatpump_optimizer/wood_fuel.py:148`: `wood_sek < finite_float(price, 0.0) / cop_f`
- `wood_fuel.py:226`: `pump = finite_float(prices[i], 0.0) / cop`

The COP there is `thermal_model.compute_cop(outdoor)`. `wood_fuel.py` imports neither `partload_factor` nor `heat_per_cop_kw`. Under a part-load derate this under-prices pump heat, the same secant error the body measures elsewhere. The wood "cheaper" flag, `cheaper_hour_count` and the night advice therefore read wood as cheaper less often than it is.

This is fix-review.md step 6: a seam the issue states that is neither in the diff nor dispositioned in the body. To cure it, either measure it (the same 16 installs x 2 price days x 2 derates, with the zero-derate null) and dispose of it, or route it with its control in `## Carry for the roster` with a stated reason. The R10-SAV-COMFORT carry already appended at 4092d06bc names only the three seams.

## Findings

- The wood advisor's pump-heat price (`wood_fuel.py:148`, `:226`) is a linear valuation under a convex part-load cost that this PR neither measures nor dispositions (see `## Block`). Carry: R10-PARTLOAD-RESIDUE
- Follow-up: `r10_partload_residue.py refill` has no positive control, only the zero-derate null. Mutant `k_r = 0.0`, which drops the derate from the error, leaves every `d=0.112` row at `0.000000`, prints `null rows not zero 0` and exits 0 (`ev/refill_mutant_positive.txt`). A broken error term would read as "immaterial", and the harness would pass. The null is also structural: `heat_per_cop_kw` returns its input exactly while `cop_partload_derate` is 0, so `k_r` is 0 by construction. A guard that every `d>0` row has `max > 0` would make the harness refuse that mutant. Carry: R10-PARTLOAD-RESIDUE
- Residual: carry 1's 272 s owner-box outlier is refused on non-reproduction in 80 seeded solves. No harness or recorded input in the tree reproduces the owner's case, so neither this review nor the body can establish its cause. The refusal rests on the synthetic owner shape alone, which the body states. Carry: dismissed: no in-tree input reproduces it; re-opens only from a diagnostics bundle (D15), which this group does not hold

## Evidence

- RESULT head 8bef9bc866a7458b19dbc00d0bf4ed07ed2f206a; merge base 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76. `git merge-tree --write-tree origin/main HEAD` exits 0 (origin/main 53273de4d), and the ledger driver merged `tests/closures.json`. `## Head` names this head, and its tree equals 306a0b76e, where the body's carry-2 figures were taken.
- RESULT the three-dot diff touches no `custom_components/` line, `VERSION`, `RELEASE_NOTES.md` or `tests/structure_budgets.json` (`git diff --quiet` passes). The 3 files are the harness, `dev/programme/delivery/3291.md` (present) and one `INERT` line in `tests/closures.json`. With no production line, the mutation proof is n/a by design.
- RESULT measured inputs identical: `git diff --quiet` on custom_components, r10_buffer_store, r10_partload_pricing, r10_cop_partload, r10_setpoint_boost and tests/profiles.py passes for b4ec2f332..306a0b76e and for 4b5d771bd..8bef9bc86.
- RESULT finder's harness `r10_partload_pricing.py` at the merge base and at the head: the outputs are identical (`ev/pricing_base.txt`, `ev/pricing_head.txt`).
  - `flat d=0.112 lp_err max 0.267290 (dhw cost max 7.0145) terminal-at-max max 4.368455 deferred-at-max max 2.139841`
  - `spread d=0.112 lp_err max 0.173106 (dhw cost max 8.0681) terminal-at-max 3.723135 deferred-at-max 0.963508`
  - both `d=0.0` rows at 0.000000, `null rows not zero 0`, rc 0
  - Every body digit matches. 0.267290/7.0145 = 3.81 %. The horizon is 96 steps of 0.25 h, so "per horizon" is per 24 h here.
- RESULT `refill` at the head (`ev/refill_head.txt`):
  - flat: terminal-at-P_r max 3.714491, deferred 0.792466, ratio max 0.79001
  - spread: 2.117798, 0.486127, ratio 0.08194
  - `null rows not zero 0`, rc 0
  - Every body digit matches. "Not immaterial" is justified: 3.71 per horizon is about half the 7.01 daily hot-water cost, and one cell's terminal error is 79 % of its predicted cost. Reserving the decision for the savings seat is consistent with `_terminal_cost`'s binding docstring.
- RESULT null-control mutant `k_r += 1e-6`: `null rows not zero 32`, rc 1 (`ev/refill_mutant_null.txt`). The null arm refuses as claimed.
- RESULT `relaxed`, pinned to `taskset -c 0` on this host (`ev/relaxed_pinned.txt`): `clamped solves 32: solve_s p50 0.574 max 2.858; relaxed_pass_s p50 0.130 max 0.452`, null 0 relaxed runs, rc 0.
  - The delta_s regrouping by `clamped` is my own (`ev/delta_stats_pinned.txt`): clamped p50 +0.254, min +0.017, max +0.856; unclamped -0.298..+0.254.
  - Absolute times cannot be re-derived digit-for-digit. This host is an `Intel Xeon @ 2.10GHz` (`ev/host.txt`) against the body's 2.30 GHz Granite Rapids, and it reads about 1.3-1.5x slower.
  - The body's noise-floor claim does not hold cleanly here: the unclamped spread (to +0.254) overlaps the clamped p50. The refusal does not depend on it. It rests on `relaxed_pass_s`, measured inside the pass, max 0.452 s, and on the null's 0.000 s.
  - The worst solve, 2.858 s, is 0.48 % of 600 s. Even at this slower host x 6.8 it is 19.4 s, so the maxiter refusal holds.
- RESULT `buffer 20`, pinned to `taskset -c 1` (`ev/buffer_pinned.txt`):

  | arm | p50 (s) | max (s) |
  |---|---|---|
  | 750 L spread | 1.241 | 2.379 |
  | 750 L flat | 1.200 | 1.729 |
  | 0 L spread | 0.667 | 1.164 |
  | 0 L flat | 0.620 | 1.005 |

  The ratios are 1.86x and 1.94x (body 1.87x and 1.93x) and the price lever 1.08x (body 1.15x). The ratios reproduce; the absolute seconds are host-bound. The worst solve is 0.40 % of budget, so the refusal holds.
- RESULT the budget is `config_flow.py:1736` `_number(10, 120, ...)`, so the minimum is 10 min = 600 s. Confirmed.
- RESULT the Pi factor 6.8x (Geekbench 6 ratio) is cited from external pages, which I did not re-fetch. Not verified here; the verdict is robust below 210x on this host's worst solve.
- RESULT cheap checks at the head (`ev/cheap_checks.txt`, `ev/entities.txt`):
  - `ALL 112 HARNESS HEADER CHECKS PASSED`
  - `STRUCTURE RATCHET PASSED`
  - entities: `every tracked file is either measured or deliberately classified` ok
  - 3 of 2645 entity checks failed locally: the coverage cache, the release ZIP build and the Pages workflow probe. They are environment-bound and read nothing this diff touches; CI's `tests / closures` is authoritative.
- RESULT forward-carry: R10-SAV-COMFORT's `carry` at 4092d06bc holds "From PR 3291, body item 213e8a10", with the zero-derate precondition and control. It names the three seams only, as the Block says.
- RESULT CI on this head, all check-run pages (`ev/checkruns.tsv`, 64 runs): `merge_train.py classify` returned `RED ... red: gate` (rc 1). Both `gate` runs, 128574120853 and 128575220710, failed with `FAIL run(s) [42429084301] at this head are still being judged; their gate decides` (`ev/gate_*.log`). That is a gate deferral, not a defect. Code run 42429084301 then concluded `completed success` (`ev/coderun.txt`). The re-classify at 01:03:33 UTC printed `GREEN 8bef9bc866a7458b19dbc00d0bf4ed07ed2f206a pending: none red: none`, rc 0 (`ev/classify3.txt`). The head is still 8bef9bc86 at that read. This block does not rest on CI.
- RESULT `## Red checks` reads the checks at d5f8f410c, not at this head. At this head the only concluded reds are the two deferral gates above. Re-state them at the next head.
- RESULT the instruments are disclosed as the fixer's own: `r10_partload_residue.py`, which is new and lands. The finder's harness is `r10_partload_pricing.py`, already in the tree.

## Friction

- The brief asks for `handoff-wip` pushes at milestones, while the payload says to push nothing but the probe ref. I pushed only the probe ref.
