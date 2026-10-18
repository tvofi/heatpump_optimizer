R10-ARCHSCORE-COVERAGE, part 4 of 5: the card and literal specs priced in the architecture score (roster items 2 and 3; ARCH2-s5, D7-s3-02).

Part of #2259.
Part of #2235.

Parts 1 to 3 (#2293, #2311, #2320) landed items 5, 4 and 7, and 1. This part is items 2 and 3, plus the dead-code carry from R10-STRUCTURE-BLIND; part 5 is item 6, the shape census. The diff is `tools/audit/archscore/` with its two registration files (`tests/closures.json`, `tests/ci_budgets.json`); `tests/structure.py` is not touched.

Resumed, not restarted: the crashed part-4 seat's commits `f872b27dc` to `8fda13ce7` (the parent of its snapshot `wip-sync/ext-wt-d480264e`, whose tree equals it) carry the metrics and cases. This seat merged `origin/main` into them, last at `52f698905` (`c12f2f524`), and re-executed steps 2 to 8 at the merged head.

What changes. Three score metrics at the floor weight. They guard no register class, so `weights.json` is unchanged and its floor applies:

- **`literal_clone_copies`** (`metrics/literal_clones.py`, item 3): copies of one declaration spelled as a call or literal more than once, such as a selector, a schema or a record. A spec is a call, dict, list, tuple or set of at least 6 nodes that computes nothing at runtime. Annotations, `except` types, generic subscripts and decorators are not specs. A clone class counts its maximal members. The clone census (`duplication_copies`) cannot see these: a spec sits inside one statement, below its window, which is why the 44 wizard selector specs read NULL.
  - C20: numbers are compared by value, an in-package callee's positionals as the keywords they bind, keywords and dict items in order.
  - C21: a local, or a module constant (the module's own or imported by name), bound once to a spec reads as that spec.
- **`card_dead_definitions`** and **`card_clone_copies`** (`metrics/card.py`, item 2). The card (`www/*.js`) is the largest UI surface, and before this part every metric read Python only. It is read by a stdlib tokenizer, never a parser, so each rule is stated on tokens.
  - Dead definitions are top-level `function`/`class`/`const`/`let` names and class members that no other token names, less the browser, lit and Home Assistant hooks. D7-s3-02's `textWidth` was one.
  - Clones are functions sharing a 20-token window once their own names are numbered and their no-op statements dropped (C22).
- **One JavaScript identifier grammar.** `prepr.sh`'s agreement lane refused the branch. The regex `[A-Za-z_$][\w$]*` was spelled in `tests/doc_claims.py`, `metrics/card.py` and attempt 44, and no entry registered it.
  - The fix is structural: one owner, `card._IDENT` (`metrics/card.py:53`). `tests/doc_claims.py` imports it at module level, directly above its reader, and its `_tokens` is `set(_IDENT.findall(text))`. Attempt 44 reads `K._IDENT.fullmatch` and builds its declaration regex from `K._IDENT.pattern` (line 25). `git grep -nF '[A-Za-z_$][\w$]*' -- tools tests` prints one line, `metrics/card.py:53`. No registry entry is needed.
  - `tools/policy/agreement.mjs` is byte-identical to origin/main: CI's lane reads the registry from the base branch (#2366), so a branch line would not be read there.
  - `tests/doc_claims.py`'s closure gains the four archscore modules it now imports.
- **The carry from R10-STRUCTURE-BLIND (#2340):** `metrics/common.py`'s `HA_CONVENTION_METHODS` and `is_ha_method` are deleted. Nothing read either, and the list had drifted from `tests/structure.py`'s.

Calibration: each metric has a planted BAD, GOOD and NULL case (`a3_literal_clone_copies_*`, `a3_card_dead_definitions_*`, `a3_card_clone_copies_*`), and each counter has a red-team attempt:
- `rt_42_literal_respelled` for C20;
- `rt_43_literal_local_hop` for C21;
- `rt_44_card_rename_locals` for C22;
- and, from the round-1 review, `rt_42c_literal_keyword_args` (C20), `rt_42b_literal_module_constant` (C21) and `rt_44b_card_noop_split` (C22).

The attempts were numbered 24 to 26 on the crashed branch. Part 3 landed its own 24 to 41, so here they are 42 to 44. `expected.json` gains exactly those fifteen cases. No recorded verdict moved, no weight changed, and no weight perturbation moves a verdict.

Alternatives considered:
- A JavaScript parser for the card lost to the tokenizer. The scorer is stdlib-only, so a parser would be a dependency, and every rule here can be stated on tokens.
- A 16-token card window lost to 20. At 16, ARCH2-s5's finite-number owner (patch C4), which is a dedupe, read one copy more. At 20, no card patch rises.
- Folding literal specs into `duplication_copies`' window lost: that census is `tests/structure.py`'s, and this group does not touch it.

## Round 1 (review `a19384631`, blocked at `28d6a60bb`)

The review blocked on two findings and noted one minor one. Each is repaired in `033998cb5`, and `c8d1382a3` records the three new attempts.

1. **Three planted games read IMPROVES.** They are closed in the instrument, not recorded as KNOWN-OPEN:
   - **P1, module alias.** C21 now folds a module constant bound once at top level to a literal, whether it is the module's own or imported by name with `from .m import X`. A name the function itself binds or takes as a parameter shadows the constant, and a name in a `global` statement is not a constant. Attempt `rt_42b_literal_module_constant`.
   - **P2, keyword respelling.** C20 binds an in-package top-level callee's positionals to its parameter names before it sorts keywords. It does this only when the callee has no `*args` and the call has no starred argument. Attempt `rt_42c_literal_keyword_args`.
   - **P3, card no-op split.** C22 drops a statement made only of literals, read identifiers and pure operators, with no call, before windowing. It drops only at parenthesis depth 0 and only at a statement start. Attempt `rt_44b_card_noop_split`.

   The reviewer's own `plants.py`, pointed at this head, prints `plant_base literal_clone_copies=184 card_clone_copies=108`. It then prints `P1_module_alias literal_clone_copies=184->184`, `P2_keyword_mix literal_clone_copies=184->184` and `P3_card_noop_split inserted=685 node_check_rc=0 card_clone_copies=108->108`. At `28d6a60bb` the review read 184->180, 184->180 and 108->98.

   What the counters still do not see is stated in `ABOUT.md` ("What part 4's censuses do not see"). The orchestrator carried that residual to R10-BRIEFS-FOLD at `72b97a4a5`. This seat did not write the roster.
2. **"No second spelling" was false.** Attempt 44 line 25 now builds its regex from `K._IDENT.pattern`. The grep above finds only the owner.
3. **Minor.** `tests/doc_claims.py`'s per-call `sys.path.insert` is gone. `tools/audit` joins the module-level path tuple at the lowest priority. `_IDENT` is imported at module level, directly above its one reader `_tokens`, so lines 1 to 2019 equal origin/main's.

## Head

`c06c9e84b4251758c5d214da9ccd3b7d640ecfab` merges the authored code head `d41773bbf98ddaaa47a5ffd5c95cac7c3cb551dd` and then merges origin/main `994695e06` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`d41773bbf98ddaaa47a5ffd5c95cac7c3cb551dd`, on PR head `2183ab58f` (`update_pr` merged `c8d1382a3` and then origin/main `d569693ad`). `git merge-base origin/main HEAD` is `d569693ad41fa4f4f95a3d4bbec7cea94ed1df26`.

`2183ab58feeeb4e062b81b557a7d7ecfa3428507` merges the authored code head `c8d1382a37ba330f1b999f9fbcba8e430e21df83` and then merges origin/main `d569693ad` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`d41773bbf` changes only `tests/doc_claims.py`: the `_IDENT` import moves from the top of the file to module level directly above `_tokens` (`## Red checks`). Between `52f698905` and `d569693ad`, origin/main touches nothing in `custom_components/`, `tools/audit/archscore/` or `tests/ci_budgets.json` (`git diff --stat` is empty). So the instrument figures below, taken at `c8d1382a3` and `033998cb5`, stand at this head. The scoped gate and today's values are re-taken here.

The harness and the reviewer's plants were taken at `c8d1382a3`. Four sets were taken at `033998cb5`, whose instrument is this head's (`c8d1382a3` adds only `expected.json` rows): the calibration record, the round-1 mutants M8 to M12, the round-1 ablations and the corpus re-measure. The round-0 mutants M1 to M7 and the C20 to C22 ablations on attempts 42 to 44 were taken at `21dd4a3e5`. The round-1 metric changes are pinned by M8 to M10, and they leave today's values unchanged.

## Mutation proof

Each mutant was applied in place on the committed head, run, and restored with `git checkout --` (`mutate_p4.sh` in the seat's scratch). For M1 to M7, the runner was `python3 tools/audit/archscore/calibrate.py --only` the twelve round-0 part-4 cases. The unmutated run, M0, classifies every case as recorded.

- **M1**, `card.dead_definitions` returns `[]`. MOVED: `a3_card_dead_definitions_control` WORSENS -> NULL, `_fix` IMPROVES -> NULL.
- **M2**, the dead test `seen[d] <= 1` becomes `<= 0`. The same two cases move.
- **M3**, the window union never joins (`len(owners) > 999`). `rt_44_card_rename_locals`'s own locator refuses: it finds no clone class to rename. Run without it, `a3_card_clone_copies_control` reads WORSENS -> NULL and `_fix` IMPROVES -> NULL (`mut_M3b`).
- **M4**, `is_spec` returns False. MOVED: `a3_literal_clone_copies_fix` IMPROVES -> NULL. The control stays WORSENS through its other terms, `dead_members` and `unread_private_globals`.
- **M7**, `tests/doc_claims.py`'s `_tokens` returns an empty set instead of `_IDENT.findall`. `tests/doc_claims.py` fails `every backticked private name in the card names something that exists` (`1 of 169 checks FAILED`), so the new import site is load-bearing.
- **M8**, C20's positional binding off (`if False and params is not None ...`). MOVED: `rt_42c_literal_keyword_args` NULL -> IMPROVES (0.0337, `literal_clone_copies`). No other case moves.
- **M9**, no module constants (`consts = {}`). MOVED: `rt_42b_literal_module_constant` NULL -> IMPROVES (0.0337). No other case moves.
- **M10**, no no-op drop (`drop_noops` not called). MOVED: `rt_44b_card_noop_split` NULL -> IMPROVES (0.1557, `card_clone_copies`). No other case moves.
- **M11**, the shadow guard ignored (`scope = {**mod_consts, **loc}`). **M12**, the parenthesis-depth guard off in `drop_noops`. Neither moves a case, and today's tree still reads `literal_clone_copies` 184 and `card_clone_copies` 108 under both. Both are over-fire guards; see `## Unpinned sites`.

M8 to M12 ran on `033998cb5` with `calibrate.py --only` the fifteen part-4 cases (`mutate_r1.sh`). The unmutated run classifies every case as its pinned verdict.
- **M5**, maximal members off: every occurrence counts, nested ones included. **M6**, decorators read as specs (the `9d94f8fe7` exclusion undone). No planted case moves their verdict. Both are pinned by value instead: `literal_clones.measure` on today's tree reads 184 at M0, 218 under M5 and 190 under M6, and the `archscore.literal_clone_copies` row of 184 refuses either as growth.

Ablation (`ARCHSCORE_ABLATE`). Each switch reopens its own attempt, and only that one:
- `C20`: `rt_42` reads IMPROVES (+0.0683), and `a3_literal_clone_copies_null` reads IMPROVES;
- `C21`: `rt_43` reads IMPROVES (+0.0086);
- `C22`: `rt_44` reads IMPROVES (+0.1565).
- On the three round-1 attempts, measured on the pin with each attempt's metric: under C20, `rt_42c` reads `literal_clone_copies` 172 -> 168; under C21, `rt_42b` reads 167 -> 163; under C22, `rt_44b` reads `card_clone_copies` 106 -> 94. Each reads NULL with its counter on. Run as `ARCHSCORE_ABLATE=<C> calibrate.py --only <attempt>` at `033998cb5`, each attempt reads IMPROVES under its own counter's ablation: `rt_42c` +0.0337 under C20, `rt_42b` +0.0348 under C21, and `rt_44b` +0.1716 under C22. These runs scored each attempt alone, so they do not show that the other cases stay put.

## Null control

- **The base reads the defects as NULL.** With the finder's harness on the base instrument, ARCH2-s5's F1 (the wizard reading its registry widgets) reads `delta_S=+0.0000`, and the four card patches together read `delta_S=+0.0000`. At this head they read `+0.4761` and `+1.0958`.
- **Each harness run's own perturbation reads 0 at both ends.** The patches are reversed onto the prototype: `perturbed_delta_S=+0.0000` and `perturbed_vector_equals_baseline=1`.
- **Honest code does not trip the new definitions.**
  - Each NULL plant reads NULL: a respelled bound, a renamed card function, a renamed parameter.
  - The full corpus re-measure is byte-identical to the stored vectors, so no corpus verdict moved.
  - `calibrate.py --record` printed RECORD for the twelve new cases alone, and in round 1 for the three new attempts alone.
  - The reviewer's plants, pointed at this head, read no change: 184->184, 184->184 and 108->108 (`## Round 1`).

## Figures

- **ARCH2-s5's finder harness**, re-run at `c8d1382a3`, with the same results as round 0. Run as `$EXPORT/dev/audit/rounds/round10/D7/arch2-s5/arch_delta.py --base 9061fbd3d <patches>` (sha1 `4fa94bb48af93fa21d1751e94a67c057b0a63f31`), where `$EXPORT` = `git archive 3930b421a dev/audit/rounds/round10/D7/arch2-s5`. The directory is copied into each tree, because the harness finds `tools/audit` from its own path. The base is a detached worktree of the merge base; the head is this branch. `PYTHONPATH=tests/hastub` both times.
  - `F1_wizard_widgets_from_registry.patch` (sha1 `fbe642521f4a3d1c174d5c7739c0c40561b5d7fd`). Base: `delta_S=+0.0000`, `admissible=1`. Head: `delta_S=+0.4761`, `literal_clone_copies=184->132`, `admissible=1`. Perturbation: `perturbed_delta_S=+0.0000` at both ends.
  - The four card patches C1 to C4, applied in order (sha1s `95ff96bf`, `4d2cb425`, `d1796855`, `048db6e9`). Base: `delta_S=+0.0000`. Head: `delta_S=+1.0958`, with `card_dead_definitions=1->0` (C1 gives D7-s3-02's `textWidth` its caller) and `card_clone_copies=108->101`. Perturbation: `perturbed_delta_S=+0.0000` at both ends.
- **Today's tree.** `card.measure` reads `card_dead_definitions` 0 with no dead name: R10-UX-SETUP (#2346) gave `textWidth` its callers. It reads `card_clone_copies` 108, and `literal_clones.measure` reads 184. These are the three new rows.
- **Corpus.** In round 1, `calibrate.py --measure-corpus --only-metric literal_clone_copies,card` at `033998cb5` leaves `corpus_vectors.json` byte-identical (`git diff --quiet` exits 0). The two changed metrics read the same 87 trees the same. In round 0, `python3 tools/audit/archscore/calibrate.py --measure-corpus --jobs 4` ran every job, which is the precondition carried from #2340. It covered 87 trees, 67 `ok` and 20 `ERRORS`. The 20 are `_family_splits_error` and `_family_orphan_overrides_error` (`KeyError: 'entity'`) on history trees that have no `entity` module. They are stored in `origin/main`'s `corpus_vectors.json` too (`grep -c _family_splits_error` 20). `git diff --quiet -- tools/audit/archscore/calibration/corpus_vectors.json` exits 0: the re-measure is byte-identical.
- **Calibration.** Round 1: `python3 tools/audit/archscore/calibrate.py --record` at `033998cb5`, the instrument of this head. It printed RECORD for exactly `rt_42b_literal_module_constant`, `rt_42c_literal_keyword_args` and `rt_44b_card_noop_split`, each GAME and NULL. The run printed `CALIBRATION 105/133 labelled cases classify as their label says`, `RED TEAM 80/80 attempts read NULL or inadmissible; IMPROVES: none` and `KNOWN-OPEN 1` (`rt_04zz1`, unchanged), and no `SENSITIVE` line. Round 0 recorded the twelve part-4 cases. `git diff origin/main -- tools/audit/archscore/calibration/expected.json` is 90 insertions and 0 deletions.
- **Mutants and ablations.** The figures above come from `calibrate.py --only <the twelve or fifteen cases>`, with the mutant applied or `ARCHSCORE_ABLATE` set.
- **Scoped gate**, every line below re-taken at `d41773bbf` (`brief_lint.mjs`: `TOTAL: 0 error(s) across 47 file(s)`). `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 4 script(s) run, 29 scoped out`. It names four scripts:
  - `tests/arch_score.py`: it re-derives the calibration recorded above and runs on CI (heavy-script rule).
  - `tests/arch_score_head.py`: `ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 169 checks PASSED`.
  - `tests/entities.py`: `ALL 2346 ENTITY CHECKS PASSED`. Its ci-ratchet null control derives the three new rows at the values recorded.
- **`run.sh`'s `run_always` scripts.** `tests/env_drift.py --claims-only d569693ad41fa4f4f95a3d4bbec7cea94ed1df26` prints `claims hygiene: d569693ad41fa4f4f95a3d4bbec7cea94ed1df26 ok`. `tests/closure.py selftest` prints `ALL 115 closure shrink pins PASSED`. `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`. `tests/layout.py` prints `layout self-test: ok`. `python3 tools/audit/seat/tmp_paths.py --check` prints `0 refused`.
- **Agreement lane.** `node tools/policy/agreement.mjs --only discovery`, run with `tools/policy/agreement.mjs` equal to origin/main (`git diff --quiet origin/main -- tools/policy/agreement.mjs` exits 0), prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (not touched).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL` (no package file changes).

## Raise justification

`tests/ci_budgets.json` gains three new rows. They are new ratchets, not raises, and no existing row moves: `archscore.literal_clone_copies` 184, `archscore.card_dead_definitions` 0 and `archscore.card_clone_copies` 108, each at the value its metric derives at this head. The rows are needed because the three metrics add keys to the score vector, and `ci_ratchet` refuses a derived key with no row as growth. The crashed branch recorded `card_dead_definitions` 1; R10-UX-SETUP has since given `textWidth` its callers, so the row is recorded at 0.

Payments considered:
1. Make the metrics gate-only. They would still be vector keys, so they would still need rows.
2. Keep them out of the vector. The score would not price them, which is the point of roster items 2 and 3.

A change to a `*_budgets.json` merges only on the owner's approving review at its head (budget-raise-gate, 0013). The orchestrator handles it under mandate 6175172275, as for parts 2 and 3.

`Architecture score: dS +0.0000 NULL`: no package file changes.

## Unpinned sites

n/a for production code. The diff touches only the instrument, `tools/audit/archscore/`, and its registrations. The new predicates are pinned by the calibration cases and by the mutants and ablations above; M5 and M6 are pinned by the `literal_clone_copies` row value.

Two round-1 guards survive their mutants, and both are over-fire guards. Under each mutant, no case moves and today's values do not move:
- **M11, the shadow guard** (`literal_clones.specs`: a module constant is not read inside a function that binds the same name or takes it as a parameter). Without it, a function that rebinds a constant's name would read the constant's literal in place of its own value. It would then over-count a spec as a clone of the constant's other readers. No function on today's tree or on the pin binds a module-constant name that a spec reads, so no value pins the guard. A planted case would be an honest-code NULL plant built only to pin it. The guard is one comprehension, and it is stated in the docstring.
- **M12, the parenthesis-depth guard** (`card.drop_noops`). Without it, the condition of a `for (let i = 0; i < n; i++)` header (`i < n`) follows a `;`, is made of pure tokens, and ends at the next `;`, so it would be dropped. No current 20-token window depends on such a run, so today's `card_clone_copies` stays 108. The guard keeps a header-shaped run from being read as a no-op. It is the precondition the `ABOUT.md` "do not see" list states ("a no-op inside a parenthesis").

## Architecture score

n/a: no package file changes. The instrument change takes effect after merge (`ABOUT.md`, "What R10-ARCHSCORE-COVERAGE part 4 moved").

## Red checks

- **`briefs`** (check-run `117611794944`, failure at `2183ab58f`), and **`pr-contract`** (`117611899608`), which is red with it.
  - Root cause: this branch's `from archscore.metrics.card import _IDENT` sat at the top of `tests/doc_claims.py`. It moved every line below it down by one.
  - `dev/programme/carries/carry-1645.json` cites `tests/doc_claims.py:476` and `:565` for `check_initial_setup_menu` and `check_simulate_plan_fields`. Origin/main has them at 477 and 568, and the branch had them at 478 and 569. Locally, `node tools/policy/brief_lint.mjs` at `2183ab58f` printed `'check_simulate_plan_fields' not found near tests/doc_claims.py:476; found at line 569 instead` and `TOTAL: 1 error(s) across 47 file(s)`.
  - Fix (`d41773bbf`): the import moves to module level directly above `_tokens`, so no cited line shifts. I did not edit the carry, which belongs to the R9 record.
  - At `d41773bbf`, `brief_lint.mjs` prints `TOTAL: 0 error(s) across 47 file(s)` and `tests/doc_claims.py` prints `ALL 169 checks PASSED`.
- No other check-run had concluded red at `2183ab58f` when read; `closures`, `fast (3.14)` and `Analyze (python)` were still in progress. CI has not run on `d41773bbf`.

## Forward-carry

- **R10-BRIEFS-FOLD (`dev/governance/dimensions/D7.md`).** The folded D7 brief can cite `literal_clone_copies`, `card_dead_definitions` and `card_clone_copies`. `tools/audit/archscore/ABOUT.md`'s part-4 section states what each reads and what each does not see, and the attempt ids carry the counters. The orchestrator wrote the residual-limits carry at `72b97a4a5`. This seat did not touch the roster.
- **Part 5 (item 6, the shape census).** It stacks on this head, because `expected.json` and `ci_budgets.json` are both appended.

## Friction

- R10-ARCHSCORE-COVERAGE-p4: unclear: the brief asks for one red-team attempt per counter, and each of this seat's attempts re-spelled its counter's own rule (float bounds, a local hop, renamed locals). Round 1 blocked on the neighbouring spellings: a module constant, a keyword argument and a no-op statement. An attempt set that covers a rule's neighbours, and not only the rule, would have found them.
- R10-ARCHSCORE-COVERAGE-p4: unenforced: `prepr.sh` passed clean at `c8d1382a3`, and CI's `briefs` job went red on the same diff. `prepr.sh` step 3f runs `brief_lint.mjs` only when the diff touches a pinned path. Otherwise it prints `skip brief_lint no pinned path changed, so CI's briefs job reads this head's copy`, which leaves CI as the first reader of a line shift under a carry's citation. Here the shift was in `tests/doc_claims.py`. Running `brief_lint.mjs` unconditionally before a handoff would have caught it.
- R10-ARCHSCORE-COVERAGE-p4: cost: the box ran at load 130 to 300 for this session. One `calibrate.py --record` took about 2.5 hours of wall time against about 40 minutes of CPU. A seat cannot shorten the full calibration, because `--record` with `--only` would overwrite `expected.json` with the subset.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

