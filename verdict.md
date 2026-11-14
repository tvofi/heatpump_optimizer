Fix review: merge 2ef5531223d56cc35d40fbbcb8f8d61ede644c57

bus-nonce: 9d90ce63f65294ddf6e0c0a1cbd8dab1
pending-ci: WAIT 2ef5531223d56cc35d40fbbcb8f8d61ede644c57 pending: gate red: none

## Findings

- `advisor.optin_sensor_off` is a key this pull request adds, and it has no row of its own in `dev/audit/rounds/round10/user-text-card.md`. Its claim is judged only inside the sweep row for `advisor.optin_heading` (record :417). I verified that claim on code. `WoodBurnAdvisorSensor` (sensor.py:3011), `MonthlyPeakSensor`, which carries `fuse_advisor` (:2130), and `FrequencyAdvisorSensor` (:2809) each set `_attr_entity_registry_enabled_default = False`. No code under custom_components/ writes `disabled_by` or calls `async_update_entity`. Check (5) pins the claim. So the text is true, and the gap is the record's bookkeeping only. Carry: dismissed: claim verified on code and pinned by card.mjs check (5); a record row adds no control

## Evidence

- Round 2, a delta review over the reviewed head f11bdd4d483c0509ad108b0e00112aaae8f1368d. Head measured: 2ef5531223d56cc35d40fbbcb8f8d61ede644c57. The PR's live head when read matched it, and so does the body's `## Head`. Merge base: e23124ff6e45bac1d48b4a775dad555a37965355. The role drift check, `git diff $(merge-base)...origin/main -- dev/governance/roles/`, is empty.
- The delta has three parts:
  - The fixer's commits 3e6d23ffe6..741f378bfd: card.js, card.mjs, the record, the new harness `r10_card_evidence_kinds.py`, one closures.json INERT entry, and a delivery row.
  - Two merges, 04f36e2e54 (origin/main in) and 2ef5531223. Each committed tree equals `git merge-tree --write-tree` of its parents: cda4d02d and 801fb086 (ev/merge-resolutions.txt). So there are no hand resolutions, and the main-side files (tools/audit/seat/*, tools/ci/selftest_closures.json, delivery rows) are main's own.
- Merge with current main: `git merge-tree --write-tree origin/main 2ef5531223` gives rc 0. origin/main was 50373173d. The closures.json ledger driver printed `LEDGER-MERGE: resolved` (ev/merge-tree.txt).
- Widening (step 12): the production delta is card.js only. It is a `{band}` placeholder fed from `refit.band_percent`, a new `advisor.optin_sensor_off` string, and a suffix on the opt-in rows. I widened to exactly the data path the card now reads. `heat_loss_refit` always publishes `"band_percent": REFIT_BAND_PERCENT` (accuracy.py:776). The sensor's `extra_state_attributes` is the advice dict as published (sensor.py `_advice`), so `attrs.refit.band_percent` reaches `restartRows`. A missing or non-finite value renders "—". No other already-reviewed code is touched.
- Prior block 1, comment evidence (resolved):
  - `advisor.refit_detail` now renders `±{band} %` from the published `band_percent` in en, sv and de.
  - The record moves the row to the Corrected table as false. Its evidence is code: accuracy.py:651, :776, coordinator.py:3278, accuracy.py:659-663 and services.py:1220-1227.
  - Own run of the builder's sweep `python3 -I dev/audit/harnesses/r10_card_evidence_kinds.py <record>` gives `rows 360 flagged 0` at the head. As its null control, the same run on the record at f11bdd4d4 gives `rows 360 flagged 29`, including `advisor.refit_detail` (ev/sweep-head.txt, ev/sweep-f11bdd4-record.txt). Both reproduce the body.
  - This harness is the fixer's instrument, not a finder's, and it is in the tree.
- Prior block 2, surviving mutant (resolved): the source regex is replaced by driving `onSaveSchedule` and `run` with a valid hot-water window and an invalid quiet one. The targeted mutants below kill both single-site mutants.
- RESULT card.mjs at head: rc 0, `ALL CARD CHECKS PASSED` (ev/card-head.txt). It ran after `PYTHONPATH=tests/hastub python3 tests/plan_view.py`, the CI invocation.
- RESULT `GOLDEN_MODE=drift node tests/card_drift.mjs` at head: rc 0, `card_drift: 21 state(s) moved and claimed, 24 identical`. Every moved state is claimed (ev/card_drift-head.txt).
- RESULT mutation proof, re-run: the merge-base card (90c6bc3b0) under the head's card.mjs, in a detached worktree, gives rc 1 and `11 CARD CHECK(S) FAILED`. They are exactly the 11 the body lists (ev/mut-basecard.txt).
- RESULT targeted mutants, own driver (ev/mut_driver.py): 8 run, 8 killed, 0 survived (ev/targeted-mutants.txt, per-mutant FAIL lines in ev/mut-*.txt):
  - `drop-quiet-find-first`: card.js:13224 reads `dhwWindows`.
  - `drop-quiet-find-second`: card.js:13343 reads `dhwWindows`.
  - `band-literal-10`: `band: "10"`.
  - `band-dropped`: the `band` key renamed, so the placeholder goes unfilled.
  - `note-none`: no opt-in row carries the note.
  - `note-all`: the degree row carries it too.
  - `sv-band-literal`: the sv text back to `±7-10 %`.
  - `de-note-missing`: the de `advisor.optin_sensor_off` deleted.
- RESULT enumerator at the head: `table 645 (unreached 0)`, `literal 4` (ev/enum-head.txt). This matches the body's Figures.
- RESULT verdict counts, re-derived from the record's per-row tables: Corrected 24 rows (false 23 + stale 1), True 330, Unverifiable 6, for 360 in all. This matches the summary table and the body. n/a 292 is still not re-derived: it comes from the reader tables, which are not in the tree. That residue is unchanged from round 1.
- Not re-run: the body's `REFIT_BAND_PERCENT = 12` features.py control, the 11-script gate table and the browser cmp. These are CI's heavy runs, cited, not re-derived.
- VERSION, the manifest version and the RELEASE_NOTES.md heading are absent from both the delta and the three-dot diff. `tests/golden/claimed_drift.txt` is untouched.
- Forward-carry: the five carries name `R11-INTAKE-R10-RESIDUE`. The packet's `carry_audit at the head` reports 5 routed, 0 unrouted and 0 bad destinations.
- CI: `merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing` and `validate / validate-hacs`. `classify 2ef5531223 --pr 3563` was polled about every 72 s, from 00:36:25Z to 01:05:16Z. It exited 3 (WAIT) every time, last `WAIT 2ef5531223d56cc35d40fbbcb8f8d61ede644c57 pending: gate red: none`, and it printed no context names after `pending:` (ev/classify.log). The review is complete, so this is returned with `pending-ci:` per the brief. No red was reported at any poll, so no red is owed an answer at return. The branch ref still reads 2ef5531223d56cc35d40fbbcb8f8d61ede644c57 at 01:05Z (`git ls-remote`).
