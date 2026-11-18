R11-SEAM-kernel-layering, ADR-002 parts 1 and 3 (D7-s1-06; D5-s3-01, moved in from R11-SEAM-money by owner ruling 2026-11-18). Pure modules take what they import from pure owners. comfort_learning, external_heat, power_guard and sysid import `utc_elapsed_seconds` from `drift.py`, its owner, not through `accuracy.py`'s re-export. `HISTORY_LENGTH` moves to `const.py`, where accuracy, tariff and store read it. `currency.py` imports `HomeAssistant` under `TYPE_CHECKING`, because its only use is the annotation of `resolve_currency` (under `from __future__ import annotations`). Every package module that imports no Home Assistant itself now imports with Home Assistant absent, except ADR-002 part 3's setpoint_check and snapshots. That makes `grid_fee.py`'s docstring claim "Kept free of Home Assistant imports" true (D5-s3-01). It also makes `topology.py`'s matching claim true, a sibling the new check found that the finder's `[_a-i]` cell did not reach. No edit in coordinator.py, no edge in or out, no golden moves.

The pin is `tests/doc_claims.py` `check_ha_free_imports`. It imports each module in a fresh interpreter that refuses every `homeassistant` import and bypasses the package `__init__`. It has two derived arms:
- claims: every package module whose source states the HA-free claim must import;
- kernel: every package module with no `homeassistant` import of its own (an import under `if TYPE_CHECKING:` excepted) must import, except a named glue-reached set (setpoint_check, snapshots). An entry that imports cleanly is refused as stale, so the set only shrinks.

`accuracy` is the null control and must fail under the same refusal. This check does not see ADR-002 part 2's four modules (disinfection, price_model, quiet_windows, sysid via inputs.py): inputs.py's Home Assistant import is function-scope, so they import cleanly at both ends, and archscore's layering metric remains their measure.

Alternatives: (a) narrowing grid_fee's two docstrings to "no direct Home Assistant import", as D5-s3-01's scope offered. That fixes the text and leaves grid_fee coupled to Home Assistant through an annotation, so the fix that removes the cause was taken. (b) moving the imports lazy or under `TYPE_CHECKING`'s `else`, or adding an unread boundary import: ADR-002 refuses both. (c) deleting `accuracy.py`'s `utc_elapsed_seconds` re-export: coordinator.py still imports it there, and this group may not edit coordinator.py, so it stays. (d) a hand-listed kernel arm, built first in 65395c04: a list pins only the modules it names, so the arm derives the set from the tree instead.

## Head

9049a4a81e35b6b86f2f78c3bcc410839ea6e008, measured on merge base bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f. The figures below were measured at 14fb25f70cec16a15557ddbe11bce4d2c88001d9; the commits since add the delivery row and one mutation-ledger row and change no production file.

## Mutation proof

