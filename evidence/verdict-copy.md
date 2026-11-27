Fix review: merge 8c7272935e9af94fe00729924851c7ba1f780c83
bus-nonce: b36db71c1ecb3c104ec686ad7a6526df

Round: 1 (full scope, first review). Measured from a detached worktree at 8c7272935e9af94fe00729924851c7ba1f780c83, merge base 190ffb10c230b6beaf77593b2926d55682e37f47. The live head is unchanged.

Note: design-placement: ADR-011 decision 2 puts a pin beside the existing checks of the same behaviour where there are any, and uses tests/guard_pins.py only otherwise. tests/features.py already checks some of the same behaviours: the _smooth_topk_sum clamp at features.py:4337, and a non-finite PeakTracker.from_dict at features.py:9380. Even so, all 39 pins went to tests/guard_pins.py and the body does not say why. This is a test-placement question with no production or architectural effect, and each pin kills its own mutant where it sits, so it is a note and not a block.
Carry: dismissed: test placement only; ADR's fallback home, kills verified in place
Note: red-checks: the body's `## Red checks` reads none. The live checks at the head show two gate reds (jobs 140283339521 and 140297407363), each printing "FAIL run(s) [45930754726] at this head are still being judged; their gate decides". Those are deferrals, and the later gate run 140313514451 is green. They also show tests / nightly-status red: main's scheduled nightly run 45731557683 failed on nightly-ha (2025.2.0), nightly-ha (stable) and slow. That check is unrequired, and this tests-only diff did not cause it.
Carry: dismissed: evidence, not a finding
Note: style: two blank lines inside the dict in `_money_pins()` carry trailing whitespace. This is cosmetic.
Carry: dismissed: cosmetic whitespace in a test file

## Evidence

- Step 1 (mutation proof): I re-ran 10 of the 39 ledger anchors myself at the head with `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --anchor '<anchor>' --scripts tests/guard_pins.py`. Each printed `killed by tests/guard_pins.py`, and its NULL_COMMENT null control survived. The 10 are grid_fee apply_catalog GUARD_OFF and RETURN_DEL#3, max_abs_component, min_component, parse_rules, price_model CONST 0f3977a9, prices_from_entity_state BOOLOP, and tariff marginal_price_per_kw plus both _smooth_topk_sum GUARD_OFFs. I stopped the other 29 for time and did not verify them myself; for those, the body's per-anchor table and CI's green `tests / mutation` stand as cited.
- Removal control (step 14): I ran five anchors against the base's tests/guard_pins.py (apply_catalog RETURN_DEL#3, CONST 5633f4fc, observe_day GUARD_OFF#2, _profile_index CMP_BOUND, _smooth_topk_sum CLAMP_DROP). Every one printed LIVES, so these pins earn the ledger rows and the instrument does not.
- Unpatched head: `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` printed ALL 130 GUARD PIN CHECKS PASSED, 39 of them R11-D3-PINS-money.
- Class (step 6): D3-FOLD.json at e8aefbb452 lists 40 findings in R11-D3-PINS-money. Compared with the `_pin_<key8>` functions, only b5a48246 lacks a pin. The body says it is a non-finding: the guard moved into `_usable_day`, where ledger row `_usable_day.CMP_BOUND.fc735ea9.json` (killed_by tests/features.py) and features.py:48223 already cover it. I confirmed both.
- Pins drive production entry points and assert outcomes; none re-states a production expression or patches production.
- Steps 4 and 5: no golden or claim file changed. `env_drift.py --claims-only <merge-base>` is ok. VERSION, the manifest and RELEASE_NOTES.md are untouched. No file under custom_components/ is in the three-dot diff.
- Ledger `layout_problems`/`completeness_problems` returned [] []. `tests/structure.py` printed STRUCTURE RATCHET PASSED.
- Step 13: `git merge-tree --write-tree origin/main HEAD` exited 0.
- Step 2: the body names no committed finder's harness. The judge's probes are cited by sha1 from an export, and they mutate in memory, so they read flat at both ends by construction. The companion is each pin's FAIL under its patch, which my kills above reproduce.
- Step 10: forward-carry none. Step 16: no actuator path.

RESULT mutation: 10/10 re-run anchors killed at the head, null held; 5/5 sampled live at the base
RESULT class: 40 findings = 39 pins + 1 verified non-finding
RESULT checks: required green; gate reds are deferrals; nightly-status unrequired, inherited
