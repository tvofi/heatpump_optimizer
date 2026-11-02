Closes #2259: this is the last open row of its item 2, card coverage. The row is "duplicated spellings of a one-statement rule".

The card's clone census (`card_clone_copies`) joins two copies only where a 20-token window matches. A rule shorter than the window was therefore invisible: the live-state guard, the nullish-or-empty test and the finite-number test are each one `&&`/`||` chain. The #2401 review spelled three of ARCH2-s5's card_shapes rules once more inline. The finder's harness read 22 -> 25 on that edit while `card_clone_copies` stayed 108 -> 108.

This adds `card_rule_copies` to `tools/audit/archscore/metrics/card.py`. It is gate-only (weight 0) and is counter C24 in `counters.py` and `ABOUT.md`.

- **What it reads.** For each `&&`/`||` chain in a card function, it takes every contiguous run of two or more operands in which one value is read twice. A value is a name with its member path, so `opts.probe` and `st.state` each count as one value.
- **The key.** Values are numbered by first use, strings keep their text, and a run must carry `RULE_TOKENS` tokens and some content (a string, a number or a member name).
- **The count.** It counts the sites (chains) whose run is spelled at another site. The module's own top-level code is a unit too, so an owner written as an expression-bodied arrow (`finiteNum`) is a site.
- **Why gate-only.** `shapes.py` gives the reason for Python's `shape_copies`: re-spelling one operand takes a site out of its class while the rule is still written again. A fall must credit nothing, and a rise is a new spelling and refuses.
- **What does not change.** The tokenizer gains `strings=True`, which still emits one token per string. The window census and the dead-definition census therefore read the same stream with strings as `S`: `card_clone_copies` and `card_dead_definitions` read the same on every tree measured below.
- **Budget row.** `tests/ci_ratchet.py` derives every vector key and refuses a key with no row. `tests/ci_budgets.json` therefore gains `archscore.card_rule_copies: 72`, the tree's own count. A new `archscore.*` row is a cap, and `budget_raise_gate.py`'s `max` kind reads an added row as no raise. No other row moves.

## Head

47ac6b92efc068209490573bffb66c87a658ce71

Merge base 907d29f0e. origin/main was at dfb4ce2b5 at 2026-11-02 07:49 UTC, past the tip `tools/pr/prepr.sh` ran against (rc=0). It was not merged in, because the brief and fixer.md step 6 merge only on a conflict:
- `git merge-tree --write-tree origin/main HEAD` reports no conflict.
- `git diff --name-only HEAD...origin/main` names no card, archscore, budget or closure path, so `card_rule_copies` 72 still describes main's card.

## Mutation proof

Three mutants. Each was run in a separate worktree at the head named in its row, then restored, and `git status --porcelain` was empty afterwards.

- **M1, the census's join predicate** (`card.rule_copies`: `if len(sites) > 1:` -> `if False:`, at 708113ac5):
  - `tests/arch_score.py` `card_rule_spellings` goes red: `FAIL card_rule_copies: the rule respelled inline at a second site reads both sites  [0 -> 0]`, `1 of 6 MUTANT1 FAILED`.
  - `calibrate.py --only rt_46_card_rule_respelled` reads `rt_46_card_rule_respelled redteam GAME NULL y 0.0000` against the recorded `WORSENS`, `admissible: false`.
  - The three null rows stay `ok`.
- **M2, the whole of `card.py` reverted to origin/main** (at 708113ac5):
  - `card_rule_spellings` raises `AttributeError: module 'archscore.metrics.card' has no attribute 'rule_copies'`.
  - `calibrate.py` stops on `KeyError: 'card_rule_copies'` in `vector.measure`.
- **M3, the module unit dropped** (`units.append(("<module>", ...))` deleted, at 22f2c34e0): `FAIL card_rule_copies: a rule whose owner is a top-level expression-bodied arrow reads both sites  [0 -> 0]`, `1 of 7 MUTANT3 FAILED`.

Failing test first: at 67d3e4608 (the test commit, before the census existed):
- `card_rule_spellings` raised `AttributeError`.
- `calibrate.py --only rt_46_card_rule_respelled` printed `MOVED rt_46_card_rule_respelled: recorded {... 'verdict': 'WORSENS'} now {... 'verdict': 'NULL', 'admissible': True}`.

## Null control

