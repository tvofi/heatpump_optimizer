Root-cause record for the `tests-red` block class: five fix reviews blocked on a red unit within 24 h (`bottleneck_check.py`: `tests-red 33% (5/15 blocks) vs 30%`, first-pass yield 0.38). Adds `dev/audit/rca/r11-tests-red-at-review.md` only. It names the cause, process state (c), the cost test and the countermeasure, per `root-cause.md`. It leaves the filed issues open and files none. No production code, policy file or budget file is touched.

Findings in the record:
- Upstream cause: a merge of main yields a tree nobody gated. For 3 of 5 the red is a stale hand-kept count (the #1218 pair note; also the HA-free module count in one). That class is `R11-RCA-PAIRNOTE-MERGE` and is not re-analysed.
- This record's cause: the dispatch refusal in `bus.sh dispatch` asks `merge_train.py classify`, which judges `Train.required()` (`gate` alone), so a unit red such as `tests / fast` is unseen until `gate` concludes.
- Countermeasure: the dispatch call passes `gating_names(req)` less `budget-raise-gate` and `tests / mutation`. Mid-round it is a proposal (`P-R11-DISPATCH-UNIT-REDS`) plus a local overlay.

## Head

c0eb1e9c8becb88064a8d6d3515e69f3e39fef64

## Mutation proof

n/a: documentation record, no production or test code changes. The replay in the record's section 7 is the equivalent: the overlay reads `UNIT-RED tests / fast (3.14)` at #3866 `6fb0f76a` and #3838 `d7029ade`, and `CLEAR` at the repaired heads.

## Null control

The overlay read `CLEAR` on 20 of 20 merge-verdict dispatches between 2026-11-25T04:01Z and 16:34Z, and an unreadable head prints `UNREAD` with rc 2, never `CLEAR`. The variant that also holds on `tests / mutation` held 1 of those 20 and stays off.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
