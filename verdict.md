Fix review: blocked b22cc1e60ec59e4fb590c58854ff8d57de5ced1f class-open: card_shapes.mjs shapes state_sig, picker_open, char_width_inline and no_plan_state each spelled once more read card_rule_copies 72 -> 72, undispositioned, so Closes #2259 is not met

bus-nonce: 510372afe56bc30ec709ef46e8c91c61

Round 1, a full review of PR #3169 (R10-ARCHSCORE-SPELLINGS) at head `b22cc1e60ec59e4fb590c58854ff8d57de5ced1f`, measured from detached worktrees at that head and at merge base `dfb4ce2b52fafb340e0320bc2efb870099a53884` (= origin/main). The role files under `dev/governance/roles/` are current: the three-dot diff of origin/main against the merge base is empty.

## Block

Each of these blocks on its own. The first line names the first.

1. **class-open: four of the finder's seven shapes are not read and the body does not disposition them** (fix-review.md step 6). The finder's harness is ARCH2-s5's `card_shapes.mjs` (sha1 677b754, `9d8a97982`). #2401's carry set this group's acceptance as "any one shape spelled once more moves the census by 1", and #2259 item 2 asks for "duplicated spellings". The census reads only `&&`/`||` chains. I spelled each shape once more inside `overlayDhwDisplay` at this head (`ev/plants.txt`):
   - `state_sig`: finder 23 -> 24, `card_rule_copies` 72 -> 72, `card_clone_copies` 105 -> 105.
   - `picker_open`: finder 23 -> 24, rule 72 -> 72, clone 105 -> 105.
   - `char_width_inline`: finder 23 -> 24, rule 72 -> 72, clone 105 -> 105.
   - `no_plan_state`: finder 23 -> 24, rule 72 -> 72, clone 105 -> 105.

   The body's enumeration rule is `card.rule_copies` itself, which cannot name what it does not read. Its "Known open" list names operand reordering and `&&`/`||` precedence, not these four shapes. So the body's `Closes #2259` is not justified at this head. Either read them, or disposition each one in the body with a route, and change `Closes` to `Part of` unless the owner accepts the narrower scope.
2. **mutation-vacuous: the three guards of `_rule_key` are unpinned.** Each of these mutants leaves `tests/arch_score.py`'s `card_rule_spellings` at 7/7 ok and `calibrate.py --only rt_46_card_rule_respelled` at its recorded `WORSENS` (`ev/mutants2.txt`):
   - MC1a, the one-value (`readers`) predicate dropped: the real tree reads 72 -> 126.
   - MC1b, `RULE_TOKENS` dropped: 72 -> 79. Lowering it to 3 also reads 79.
   - MC1c, the `content` predicate dropped: 72 -> 91.
   - MC1, all three dropped: 72 -> 548.

   The body's null control "a chain over two values reads nothing" plants that chain only once. With no second site it cannot fail under the mutant it names (MC1a). Each null needs a twin: plant the two-value chain, the short run and the content-free run at two sites each, and each must read 0. Only the `archscore.card_rule_copies` budget row of 72 would refuse these mutants, and only on today's tree. The body's own mutants M1 to M3 and my MA, MB and MC2 are red (below).
3. **architecture-unsound: concepts duplicated in the added lines** (fixer.md step 17, "no concept duplicated"; `ev/duplicated_code.txt`).
   - `rule_copies` copies `clone_copies`' union-find and class-grouping block in the same module: 17 lines, `card.py:499-515` against `card.py:359-375`. The only difference is the renamed loop variables `owners`/`sites`. `counters.py:189-204` holds a third copy, which was already on main.
   - It also copies the function-unit construction (the `nested`/`outer` comprehensions, `card.py:479-480` = `354-355`).

   One shared helper per concept in `card.py` (for example `_classes(owners_by_key)` and `_units(toks, fns)`) pays for both. The body names no alternative it considered (step 17). The package vector cannot see this: the score reads `custom_components/` only, so dS is 0 whatever the instrument code does.

## Findings