- **Synthetic card** (`tests/arch_score.py` `card_rule_spellings`): three unrelated lines are planted beside the rule's owner, and each leaves `card_rule_copies` where it was (`ok   card_rule_copies null: ... reads nothing`, three rows). The three lines are:
  - a test of one value against other strings, `h.mode === "heat" || h.mode === "cool"`;
  - a chain over two values, `h.state === "unavailable" || cfg.state === "unknown"`;
  - a statement with no chain.
- **The owner alone** reads 0 (`ok   card_rule_copies: the rule's owner alone is no copy`).
- **The unmodified pinned tree** (7952d8f9e): `card_rule_copies` 53. The red-team attempt reads 54 on the same tree, while `card_clone_copies` reads 87 -> 87 and `card_dead_definitions` 0 -> 0.
- **The calibration** (`tests/arch_score.py`, full, 263 checks): every other planted, red-team and corpus verdict is unchanged; only `rt_46_card_rule_respelled` is a new row.

## Figures

- **Census, before and after.** Base instrument at origin/main 907d29f0e and head instrument, on this tree: `card_dead_definitions` 0 / 0, `card_clone_copies` 105 / 105, and `card_rule_copies` absent / 72. Command: `python3 -c "import sys; sys.path.insert(0,'<instrument>/tools/audit'); from pathlib import Path; from archscore.metrics import card as K; print(K.measure(Path('.')))"`, with `<instrument>` set to `git archive origin/main tools/audit` and to the head. Rule: `card.measure`.
- **Finder's harness at both ends.** `node card_shapes.mjs <card>` is ARCH2-s5's census at `9d8a97982:dev/audit/rounds/round10/D7/arch2-s5/card_shapes.mjs`, sha1 677b75421ca84ac0f404dc90fa0b6a0b72edea0e. It reads `RESULT total=23` on this tree's card. On the companion plant it reads `RESULT total=26`. The plant spells the live guard, the nullish-or-empty test and the finite test once more each, inside `finiteProbe`.
  - Same plant, base instrument: `card_clone_copies` 105 -> 105, `card_rule_copies` absent. This is the defect at the baseline.
  - Same plant, head instrument: `card_clone_copies` 105 -> 105, `card_rule_copies` 72 -> 76.
  - Why +4 here and +3 for the finder: the finder counts inline spellings with each owner excluded by its pattern. The census counts class members, so the finite test's first new copy also brings its owner (`const finiteNum = (n) => ...`) into a class.
- **Red-team attempt 46 on the pinned tree.** `card_rule_copies` 53 -> 54, `card_clone_copies` 87 -> 87, `card_dead_definitions` 0 -> 0. Command: `python3 tools/audit/archscore/calibrate.py --only rt_46_card_rule_respelled`, row `rt_46_card_rule_respelled redteam GAME WORSENS n 0.0000 card_rule_copies 53->54`.
- **Seams of the class.** The rule that enumerates them is `card.rule_copies` over `tokenize(card, strings=True)`. Every one of its classes on this tree is the tree's own standing count (72 sites, 23 classes), which the new budget row caps. No site is closed or moved in this diff, and none is a distinct finding filed here.
  - Known open, a spelling the rule does not join: operands reordered (`"unknown" || "unavailable"`), and `&&` and `||` read as one separator (precedence not modelled).
  - Known open, a spelling it joins too broadly: a rule whose strings differ only in quoting style reads as one rule. This is intended.
- **Architecture score.** `python3 tools/audit/archscore/score.py --diff origin/main` prints `Architecture score: dS +0.0000 NULL`. The diff touches no package file, and the base instrument runs the check.
- **Ratchet rows.** `tests/ci_ratchet.py`'s `compare` over the archscore rows of `tests/ci_budgets.json` against `archscore_metrics()` on this tree prints `ok    archscore.card_rule_copies: 72 (budget 72)`, `ok    archscore.card_clone_copies: 105 (budget 108)`, `grew 0`.
- **Structure ratchet.** `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- **Scoped gate.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 4 script(s) run, 29 scoped out`. `GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh` printed:
  - `ALL 2592 ENTITY CHECKS PASSED`
  - `ALL 263 ARCHITECTURE SCORE CHECKS PASSED`
  - `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`
  - `8 TEST SCRIPT(S) PASSED; 27 SCOPED OUT AND NOT RUN`, rc 0.

## Architecture score

dS +0.0000 NULL; no gate metric rises (the diff changes the instrument, and the required check runs the base's copy of it).

## Red checks

none

## Forward-carry

none

## Friction

none
