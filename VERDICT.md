Fix review: merge 264162c0d754bb24e4e41d24027c005cb779327e

bus-nonce: 1a761d368288ebeed6235a19c79bdc9f
pending-ci: gate

## CI state

Round 1 (first round: no reviewed head). The review is complete; the head's CI has not concluded. Run 43915602612 (`CI code pr=3677`, head 264162c0d754bb24e4e41d24027c005cb779327e) ended `cancelled` at 17:43:20Z, with `tests / fast (3.14)`, `tests / mutation`, `tests / closures` and `tests / coverage` unconcluded. The orchestrator's inbox command `CMD 1 NOTE` says it cancelled the runs at this head (17:45-18:00Z) to free runners and will re-run them within the hour; a cancelled check is a wait. I checked this independently: neither the PR head nor origin/main (6f422812d5d8b918beace0283419c153f6df66ce) moved. Every later `gate` fails only with `FAIL tests: no run at this head judged base 'main'`, classify read `RED ... pending: none red: gate` from 17:54Z, and at 18:06:38Z it read `WAIT 264162c0d754bb24e4e41d24027c005cb779327e pending: gate red: none` (the re-run is under way). I return `merge` with `pending-ci: gate`, as the brief's pending-ci route allows: the relay posts it only once CI is green at this head and refuses it over a red, so a real red from the re-run still stops it.

## Red checks

- `gate` (owed-reds): a cancellation, not a failure. The orchestrator cancelled the code CI run at this head (CMD 1), so no run judged base `main`. It is not a defect of the branch and no detector applies; the re-run decides, and the relay's pending-ci gate enforces that. `tests / nightly-status` failed too and is not in the `owed-reds` set, so it owes no answer.

## Findings

- Note: figure: the body's class census says "At the base (M1, M2): all 10 simulate_plan comfort and hot-water bounds are open". Running the body's own rule (every `number` selector probed one step past each bound against its registered validator; `ev/census.py`) at the merge base gives 16 open bounds on 8 comfort and hot-water fields (`ev/census-base.txt`). I cannot re-derive "10". Carry: dismissed: a paperwork figure in the body; the check it describes is the committed one and the head result (0 open outside the dispositioned seams) is what I measured
- Note: figure: the body's M2 lists four failing checks; at M2 I measured `5 of 2725 ENTITY CHECKS FAILED`, the fifth being the in-check null control (`null control: an unbounded comfort_weight ...`), which also fails because the base tree adds findings beyond the planted two. The kill holds either way. Carry: dismissed: a paperwork count; the mutant is killed as claimed
- Note: harness: the finding (roster item R11-SERVICE-SCHEMA) names no committed finder harness (the packet: `Finder's harness: none named`). The class check the fixer committed in `tests/entities.py` (r11-service-schema blocks) is the builder's instrument, not the finder's; it carries its own planted null control and a 348-case spelling corpus with production as oracle. I re-ran it, and my own independent census (`ev/census.py`), at base and head. Carry: dismissed: the fixer's check is committed in the tree and is the only harness this roster item has; disclosed here as the builder's per fix-review.md step 9

## Evidence

