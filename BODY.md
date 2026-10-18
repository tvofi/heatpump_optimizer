Docs and comments that drifted against the code (class I5; D5-s1-01, D5-s2-01, D5-s3-51 and the non-policy half of D11-s1-51) and the product page's declared image height (D6-s9-01). Part of #2222. Part of #2298. Each stale statement is corrected or, where a number would go stale again, the number is deleted; four new arms in `tests/doc_claims.py` derive each fact from the production artifact and pin it, each with a null control.

Corrections, each checked against the code:
- UI labels (D5-s1-01): `strings.json` labels the config-flow menu button `Enter thermal values directly` and `manifest.json` names the integration `Heat Pump Cost Optimizer`. README.md, docs/configuration.md (three places) and docs/setup.md named the button with an "(expert)" suffix, and docs/configuration.md named the picker entry "Heat Pump Optimizer". All five now read what the UI shows.
- Console banner (D5-s2-01): the card prints `%c ${CARD_TAG} %c v${CARD_VERSION}` and `tools/release/stamp.py` rewrites `CARD_VERSION` on every release without touching the doc, so a literal version in the sample is stale by the next stamp (it read v6.6.8 at 7.0.0). The sample now reads `v<version>`, and the sentence after it says what `<version>` is. The existing D5-s1-03 banner null control anchored on the sentence this rewords, so its anchor moved with it and the control now also requires its plant to change the text (it was vacuous on a missing anchor).
- Service counts (D5-s3-51): `_async_register_services` registers 13 services on a FakeHass; three statements in `__init__.py` said twelve and one said eleven. The numbers are deleted, not corrected (fixer.md step 9): the sentences do not need them, and `services.py`'s module docstring keeps the one count, now pinned by the new arm.
- `tests/structure.py` (D11-s1-51): two comments named `cross_seam_edges` as a live ratcheting row; #1738 folded it into `seam_cut_total`. They now say so. The `cut_views` mention in `cap_problem`'s docstring is left as written: it recounts what the script printed at the time, a record, and `tests/entities.py` requires the three grader copies of `cap_problem` to match `structure.py`'s character for character (see Red checks).
- `tests/stress.py` (comment only): "the merge base solves the same fifty-one scenarios" is present tense and the live set has a different size; the number is deleted. This merges after or beside #2368, which also changes `tests/stress.py`: this edit is one comment line in the `__main__` block's baseline-capture comment, and no hunk of #2368 touches or neighbours it.
- `docs/index.html` (D6-s9-01, #2298): `img/card/plan-why-light.png` was declared 1056x616 and the file is 1056x792; it now declares 792. The new arm compares every sized `<img>` on every published page against the PNG header. A published page is README.md, the reader docs the file already scans (`DOCS`) and every top-level `docs/*.html`, which GitHub Pages serves; today the sized tags are all on `docs/index.html`, and the arm's anchor is red if that page leaves the list. A first cut read every tracked .md and .html, which put about 1200 records and programme files in `doc_claims.py`'s recorded closure; records are not pages a browser lays out, and fixer.md step 10 leaves them as written.
- Closures: the arm opens each PNG it compares (the product page's images were only stat()ed before, so they sat under the INERT `docs/` prefix). The ten it opens are added to `INERT_EXCEPT` in `tests/closure.py`, the route #1413 and R9-WEB-1 took for the docs `doc_claims.py` reads, and `tests/closures.json` is re-derived with `./tests/derive_closures.sh --single tests/doc_claims.py`. A new sized `<img>` adds its PNG there; the closure check refuses it until it does. Alternative considered: a prefix predicate taking all of `docs/img/*.png` off INERT would make the 18 unread PNGs orphans.

Alternatives considered for the banner: correcting the literal to the live version would be stale at the next stamp; teaching `stamp.py` to rewrite the doc too adds a second generator target for a sample that needs no specific number. The placeholder removes the cause. For the service counts: correcting twelve to thirteen leaves four sentences a fourteenth service falsifies; the check would catch it, but deleting a number nothing needs is the smaller surface.

Not in this group: the D7.md and D9.md lines of #2222 (policy, R10-BRIEFS-FOLD), the `money_currency` comment in coordinator.py (D5-s3-01, R10-CURRENCY), the hot_water_pumps label (R10-UX-SETUP). Per the roster carry, #2222 is fully delivered only when this group merges last of those four; the orchestrator checks. #2298 is fully delivered here.

## Head

7a7102eb844cf4f549d52af241b7bdc8e5a74797

## Mutation proof

Failing first: the head's `tests/doc_claims.py` (7a7102eb8) copied onto a `git archive` export of merge base 106af95a3 and run there as `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `5 of 183 checks FAILED`: "every 'Add integration' name and menu-button label in the docs is what the UI shows", "the sample shows the placeholder, not a literal version", "a literal version planted in the sample is refused (null control)" (its plant's anchor is the placeholder line, absent at base), "no comment or docstring states a whole-registry count that differs from it", "every declared width and height equals the PNG header". On an export of the head the same command prints `ALL 183 checks PASSED`.

Per production file, on that head export: the file replaced by its merge-base copy, the same command run, the file restored.
- `README.md`: 2 of 183 FAILED, "the three setup-flow diagrams are identical" and "every 'Add integration' name and menu-button label in the docs is what the UI shows".
- `docs/configuration.md`: 2 of 183 FAILED, the same two.
- `docs/setup.md`: 2 of 183 FAILED, the same two.
- `docs/dashboard-card.md`: 2 of 183 FAILED, "the sample shows the placeholder, not a literal version" and "a literal version planted in the sample is refused (null control)".
- `custom_components/heatpump_optimizer/__init__.py`: 1 of 183 FAILED, "no comment or docstring states a whole-registry count that differs from it".
- `docs/index.html`: 1 of 183 FAILED, "every declared width and height equals the PNG header".

The `tests/structure.py` and `tests/stress.py` edits are comments no check reads; their evidence is the sweep's W2 and W3 rows below. The `tests/closure.py` entries are pinned by the closure check itself: without them `./tests/derive_closures.sh --single tests/doc_claims.py` refused the recording ("files on the INERT list are actually read by tests", naming the ten PNGs).

## Null control

Each new arm plants its defect in memory and requires the reader to fire, and each has an anchor that is red when its subject is absent:
- UI labels: a drifted picker name plus a suffixed button label give exactly 2 findings.
- Banner: a literal `v6.6.8` planted in the sample gives exactly 1 finding, and the plant must change the text.
- Service counts: `"""Registers the twelve services."""` reads as `[(1, 12)]`; a "one of two services" subset reads as `[]`.
- Image size: a PNG of 10x20 against declared heights 20 and 30 compares 2 tags and refuses exactly the one at 30.

The finder harnesses' own controls, at merge base 106af95a3: `sweep_i5.py --null` prints `null_stale=0`; `card_banner.py --perturb` prints `banner_mismatch=0`; `web_claims.py --perturb-dims` prints `img_dim_mismatch=0`.

## Figures

Base is a `git archive` export of merge base 106af95a3, head a `git archive` export of 7a7102eb8; each harness run from that root as `PYTHONPATH=tests/hastub python3 <harness>` with the harness taken from the head's tree.
- `dev/audit/rounds/round10/D5/s1/ui_labels.py`: `mismatches` 5 at base, 0 at head.
- `dev/audit/rounds/round10/D5/leads/service_count_comments.py`: `stale_count_statements` 4 at base, 0 at head.
- `dev/audit/rounds/round10/D5/s2/card_banner.py`: `banner_mismatch` 1 at base; at head it raises `AttributeError` on `re.search(...).group`, because its regex reads a numeric version and the sample now carries none, which is the intended end state. Companion, applying the tree's own rule: `tests/doc_claims.py`'s banner arm, red at base and green at head (Mutation proof).
- `web_claims.py` from `handoff/audit-r10-d6-web` at 39909e462 (`$EXPORT/dev/audit/rounds/round10/D6/web/web_claims.py`, sha1 5ec0c0a704ad77bb138ddd443ba21dead669b4d5): `img_dim_mismatch` 1 at base, 0 at head.
- `node dev/audit/rounds/round10/D11/leads/stale_structure_refs.mjs`: `retired_key_claims` 3 at base, 2 at head; `lint_missed_stale_counts` 1 at both. What remains is D7.md, policy, R10-BRIEFS-FOLD.
- Class enumerator `dev/audit/rounds/round10/D14/I5/sweep_i5.py` (sha1 7e4115368a0b36069b5a5f51bf77b09bbfeb5a76), STALE lines by arm: base F1 5, F2 1, F3 5, F4 4, W1 1, W2 3, W3 2 (`stale_total=21`); head F3 5, W2 2, W3 1 (`stale_total=8`). Rule: every line the enumerator prints beginning `STALE`, grouped by its second field. Each seam it returns at head, with its disposition:
  - F3 `coordinator.py` `money_currency`: D5-s3-01, R10-CURRENCY.
  - F3 `inputs.py` `ATTR_MIN_TEMP`, `ATTR_MAX_TEMP`: not a defect; the comment names Home Assistant's own constants for the `min_temp`/`max_temp` keys the next line uses.
  - F3 `optimizer.py` `manual_plan_released`: not a defect; it is the event-name suffix `notifier.py` builds as `f"{DOMAIN}_manual_plan_released"`.
  - F3 `plan_step.py` `FORECAST_STEP_MINUTES`: not a defect; the docstring recounts how two modules spelled the step before R10-PUMP-MODEL, a record.
  - W2 `tests/structure.py` `cut_views` in `cap_problem`'s docstring: a record of a past output, left as written (Corrections).
  - W2 `dev/governance/dimensions/D7.md` `cross_seam_edges` and W3 `dev/governance/dimensions/D9.md` "51 scenarios": policy, R10-BRIEFS-FOLD.
  In the git checkout (not the archive) the enumerator also prints three F5 rows at head, all `dev/governance/dimensions/D7.md` lines 13, 17 and 18: policy, R10-BRIEFS-FOLD.
- `python3 tests/closure.py select --diff 106af95a3` at 7a7102eb8: `MODE: FULL`, because the diff edits `tests/closure.py`, a gate file; CI runs every script. At d32bdf502, before that edit, it read `MODE: SCOPED`.
- Closure reads of the first cut: at d32bdf502, a `--record-only` recording of the 25 recordable scoped scripts checked with `PYTHONPATH=tests/hastub python3 tests/closure.py check --in-dir <recording> --partial` printed 1200 lines `tests/doc_claims.py: <path>` under INERT READS UNDER-APPROXIMATED (722 under `dev/programme/`, 383 under `dev/audit/`); at da78ee636, with the page list, the same check over a `tests/doc_claims.py` recording named 10 paths, the ten PNGs now in `INERT_EXCEPT`. Rule: lines of that output naming `tests/doc_claims.py`.
- PNGs under `docs/img/`: `git ls-files 'docs/img/*.png' | wc -l` prints 28; 10 are opened by the arm, so 18 would be orphans under a prefix predicate.
- Run locally with `PYTHONPATH=tests/hastub`, each line the script's own last summary line and its exit code:
  - at 7a7102eb8: `tests/structure.py` rc=0 STRUCTURE RATCHET PASSED; `tests/doc_claims.py` rc=0 ALL 183 checks PASSED; `tests/closure.py selftest` rc=0 ALL 115 closure shrink pins PASSED; `tests/entities.py` rc=0 ALL 2347 ENTITY CHECKS PASSED.
  - at d32bdf502 (not re-run at 7a7102eb8; CI runs them at the head under `MODE: FULL`): `tests/deployment_shape.py` rc=0 ALL DEPLOYMENT SHAPE CHECKS PASSED; `tests/validate.py` rc=0 (it prints no summary line); `tests/arch_score_head.py` rc=0 ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED; `tests/env_drift.py --claims-only origin/main` rc=0 claims hygiene: origin/main ok.
  - at 7a4a815e3 (not re-run at 7a7102eb8; CI runs them at the head under `MODE: FULL`): `tests/config_flow_steps.py` rc=0 ALL 499 checks PASSED; `tests/harness_headers.py` rc=0 ALL 109 HARNESS HEADER CHECKS PASSED; `tests/layout.py` rc=0 layout self-test: ok; `node tests/md_tables.mjs` rc=0.
  - `tests/stress.py` and every other script are left to CI, which runs the full suite on this diff (`MODE: FULL`); `stress.py` changes by one comment line here.

## Red checks

`tests/entities.py`, locally, at 7a4a815e3: `1 of 2347 ENTITY CHECKS FAILED`, "every grader's copy of the barrier is the original, character for character", copies differing: `tests/mutation_table.py`, `tests/coverage_ratchet.py`, `tests/typing_ruler.py`. Cause: this branch had reworded one line of `cap_problem`'s docstring in `tests/structure.py`, and the three graders carry that function verbatim. Answer: the line is a record and is restored as written (d32bdf502); at d32bdf502 `tests/entities.py` reads ALL 2347 ENTITY CHECKS PASSED. The cheaper detector already exists and is the one that fired, before any push; nothing new is owed.

## Forward-carry

The D7.md and D9.md lines of #2222 are already in R10-BRIEFS-FOLD's brief, the `money_currency` comment in R10-CURRENCY's and the hot_water_pumps label in R10-UX-SETUP's (`dev/programme/rosters/wave-r10-groups.json`, this group's `carry`). This pass found nothing new that changes how a later stage must work: the three extra F3 rows the enumerator returns are not defects (Figures).

## Friction

none
