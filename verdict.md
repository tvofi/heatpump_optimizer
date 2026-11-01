Fix review: blocked 822946aae49ec0cec8e9a9d1812334dae14aee04 class-open: peak_tariff_offpeak_factor "which is how it worked before" / "som det fungerade tidigare" in strings.json, en.json and sv.json

bus-nonce: 7f3ceff478669e1dd5c250a4c0ac4762

## Round

Round 1. Measured head 822946aae49ec0cec8e9a9d1812334dae14aee04 (still the PR head at verdict time, per `git ls-remote`). Base f3c9144b80883ae510f0207c30855b8c93c51a0a (three-dot merge base). The role files show no diff against origin/main.

## Block

Carry 21 (udf-strings-history) says: "User-facing text states current behaviour only." The body claims its census removed "every history hit", and that the new `tests/entities.py` check "keeps it so". One leaf in the same class is still in the head, in all three catalogues:

- `options.step.grid.data_description.peak_tariff_offpeak_factor`
  - strings.json and en.json: "1.0 treats every hour the same, **which is how it worked before**."
  - sv.json: "1,0 behandlar varje timme lika, **som det fungerade tidigare**."

This is the same kind of text as the removed `heat_pump_mode_entity` "exactly as before". It describes how the integration behaved in an older version, and it means nothing to a user who never ran that version. The body's census pattern missed it because "worked before" is not "as before". Its sv pattern lists `som tidigare` but not `tidigare` alone. The new check misses it for the same reason: its phrase list is `as before|used to be` and `som tidigare|som förut|dessförinnan var`, and CI is green with this leaf present. A wider net catches it: `tidigare` in sv, which leads to its en counterpart. That makes the class open at this head (fix-review.md step 6).

Repair: rewrite the leaf in all three files to state current behaviour, for example "1.0 treats every hour the same." and "1,0 behandlar varje timme lika." Then widen the marker list so it holds this phrasing (en `worked before`, or `\bbefore\.` at sentence end; sv `fungerade tidigare`). The test must fail first on this leaf.

## Findings

- The no-meter **unconverged** bar is unpinned. At the head, `!observable ? 0` also empties the bar of an unconverged install with no power meter. My harness reads it as 40 % at the base and 0 % at the head. The body only claims the converged case ("still drew its learned bar FULL when the learner had converged"). The narrower mutant `hl.learned ? (observable ? 1 : 0) : house ? house.share : 0` survives `node tests/card.mjs` (ALL CARD CHECKS PASSED). So the behaviour change on the unconverged arm is neither stated in the body nor pinned by a check. `## Unpinned sites: none` is therefore inaccurate for this arm. Repair: in the same re-cut, state it in the body and add a no-meter unconverged check (bar 0). Carry: R10-UX-HEALTH
- Carry 22's forward-carry (sysid sizer `HousePlant.of_params` reads `heat_loss_coefficient` on two-zone plants) is routed to "the orchestrator, for a group owning sysid.py", and no group is named yet. It is pending, not a control. It stays on R10-UX-HEALTH's carry list until the orchestrator assigns the group. Carry: R10-UX-HEALTH
- `docs/configuration.md`'s "exactly as before" for the heat-pump mode row is routed to R10-USER-DOCS-FINAL. The same docs page should be checked for the `peak_tariff_offpeak_factor` "how it worked before" wording when that group runs. Carry: R10-USER-DOCS-FINAL

## Evidence

- HEAD: `ev/HEAD.txt` holds 822946aae49ec0cec8e9a9d1812334dae14aee04. The head over the merge commit 4502c5ab3 adds exactly `A dev/programme/delivery/3062.md`.
- No finder's harness is committed for (a); the packet says "Finder's harness: none named". I built my own, `ev/bar.mjs`. It loads the card in `card_rig.mjs`'s context and calls `healthModelHtml` with a stub plan. Results are in `ev/bar_results.txt`:
  - RESULT base nometer-converged: bar 100%. RESULT head: bar 0%. The defect reproduces and is fixed.
  - RESULT base/head metered-converged: bar 100% / 100%. The null control holds.
  - RESULT base/head metered-unconverged: 40% / 40%. Unchanged.
  - RESULT base/head nometer-zero-share and metered-zero-share: 0% / 0%. The flat null holds.
  - RESULT base/head nometer-unconverged: 40% / 0%. Unstated and unpinned; see Findings.
  - The W/K value and the "Not observable without a power meter." text are unchanged.
