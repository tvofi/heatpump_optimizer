# Round 9 judge: dedup (Phase C step 1)

Judge: round-9 Phase C judge seat, 2026-09-26. Input: 156 registered findings (register @089d3470),
panel PANEL.json (111 unanimous, 41 split, 3 disputed, 1 killed), predup.json (6 candidate clusters).
Rule (judge.md): a finding is merged into a canonical one only where the canonical's perturbation
moves the merged finding's harness too. A shared class or a shared file is not enough; those are
recorded below as siblings to fix together, not merges.

Killed at panel, out of the batch: **D1-s2-01** (three refutes with executed numbers; stub-only).

## Merges (7): 156 - 1 killed - 7 merged = 148 canonical

| canonical | merged | evidence that the canonical's perturbation moves the merged harness |
|---|---|---|
| D2-s3-01 | D8-s1-01 | judge run `tools/audit/round9/judge/cross/d8_under_d2.py`: D8-s1-01's price15.py with D2-s3-01's perturbation (the seam's 1 h span -> 15 min, inside `_current_spot_price` only): `wrong_quarters` 95 -> 0, worst_abs_error 0.30 -> 0.00. Same symbol, same mechanism. |
| D12-s3-01 | D4-s2-04, D12-s1-02 | judge run `tools/audit/round9/judge/cross/under_d12s301.py` (flow_paths.py's `explicit_presence` copied verbatim): D4-s2-04 zones_default.py `two_zone_expert_defaults` 1 -> 0 (null `two_zone_describe_defaults` 0 -> 0); D12-s1-02 phantom_dhw.py `options_hot_water_dhw_plan_steps` 9 -> 0, `options_hot_water_tank_dhw_plan_steps` 9 -> 0, `wizard_dhw_step_dhw_plan_steps` 9 -> 0 (control 0 -> 0). One phenomenon: presence inferred from keys that untouched form defaults write. |
| D1-s2-54 | D6-s1-04 | D6-s1-04's own perturbation `--perturb=clamp_expiry` is D1-s2-54's `--clamp` (expires_at capped at now + MANUAL_PLAN_WINDOW_HOURS), recorded to_zero on D6-s1-04's harness (manual_pin_hours_beyond_20 4 -> 0). D1-s2-54 names D6-s1-04 as its doc half. |
| D6-s2-05 | D5-s1-06 | Same five wood_* fields. D5-s1-06's perturbation (strip wood_* from SERVICE_SCHEMA_SIMULATE_PLAN) is exactly verifier G4-V3's replacement perturbation for D6-s2-05 (`tools/audit/round9/D6/verify-v3/s2_05_own_perturb.py`); judge run: `simulate_plan_schema_only` 5 -> 0. Canonical kept as D6-s2-05 per J.md; the batch uses the v3 perturbation because the finder's own does not move its metric. |
| D11-s1-04 | D11-s2-03 | D11-s1-04's `--perturb reattribute` (seat-given reviews carry a distinct identity) is D11-s2-03's in-harness perturbation; judge run of owner_review.py on its committed snapshot: seat_counted_as_owner 6, perturbed_seat_counted 0. G4-V3 agrees (one phenomenon, I3). |
| D14-s2-02 | D4-s2-02 | D4-s2-02's single count (wood-price widget labelled SEK/m3 on an EUR instance, 1 of 4 money fields) is D14-s2-02's cell B (`B_money_widgets_off_instance[EUR]=1 of 4`), the same measurement; D14-s2-02's seam rule enumerates it and its fix scope names it. |

(7 merged ids in 6 rows.)

## Carried as disputed, merge decided after the re-run

- **D0-s2-01** (disputed) is the ftol=1e-6 stop that **D14-s3-02** measures as its metric's reference
  (production candidates re-run at ftol 1e-12). Setting production's ftol to 1e-12 (D0-s2-01's
  perturbation) makes D14-s3-02's gap zero by construction. Both stay in the batch; if D14-s3-02 is
  verified, D0-s2-01 is merged into it.

## Not merged: siblings to fix together (distinct perturbations)

| findings | why not one | fix note |
|---|---|---|
| D8-s1-03, D12-s2-01 | D12-s2-01's perturbation patches `_power_to_heat_pump_schedule` only; D8-s1-03 reads `get_current_action`'s `heat_pump_on`, so it does not move. | Same on-threshold rule at both seams (D12-s2-01's seam rule lists both). The fixes conflict: D8-s1-03's "publish 0 when off" would hide D12-s2-01. Fix D12-s2-01 at both seams first; D8-s1-03 then re-measures. |
| D8-s2-02, D8-s2-03 | Different mechanisms (label from mode vs torn write); predup low. | G2-V3: D8-s2-03's fix conflicts with D8-s2-02's. One fixer, one PR. |
| D12-s1-01, D12-s1-02 (now in D12-s3-01) | Different seams: DHW start state vs DHW presence. | Same plant area; D12-s1-01 stays its own finding. |
| D1-s5-01, D1-s5-51 | Different functions (`age_of` precedence vs `_age_gate` threshold). | Same module, one fixer. |
| D1-s2-51, D1-s2-91 | D1-s2-51's fence covers its two seams; D1-s2-91's harness calls `_record_accuracy` directly, which that fence does not reach. | Same property (G1-V3: P2, same phenomenon); D1-s2-51's seam rule lists the `_record_accuracy` call. Fix together. |
| D1-s5-52, D1-s1-03, D1-s2-02 | Different boundaries (InputReader, DHW learner, weather forecast); each harness drives its own. | One class: a live or external value with no physical-plausibility bound (3 instances). |
| D1-s1-04, D1-s3-05 | Different stores (cusum/snapshot/curve vs boost). | One class: a persisted future instant trusted without bound. |
| D14-s1-01 and D1-s1-01, D1-s1-02, D1-s3-01, D1-s3-03, D1-s2-03 | D14-s1-01 is the P1 class detector; its perturbations are upward controls, not fixes. The D1 findings are instances at seams it lists (best_restore, pump_arbiter._load, naive stored stamps). | Phase D sweeps P1 once; the fix plan clusters these. |
| D1-s1-52, D3-s1-91 | D1-s1-52 is the stub clock; D3-s1-91 is a test gap whose fix is a scenario, not the stub. | Fixing D1-s1-52 alone does not add the missing scenario. |
| D2-s4-01, D14-s3-03, D2-s4-81, D7-s2-01 | Different bias sources (noise and anchor; free-heat prior; bar; Euler roll). | One class, P5. |
| D5-s1-01, D6-s2-01, D6-s2-02 | Each harness counts a different stale fact in configuration.md's Initial setup section. | One doc rewrite. |
| D5-s1-05, D6-s1-02 | Labels vs pages, different docs. | One doc PR. |
| D7-s1-71, D5-s2-03 | Duplicated constant vs a comment. | Fix together. |
| D12-s3-81, D14-s2-02 | Bounds vs labels. | Same class, P8. |

## Conflict ruled: D6-s1 non-finding vs D6-s2-03

Not comparable. D6-s1 checked "0.5 K/week" as a config-default equality (the shipped default equals
the documented figure); D6-s2-03 checked it as a runtime bound on `CurveLearner.record_day`
(0.6 K accrued in a 7-day window). Both can be true at once. The judge decides on D6-s2-03's own
runtime measurement, re-run in the batch; D6-s1's non-finding stands for what it measured.
