Part of #2259; this does not close it. Part 2 closes it.

#2259's last open row is "duplicated spellings of a one-statement rule". PR #3169 adds the gate-only census `card_rule_copies` (72 on this tree) and, in this part, pays one real copy class so the score reads an improvement:

- `stateSignature(st)` in `heatpump-optimizer-card.js` replaces four spellings of the `state@last_updated` signature part: the headline stat part, the headline indoor part, `advisorSignature`, and `healthSignature`'s local `sig`.
- `tools/audit/archscore/metrics/card.py` shares one `_units` and `_classes` between the clone census and the rule census.

Part 2 is the generic template census, paid by deduplicating the real copies it reads. A round-3 measurement found 36 or more real copies (SVG path points, edge keys x3, `quietOverlapProblem` time ranges x4, `storageKey`/`storageKeyLegacy`, summary sign formatting), so 72 cannot fall with this payment alone. No budget is raised here: `archscore.card_rule_copies` stays 72.

## Head

Code head `b51dc761fdd4020ec69111edb2342649a6e38383`, a fast-forward from the PR head `b22cc1e60ec59e4fb590c58854ff8d57de5ced1f` (ancestor verified with `git merge-base --is-ancestor`). Handoff head: the same SHA, pushed to `handoff/r10-archscore-spellings`. The prototype commit 4b6ea5ec is not in this history; it stays on `handoff-wip/r10-archscore-spellings`.

Merge base `dfb4ce2b5`. origin/main was `3905069f3` at 2026-11-02 12:34 UTC. `git merge-tree --write-tree HEAD origin/main` reports no conflict, so main was not merged.

## Mutation proof

- **M1, the helper's key** (in `stateSignature`, the stamp `${st.last_updated || ""}` dropped, run in the tree then restored; `git status --porcelain` empty afterwards): `node tests/card.mjs` goes red: `FAIL  UX-7: the render signature follows the model status sensor`, `1 CARD CHECK(S) FAILED`, rc 1.
- **M2, the census join** (from the earlier part, unchanged here): `card.rule_copies` `if len(sites) > 1:` -> `if False:` turns `tests/arch_score.py` `card_rule_spellings` red, as recorded in the PR's first body.
- The `stateSignature` change is a refactor with no new behaviour to fail first: the failing-test-first obligation is carried by the tests that already drive the signatures (`tests/card.mjs`, `tests/card_drift.mjs`), which stayed green across the refactor (see Null control).

## Null control

`stateSignature` against the four former copies, 8 inputs, driven by extracting the function text from the card (`node` script, the headline copy `st ? \`${st.state}@${st.last_updated || ""}\` : "-"` and the advisor/health copy `st ? \`${st.state}@${st.last_updated}\` : "-"`):

| # | input | helper | headline copies | advisor/health copies |
|---|---|---|---|---|
| 0 | `null` | `-` | same | same |
| 1 | `undefined` | `-` | same | same |
| 2 | `{state:"on", last_updated:"2026-01-01T00:00:00Z"}` | `on@2026-01-01T00:00:00Z` | same | same |
| 3 | `{state:"", last_updated:"t"}` | `@t` | same | same |
| 4 | `{state:0, last_updated:"t"}` | `0@t` | same | same |
| 5 | `{state:"x", last_updated:""}` | `x@` | same | same |
| 6 | `{state:"x", last_updated:null}` | `x@` | same | **differs**: `x@null` |
| 7 | `{state:"x"}` | `x@` | same | **differs**: `x@undefined` |

So the helper returns exactly what the two headline copies returned on all 8 inputs. It differs from the advisor and health copies on inputs 6 and 7 only (a missing `last_updated`): they printed `null` or `undefined`, the helper prints an empty stamp. This is a deliberate choice: a signature is compared only for equality across renders, so the old text carried no meaning, and the helper's doc comment says so. Home Assistant always writes `last_updated`, so the case is unreachable in production. `node tests/card.mjs` (182 s) and `node tests/card_drift.mjs origin/main` are green.

## Figures

- **Architecture score.** `python3 tools/audit/archscore/score.py --diff origin/main` prints `Architecture score: dS +0.0275 IMPROVES` with `card_clone_copies 105 -> 103  +0.0275`. No gate metric rises. The instrument is the one at this head, rule `vector.py`.
- **Census.** `python3 -c "import sys; sys.path.insert(0,'tools/audit'); from pathlib import Path; from archscore.metrics import card as K; print(K.measure(Path('.')))"` prints `card_dead_definitions` 0, `card_clone_copies` 103, `card_rule_copies` 72. The rule is `card.measure`. `card_rule_copies` 72 is unchanged from the PR head.
- **Structure ratchet.** `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- **Scoped gate.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 10 script(s) run, 23 scoped out.` `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` ended `13 TEST SCRIPT(S) PASSED; 22 SCOPED OUT AND NOT RUN`, rc 0, with `ALL 2592 ENTITY CHECKS PASSED`, `ALL 263 ARCHITECTURE SCORE CHECKS PASSED`, `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`, `ALL CARD CHECKS PASSED`.
- **Claim files and version.** `git diff --quiet $(git merge-base origin/main HEAD) HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION` exits 0.
- **Seams of the class.** The enumerating rule is `card.clone_classes` over `tokenize(card)`. Its classes on this tree are the `clone_classes` and `rule_classes` lists printed by the census command above (`details`). Four are closed by this diff (the signature spellings); the rest are the generic census's work in part 2 (`r10-archscore-spellings-p2`).

## Architecture score

dS +0.0275 IMPROVES; no gate metric rises, so no `## Architecture score` explanation is owed.

## Red checks

none: the whole check-run set of the PR head `b22cc1e60` (55 runs, one page, from `get_check_runs`) has no concluded red check; every run is `success` or `skipped`.

## Unpinned sites

`tools/audit/archscore/metrics/card.py` is a `tools/` site: the sites the diff adds are pinned by `tests/arch_score.py`'s card census checks (value checks on `card_rule_copies` and `card_clone_copies`), which the scoped gate ran green. The card's `stateSignature` is under `custom_components/`, pinned by `mutation-autofix`'s lane and by `tests/card.mjs`.

## Re-cut note

Round 4, a split, by the owner's ruling under the mandate's three-round rule: no budget raise. Round 3 returned BLOCKED on wip 4b6ea5ec with valid measurements (the generic census reads 36 or more real copies). This round keeps only commit b51dc761f (the `stateSignature` dedupe plus the shared `_units`/`_classes`) and drops the prototype.

## Forward-carry

The generic template census, paid by deduplicating its real copies, is a new held group, topic `r10-archscore-spellings-p2`, and closes #2259. Carry: #2259 (it stays open and owned until part 2 lands; the orchestrator cuts the group r10-archscore-spellings-p2 in `dev/programme/rosters/wave-r10-groups.json`)

## Friction

none