- The named mutation is killed. Dropping `!observable ? 0 :` gives `1 CARD CHECK(S) FAILED`, `UX-HEALTH D: with no power meter the learned heat loss draws no learned bar (#2499)` (`ev/card_mutant_full_condition.txt`). Clean head: ALL CARD CHECKS PASSED, and both new checks are ok (`ev/card_head.txt`).
- I did not view the card at 375 px in a browser; this cloud seat did not run `tests/card_browser.mjs`. CI `tests / browser` is green at the head. The change touches only a width percentage of an existing bar, with no fixed pixel widths and no colour change.
- Strings check: I planted "as before" in strings.json, "used to be" in en.json and "som tidigare" in sv.json, all on `peak_tariff_offpeak_factor`, plus the null "Used to read your hourly electricity prices." on `peak_tariff_price_per_kw` in strings.json and en.json. Result: `3 of 2496 ENTITY CHECKS FAILED`. These are exactly the three history checks, each naming one leaf, the planted one; the null leaf is not listed (`ev/entities_planted.txt`). The other FAIL lines in that log are the self-tests' internal negative controls. The tree was restored afterwards.
- Census (`ev/census.py`, a wider net: en `as before|previously|formerly|no longer|used to|anymore|any more|until now|earlier`, sv `tidigare|förut|numera|inte längre|dessförinnan|innan|brukade|hittills`):
  - Base: strings 28, en 28, sv 35.
  - Head: strings 23, en 23, sv 30.
  - Remaining head hits by kind:
    - `used to <verb>` as an instrument.
    - `no longer` and `inte längre`: repair runtime states.
    - `until now` (pump_mode_unreadable): runtime history.
    - `brukade`, `cop_degradation`: a measured comparison.
    - `earlier` and `tidigare` (dhw booster, legionella elastic): "heat earlier", a time adverb, current behaviour.
    - `förut` ×2: `förutse` (to predict), not history.
    - `innan` ×21: "before (time)", current behaviour.
    - **`peak_tariff_offpeak_factor` "som det fungerade tidigare"**: change history. This is the block.
  - A grep for `before` over en.json also returns `pump_mode_unreadable`: "which is what it assumed before you configured this entity". This is config-relative and describes current fallback behaviour, so I judge it acceptable.
- The body's census figures re-derive under its own pattern (`ev/bodycensus.py`): substring and case-insensitive gives 65 → 50; excluding the two `förutse` matches gives the body's 63 → 48. Either way 15 were removed. The pattern itself missed the blocking leaf.
- price_prior_enabled's rewrite is true against the code. `coordinator._price_prior()` returns None when the option is off. `price_model.extend_price_series` with `model is None` appends `last_known` for every unknown step, so it repeats the last price. The Swedish rewrites are correct Swedish and say the same as the English ("Fram till dess fylls ... från din inlärda prisprofil"; "Avstängt upprepar resten av horisonten senaste priset").
- Carry 22 harness at the head, run by me (`ev/carry22_harness.txt`):
  - two_zone_max_dkw=0.000000
  - two_zone_max_dcost=0.000000
  - two_zone_sysid_steps=1.738,3.386,None
  - single_zone_sysid_steps=1.738,3.386,None
  - single_zone_max_dkw=4.921374. The body's 4.999993 was taken on macOS at bbbce602d, and I could not re-derive that exact figure here. It only needs to be non-zero, and it is.
  - The sizer numbers (1.738, 3.386, none at 1.0) re-derive exactly. The decision not to hide or label the field is sound: sysid's step sizer reads it on two-zone plants, so "unused" would be false.
- Carry 14 and 17, and the dispositions above: the roster group R10-UX-HEALTH at 2fd6806cf and at the current origin/handoff/audit-r10-roster holds 22 carries. The packet's carry_audit reports `4 routed, 0 unrouted, 0 bad destination(s)`, and R10-USER-DOCS-FINAL resolves on the roster ref.
- Gate:
  - `merge_train.py classify` prints `GREEN 822946aae49ec0cec8e9a9d1812334dae14aee04 pending: none red: none`. No check is red at the head, which matches `## Red checks: none`.
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `git merge-tree --write-tree origin/main 822946aae` (origin/main 61b0076f4) exits 0, with `LEDGER-MERGE: resolved tests/closures.json`.
  - Claim files, VERSION, RELEASE_NOTES.md and manifest.json are byte-identical to origin/main.
  - The host-note wrapper left no residue: the tree diff has only the 9 listed files.
  - I did not re-run the scoped-gate MODE line, per the brief's cite-CI rule. CI `gate` and `tests / closure-scope` are green.
