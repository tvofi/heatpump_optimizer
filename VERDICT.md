Fix review: merge b392956a14ea5f0f59a07e3805b15eeb8b7082ec

bus-nonce: 40f5cd3df85ea45fca0eb45c5eb82b4f
pending-ci: gate

## Summary

Round 3. This is a delta review over the reviewed head 3fa750ea3861bf623ea3ff58e8e514321c511b52, measured at head b392956a14ea5f0f59a07e3805b15eeb8b7082ec. `review_carry.py` prints FRESH-REVIEW, so the scope is the delta (fix-review.md step 12).

The delta has three parts:
- Main merges.
- Three stacked product heads: 3532 fd5fe52fa7, 3562 ced9b23358 and 3556 fe11888ad6. The owner ruled on 2026-11-14 that they may be stacked, and the body states this pull request merges only after them.
- This pass's own two commits, f5fd6426ab and 254f0ed03e. They touch docs/configuration.md, docs/setup.md, docs/how-it-works.md, docs/dashboard-card.md and tests/doc_claims.py (`check_late_delta_claims`).

The authored delta changes no production line, so the review does not widen. The stacked heads' production code comes in only through their own pull requests' merges, and their own reviews and CI judge it, not this one.

The previous verdict (round 2, at 3fa750ea38) had no findings, so nothing is outstanding from it.

## Findings

none

## Evidence

- Head measured: b392956a14ea5f0f59a07e3805b15eeb8b7082ec (ev/HEAD.txt). It is the same head as the body's `## Head`.
- Merge resolutions are clean. `git show --remerge-diff` of c8d2d289c9, 1fa71adc14, 69afda819f and b392956a14 shows no hand edit. The only output is the ledger driver's `LEDGER-MERGE: resolved tests/closures.json` (ev/remerge.txt).
- doc_claims at the head: ALL 368 checks PASSED, rc 0 (ev/doc_claims_head.txt). That is 356 plus 12, as the body says. The five `check_late_delta_claims` null controls each print ok.
- Mutation proof, re-run by me (ev/mutants.txt). Each mutant fails its named check, and every file was restored afterwards: ALL 368 PASSED, `git status --short custom_components` empty.
  - M1 `wood_mean_temperature` `top - 3.0`: rc 1, wood rows FAIL in both docs/configuration.md and docs/setup.md.
  - M2 `dhw_step_target_c` with `rounding='up'`: rc 1, cycle FAIL (driven 65.0).
  - M3 `FLOW_BIAS_CLAMP_K = 10.0`: rc 1, bias FAIL.
  - M4 `FLOW_SUPPLY_MAX_C = 80.0` (my own addition): rc 1, bias FAIL.
  - M5 `leg_rule` `first = "dhw"`: rc 1, split FAIL.
  - M6 `GridFeeSchedule.from_config` `if True:`: rc 1, fee FAIL.
  - M7 `wood_mean_temperature` returning `bottom` when the top is None (my own addition): rc 1, wood FAIL on both pages.
- The changed sentences were read against executable code at the head by a subagent seat I dispatched and spot-checked by me. These are TRUE:
  - quick setup's device page, where an empty pick skips (config_flow.py `async_step_device_prefill`)
  - comfort temperatures (optimizer.py `get_comfort_temp`, `comfort_targets`)
  - the solar sensor's current reading (coordinator.py)
  - the upper-floor emitter on two-zone only, and the heavy floor in house mass (presets.py)
  - `resolve_with_fallback` name matching
  - the energy meter's two readers
  - `apply_catalog` sets the rules mode and switches the peak tariff on
  - disinfection above the charge limit (`dhw_hard_max_temp`)
  - the flow-bias bounds 15 K and 75 °C (flow_lift.py `observe`)
  - the wood one-probe readings
  - the fixed fee is ignored under None
  - the planned start count is not published
  - the both-step leg order and the 5-minute plus median-off merge (duty_legs.py `SPLIT_MIN_MINUTES`, `both_step_legs`)
  - the learner phases and the 12 h settle tail after a full 2 h boost (const.py `BOOST_SPACE_SETTLE_TAIL_HOURS`, boost.py `settle_tail`)
- Wording observation, not a defect. The space-heating set-point row says a boost writes "the entity's own maximum (see below)", while `pump_arbiter._boost_ceiling_c` returns `min(caps)` of that maximum, a non-default `flow_heat_c` and the controller's upper limit, and returns None outside the gate and 70 °C. The row points "see below" to the flow-ceiling row, which states that cap. I read it as a summary with a pointer, not a false claim. Carry: dismissed: evidence, not a finding
- The old-basis sentence in docs/dashboard-card.md matches `MonthlyLedger.savings_months` (`old_basis = meta_mean(REFERENCE_BASIS_META) != REFERENCE_BASIS`). It is conditional ("when an update changes how the baseline is booked"), so it holds at this head's `REFERENCE_BASIS = 1` and at 3574's `2`.
- Re-derived figures:
  - `closure.py select --diff <merge-base>`: `MODE: SCOPED -- 30 script(s) run, 3 scoped out.`
  - `--diff 69afda819f`: `MODE: SCOPED -- 4 script(s) run, 29 scoped out.` The body names four scripts (ev/scope.txt).
  - `doc_claims.py --markers --user`: `0 user-doc marker(s), 0 due`.
  - STRUCTURE RATCHET PASSED (ev/structure.txt).
- Not re-derived: the body's local entities (2713), harness_headers (115) and md_tables results. I cite CI for these.
- VERSION, manifest.json and both claim files are untouched against origin/main (three-dot diff empty). No golden fixture moves.
- Merge with main: `git merge-tree --write-tree origin/main b392956a14` rc 0, with origin/main at 1791869fdb.
- Role contract is current: `git diff mb...origin/main -- dev/governance/roles/` is empty.
- Red checks: `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`. The body's `## Red checks` answers the stacked heads' historical reds as theirs. The CI state at this head is in the classify lines below.
- Ordering: the three stacked heads are not on origin/main (`git merge-base --is-ancestor` fails for fd5fe52fa7, ced9b23358 and fe11888ad6). The body's `## Head` says this pull request merges only after them, and the train must honour that.
- CI: `merge_train.py classify b392956a14 --pr 3568` printed `WAIT b392956a14ea5f0f59a07e3805b15eeb8b7082ec pending: gate red: none` on every run from 11:54 to 12:24 UTC, 30 runs (ev/classify_poll.txt). No required check reads red, so this verdict returns with `pending-ci: gate`. The PR head was still b392956a14 at 12:24 (`git ls-remote origin refs/pull/3568/head`).
