Fix review: merge 8d3708cde00393bd9f3ce2dc51dee828fede975d

bus-nonce: d778591a9e0a6969c46ab63d35065074

## Round

Round 2 (delta review) of PR #3169, part 1 of the split #2259 work. Head 8d3708cde00393bd9f3ce2dc51dee828fede975d, merge base a9c149289922e92bae57cad87afc4abd3ef6c235 (= origin/main at review). Judged from detached worktrees at both SHAs, through the three-dot diff.

## Findings

- awaySignature (heatpump-optimizer-card.js:5854 at the head) still spells `${id}:${st.state}:${st.last_updated || ""}`. It is a fifth near-copy of the state-and-stamp signature part, with a different separator and the entity id in front. This PR scopes itself to the four `state@last_updated` copies and does not claim to close the class. Part 2's generic census should read it or rule on it. Carry: #2259
- The part-2 group `r10-archscore-spellings-p2` is not yet in `dev/programme/rosters/wave-r10-groups.json` on origin/main or on any remote ref. The body hands that roster cut to the orchestrator. It is owed after this merge so that #2259 keeps an owner. Carry: #2259

## Evidence

- RESULT history: `git merge-base --is-ancestor 4b6ea5ec <head>` is false, so the prototype is absent. The three-dot range holds b51dc761f, which is the round-2 delta over the round-1 head b22cc1e60.
- RESULT body: says "Part of #2259; this does not close it". It records picker_open/char_width_inline/no_plan_state, the 4-copies-to-1-helper count, and part 2 in Forward-carry with a roster destination. `## Head` names 8d3708cd…. Its "Merge base dfb4ce2b5 … main was not merged" sentence is about the code head b51dc761f. The head itself also merges origin/main a9c149289, and the same section says so.
- RESULT null control (my own 10 inputs, ev/null-control.txt). Inputs: null, undefined, an ISO stamp, empty state and stamp, null state, a unicode state "Ünïcødé ☃ 温度", missing stamp, null stamp, 0 stamp, and a state containing '@'. The helper equals the former headline copies on all 10. It equals the former advisor/health copies on 7. It differs only where `last_updated` is missing, null or 0: before it printed `x@undefined`/`x@null`/`x@0`, now `x@`. The body discloses this (its inputs 6 and 7). It is harmless because a signature is only compared for equality with itself across renders, and Home Assistant always writes an ISO `last_updated`.
- RESULT mutation (tests/card.mjs at the head, plan payload from tests/plan_view.py at the head; ev/mutant-*.txt):
  - A: dropping the stamp in stateSignature is killed: `UX-7: the render signature follows the model status sensor`.
  - C: advisorSignature mapped to "-" is killed: `the card's render signature includes the advisor sensors`.
  - D: healthSignature's sig made state-blind is killed, with 3 fails (Input Problem sensor, waiting sensors, UX-7).
  - B: swapping the field order inside the one helper passes. B is an equivalent mutant: the four copies are now one function, so no copy can diverge from another, and the swapped key is still injective over the same inputs. Clean head: ALL CARD CHECKS PASSED, rc 0 (ev/card-head.txt).
- RESULT card_drift: `node tests/card_drift.mjs a9c149289` gives "identical in all 45 states", rc 0 (ev/card_drift.txt).
- RESULT archscore (instrument at the head): `score.py --diff a9c149289` gives `Architecture score: dS +0.0275 IMPROVES`, `card_clone_copies 105 -> 103` (ev/archscore-base-to-head.txt). The census reads card_rule_copies 72 at the head; the base instrument has no such metric (ev/census.txt).
- RESULT metric-gamed check (step 14): I ran the round-1 card.py (b22cc1e60) and the head card.py on both trees' card source. clone_copies and rule_copies return identical classes: 105/72 on the base card and 103/72 on the head card (ev/refactor-equivalence.txt). So the `_units`/`_classes` refactor moves no number, and the whole dS comes from the card change. Removing the card change (base card, head instrument) gives back 105.
- RESULT planted red-team 46, applied to a copy of the head: card_rule_copies 72 -> 73 and card_clone_copies 103 -> 103, so it still rises as calibration/expected.json records (WORSENS) (ev/rt46.txt). The vector.py, counters.py, ABOUT.md and expected.json hunks are unchanged from the round-1 head, apart from the merge of main.
- RESULT standing (ev/standing.txt):
  - Claim files, VERSION, manifest.json and RELEASE_NOTES.md are byte-identical to the merge base.
  - No host path appears in the added lines.
  - The only budget-file change is the new row `archscore.card_rule_copies: 72`. It is the tree's own count, a new metric rather than a raise, and budget-raise-gate is green.
  - The delivery row dev/programme/delivery/3169.md is in the three-dot diff.
  - tests/closures.json names red-team 46 in both closures.
- RESULT merge: `git merge-tree --write-tree origin/main 8d3708cd…` gives rc 0 and tree 9cbdb28e7e42, so there is no conflict.
- RESULT CI: `merge_train.py classify 8d3708cd… --pr 3169` printed `GREEN 8d3708cde00393bd9f3ce2dc51dee828fede975d pending: none red: none`, rc 0 (ev/ci-classify.txt). The live check-run set has no concluded red run, so step 11 owes nothing at this head, and the body's `## Red checks: none` holds. The head is still 8d3708cd… on fix/r10-archscore-spellings at verdict time.