- class-open, as Block 1: the four card_shapes shapes `state_sig`, `picker_open`, `char_width_inline` and `no_plan_state` are each read by neither card census. Carry: R10-ARCHSCORE-SPELLINGS | #2259
- mutation-vacuous, as Block 2: the `_rule_key` guards (one-value, `RULE_TOKENS`, content) survive their mutants. Each null control needs a second site. Carry: R10-ARCHSCORE-SPELLINGS
- architecture-unsound, as Block 3: the union-find block and the function-unit block are copied inside `metrics/card.py`. Carry: R10-ARCHSCORE-SPELLINGS
- #2259's body states "Every new counter gets a calibration case (planted good and planted bad) in the score's expected.json and a red-team case". C23 (#2401) carried `a3_shape_copies_control`, `_fix`, `_null` and `_respelled_control`. This PR adds only the red-team row `rt_46_card_rule_respelled` to `calibration/expected.json`, and no planted control/fix pair. It must add them, or the body must say why not, before `Closes #2259`. Carry: R10-ARCHSCORE-SPELLINGS | #2259
- The body's `## Head` contradicts itself. It says origin/main `dfb4ce2b5` "was not merged in", but `32645d21a` merges `dfb4ce2b5` into the code head (as the paragraph above it says), and "Merge base 907d29f0e" is no longer the merge base (`dfb4ce2b5` is). Correct it on the next push. Carry: R10-ARCHSCORE-SPELLINGS

## Evidence

- Head measured: `b22cc1e60ec59e4fb590c58854ff8d57de5ced1f`. The PR body's `## Head` names it (step 7). `ev/HEAD.txt`.
- Merge: `git merge-tree --write-tree origin/main b22cc1e6` exits 0 with tree `e58c9797f`. There is no conflict and no claim-driver line (`ev/merge_tree.txt`).
- The three-dot diff (`git diff dfb4ce2b5...b22cc1e6`) is 10 files, +260/-10, matching the brief. It includes the delivery row `dev/programme/delivery/3169.md`.
- `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to origin/main. `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched. There is no host path in the added lines, and no Co-Authored-By, Claude-Session or footer in the branch's commit messages.
- THE FINDER'S HARNESS (`ev/finder_card_shapes.mjs`, sha1 677b75421ca84ac0f404dc90fa0b6a0b72edea0e from `9d8a97982`) and my own plant script (`ev/plant.py`, **the reviewer's instrument**, not the fixer's). The plant spells live_guard, null_number and finite_inline once more each in `overlayDhwDisplay` (the fixer used `finiteProbe`).
  - RESULT base-instrument plant=finder3 finder_total 23->26 card_clone_copies 105->105 card_dead_definitions 0->0 card_rule_copies absent: the defect reproduces at the baseline.
  - RESULT head-instrument plant=finder3 finder_total 23->26 card_clone_copies 105->105 card_dead_definitions 0->0 card_rule_copies 72->76.
  - Singly: live_guard 72->73, null_number 72->73, finite_inline 72->74. The finite owner `finiteNum` joins the class, as the body says. Operand order reversed (`Number.isFinite(x) && typeof x === "number"`) reads 72->72 and the finder 23->23; the body discloses operand reordering.
  - The brief quotes 22 -> 25 and 108 -> 108 from #2401's tree. Today's card reads finder 23 and clone 105. I re-derived the movement (+3, clone flat), not those absolute figures.
- NULL CONTROLS at the head, base 72 (`ev/plants.txt`). Each reads `card_rule_copies` 72, clone 105 and dead 0:
  - an unrelated one-statement line;
  - a distinct legitimate one-value rule (`opts.kind === "dhw_overlay" || opts.kind === "dhw_window"`);
  - an identical existing statement (`const v = Number(opts.probe);`);
  - a `//` line comment and a `/* */` block comment holding the live_guard and null_number text;
  - a `/** */` docstring holding the finite text;
  - a string literal holding the live_guard text. The finder reads 24 on this one; the census correctly reads 72.
