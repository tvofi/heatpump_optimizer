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

`ba9653fa067c003bc19cbeed5177e3b1fbf71e05` on `r10-rca-structure-blind`. It merges `origin/main` `55dc8d9c2` into the authored head `bec623af494f75131610e27b1f711dde45dfcdc6` with no conflict. The merged commits touch `.github/`, `tools/pr/codeql_scope.py` and delivery rows only: no package file, no `tests/structure*`, nothing an instrument here reads. So every figure measured at `bec623af4` (on `f1b21daab`) holds. Re-taken on the merge: `tests/structure.py` passes, the plant harness reads `plant_refused=1 (name_kept_members)`, and `score.py --diff origin/main` reads `dS +0.0000 NULL`. Measured in a full clone (`git fetch --unshallow --tags origin`) with `/etc/profile.d/hpo-toolchain.sh` sourced, on 2026-10-18.

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
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`, `MODE: SCOPED`, 8 scripts. See Red checks for the two that went red here.

## Architecture score

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff origin/main`). No package file changes.

## Red checks

`tests/stress.py` went red once in the local scoped gate: `shoulder/tariff+pv+cycle used 12324 ms of CPU = 290x the 42.5 ms reference measured beside it (budget 268x)`. The diff changes no package file, so solver CPU is not this PR's; the one re-run alone under the lease read `ALL 110 STRESS CHECKS PASSED`. No cheaper detector exists for box-load timing. Its own re-measure is the instrument.

`tests/harness_headers.py` went red locally on the first run. The new harness inlined a `repo_root` that differed from the canonical helper (`FAIL every inlined walk matches the canonical helper`). Fixed before the commit. The cheaper detector already exists: the same check, run locally before handoff, which is how it was caught. No new detector is owed.

## Forward-carry

- **Carry: #2259 item 2**, R10-ARCHSCORE-COVERAGE part 4 (#2373). When it merges, `card_dead_definitions` registers as a `field_coverage.mjs` census with the `arch-score` gate, and the ledger's "Not reached" entry for the card `.js` is struck (RCA §5.3).
- **To the orchestrator:** whether the hint-keyed finder harness and the hard-coded D14 sweep enumerator fold as `beyond_finding` seams, or go to the D14 brief by `finding-propagation.md` (RCA §8, question 1).
- **To tvofi**, both policy-shaped:
  - the sentence "a declared unmeasured shape is a gated count" in `fixer.md` or the D7 brief;
  - a `fold_ledger.py check` arm (RCA §8, questions 2 and 3).

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