- HEAD: `ev/HEAD.txt`. The live head is 264162c0d754bb24e4e41d24027c005cb779327e (`git ls-remote`: refs/heads/fix/r11-service-schema and refs/pull/3677/head), so no head moved.
- Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty (the merge base is origin/main, 6f422812d5d8b918beace0283419c153f6df66ce).
- Merge: `git merge-tree --write-tree origin/main 264162c0d7` exits 0 (tree 7a4dd1a1248d1dce2b90d315ed241ebeb82bb856). No conflict.
- The body's measured SHA: de4769fd1e0956cfce1b527d5e99a2ce522ba9b7. `review_carry.py de4769fd1e 264162c0d7` prints `CARRY`: the head adds only the main merge 0b519edd5f and the delivery-row commit.
- VERSION, the manifest and RELEASE_NOTES.md: untouched in the three-dot diff. No golden or claim file is in the diff, so step 4 has nothing to compare.
- Head: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2725 ENTITY CHECKS PASSED` (`ev/entities-head.txt`), which matches the body.
- Mutation proof (step 1), each run on the full `tests/entities.py` in a head worktree (`ev/mutant-*.diff`, `ev/entities-m*.txt`):
  - M1 (the body's): `services.py` and `config_flow.py` at the base. Result: `2 of 2725 ENTITY CHECKS FAILED`, the class check and its null control. KILLED.
  - M2 (the body's): `services.yaml` at the base. Result: `5 of 2725 ENTITY CHECKS FAILED`: the R10 selector check, the class check, the null control, the no-dated-example check (listing set_away.return_time and apply_manual_plan.space_slots/dhw_slots/expires_at) and `a5:service_bounds ... yaml edges`. KILLED.
  - M3 (mine): simulate_plan `target_temp` back to bare `vol.Coerce(float)`. Result: `2 of 2725 FAILED` (`simulate_plan.target_temp: accepts 4.5`). KILLED.
  - M4 (mine): services.yaml simulate_plan `comfort_weight` selector max 20 -> 40, with the schema left alone. Result: `3 of 2725 FAILED` (the R10 selector check and the class check, `selector 0.1..40`). KILLED.
  - M5 (mine): simulate_plan `dhw_min_temperature` -> `_float_range(20, 70)`, which drifts from apply_schedule. Result: `2 of 2725 FAILED` (`accepts 34`). KILLED.
  - The three `option_range` ledger pins (BOOLOP, GUARD_OFF, RAISE_DEL -> tests/config_flow_steps.py) are as the packet's ledger diff shows; per fix-review.md 11 the heavy mutation table is CI's to cite. Its run at this head was cancelled, which is the block above.
- Class (step 6), rule as the body names it, run independently with `ev/census.py`:
  - At the head: 35 open probes (`ev/census-head.txt`). simulate_plan has 5: `silent_mode_power_fraction` (1), `wood_price_sek_m3` (2) and `wood_furnace_efficiency` (2). apply_schedule has `silent_mode_power_fraction` (1). set_thermal_parameters has 29 probes on 23 fields, matching the body's "29 bound seams".
  - Every one is dispositioned by name in the body and in `_SS_EXEMPT`, or is carry 2 or carry 3 (owner questions, with `Carry: R11-SERVICE-SCHEMA` naming a pending owner ruling, the fixer.md exception). No seam is open and undispositioned. class-open: none.
  - At the base: 51 open probes.
- A user-facing regression check on the new refusals: the card's only `simulate_plan` call (`heatpump-optimizer-card.js` `overrides()`) sends `target_temp` and `comfort_temp_day` from a 16..24 slider, which is inside 5..30, and `dhw_min_temperature` from `DHW_MIN_FLOOR` 35 up to the published ceiling, which is inside 35..55. No other in-tree caller goes through `SERVICE_SCHEMA_SIMULATE_PLAN`. The narrower schema refuses nothing the card sends.
- Figures re-derived at the head:
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, `const_modules_over_50 3 <= 3` (`ev/structure.txt`).
  - `python3 tests/closure.py select --diff 6f422812d5`: `MODE: SCOPED -- 22 script(s) run, 11 scoped out.`, which matches the figure block (`ev/closure-select.txt`).
  - `score.py --diff 367c3b9cac HEAD`: `Architecture score: dS +0.0493 IMPROVES`, `literal_clone_copies 118 -> 114` (`ev/archscore.txt`). Step 14: earned. The four removed copies are the `vol.All(vol.Coerce(float), vol.Range(...))` literals now shared as `_COMFORT_TEMP_C`, `_DHW_SETPOINT_C` and `_DHW_MIN_TEMP_C`, a real de-duplication between the what-if and the save path.
  - The D6 claims harness, regenerated at the head: rc 0 and the tree stays byte-identical, so C22 `examples=9` holds.
- Architecture (step 15): `config_flow.option_range` makes the options table the one owner of the four options-only ranges. services.py already imported from config_flow (`identity_update`), so no new dependency edge. No breach.
- Step 16: no actuator-write path is added; the change is a schema-level refusal of a what-if input.
- CI (`ev/classify-log.txt`): WAIT from 17:23Z, then RED `red: gate` from 17:44Z with one interval of WAIT at 17:46–17:53Z, then RED again. Last line: `RED 264162c0d754bb24e4e41d24027c005cb779327e pending: none red: gate`. Concluded green at this head: `instrument-self-tests` (success at 17:42:48Z, so no introduced red), `policy-docs`, `env-matrix`, `wave-script`, `briefs`, `closure-scope`, `typing`, `browser`, `arch-instrument`, `arch-score`, `budget-raise-gate`, `hassfest`, `validate-hacs` and all three codeql analyses.
- review_packet's refusal `introduced-red: unreadable ... instrument-self-tests ... in_progress` is superseded: that job concluded success.
