R10-ARCHSCORE-COVERAGE, final part: the card's dead-definition count registered as a gated census (the R10-RCA-STRUCTURE-BLIND precondition on part 4).

Part of #2259.
Part of #2235.

#2373 (part 4) closed empty, because #2401 (part 5) had already landed its code. The precondition #2415 carried onto part 4 (RCA `dev/audit/rca/R10-N-structure-blind.md` section 5.3; the group's `brief` and `carry` in `dev/programme/rosters/wave-r10-groups.json`) was not delivered. This branch delivers it.

**Stacked on #2415.** The precondition is written against #2415's census mechanism: the `gate` field, the `UNGATED` verdict, and the card's `.js` in the `Not reached` clause. None of these is on `origin/main`. This branch merges #2415's head `bd8011e9231944317162ffbde7824ffcad89ff2e` (and `origin/main` `abb397938097b0b64e49d29fbbfd0ce59afbaf7b`), so #2415 must merge first. This branch's own delta is three files against `git merge-tree --write-tree origin/main bd8011e92`: `tools/policy/field_coverage.mjs`, `tests/ci_ratchet.py` and `dev/audit/config/bugclasses.json`.

What changes:

- **The census arm takes an instrument per census.** Before, `censusCount` always ran `tests/structure.py` and looked for `FAIL <gate> `. Now each `CENSUSES` entry names an `instrument`: the `argv` it runs in the tree copy, and how that program reports a refusal on the `gate` row. There are two instruments.
  - `STRUCTURE_PY` is the old behaviour, unchanged.
  - `ciRatchet(job)` imports the ci-ratchet job's own `tests/ci_ratchet.py`. It runs `budget_problems` and `compare` over the real `tests/ci_budgets.json`, and `archscore_metrics(only={job})` gives it the score vector. Its refusal is a `  GREW  <row>: ` line plus a non-zero exit.
  - The tree copy also carries `tests/ci_ratchet.py`, `tests/ci_budgets.json` and `tools/audit/archscore/`.
  - A census with no instrument reads no count, so it is REFUSED.
- **`card_dead_definitions` is registered.** Its `gate` is `archscore.card_dead_definitions`, the ci-ratchet row #2401 recorded. Its plant is one unused top-level card function, `_censusPlantedDeadCardFunction`, appended to `www/heatpump-optimizer-card.js`.
- **The rest of the class is folded in.** Four other ci-ratchet rows count definitions nothing reaches, and nothing planted them either. Each is now registered with an append plant that moves it by exactly one: `archscore.dead_members` (job `structure`), `archscore.public_unused`, `archscore.unread_private_globals` and `archscore.unused_boundary_imports` (job `layering`).
- **`tests/ci_ratchet.py` `archscore_metrics` takes `only`.** It passes the filter to `vector.measure`'s existing job filter. With no argument the call is unchanged, so the ci-ratchet job still measures the whole vector.
- **`bugclasses.json`, N-structure-blind `barrier`.** The card's `.js` is struck from `Not reached`. The census-arm sentence now says the arm reaches the card's `.js` through `archscore.card_dead_definitions` (#2401), and reaches the four rows above.
- **The `UNGATED` line** now ends `no refusal on <row>`, not `no FAIL on <row>`. `FAIL` is only how `structure.py` spells a refusal; ci_ratchet spells it `GREW`.

Alternatives, and why each lost (fixer.md step 17):

- Run ci_ratchet's full vector for the card census. It costs about 45 s per `vector.measure`, twice per census. The `only` filter runs the same `vector.measure` card job and the same `compare`.
- Read `metrics/card.py`'s `measure` directly. That skips `vector.py`'s wiring and ci_ratchet's key prefix and comparison. A vector that stopped deriving the card row would then read as gated while the real ratchet no longer grades it (step 11: the check must read the gate's own artifact).
- Monkeypatch `vector.measure` inside the snippet instead of adding the parameter. That leaves `tests/ci_ratchet.py` untouched, but it ties the census to how `archscore_metrics` calls `vector.measure` internally. The parameter is the existing mechanism, exposed.
- Leave the four sibling rows unregistered. Refused: they are the same unplanted, ungated class, and each costs one plant.

Architecture score: no `custom_components/` file changes, and `tests/arch_score_head.py` passes at this head (`## Figures`). Caps: `node tools/policy/policy_lint.mjs --budgets` rc=0. No ratchet row moves and no raise is made, so no constraint binds.

## Head

`fbcf5c3e8f384fc240f8f15b28f68ccf5b3f441a`. That is `origin/main` `abb397938097b0b64e49d29fbbfd0ce59afbaf7b` merged, plus #2415's head `bd8011e9231944317162ffbde7824ffcad89ff2e` merged. `origin/main` tip read at 2026-10-19 06:05 UTC. Every figure below was measured at this head.

## Mutation proof

Each mutant was run from the worktree with `node tools/policy/field_coverage.mjs --only census`, then restored with `git checkout -- <file>`. The tree was clean afterwards (`git status --short | wc -l` printed 0).

- **M1, the row uncapped.** `tests/ci_budgets.json` `archscore.card_dead_definitions` 0 -> 9999. Printed `BLIND census archscore card_dead_definitions: UNGATED, 0 -> 1 with one planted member and no refusal on archscore.card_dead_definitions`, then `RESULT read=7 ... blind=1` and `FIELD COVERAGE REFUSED`, rc=1.
- **M2, a dead definition dropped.** In `tools/audit/archscore/metrics/card.py` `definitions()`, `t in ("function", "class")` became `t in ("class",)`, so top-level functions are no longer enumerated. Printed `BLIND census archscore card_dead_definitions: one planted member moved the count 0 -> 0, not by one` and `FIELD COVERAGE REFUSED`, rc=1.
- **Self-test arms**, from `node tools/policy/field_coverage.mjs --self-test`, rc=0:
  - `every registered census names its gate row, its instrument, a reader and a plant`;
  - `a census with no instrument reads no count, so it is REFUSED`;
  - `the ci-ratchet reader refuses on its own row only`, which refuses `GREW` on the row and not on an `ok` line or on the `_x`-suffixed key;
  - `the ci-ratchet row reader reads its own row only`, which reads nothing from a `?` not-derived line or a suffixed key.
