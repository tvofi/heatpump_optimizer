Closes #2259

Part 2 of R10-ARCHSCORE-SPELLINGS, the rest of the split ruling. Part 1 (#3169, merged as 871a20da) added `card_rule_copies` (counter C24) for `&&`/`||` rules. Part 2 does two things:

- It makes C24 read a rule spelled as a **template literal**.
- It pays for what the new census reads by deduplicating the real copies in the card.

No budget is raised. `archscore.card_rule_copies` stays capped at 72, and the tree now reads 70.

- **The census** (`tools/audit/archscore/metrics/card.py`). With `strings=True`, `tokenize` keeps each template text segment as one token: a backtick, its place (`W`, `H`, `M`, `T`) and its text. `_templates` lists every template that has a `${..}`, nested templates included. In `rule_copies`, each run of two or more of a template's `${..}` is keyed by `_rule_key`, with the text between them as joints and `roots=True`. Under `roots=True` a value is its root name, numbered, and its members stay as spelled. A run is a rule when some value is read twice, it is `RULE_TOKENS` long, and it carries content. A site is one template. The chain census still reads a template's text as `S`, so its keys are unchanged.
- **The generic exclusion.** A MARKUP template is left out: one whose own text opens or closes a tag (`_MARKUP = <[A-Za-z/!]`). Its `${..}` fill different slots of what it draws, so it is not a rule, and markup belongs to `card_clone_copies`. This criterion excludes the SVG coordinate markup (shared bands, value axis and grid, chart rects, series paths, setup pipe paths) and the quiet-window form. It does not exclude a path string written without a tag, such as `pathPoint`.
- **The payment** (`heatpump-optimizer-card.js`). Every real copy the census reads is now shared:
  - `edgeKey`: `setupSvgHtml`, two sites in `evaluate`, and `removeEdge`.
  - `windowRange`: `formatWindows`, `draftSignature` (through a local `windowSig`), and both clash messages.
  - The overlap `span` in `quietOverlapProblem`, now one loop over the hot-water windows and then the silent ones, in the same order.
  - `storageKey`, built on `storageKeyLegacy`, which is its prefix.
  - `pathPoint`: `steppedLine` and `smoothLine`.
  - One `dropText` in the what-if `summary`.

  Every string the card writes is unchanged (Null control). The brief named four of these. `windowRange` and `dropText` are the two further real copies the census reads; without them the count would have been 77, over the cap.

## Head

`79420455c0717f1fb4f8161787e1603a60304f60`: the fix commits plus a merge of origin/main.

Merge base `b8e823699981866383f1afa54ce708ded3419316`. origin/main was at `b8e82369` on 2026-11-02 at 19:53 UTC. It had moved from the dispatch base 871a20da, by `dev/programme` records only, before any `tools/pr/prepr.sh` run. So it was merged once, by the brief's rule, and every figure below is taken at this head.

## Mutation proof

Each mutant was run in a detached copy of the fix commit `d85ff06ac` and then restored; `git status --porcelain` was empty afterwards. The C24 checks were driven through `tests/arch_score.py`'s `card_rule_spellings` and `card_template_spellings` with `PYTHONPATH=tests/hastub`.

- **M1, the template arm off**: in `rule_copies`, `enumerate(_templates(body))` -> `enumerate(_templates(body)[:0])`. Red: `FAIL card_rule_copies: a template rule respelled inline at a second site reads both sites  [0 -> 0]`. rt_47 on the pinned tree 7952d8f9 read `card_rule_copies` 53 -> 53 under M1 (no rise, so no WORSENS) and 77 -> 78 restored.
- **M2, the markup criterion off**: `if not any(_MARKUP.search(x, 2) for x in texts):` -> `if True:`. Red: `FAIL card_rule_copies null: markup drawn again reads nothing  [0 -> 2]`. On the real card it reads 85, not 70.
- **Failing test first**: commit `9ac93f83e` (the test, rt_47 and its `expected.json` row) comes before the census commit `41450b407`. At that commit the check above fails (`0 -> 0`).

## Null control

- **The census's own nulls**, green at this head:
  - an unrelated one-value template `${h.a}/${h.b}`
  - the same template over two values `${h[0]}>${cfg[1]}`
  - markup drawn again

  None of them moves the count. Part 1's three chain nulls are still green.
- **The card's strings, base against head.** A `node` differential loads every top-level card function from origin/main's card and from this head's card and compares their outputs over 229 cases:
  - `formatWindows`
  - `quietOverlapProblem` on 216 spec triples, 128 of which return a clash message
  - `steppedLine` and `smoothLine` at 1, 2, 3, 5 and 17 points

  `229 cases, 0 differ`. The perturbed control (`pathPoint` x to 3 decimals) printed `229 cases, 10 differ`. The other dedupes are textual identities, checked by eye: `edgeKey`, `storageKey` (legacy prefix plus `:${title}:${cfg.hours}`), `windowSig` and `dropText`.
- **No new undefined name.** `eslint` with `no-undef` reports 69 findings on origin/main's card and the same 69 on this head's (browser globals). A planted `edgeKeyX` was reported, so the check can see one.
- **The old instrument on both trees.** origin/main's `card.py` reads `card_rule_copies` 72 on origin/main's card and 70 on this head's card: the shared `dropText` also removes a chain copy.

## Figures

- **Architecture score.** `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`, with `card_rule_copies 93 -> 70  (gate only)`. Both trees are read by this head's instrument; 93 is origin/main's card under the template-aware census. No metric gets worse.
- **Census at head.** `python3 -c "import sys; sys.path.insert(0,'tools/audit'); from pathlib import Path; from archscore.metrics import card as K; m=K.measure(Path('.')); print(m['card_dead_definitions'], m['card_clone_copies'], m['card_rule_copies'])"` prints `0 103 70`. The rule is `card.measure`. The cap in `tests/ci_budgets.json` is 72 and is untouched.
- **Seams of the class.** The enumerating rule is `card.rule_copies(card.card_tokens(root, strings=True))`:
  - On origin/main's card it returns 7 template classes (21 sites, 93 - 72 + 0). All 7 are closed in this diff: edge key ×3, window range ×5, overlap span ×4, path point ×3 + ×2, storage key ×2 and signed drop ×2.
  - At this head it returns 22 classes and 70 sites, of which 0 are template-site classes.
  - The 15 markup sites (M2's 85 - 70) are dispositioned by the stated `_MARKUP` criterion.
- **Structure ratchet.** `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- **Scoped gate.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 10 script(s) run, 23 scoped out.` `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub bash tests/run.sh`: ended `13 TEST SCRIPT(S) PASSED; 22 SCOPED OUT AND NOT RUN`, rc 0, with `ALL 2602 ENTITY CHECKS PASSED`, `ALL 269 ARCHITECTURE SCORE CHECKS PASSED`, `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`, `ALL 4777 FEATURE CHECKS PASSED`, `ALL CARD CHECKS PASSED`.
- **Closures.** `tests/derive_closures.sh --single tests/arch_score.py` and `--single tests/entities.py`, run on Linux, add `47_card_template_respelled.py` to both closures (commit `49ebf21fd`). The new file is classified that way.
- **Claim files and version.** `git diff --quiet $(git merge-base origin/main HEAD) HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION` exits 0.

## Architecture score

dS +0.0000 NULL. No gate metric rises: `card_rule_copies` falls 93 -> 70 on the head's instrument and 72 -> 70 on main's.

## Red checks

none: no PR exists yet for this head.

## Unpinned sites

The `tools/audit/archscore/metrics/card.py` sites are pinned by `tests/arch_score.py`'s `card_template_spellings`, which are value checks on `card_rule_copies`; M1 and M2 above are its in-tree mutants. The card's new helpers under `custom_components/` are pinned by `tests/card.mjs`, which drives `quietOverlapProblem`, `storageKey`, `smoothLine`, `steppedLine`, `removeEdge` and `evaluate`, and by `mutation-autofix`'s lane.

## Forward-carry

none

## Friction

none
