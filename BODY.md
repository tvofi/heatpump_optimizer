R10-ARCHSCORE-COVERAGE, part 4 of 5: the card and literal specs priced in the architecture score (roster items 2 and 3; ARCH2-s5, D7-s3-02).

Part of #2259.
Part of #2235.

Parts 1 to 3 (#2293, #2311, #2320) landed items 5, 4 and 7, and 1. This part is items 2 and 3, plus the dead-code carry from R10-STRUCTURE-BLIND; part 5 is item 6, the shape census. The diff is `tools/audit/archscore/` with its two registration files (`tests/closures.json`, `tests/ci_budgets.json`); `tests/structure.py` is not touched.

Resumed, not restarted: the crashed part-4 seat's commits `f872b27dc` to `8fda13ce7` (the parent of its snapshot `wip-sync/ext-wt-d480264e`, whose tree equals it) carry the metrics and cases. This seat merged `origin/main` `6e5753a4a` into them and re-executed steps 2 to 8 at the merged head.

What changes. Three score metrics at the floor weight. They guard no register class, so `weights.json` is unchanged and its floor applies:

- **`literal_clone_copies`** (`metrics/literal_clones.py`, item 3): copies of one declaration spelled as a call or literal more than once, such as a selector, a schema or a record. A spec is a call, dict, list, tuple or set of at least 6 nodes that computes nothing at runtime. Annotations, `except` types, generic subscripts and decorators are not specs. A clone class counts its maximal members. The clone census (`duplication_copies`) cannot see these: a spec sits inside one statement, below its window, which is why the 44 wizard selector specs read NULL.
  - C20: numbers are compared by value, keywords and dict items in order.
  - C21: a local bound once to a spec reads as that spec.
- **`card_dead_definitions`** and **`card_clone_copies`** (`metrics/card.py`, item 2). The card (`www/*.js`) is the largest UI surface, and before this part every metric read Python only. It is read by a stdlib tokenizer, never a parser, so each rule is stated on tokens.
  - Dead definitions are top-level `function`/`class`/`const`/`let` names and class members that no other token names, less the browser, lit and Home Assistant hooks. D7-s3-02's `textWidth` was one.
  - Clones are functions sharing a 20-token window once their own names are numbered (C22).
- **The agreement lane.** The JavaScript identifier grammar `[A-Za-z_$][\w$]*` was shared by `tests/doc_claims.py`, `metrics/card.py` and attempt 44, and was unregistered, so `prepr.sh` refused the branch. Attempt 44 now reads `card._IDENT`, so there is one copy fewer. `tools/policy/agreement.mjs`'s `SHARED_GRAMMARS` now records the two remaining readers as one concept. This is the one line outside `tools/audit/archscore/` and the registration files. `node tools/policy/agreement.mjs` reads `unregistered=0`, and `--self-test` reads `13 of 13`.
- **The carry from R10-STRUCTURE-BLIND (#2340):** `metrics/common.py`'s `HA_CONVENTION_METHODS` and `is_ha_method` are deleted. Nothing read either, and the list had drifted from `tests/structure.py`'s.

Calibration: each metric has a planted BAD, GOOD and NULL case (`a3_literal_clone_copies_*`, `a3_card_dead_definitions_*`, `a3_card_clone_copies_*`), and each counter has a red-team attempt:
- `rt_42_literal_respelled` for C20;
- `rt_43_literal_local_hop` for C21;
- `rt_44_card_rename_locals` for C22.

The attempts were numbered 24 to 26 on the crashed branch. Part 3 landed its own 24 to 41, so here they are 42 to 44. `expected.json` gains exactly those twelve cases. No recorded verdict moved, no weight changed, and no weight perturbation moves a verdict.

Alternatives considered:
- A JavaScript parser for the card lost to the tokenizer. The scorer is stdlib-only, so a parser would be a dependency, and every rule here can be stated on tokens.
- A 16-token card window lost to 20. At 16, ARCH2-s5's finite-number owner (patch C4), which is a dedupe, read one copy more. At 20, no card patch rises.
- Folding literal specs into `duplication_copies`' window lost: that census is `tests/structure.py`'s, and this group does not touch it.

## Head

`6dae14c46b36db5e136f845543cc9030c38ce54d`. Origin/main `6e5753a4a` is merged in, and `git merge-base origin/main HEAD` is `6e5753a4aca8b240559e8e11e8a68c7de988cd73`. The figures below were taken at `21dd4a3e5`. The one commit since then, `6dae14c46`, changes attempt 44's identifier test to read `card._IDENT` and registers that grammar. At this head, `calibrate.py --only rt_44_card_rename_locals` reads NULL again, and the scoped-gate selection is the same three scripts.

## Mutation proof

Each mutant was applied in place on the committed head, run, and restored with `git checkout --` (`mutate_p4.sh` in the seat's scratch). The runner was `python3 tools/audit/archscore/calibrate.py --only` the twelve part-4 cases. The unmutated run, M0, classifies every case as recorded.

- **M1**, `card.dead_definitions` returns `[]`. MOVED: `a3_card_dead_definitions_control` WORSENS -> NULL, `_fix` IMPROVES -> NULL.
- **M2**, the dead test `seen[d] <= 1` becomes `<= 0`. The same two cases move.
- **M3**, the window union never joins (`len(owners) > 999`). `rt_44_card_rename_locals`'s own locator refuses: it finds no clone class to rename. Run without it, `a3_card_clone_copies_control` reads WORSENS -> NULL and `_fix` IMPROVES -> NULL (`mut_M3b`).
- **M4**, `is_spec` returns False. MOVED: `a3_literal_clone_copies_fix` IMPROVES -> NULL. The control stays WORSENS through its other terms, `dead_members` and `unread_private_globals`.
- **M5**, maximal members off: every occurrence counts, nested ones included. **M6**, decorators read as specs (the `9d94f8fe7` exclusion undone). No planted case moves their verdict. Both are pinned by value instead: `literal_clones.measure` on today's tree reads 184 at M0, 218 under M5 and 190 under M6, and the `archscore.literal_clone_copies` row of 184 refuses either as growth.

Ablation (`ARCHSCORE_ABLATE`). Each switch reopens its own attempt, and only that one:
- `C20`: `rt_42` reads IMPROVES (+0.0683), and `a3_literal_clone_copies_null` reads IMPROVES;
- `C21`: `rt_43` reads IMPROVES (+0.0086);
- `C22`: `rt_44` reads IMPROVES (+0.1565).

## Null control

- **The base reads the defects as NULL.** With the finder's harness on the base instrument, ARCH2-s5's F1 (the wizard reading its registry widgets) reads `delta_S=+0.0000`, and the four card patches together read `delta_S=+0.0000`. At this head they read `+0.4761` and `+1.0958`.
- **Each harness run's own perturbation reads 0 at both ends.** The patches are reversed onto the prototype: `perturbed_delta_S=+0.0000` and `perturbed_vector_equals_baseline=1`.
- **Honest code does not trip the new definitions.**
  - Each NULL plant reads NULL: a respelled bound, a renamed card function, a renamed parameter.
  - The full corpus re-measure is byte-identical to the stored vectors, so no corpus verdict moved.
  - `calibrate.py --record` printed RECORD for the twelve new cases alone.

## Figures

- **ARCH2-s5's finder harness.** Run as `$EXPORT/dev/audit/rounds/round10/D7/arch2-s5/arch_delta.py --base 9061fbd3d <patches>` (sha1 `4fa94bb48af93fa21d1751e94a67c057b0a63f31`), where `$EXPORT` = `git archive 3930b421a dev/audit/rounds/round10/D7/arch2-s5`. The directory is copied into each tree, because the harness finds `tools/audit` from its own path. The base is a detached worktree of `6e5753a4a`; the head is this branch. `PYTHONPATH=tests/hastub` both times.
  - `F1_wizard_widgets_from_registry.patch` (sha1 `fbe642521f4a3d1c174d5c7739c0c40561b5d7fd`). Base: `delta_S=+0.0000`, `admissible=1`. Head: `delta_S=+0.4761`, `literal_clone_copies=184->132`, `admissible=1`. Perturbation: `perturbed_delta_S=+0.0000` at both ends.
  - The four card patches C1 to C4, applied in order (sha1s `95ff96bf`, `4d2cb425`, `d1796855`, `048db6e9`). Base: `delta_S=+0.0000`. Head: `delta_S=+1.0958`, with `card_dead_definitions=1->0` (C1 gives D7-s3-02's `textWidth` its caller) and `card_clone_copies=108->101`. Perturbation: `perturbed_delta_S=+0.0000` at both ends.
- **Today's tree.** `card.measure` reads `card_dead_definitions` 0 with no dead name: R10-UX-SETUP (#2346) gave `textWidth` its callers. It reads `card_clone_copies` 108, and `literal_clones.measure` reads 184. These are the three new rows.
- **Corpus.** `python3 tools/audit/archscore/calibrate.py --measure-corpus --jobs 4`, every job, which is the precondition carried from #2340. It covered 87 trees, 67 `ok` and 20 `ERRORS`. The 20 are `_family_splits_error` and `_family_orphan_overrides_error` (`KeyError: 'entity'`) on history trees that have no `entity` module. They are stored in `origin/main`'s `corpus_vectors.json` too (`grep -c _family_splits_error` 20). `git diff --quiet -- tools/audit/archscore/calibration/corpus_vectors.json` exits 0: the re-measure is byte-identical.
- **Calibration.** `python3 tools/audit/archscore/calibrate.py --record --jobs 4` at `210b1f1e5`, the same instrument as this head. It printed RECORD for exactly the twelve part-4 cases. `git diff origin/main -- tools/audit/archscore/calibration/expected.json` is 72 insertions and 0 deletions. The run printed `CALIBRATION 105/133 labelled cases classify as their label says`, `RED TEAM 77/77 attempts read NULL or inadmissible; IMPROVES: none` and `KNOWN-OPEN 1` (`rt_04zz1`, unchanged), and no `SENSITIVE` line.
- **Mutants and ablations.** The figures above come from `calibrate.py --only <the twelve cases>`, with the mutant applied or `ARCHSCORE_ABLATE` set.
- **Scoped gate.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 3 script(s) run, 30 scoped out` and names `tests/arch_score.py`, `tests/arch_score_head.py` and `tests/entities.py`.
  - `tests/arch_score_head.py`: `ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
  - `tests/entities.py`: `ALL 2346 ENTITY CHECKS PASSED`; its ci-ratchet null control derives the three new rows at the values recorded.
  - `tests/arch_score.py` re-derives the calibration recorded above and runs on CI (heavy-script rule).
  - `run.sh`'s `run_always` scripts: `tests/env_drift.py --claims-only 6e5753a4aca8b240559e8e11e8a68c7de988cd73` (`claims hygiene: ... ok`), `tests/closure.py selftest` (`ALL 115 closure shrink pins PASSED`), `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`), `tests/layout.py` (`layout self-test: ok`). `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
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

## Architecture score

n/a: no package file changes. The instrument change takes effect after merge (`ABOUT.md`, "What R10-ARCHSCORE-COVERAGE part 4 moved").

## Red checks

none at the handoff; CI has not run on this head.

## Forward-carry

- **R10-BRIEFS-FOLD (`dev/governance/dimensions/D7.md`).** The folded D7 brief can cite `literal_clone_copies`, `card_dead_definitions` and `card_clone_copies`. `tools/audit/archscore/ABOUT.md`'s part-4 section states what each reads, and the attempt ids carry the counters. The roster carry is the orchestrator's to write.
- **Part 5 (item 6, the shape census).** It stacks on this head, because `expected.json` and `ci_budgets.json` are both appended.

## Friction

- R10-ARCHSCORE-COVERAGE-p4: cost: the box ran at load 130 to 300 for this session. One `calibrate.py --record` took about 2.5 hours of wall time against about 40 minutes of CPU. A seat cannot shorten the full calibration, because `--record` with `--only` would overwrite `expected.json` with the subset.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