- **Unkilled.** Deleting the `card_dead_definitions` entry from `CENSUSES` passes every check. No instrument enumerates which rows must carry a census. See `## Forward-carry`.

## Null control

At the head, unmutated: `node tools/policy/field_coverage.mjs --only census` prints `census archscore card_dead_definitions: 0 -> 1 with one planted member, refused on archscore.card_dead_definitions`, `RESULT read=8 ignored=0 declared_none=0 blind=0 dead=0 refused=0` and `FIELD COVERAGE ok`, rc=0. The card's count is 0 unplanted, which matches #2401's recorded row. It reads 1 with the one planted function.

At the stacked base, before this branch's commits (`1128c3937`, #2415 merged onto `913ce1ff5`), the same command printed `RESULT read=3`. That is the three `structure.py` rows only, with no card line. So the base registered no census on the card.

## Figures

The rule for every census line: one run of the census arm, which plants one member per registered census in a temporary tree copy and reads the row's printed count before and after.

- `node tools/policy/field_coverage.mjs --only census`, at the head: 8 censuses read, 0 blind, 0 refused. `n` for each:
  - `dead_methods` 0 -> 1;
  - `dead_top_level_symbols` 1 -> 2;
  - `name_kept_members` 38 -> 39;
  - `archscore.card_dead_definitions` 0 -> 1;
  - `archscore.dead_members` 1 -> 2;
  - `archscore.public_unused` 1 -> 2;
  - `archscore.unread_private_globals` 0 -> 1;
  - `archscore.unused_boundary_imports` 1 -> 2.
  - Each is refused on its own row. The run's own `seconds=` field is the arm's cost, read from that instrument.
- The seam rule (fixer.md step 8): `jq -r 'keys[]' tests/structure_budgets.json tests/ci_budgets.json | grep -iE 'dead|kept|unused|unread|orphan'` returns 9 rows. Disposition of each:
  - closed by #2415 and already planted: `dead_methods`, `dead_top_level_symbols`, `name_kept_members`;
  - closed in this diff: `archscore.card_dead_definitions` (the precondition), `archscore.dead_members`, `archscore.public_unused`, `archscore.unread_private_globals`, `archscore.unused_boundary_imports`;
  - not closed: `archscore.family_orphan_overrides`. It is not a liveness count: it counts `ENTITY_FAMILY_OVERRIDES` entries whose family has fewer than two members. The arm's append-only plant cannot reach it, because `family_splits.overrides` reads the first `ENTITY_FAMILY_OVERRIDES` assignment, and an appended second dict is never read. Carried in `## Forward-carry`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 8 script(s) run, 25 scoped out`. All of these ran locally with `PYTHONPATH=tests/hastub`, each rc=0:
  - `tests/structure.py`;
  - `tests/arch_score.py`: `ALL 255 ARCHITECTURE SCORE CHECKS PASSED`;
  - `tests/arch_score_head.py`: `ALL 18 ... PASSED`;
  - `tests/doc_claims.py`: `ALL 169 checks PASSED`;
  - `tests/harness_headers.py`;
  - `tests/features.py`: `ALL 4198 FEATURE CHECKS PASSED`;
  - `env -u BASH_ENV python3 tests/entities.py`: `ALL 2349 ENTITY CHECKS PASSED`;
  - the run_always lines: `tests/layout.py`, `tests/closure.py selftest`, and `tests/env_drift.py --claims-only <merge base>`.
  - `tests/stress.py` is left to CI.
- `python3 tools/audit/fold_ledger.py check`: `0 violation(s)`, rc=0.

## Red checks

none. No CI has run on this head yet.

## Forward-carry

- **To the orchestrator: merge order.** #2415 must merge before this branch, which carries #2415's head.
- **To the orchestrator, R10-RCA-STRUCTURE-BLIND: the record row.** Its `bugclasses.json` RCA row `R10-N-structure-blind` still reads `card language arm carried to #2259 item 2 (#2373)` with `landed: null`. That is a recounting record and this branch leaves it as written. The orchestrator's record step should name this PR as the arm's landing.
- **To the orchestrator, unkilled mutant: a registration pin.** Deleting a `CENSUSES` entry is caught by nothing. A pin that every dead/unused ratchet row named by the seam rule above carries a census would kill it. Not built here, because the rule is a grep over key names, not a declared registry.
- **To tvofi, an owned path: the CI trigger.** `.github/workflows/governance.yml`'s field-coverage step runs on a pull request only when one of its listed inputs changes. `tests/ci_budgets.json`, `tests/ci_ratchet.py`, `tools/audit/archscore/` and the card's `.js` are not on that list. So a pull request that uncaps a census's ci-ratchet row (M1's shape) is caught on the schedule run, not on its own run, while budget-raise-gate still refuses the raise itself. Adding those paths needs tvofi's review.
- **To the D7 brief, through R10-BRIEFS-FOLD: `archscore.family_orphan_overrides`.** It has no planted census, and the arm's append plant cannot reach it.

## Friction

- `hpo-main-checkout-guard: unclear: the user-level PreToolUse hook resolves the target from the tool call's cwd or a literal git -C, not a leading cd, so cd <seat worktree> && git merge was denied as the main checkout; git -C <seat worktree> merge (the hook's own form) passed`
