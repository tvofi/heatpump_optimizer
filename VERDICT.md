Fix review: blocked b55fc8eb5bfce6a3c2022314116d0b19d1a901e6 pin-missing: fold state across a hass refresh and focus return to the dialog copy of a header are claimed in the body but unpinned; mutants R1 and R2 survive tests/card.mjs

bus-nonce: 561e6cbe79fd65fe8438be412ba6ea95
pending-ci: gate

Round: first review (round 1), full scope. Measured head: b55fc8eb5bfce6a3c2022314116d0b19d1a901e6. At post time it is still the tip of fix/r10-card-collapse (git ls-remote).

## Block

- **R1 survives.** The body's design decision says fold state "survives every plan-refresh rebuild". Adding `this._folds = { narrative: false, whynow: false };` to `set hass` (heatpump-optimizer-card.js:15215) resets every fold on each hass update, and `tests/card.mjs` stays green (rc=0, 0 FAIL). No check in the suite sets a second hass while a fold is open. This is the plan-refresh survival the brief asks for. The production code does keep the state: the reviewer probe shows aria-expanded `true,false,true,false` both before and after a fresh hass. The property is just unpinned.
- **R2 survives.** The body says "Focus returns to the rebuilt copy of the pressed header", and the headline renders twice when the dialog is open (4 `[data-fold]` heads). Replacing the index lookup with `this.shadowRoot.querySelector(`[data-fold="${key}"]`)` sends focus to the card copy behind the modal dialog. `tests/card.mjs` stays green. The `collapse: focus returns to the rebuilt header` check clicks only the card copy, with the dialog closed. The browser lane's `cardCollapse` also presses only `ha-card [data-fold]`. The production code is correct: the probe shows a click on dialog copy index 2 returns focus to index 2 of 4. A one-key regression to the obvious selector would pass every lane, though.
- **What clears it.** Two checks in the R10-CARD-COLLAPSE block of `tests/card.mjs`, each re-proved with its mutant (R1, R2 as in `ev/mut_driver.py`):
  1. Open a fold, set a new hass, and assert the fold is still open.
  2. Open the dialog, click the dialog copy of a header, and assert `activeElement` is that copy (index 2 or later) and not the card's.
  Production code needs no change.

## Findings

none beyond the block

## Evidence

- RESULT `PYTHONPATH=tests/hastub node tests/card.mjs` at head: `ALL CARD CHECKS PASSED`, rc=0 (`ev/card_head.txt`; needed `tests/plan_view.py` first, `ev/plan_view.txt`).
- RESULT `PYTHONPATH=tests/hastub node tests/card_drift.mjs`: `card_drift: 44 state(s) moved and claimed, 1 identical`, rc=0 (`ev/card_drift_head.tail.txt`, tail of a 17 MB log). This matches the claim block in `tests/golden/card_claimed_drift.txt`: every rendering state is claimed, and editor_schema is identical. claims-for stays 7.1.10 = VERSION.
- RESULT `python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok` (`ev/claims_only.txt`).
- RESULT `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
- RESULT `python3 tools/audit/archscore/score.py --diff dbd1ab5b0712ebc51e29ef8c001a2c0ef68af3cd`: `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`). This re-derives the body's figure. The `card_clone_copies` 103 -> 108 intermediate is not re-derived, because it was at a superseded head.
- Mutants re-created at the head, each run through `tests/card.mjs` and restored (`ev/mut_driver.py`, `ev/mutants_all.txt`):
  - NULL (comment edit): SURVIVED, as a null must.
  - M1 KILLED (5 FAIL), M2 KILLED (19), M3 KILLED (6), M4 KILLED (1), M5 KILLED (1), M6 KILLED (5), M7 KILLED (2). The killing checks match the body's named checks.
  - Reviewer's own mutants:
    - R3 aria-expanded always "false": KILLED (2).
    - R4 why-now lead picks the weakest driver: KILLED (1).
    - R5 body rendered while folded: KILLED (3).
    - R1 and R2: SURVIVED (see Block).
  - The M4 anchor string occurs twice in the file, so the driver anchors it with the preceding fold-handler line. The first pass was cut off at that assertion (`ev/mutants_firstpass_partial.txt`) and resumed from M4.
- Reviewer probe (`ev/reviewer_probe.txt`, `ev/reviewer_probe_note.txt`): with the dialog open the shadow root has 4 fold heads and no duplicate `id`. This confirms the no-id/aria-controls decision: no duplicate ids in the doubly rendered headline.
- Keyboard: the headers are native `<button type="button">`, so Enter and Space arrive as click. The browser lane's `cardCollapse` checks Enter, then Tab and Space, in light and dark. Not re-run here: no scope selects that lane, and CI's `tests / browser` is cited instead (fix-review step 11).
- docs/dashboard-card.md claims, checked against the code at the head:
  - Folded summaries (the kWh and cost total, else the first line; the strongest driver).
  - Both folds start folded on page load; each toggles on its own.
  - Screen readers hear the expanded state (`aria-expanded`).
  - The chips and footnote appear only in the enlarged view.
  - The why-now driver list (price rank, comfort floor, forecast, mold guard, away) equals the five `whynow.driver_*` keys at card.js:921-933.
  - README and docs/index.html carry the same sentence.
  - All hold.
- `git merge-tree --write-tree origin/main b55fc8eb5bfce6a3c2022314116d0b19d1a901e6`: rc=0, no conflict (`ev/merge_tree.txt`).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched in the three-dot diff.
- CI: `merge_train.py classify` still prints `WAIT ... pending: gate red: none` after more than 40 min of polling at 60 s+ intervals (`ev/classify.log`, `ev/classify.txt`).
  - `tests / nightly-status` is red. It is outside the required set that `merge_train.py owed-reds` prints (`ev/owed_reds.txt`), so it is not this PR's and is owed no answer.
  - The body's `## Red checks: none` is consistent with that.
- There is no finder harness: this is an owner request, and the body says so. The before-and-after is the PR's own `tests/card.mjs` block. Not re-run at the merge base: the base renders no `[data-fold]`, and that is evident from the diff.
