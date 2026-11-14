Fix review: blocked 22e9330193f147e8b02b0171890b9c338ef6b0e3 reference-basis-unbumped: the diff changes the booked savings reference behind a valve but leaves ledger.REFERENCE_BASIS at 1, whose own definition is the removed steady-demand spread

bus-nonce: 06b928f51a6c4e4ccb145654e9ded7ee

## Block

Round 1 (first round), measured at head `22e9330193f147e8b02b0171890b9c338ef6b0e3`, merge base `50373173d486faf394b24637c177ab38b691b394`.

`custom_components/heatpump_optimizer/ledger.py:73-75` at this head:

    #: The reference in force: a heat-pump thermostat with no wood tank and no fire,
    #: its horizon spread by steady demand. Bump when the booked reference changes.
    REFERENCE_BASIS = 1

- Basis 1 is the spread reference. `REFERENCE_BASIS = 1` and the spread (`_apportion_by_steady_demand`) were introduced in the same commit, a9f8cb2b50 (R10-HOTFIX-SAV-ESTIMATE). Both are in the released v7.1.15: its `ledger.py` holds the same three lines, and its `optimizer.py` names `_apportion_by_steady_demand` twice (`ev/reference_basis.txt`).
- This diff removes the spread, so the booked reference changes for every valved install. The PR's own golden drift measures the move in `baseline_cost`: eight valved fixtures, in both directions. Examples: `valve_storage_low_target` 113.037 -> 115.889 and `valve_storage_small_tank` 128.370 -> 126.962.
- The diff does not touch `ledger.py`. `git diff 50373173...HEAD -- custom_components/heatpump_optimizer/ledger.py` is empty, so `REFERENCE_BASIS` stays 1 and its comment now describes code that no longer exists.
- Consequence, read from the code at this head and not run as a probe:
  - `add_savings_settlement` stamps the basis only on a month's first booking (`ledger.py:369-370`, `setdefault`).
  - The monthly row withholds savings only when `meta_mean(key, REFERENCE_BASIS_META) != REFERENCE_BASIS` (`ledger.py:513-516`).
  - So a month that a v7.1.15 install began under the spread reference, and finishes after upgrading to this code, keeps stamp 1 and still equals `REFERENCE_BASIS`.
  - It therefore states one savings figure summed over two different references. The basis mechanism exists to refuse exactly that mix (`ledger.py:67-70`: "a month's totals cannot be rebooked").
- `ledger.py` is in this group's roster `files` (`dev/programme/rosters/wave-r10-groups.json`, group R10-SAV-VALUATION-RESIDUE). The bump is in scope for this PR.
- What clears this block:
  - Bump `REFERENCE_BASIS` (and its comment) in this PR.
  - Pin the bump with a check that fails at this head. For example, a month stamped with the prior basis states no saving after the change.
  - Or record in the body an owner's ruling that this reference change does not warrant a new basis.
- Note for whoever traces this: R10-SAV-COMFORT p4 (b3114866c8) changed the spread (it capped it) without bumping the basis either. I did not establish whether that change was released between two tags, so I make no claim about it.

## Findings

none

## Evidence

- Mutation proof, re-run. The mutant is this head with `optimizer.py` restored from the merge base, which puts back the spread and its call (`ev/mutproof_wtm.log`). The command is `features_block.py` from the marker `from profiles import house as _hb_house` to `# The start's settlement, at its limits`, with a prelude emitted at the head (`ev/prelude_a.log`).
  - Mutant: `FAIL behind a valve, the booked reference's first step holds its held state [power 1.4408104309112266; room 19.399999999999636 -> 19.399999999999636, slab 23.599999999999568 -> 23.599999999999586, tank 25.99999999999953 -> 26.16979405144286]`, `1 of 11 FEATURES BLOCK FAILED`, rc=1.
  - Head: `ALL 11 FEATURES BLOCK PASSED`, rc=0 (`ev/mutproof_wt.log`).
  - The FAIL line matches the body's. The body's mutant count `1 of 15` does not re-derive: I measured 11 checks in both arms.
- Residual attribution, `r10_sav_residual_attribution.py flat` (sha1 4b214a9b..., the head's copy run in both trees):
  - Base: `+6.84 %`, `non-steady -6.83; reference stored +11.11 kWh_th`, `plant steps seen 192 of 192` (`ev/attr_flat_wtb.log`).
  - Head: `+4.03 %`, `reference stored +0.00 kWh_th`, `plant steps seen 192 of 192` (`ev/attr_flat_wt.log`).
  - These match the body. The comfort (+6.18 kWh_e) and stored (-5.07 kWh_e) terms are identical at both ends, which matches the body's null control.
  - The winter_typical arm was not re-taken: the base run was still running when I wrote this. Carry: dismissed: evidence, not a finding
- Census (base figure `worst first-step dS +0.0000`): not re-run by me. Unverified.
- The Carry 9 and Carry 10 figures, and the restated-pin null control (`state = initial_state` mutant, 9 of 9 failing): not re-run. Unverified.
- Golden fixtures, `GOLDEN_MODE=drift tests/golden.py` at the head: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`, `NO STALE FIXTURE`, rc=0 (`ev/golden_drift_head.log`).
- Fixture drift, `env_drift.py --all 50373173...`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE`, rc=0 (`ev/env_drift_all.log`).
- I did not check that each of the eight claims moves.
- Structure, `tests/structure.py` at the head: `ok class_excess_loc 17470 <= 17470`, rc=0 (`ev/structure_head.log`). The move is earned: the 33-line method was deleted.
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. The three-dot name list does not include them.
- Merge with main: `git merge-tree --write-tree origin/main 22e93301...` gives tree 4e5f7510..., rc=0. No conflict.
- Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Head check: the body names `22e9330193f147e8b02b0171890b9c338ef6b0e3` as the head and `b48274c195` as the authored code head. The extra commit adds only `dev/programme/delivery/3574.md`.
- The body contains a literal `@@GATE@@` placeholder in `## Figures`, apparently never rendered.
- CI, from `merge_train.py classify ... --pr 3574`, which polled from 23:59 to 00:06 UTC (`ev/classify.log`): last line `WAIT 22e9330193f147e8b02b0171890b9c338ef6b0e3 pending: gate red: none`. CI was still pending when I returned this block. The block does not rest on CI.
- Class enumeration (step 6): I found no other caller that re-spreads by steady demand. `_floor_demand_at_target` is now called only at `optimizer.py:800, 916, 993`, inside the held-state builders.