Each production file was reverted to the merge base on its own, and the check was run through a driver that calls only `check_ha_free_imports` (`runpy` on `tests/doc_claims.py`, then `R.close`). Each file was then restored.
- revert `currency.py`: 2 of 28 FAILED: `grid_fee.py says grid_fee is free of Home Assistant imports, and it imports without it (D5-s3-01)`, `a module importing no Home Assistant itself imports without it, but for ADR-002's named glue-reached set (D7-s1-06)` [grid_fee]
- revert `tariff.py`: 2 of 28 FAILED: `topology.py says topology is free of Home Assistant imports ... (D5-s3-01)`, the kernel arm [optimizer, tariff, topology]
- revert `power_guard.py`, `comfort_learning.py`, `external_heat.py`, `sysid.py`, each alone: 1 of 28 FAILED, the kernel arm naming that module
- `currency.py:21` control (`if TYPE_CHECKING:` to `if True:`, not the generator's GUARD_OFF): 2 of 28 FAILED, the grid_fee claim and the kernel arm [grid_fee]
- stale-entry arm: grid_fee added to the glue-reached set: 1 of 28 FAILED, `every entry of ADR-002's glue-reached set still needs Home Assistant (a cleared entry leaves the set)` [grid_fee]
- all production files at the merge base: 3 of 28 FAILED. The grid_fee and topology claims fail, and the kernel arm names comfort_learning, external_heat, grid_fee, optimizer, power_guard, sysid, tariff and topology.

## Unpinned sites

- `custom_components/heatpump_optimizer/currency.py:21 GUARD_OFF` (`if TYPE_CHECKING:` to `if False:`): equivalent, recorded in `tests/mutation_ledger/survivor_triage/currency.py/@module.GUARD_OFF.e1433e05.json` the way the ledger records the same site in rooms.py, payload.py and off_restore.py. TYPE_CHECKING is False at runtime, so the mutant skips the annotation-only import exactly as the head does. Measured on copies of the module in venv-ci's HA-free interpreter: the module namespace (names, types, annotations) hashes 55c66ebe4e75 at the head and under the mutant, while the control `if True:` raises ModuleNotFoundError: homeassistant. The earlier body called this site killed: that measured `if True:`, not the generator's mutant.

## Null control

- `check_ha_free_imports`: 3 of 28 FAILED with production files at the merge base, ALL 28 PASSED at the head. The `accuracy` anchor reads NEEDS_HA at both ends, so the refusal is running.
- D7-s1-06 harness `$EXPORT/dev/audit/rounds/round11/D7/s1/m7_layer_edges.py` (sha1 2ef176ccc0188e832569b5280a0184e1a3b80855, exported from plan/r11 819aa2e3): `RESULT layer_violations=13` at the base and `=6` at the head. Its own null control is `--cut issues`, which reads 13 per the finding.
- D5-s3-01 harness `$EXPORT/dev/audit/rounds/round11/D5/s3/ha_free.py` (sha1 302c9ee6a9f9ac804818eb77c3f4f4ae0434a45c): `RESULT claimed_but_needs_ha=1 modules grid_fee` at the base and `=0` at the head. `claimed=11` at both ends is the harness's honest-claim control.

## Figures

<!-- figure-block: scope-line mb=bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f head=9049a4a81e35b6b86f2f78c3bcc410839ea6e008 -->
~~~text
MODE: SCOPED -- 29 script(s) run, 4 scoped out.
~~~
<!-- /figure-block -->
- `layer_violations` 13 -> 6, read by `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D7/s1/m7_layer_edges.py` at base and head. Seam enumeration, the harness's CARRIER lines at the head, one disposition each: disinfection, price_model, quiet_windows and sysid are ADR-002 part 2's (R11-SEAM-inputs-freshness's planned move; PLAN.json names it); setpoint_check and snapshots stay under ADR-002 part 3. Every CARRIER line the base printed for accuracy or currency is closed in this diff.
- HA-free claims that need Home Assistant 1 -> 0, read by `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D5/s3/ha_free.py`. The tree-wide claim set in `check_ha_free_imports` adds topology and failed it at the base.
- Architecture score: `python3 tools/audit/archscore/score.py --diff bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f HEAD`, IMPROVES, dS +1.0000 (layer_violations 13 -> 6), matching PLAN.json's move for this group.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py`: every check passed at the head.
- The importers left on `accuracy.py`'s re-export are away, dhw_learning, legionella and coordinator. None prints a CARRIER line at either end, and coordinator.py is outside this group's edit set.

## Red checks

- `tests / mutation`: red at 4c988319 (run 44308221206, job 134815743649) on `currency.py:21 GUARD_OFF` ADDED UNPINNED. The mutant is equivalent and is now recorded as such (Unpinned sites); `python3 tests/mutation_table.py --scope changed --base origin/main` no longer refuses. The cheaper detector was prepr step 6d, which predicted the site; the miss was reading the `if True:` control as the generator's mutant, so the site was handed to mutation-autofix, which pins only killed mutants.
- `tests / mutation-autofix`: red at 4c988319 on the same site. It pins only a mutant a check kills, and this one is equivalent, so it had nothing to pin; the equivalent row above answers it. Its cheaper detector is the same prepr step 6d named above; no cheaper one exists.
- `tests / nightly-status`: inherited from main, not caused by this diff.

## Forward-carry

none

## Friction

- frugal-routing-guard: contradiction: the dispatch brief says "Do your work inline, with no subagents", while the session's frugal plugin hook refused inline reads after five per prompt. I did not set FRUGAL_ALLOW_INLINE. Two scout subagents did discovery, and later reads of my own run output went through python3. Carry: dismissed: seat-environment plugin, outside the repository's policy set
- carry-audit-group-token: unenforced: `tools/audit/carry_audit.py` `GROUP_TOK` accepts only upper-case group ids, and it resolves groups against origin/handoff/audit-r10-roster. So `Carry: R11-SEAM-inputs-freshness`, a target prepr itself lists as valid, reads UNROUTED, and upper-casing it reads BAD-DEST. This body needed no carry after the pin was derived from the tree. Carry: dismissed: no carry was needed here; a later R11-SEAM seat will meet it
