Fix review: merge f0068ae2fcd781d34d56320bec51432d2b71432b

bus-nonce: 1dfe5659d9baa05e829d6ee2bb340f9a
pending-ci: gate

## Round

First round (review_packet: "Review scope: full (first round: no --reviewed-head)"). Merge base bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f; `dev/governance/roles/` has no diff between the merge base and origin/main 9fe63d00, so the contract read is current.

## Evidence

- Mutation proof (step 1), re-run at the head with my own driver `ev/drive.py` (runpy on tests/doc_claims.py, `check_ha_free_imports` only, `R.close`); output `ev/mutation_proof.txt`. Head: ALL 28 checks PASSED. Each production file reverted to the merge base alone: currency 2 of 28 FAILED (grid_fee claim, kernel arm [grid_fee]); tariff 2 of 28 (topology claim, kernel arm [optimizer, tariff, topology]); power_guard, comfort_learning, external_heat, sysid 1 of 28 each (kernel arm naming that module); const 2 of 28 (topology claim, kernel arm). All production files at the merge base: 3 of 28 FAILED, kernel arm naming comfort_learning, external_heat, grid_fee, optimizer, power_guard, sysid, tariff, topology. These match the body's figures exactly.
- store.py and accuracy.py reverted alone pass, as expected: accuracy re-exports HISTORY_LENGTH from const, so either half of the move works alone. The body does not claim either one is pinned.
- currency.py:21 `if TYPE_CHECKING:` -> `if True:` (control): 2 of 28 FAILED. `-> if False:` (GUARD_OFF): ALL 28 PASSED. This confirms the ledger row records an equivalent mutant: the guarded block holds only an annotation import, under `from __future__ import annotations`.
- Stale-entry arm: grid_fee added to `_HA_REACHED_THROUGH_GLUE` makes 1 of 28 FAIL ("cleared, remove from the set: ['grid_fee']").
- Claims arm planted: an HA-free docstring claim prepended to coordinator.py makes 1 of 29 FAIL (coordinator NEEDS_HA). The claim set is derived from the tree, not listed.
- Finder harnesses (step 2): exported from 819aa2e3; the sha1 of each matches the body (m7_layer_edges.py 2ef176cc..., ha_free.py 302c9ee6...). Run with `PYTHONPATH=tests/hastub` at the merge base and at the head; output `ev/finder_harnesses.txt`. m7_layer_edges `RESULT layer_violations=13` at the base and `=6` at the head; `--cut issues` reads 13 and 6. ha_free `RESULT claimed_but_needs_ha=1 modules grid_fee` at the base and `=0` at the head; `claimed=11` at both ends; `--perturb` at the base moves it to 0, so the harness responds to its own perturbation.
- Class enumeration (step 6): the head's CARRIER lines are disinfection, price_model, quiet_windows, setpoint_check, snapshots and sysid (sysid via quiet_windows only). The body dispositions all six: ADR-002 part 2's four and part 3's two. Every CARRIER line the base printed for accuracy, currency or tariff is gone. No seam is open.
- Claim spelling widened beyond `_HA_FREE_CLAIM`, with a case-insensitive pattern that also matches "free of any" and "no Home Assistant" (`ev/claimset.py`, `ev/claimset.txt`; my own definition). The derived set is 24 modules. Widening adds duty_switch and entity, which are not import claims, plus manual_plan and rooms, which import cleanly and are covered by the kernel arm. It also adds snapshots: see Findings.
- Structure, archscore, protected files: `ev/cheap_checks.txt`. `tests/structure.py` prints STRUCTURE RATCHET PASSED and no `*_budgets.json` is touched. `score.py --diff bc658f9d HEAD` prints dS +1.0000 IMPROVES, layer_violations 13 -> 6. A three-dot diff of VERSION, manifest.json, RELEASE_NOTES.md and both claim files is empty (steps 4, 5). No path under `tests/golden/` is in the diff, so no fixture moved and no claim is owed.
- Step 14: the only figure that moves is layer_violations. It moves only through the import edges the diff changes: reverting those files restores the base's carriers, as the per-file reverts show. tests/closures.json, INERT and every budget are untouched. The mutation-ledger row is an equivalent mutant I re-measured above.
- Step 15: the added lines are import moves and one constant relocated to const.py. coordinator.py is not edited, so the `accuracy.utc_elapsed_seconds` re-export it still uses stays, as the body's alternative (c) states. Nothing here breaches layering.
- Step 16: no actuator write path is touched.
- Step 13: `git merge-tree --write-tree origin/main f0068ae2` exits 0 against origin/main 9fe63d00, so the head merges cleanly.
- Step 7: the body's `## Head` names f0068ae2fcd781d34d56320bec51432d2b71432b, the head I measured.
- Step 11: the body answers the reds at 4c988319 (`tests / mutation`, `tests / mutation-autofix`). It names prepr step 6d as the cheaper detector and the misread `if True:` control as the miss. `tests / nightly-status` is red and is not in the `merge_train.py owed-reds` set, so it is neither answered nor a block.
- Step 9: the finder's harnesses are committed on plan/r11 (819aa2e3), not on main. The in-tree pin is `check_ha_free_imports`, which is the fixer's instrument and is disclosed as theirs.
- CI on this head: `ev/classify.log`. `merge_train.py classify` printed WAIT (exit 3) from 15:01 to 15:35 UTC, last `WAIT f0068ae2fcd781d34d56320bec51432d2b71432b pending: gate red: none`. Classify printed no red, so the merge verdict is posted only once CI is green at this head (`pending-ci`).

## Findings

- Note: claim-coverage: `snapshots.py`'s docstring says "this file needs no Home Assistant to test", but snapshots does not import with Home Assistant absent (NEEDS_HA through store). `_HA_FREE_CLAIM` does not match this spelling. Snapshots is in the PR's dispositioned ADR-002 part 3 glue-reached set, and the stale-entry arm forces it out of that set once it is cleared. The docstring's wording is part 3's to settle with the move. Carry: dismissed: dispositioned in the body as ADR-002 part 3's seam, which the stale-entry arm pins until cleared
- Note: test-mutant-survivor: in `tests/doc_claims.py`, `_imports_ha_itself`'s TYPE_CHECKING exemption can be disabled (`node.test.id == "NEVER"`) with all 28 checks still passing. currency then leaves the kernel set, but the claims arm still reaches it through grid_fee. Disabling the `Refuse` finder (`return None`) also passes all 28, because venv-ci has no homeassistant installed (`import homeassistant` raises ModuleNotFoundError). The refusal is defence for an interpreter that does have it. Neither changes a production verdict. Carry: dismissed: test-side redundancy, no production line unpinned
- Note: style: store.py adds `from .const import HISTORY_LENGTH` below price_tiles, although `from . import const as c` is already there. comfort_learning.py now carries two `from .drift import` lines. Carry: dismissed: cosmetic, no behaviour
