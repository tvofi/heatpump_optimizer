Round-10 root-cause record for class N-structure-blind (#2235): `dev/audit/rca/R10-N-structure-blind.md`. It also builds the two countermeasures the record proposes. The analysis follows `dev/governance/roles/root-cause.md` under `dev/governance/rules/defect-root-cause.md`.

Part of #2235.
Part of #201.

Session: https://claude.ai/code/session_01CgzB6p4kRfdYooPCN1S3mT

**Cause.** #1838 (F10.4) carried out RCA-BULK-2's "declared blind shapes are counted" as a printed `unmeasured:` line. The line sat outside `measure()`'s `metrics`, so no budget row read it. It rose 124 → 152 over `v6.7.14`..`v7.0.0` with the ratchet green. On `origin/main` today, a planted dead `as_dict` that only an untyped load reaches passes both `tests/structure.py` and `arch-score` (`NULL`, no rise).

**State: (c).** The barrier ran and the item was carried out, but its unit was wrong in three ways:
- a printed count, not a ratchet;
- one plant per past instance, not per shape;
- one instrument in one language.

**Cost test.** 0.8 instances per release × 9.8 h per finding = 7.8 h per release expected, against ≤ 2.9 h (an estimate) and 0 s of CPU for the row.

What changes:
- **`tests/structure.py`** gains the ratchet row `name_kept_members`: the name-kept table's length, which was printed before. `tests/structure_budgets.json` records it at 38. A new `MAX` key is not a raise under `tools/policy/budget_raise_gate.py`. The row was added by hand, and `recorded_at` is unchanged.
- **`tools/policy/field_coverage.mjs`'s census arm** now requires each registered count to name its `gate`, the budget row that must refuse the planted member. A count that moves with no `FAIL <gate>` is `BLIND: UNGATED`; a census with no gate, or one already red unplanted, is `REFUSED`. A third census registers `name_kept_members`. CI runs the base's pinned copy, so this takes effect after merge; `--self-test` runs from this branch.
- **`dev/audit/config/bugclasses.json`**: the class's `barrier` names every instrument it now spans, and its "Not reached" list holds only shapes with a named owner. The `rca` list and an `_rca` row cite the record.
- **`dev/audit/harnesses/r10_rca_name_kept_plant.py`** is the acceptance harness: four plant arms through the production `measure()`, in memory.
- **`tests/closures.json`** gains its INERT READS entry (`tools/pr/ci_predict.py --apply-inert`).

**Two things a reviewer will ask.**

- **The budget row was added by hand.** `tests/structure.py --record` was denied in this seat's sandbox, so `name_kept_members: 38` was inserted into `tests/structure_budgets.json` directly. `--record` would have written the same table: `measure()` at this head differs from the committed table in no row (`name_kept_members` measures 38), and the only other difference would be `recorded_at` moving from `e5f7e169d` to the merge base `55dc8d9c2`. `recorded_at` is unchanged and is still an ancestor of `origin/main`, so `ratchet` reads it as reachable.
- **`tools/policy/field_coverage.mjs` is not under the policy cap.** It is not matched by `tools/policy/policy_lint.mjs`'s `POLICY_GLOBS` (CLAUDE.md, AGENTS.md and the rule, role, dimension, brief, README, skill and template markdown), and it sits under none of its `POLICY_DIRS`. It has no entry in `dev/governance/config/policy_budgets.json` and no line in `.github/CODEOWNERS`. It is a governance check, not policy text, so this PR needs no owner approval under CLAUDE.md's policy rule. CI runs the base's pinned copy, so its change takes effect only after merge.

## Head

`2a01f9ee2dd4d6093780d24b9cd75b92ff9d3cb9` is the code head: it merges `origin/main` `913ce1ff5` into this PR's head `45ecca4f9a0cd2cd25712e9cc2252a32b6f6dfa3` with no conflict (`git merge origin/main`, no rebase). The authored work is unchanged since `bec623af4`; the merge brings in main's round-10 merges up to `913ce1ff5`, and the range `fa16596c3..913ce1ff5` touches only `dev/programme/delivery/` rows (`git diff --name-only fa16596c3 913ce1ff5`). This PR still changes no file under `custom_components/`: `git diff --name-only origin/main...HEAD | grep -c custom_components` reads 0.

The merge was checked for a semantic break, not only a textual one. #2406 removed `roster_lib.DEFAULT_ROSTER_REF`: `grep -rln DEFAULT_ROSTER_REF . --include='*.py' --include='*.sh' --include='*.mjs'` at this head prints nothing, so no file here reads it. #2421 (the train raise hold) cannot hold this PR: it adds one `MAX` key to `tests/structure_budgets.json` and moves no existing row (see Budget below).

Re-taken at this head, 2026-10-19, on a box at load average above 250, with the seat interpreter shims first on `PATH` and `PYTHONPATH=tests/hastub`:

- `python3 tests/structure.py` ends `STRUCTURE RATCHET PASSED`, with `ok name_kept_members 38 <= 38`.
- `python3 dev/audit/harnesses/r10_rca_name_kept_plant.py` reads `plant_refused=1 count (name_kept_members)`, `null_refused=1 count (dead_methods)`, `typed_refused=0`, `row_in_budgets=True`.
- `node tools/policy/field_coverage.mjs --only census` reads `read=3 ignored=0 declared_none=0 blind=0 dead=0 refused=0`, with `name_kept_members: 38 -> 39 with one planted member, refused on name_kept_members`; ends `FIELD COVERAGE ok`.
- `node tools/policy/field_coverage.mjs --self-test` ends `FIELD COVERAGE SELF-TEST ok`.
- `python3 tools/audit/fold_ledger.py check` reads `0 violation(s)`.
- `python3 tools/audit/archscore/score.py --diff origin/main` reads `Architecture score: dS +0.0000 NULL`.
- `python3 tools/pr/ci_predict.py --base origin/main` reads `no closures or fast red predicted`.

The mutation proof and the RCA figures below were taken at `bec623af4`/`ba9653fa0`; the merge changes none of `tests/structure.py`, `tools/policy/field_coverage.mjs`, `dev/audit/config/bugclasses.json` or the harness (`git diff --name-only 45ecca4f9 HEAD` names none of them), so those figures hold.

## Budget

No budget row is raised. `tests/structure_budgets.json` gains the new key `name_kept_members: 38`; every existing row is unchanged and `recorded_at` is unchanged. A new `MAX` key is not a raise under `tools/policy/budget_raise_gate.py`, and the `budget-raise-gate` check read green on the previous head. Nothing here is argued as unpayable because nothing rises.

## Mutation proof

Each mutant was applied to this head's `tests/structure.py` in a scratch worktree, run, and restored.

- **M0, unmodified.** `ok 56 counting rules hold`, `ok name_kept_members 38 <= 38`, `STRUCTURE RATCHET PASSED`.
- **M1, the row dropped from `measure()`.** `FAIL name_kept_members: in the budget table but never measured -- re-record`, rc=1.
- **M2, the row hard-coded to 0.** `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`, rc=2.
- **M3, typed receivers ignored** (`owners = None` in `dead_members`). The run reads `3 COUNTING RULE(S) BROKEN`, rc=1, from the self-check, before the row is read.
- **The defect itself.** With the row and budget absent, the plant arm reads `plant_refused=0`, against `plant_refused=1 (name_kept_members)` with the row.
- **The census arm, red.**
  - On main's `structure.py` and budgets, `name_kept_members` is `REFUSED` because the count line cannot be read.
  - With this head's `structure.py` and the row uncapped (9999), it reads `BLIND census structure.py name_kept_members: UNGATED, 38 -> 39 with one planted member and no FAIL on name_kept_members`.
  - Both runs end `FIELD COVERAGE REFUSED`.
- **The census self-test's new arms** (UNGATED, no gate, red unplanted) each fail when `censusRun`'s matching branch is removed; all pass on this head.

## Null control

- The unmodified head reads `clean_refused=0` and `typed_refused=0`.
- The unique-name null reads `null_refused=1 (dead_methods)` at both ends, as it did before this change.
- `node tools/policy/field_coverage.mjs --only census` on this head reads `read=3`, with each census refused on its own row: `dead_methods 0 -> 1`, `dead_top_level_symbols 1 -> 2`, `name_kept_members 38 -> 39`.
- `python3 tools/audit/fold_ledger.py check` reports `0 violation(s)`.

## Figures

- Plant arms, head: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_rca_name_kept_plant.py`. On main, add `--structure` and `--budgets`, each exported with `git show origin/main:<path>`.
- Census arm: `node tools/policy/field_coverage.mjs --only census`. Self-test: `node tools/policy/field_coverage.mjs --self-test`, ending `FIELD COVERAGE SELF-TEST ok`.
- Ratchet: `PYTHONPATH=tests/hastub python3 tests/structure.py`.
- Ledger: `python3 tools/audit/fold_ledger.py check`.
- Every figure in the RCA (the 124 → 152 series, release counts, fix spans, enumerator and finder-harness re-runs, the arch-score plant) is in its section 7, each with its command.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`, `MODE: SCOPED`, 8 scripts, at this head. `tests/stress.py` is red locally on an unmodified `origin/main` too; see Red checks.

## Architecture score

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff origin/main`). No package file changes.

## Red checks

The latest CI on the previous head `45ecca4f9` has one red, `pr-contract`, and it is answered here.

- **`pr-contract`**: its `pr-body` step refused the old body: "check `wave-script` is red and `## Red checks` does not name it". At the time that step ran, `wave-script` and `delivery-status` were red because `origin/main` was red from `5756f2b1` until #2423, #2424 and #2420 merged. Both read `pass` in the same run's later job results, and main is green again. This merge brings those three fixes in, so `wave-script` and `delivery-status` are cleared by the main merge (their cause was main's, not this diff's; this diff touches no `.github/` or wave script). The re-taken body names them, which is the repair.
- `closures` and `fast (3.14)` read `pass` on that head (30m and 53m runs), including `tests/stress.py`.

Local scoped gate (`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`, `MODE: SCOPED -- 8 script(s) run, 25 scoped out`): `features`, `entities`, `doc_claims`, `structure` (`STRUCTURE RATCHET PASSED`), `arch_score` (`ALL 255 ARCHITECTURE SCORE CHECKS PASSED`), `arch_score_head` (`ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`) and `harness_headers` (`ALL 109 HARNESS HEADER CHECKS PASSED`) are green. `tests/stress.py` is red locally, twice, with the same economics figure:

- `FAIL shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`, plus a CPU-budget miss under the box load (`shoulder/tariff+pv+cycle` at 222x to 300x of its reference against a budget of 268x).
- The control: `python3 tests/stress.py` on an unmodified `origin/main` checkout (`913ce1ff5`) in this seat prints the same `FAIL shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`. A PR that changes no file under `custom_components/` cannot move a solve, so the figure is this seat's interpreter and box, not the diff. `fast (3.14)` on CI, which runs the same script on the Linux toolchain, reads `pass` at the previous head. The cheaper detector is the one CI already runs; none is added.

## Forward-carry

- **Carry, landed past its carrier: #2259 item 2, part 4 (#2373).** #2373's branch is now empty against `main`: its tree after `git merge origin/main` is identical to `origin/main`, because #2401 (part 5) was stacked on part 4 and carried its code and its `tests/ci_budgets.json` rows (`card_dead_definitions`, `card_clone_copies`, `literal_clone_copies`) onto `main`. The precondition this PR carried to part 4 was therefore not delivered by it: on `origin/main`, `tools/policy/field_coverage.mjs` CENSUSES registers no `card_dead_definitions`, and N-structure-blind's `barrier` in `dev/audit/config/bugclasses.json` still lists the card `.js` under "Not reached" (`git grep card_dead_definitions origin/main -- tools/policy dev/audit/config` prints nothing). The same precondition is already in the R10-ARCHSCORE-COVERAGE group's `brief` and `carry` in `dev/programme/rosters/wave-r10-groups.json` on `origin/main` (the R10-ARCHSCORE-COVERAGE group and the group that records the card rows). **Owed by the orchestrator:** re-point that carry at a live group, since #2373 will not run, and say which group registers the card census.
- **To the orchestrator:** whether the hint-keyed finder harness and the hard-coded D14 sweep enumerator fold as `beyond_finding` seams, or go to the D14 brief by `finding-propagation.md` (RCA section 8, question 1).
- **To tvofi**, both policy-shaped:
  - the sentence "a declared unmeasured shape is a gated count" in `fixer.md` or the D7 brief;
  - a `fold_ledger.py check` arm (RCA section 8, questions 2 and 3).

## Friction

none


🤖 Generated with [Claude Code](https://claude.com/claude-code)
