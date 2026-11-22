# BLOCKED: r11-owner-extheat-override (#3862)

Seat: cloud fixer. Base: origin/main baa9a467ac518bc3f8733d2603ea8ae406b235af.
Design: ee6bb4da3329dcf1ba16e6a40fd63ef80cdba289 (verdict 5d7384e5, approve).
Code state: 663cfb94 and this BLOCKED.md commit on top, parent chain from baa9a467. Not handed off;
no handoff/ or handoff-body/ ref pushed.

Question: three rulings are needed before handoff; each blocks prepr.sh or the approved shape.

1. Card group not on main. R11-OWNER-CARD-EXTERNAL-HEAT has a design and verdict
   (design/R11-OWNER-CARD-EXTERNAL-HEAT 6ed233f9, design-verdict d9e94890) and
   no fixer head; `git log origin/main` holds none of it, and
   `grep -n external_heat custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`
   at baa9a467 finds only the health-input strings. The design is merge-gated
   `after` it and this group owns the statusPill reconciliation (evidence 6c,
   mutation target `block_ignored !== true`). Hold this group until the card
   group merges, or hand off without the card clause and carry it to the card
   group's brief?

2. Entity-name family (#1760) against the owner's name (Q9). Translation key
   `external_heat_ignore_block` puts the switch in the `external` family; its
   name "Override External Heat Block" (en; sv "Åsidosätt blockering vid extern
   värme", de "Sperre bei Fremdwärme übersteuern") sorts away from "External
   Heat Source", so tests/entities.py's "every declared family sorts as one
   contiguous run in every shipped language (#1760)" fails in en, sv and de
   (`_FAM_SPLIT_ALLOWED` is empty and says a split waits for an owner ruling).
   The only in-tree escape, an `ENTITY_FAMILY_OVERRIDES` entry homing the key
   in a one-member family, is what this ref carries now and archscore refuses
   it: `tools/audit/archscore/score.py --diff <merge-base>` prints
   `family_orphan_overrides 0 -> 1` (gate only, inadmissible; counter C6).
   Options: (a) a name that leads with the family word, e.g. "External Heat
   Block Override" (owner's Q9 wording changes); (b) the owner allows
   en/sv/de `external` in `_FAM_SPLIT_ALLOWED`; (c) a translation key whose
   lead token is not `external` (the unique key and entity id unchanged), which
   departs from the design's "unique and translation key". Which?

3. Ratchet: `python3 tests/structure.py` at this head prints
   `FAIL class_excess_loc 17325 > 17317 (+8)`. The design's ratchet section
   expected a fall; it priced only the coordinator class, but
   `ExternalHeatDetector` was already over GOD_CLASS_LOC_LIMIT (300) at base
   (span 309, measured by an `ast` walk of class end_lineno - lineno + 1), so
   every line of `ignore_effective`/`blocking`/`view` the design puts on it
   counts. Payments taken: `_decay`'s two identical zero-and-return branches
   merged (-3), the three new methods compacted, `_external_heat_view`'s body
   moved off the coordinator (-4 net with the extracted local at the solve
   site); measured result +8. Payments refused as not improving the code:
   re-flowing multi-line expressions (`_external_heat_config`'s
   `interval_hours`, `_update_displacement`'s None test). Archscore also
   reads `coord_footprint 2525 -> 2530` (the three `boost.extheat_block_ignored(self)`
   reads the design specifies). Under the mandate a raise is the
   orchestrator's to rule (HANDOVER.md "The mandate"): approve a +8
   `class_excess_loc` raise, or name a payment?

## What is built and measured on this ref

- boost.py: `BoostState.ignore_extheat_block`, `extheat_block_ignored`,
  `set_extheat_block_ignored` (awaits the restore gate), store key only while on,
  restore adopts it before the gate opens.
- external_heat.py: `ignore_effective`, `blocking`, `view`; `as_dict(block_ignored)`
  publishes the key only when given.
- coordinator.py: solve state `external_heat_active=self._external_heat_active
  and not block_ignored` (cache kept); forecast gate `blocking(...)`;
  `_external_heat_view` delegates; 5203, 3757, 6844 untouched.
- switch.py: `ExternalHeatIgnoreBlockSwitch`, no RestoreEntity; a shared
  `_KeyedSwitch` base now carries the keyed `__init__` for it, AwaySwitch and
  TimedDutySwitch (archscore `shape_copies` 38 at base, 37 here).
- binary_sensor.py, diagnostics.py (`external_heat_block_ignore` row),
  payload.py, strings/icons/translations, README, docs.
- tests/features.py "#3862" block: 20 checks, every one with its switch-off or
  detection-off twin; fails at base (`AttributeError: 'ExternalHeatDetector'
  object has no attribute 'blocking'`); passes here.
- Mutation (features_block.py over the #3862 block): M1 `and not`->`and` in
  `blocking` 5 checks fail; M2 drop `and self.config.enabled` 3; M3 drop the
  `is not None` guard in `as_dict` 3; M4 forecast gate back to `.suppressing` 1;
  M5 solve term dropped 3; M6 solve `and not`->`and` 6; M7 store guard `if True` 2;
  M8 restore line deleted 1. Switch `async_turn_on` and the binary sensor
  key guard are pinned in tests/entities.py, not yet mutation-run.
- dev/audit/harnesses/solve_inputs_parity.py (sha1 e77213759f4b2c2d685d9ade3ec43b7e7b717b56)
  at baa9a467 and at this head: output byte-identical (`diff` exit 0).

- tests/entities.py at 70737a32 against baa9a467 (FAIL lines compared by
  `comm` of the two logs' sorted FAIL names; the base log's FAIL lines are
  its own self-test negatives, rc 0): two new FAILs. "EG-B3: Payload declares
  exactly the keys the producers publish" (the census could not follow
  `_external_heat_view` into the detector; fixed at 663cfb94 by resolving a
  listed returned view; the rerun at 663cfb94 no longer prints it). "and main() passes the committed table at its own
  recorded count (the null control)": `ci_ratchet.main()` grades the
  `archscore.*` rows, which question 2 and 3's archscore regression reddens;
  it clears with whichever ruling removes `family_orphan_overrides` and the
  footprint growth, or with their re-record.

Not yet run: the rest of the 30-script scope `tests/closure.py select` names,
goldens in drift mode, prepr.sh.