- MUTANTS planted by me in `card.py`, each restored with `git status --porcelain` empty (`ev/mutants.txt`). The unmutated run is 7/7 ok, rt_46 WORSENS (53->54) and the tree 72.
  - MA, the one-statement arm dropped (`owners[key].add(site)` -> `pass`): 2 FAIL in `card_rule_spellings`, rt_46 NULL, tree 0. Red.
  - MB, exact text only (values not numbered): 2 FAIL, rt_46 NULL, tree 37. Red.
  - MC2, widened to any statement (single-operand runs, guards dropped): 6 FAIL, rt_46 NULL, tree 17143. Red.
  - MC1 and MC1a-d (the guards): green under both checks (Block 2).
- The body's mutation proof (M1 join predicate, M2 card.py reverted, M3 module unit) agrees with MA and with the arrow check that fails under the module unit. I did not re-run M2 or M3 separately.
- FALSE-POSITIVE COST, the real tree's whole vector (`ev/vec_table.txt`, `ev/vec_*.json`): base instrument on the base tree against head instrument on the head tree, plus head instrument on the base tree. All 24 shared metrics are equal. Only `card_rule_copies` differs, None -> 72, and it reads 72 on the base tree too, since the diff touches no package file. `card_clone_copies` 105 and `card_dead_definitions` 0 are unchanged, so the `strings=True` tokenizer path leaves both censuses' stream intact.
- `calibration/expected.json`: the diff adds exactly one row, `rt_46_card_rule_respelled` {GAME, redteam, WORSENS, admissible false}. `calibrate.py --only rt_46_card_rule_respelled` at the head prints `rt_46_card_rule_respelled redteam GAME WORSENS n 0.0000 card_rule_copies 53->54`, as the body quotes. I did not re-run the full calibration (the 263-check `tests/arch_score.py`); CI's arch-instrument lane owns it.
- REPORT dS: `python3 tools/audit/archscore/score.py --diff dfb4ce2b52fafb340e0320bc2efb870099a53884`, run at the head (`ev/score_diff.txt`), prints `Architecture score: dS +0.0000 NULL`. The per-metric table is `ev/vec_table.txt`: every score and gate metric is equal at both ends, and the gate-only `card_rule_copies` is None at the base, so it drops from the comparison. The new instrument code is itself duplicated (Block 3); the score cannot see it.
- BUDGETS AND CLOSURES:
  - `tests/ci_budgets.json` +1 is a new row, `archscore.card_rule_copies: 72`, equal to the census's measured 72 at the head. No existing row moves. It is a new cap for a new gate-only vector key, which `ci_ratchet` needs because it refuses a derived key with no row. It is not a raise, and `budget-raise-gate` concluded success.
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - `tests/closures.json` +2 adds `46_card_rule_respelled.py` to the closures of `tests/arch_score.py` and `tests/entities.py`, beside its sibling 45 in both. Commit 47ac6b92e re-records entities.py with `--single`. I did not re-derive the closures myself; CI's `tests / closures` check covers that.
- Scoped gate: `python3 tests/closure.py select --diff dfb4ce2b5` prints `MODE: SCOPED -- 4 script(s) run, 29 scoped out.`, keyed on the mode line.
- #2259: #2401's table lists items 1 and 3-7 as delivered (#2293, #2311, #2320, #2373, #2401) and item 2's one-statement row as the only one not delivered. The roster's R10-ARCHSCORE-COVERAGE is `done` (#2441). This PR's diff therefore owns the whole remaining request, and Block 1 and the calibration-case finding are where it falls short.
- CI at this head: see the Red checks and CI lines below.
- CI: `python3 tools/audit/seat/merge_train.py classify b22cc1e60ec59e4fb590c58854ff8d57de5ced1f --pr 3169` exited 0 at 08:59 UTC and printed `GREEN b22cc1e60ec59e4fb590c58854ff8d57de5ced1f pending: none red: none`. The head's 41 check-runs, all on one page, include `tests / arch-instrument`, `fast (3.14)`, `coverage`, `closures`, `mutation`, `arch-score` and `budget-raise-gate`. None concluded red.
- Red checks: none at this head, so step 11 has nothing to answer.
- Re-read before return: `refs/pull/3169/head` is still `b22cc1e60ec59e4fb590c58854ff8d57de5ced1f`. origin/main has moved to `8fcaf47e1` since I measured. `git merge-tree --write-tree` against it still exits 0, and every figure above was taken at the merge base `dfb4ce2b5`.
