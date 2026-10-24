R10-ARCHSCORE-COVERAGE, part 3 of 5: layering and private crossings in the architecture score (roster item 1, ARCH2-s4).

Part of #2259.

**Stacked on #2293 and part 2** (`handoff/r10-archscore-coverage-p2`, PR #2311). This branch contains part 2's head `134810973`, which in turn contains part 1, so until both merge, its diff against main includes theirs. The part-3 delta alone is `git diff 134810973...HEAD`. It merges after both.

What changes: a new metric module, `tools/audit/archscore/metrics/layering.py`, with two score metrics at the floor weight. They guard no register class: `weights.json` is unchanged and its floor applies. There is also one gate-only tripwire and three counters.

The layers, lowest first:
- **pure**: imports neither boundary.
- **solver**: imports scipy.
- **glue**: imports Home Assistant.

A module's layer is the highest boundary it imports itself. An import may go down or across, never up.

- **`layer_violations`**: (module, layer) pairs where a module reaches, through other package modules, a layer above its own. The import graph counts a relative import at any scope; an import under `TYPE_CHECKING` is not an edge.
  - Today: 22 at the merged head (21 before origin/main `12cf1764d`, whose R10-FAHRENHEIT change left `setpoint_check` importing neither boundary while it reaches both). The pure modules `quiet_windows` and `silent_mode` reach the solver for its private `_utc_step_starts`, and `optimizer` and `dhw_planner` (solver) reach the glue.
  - At the pin: 3.
- **`private_cross_module`**: distinct private names of one module that another names. That covers `from .m import _x`, `m._x` through a module binding, and `getattr(m, "_x")`. Today: 17 at the merged head. It was 19 before origin/main `12cf1764d` removed two; the attribute spellings include `coordinator`'s `away_mode._parse_return_time`.
- **`unused_boundary_imports`** (gate-only): a boundary import whose names the module never reads. Today: 1, `config_flow`'s `device_registry as dr`.
- **Counters:**
  - C17: a function-scope import is an edge (attempt 21, a lazy solver import).
  - C18: `m._x` is a crossing (attempt 22).
  - C19: the tripwire (attempt 23, each violating module climbing a layer with an unread boundary import).

ARCH2-s4's P1 prototype (one owner of the UTC clock) read delta-S +0.0000 on every earlier metric. It now reads IMPROVES (`score_delta.py`, below).

**Calibrated first, and one definition dropped.** The first definition counted modules bound to a boundary, whether by importing it or by reaching it. It read four GOOD corpus decompositions as WORSENS (`ca937daa`, `69781076`, `ec263d82`, `33cedffa`), because a module extracted from the glue that imports Home Assistant is one more bound module. The layer rule counts an extracted glue module as glue, and no recorded corpus verdict moves under it.

`56cb0027` (GOOD) already read WORSENS on `duplication_copies`, and it also rises on `layer_violations`. Its unit read made `price_model`, a pure module, reach Home Assistant through `inputs`. That is a real leak, and the gate asks for its explanation.

Calibration cases:
- `a3_layer_violations_*`:
  - BAD: `drift.py`, pure, imports the optimizer.
  - GOOD: the horizon clock moves to `step_clock.py`, and `silent_mode` imports it there.
  - NULL: the import moves within module level.
- `a3_private_cross_module_*`:
  - BAD: `drift.py` imports `freq_control._finite`.
  - GOOD: `away._parse_return_time`, used across modules, is declared public.
  - NULL: the same private imported under an alias.
- Attempts `rt_21`, `rt_22` and `rt_23`.

`expected.json` gains those nine cases. The corpus vectors were re-measured for the `layering` job.

Alternatives considered:
- A raw import-closure size per module (ARCH2-s4's `layering.py` metric 1): every module added or extracted grows someone's closure, so it rises on every decomposition.
- A statement-weighted closure: rises on any added code anywhere.
- The module-bound count: calibrated and refused, as above.
- Counting only modules that reach without importing: the module that adds the boundary import escapes. That was attempt 23's first form; C19 closes it.

## Head

`507bf3efd63e47ea7b1f2dd527ed0141d0d0bff6` (part 2 `134810973` and origin/main `12cf1764d` merged in; measured `2026-10-16T00:44Z`)

## Mutation proof

Each mutant was applied in place on the committed head, run, and restored with `git checkout` (script `mutate_p3.sh` in the seat's scratch). The runner was `calibrate.py --only` the nine new cases, against the recorded `expected.json`. M0 (no mutation) moved nothing.

- M1, import-time edges only (`live = _module_level(..)` always). MOVED: `rt_21` (NULL -> IMPROVES).
- M2, attribute crossings not counted. MOVED: `rt_22` (NULL -> IMPROVES).
- M3, the tripwire reads nothing. MOVED: `rt_23` (WORSENS -> IMPROVES).
- M4, no layer is above another (`r > 2`). Run by hand (`calibrate.py --only a3_layer_violations_control,a3_layer_violations_fix`), because the script's M4 printed no line. Disclosed rather than repaired: the mutant applied, and the hand run is the measurement. `layer_violations` reads 0 on today's tree. MOVED: `a3_layer_violations_control` (WORSENS -> NULL), and `a3_layer_violations_fix` falls from +0.5849 to +0.1699, its private term alone.
- M5, imported private names not counted. MOVED: `a3_private_cross_module_control` (WORSENS -> NULL), `rt_22` (NULL -> WORSENS).

Ablation (`ARCHSCORE_ABLATE=C17|C18|C19` on the nine cases): each switch reopens only its own attempt, which reads IMPROVES (rt_21 +1.1699, rt_22 +0.2224, rt_23 +2.0000), and leaves the other two closed.

## Null control

- The base instrument has no layering metric, so ARCH2-s4's P1 read `delta_S=+0.0000` NULL there (`score_delta.py`, below). `--revert` at the head reads `+0.0000` NULL.
- Honest code: no recorded corpus, planted or red-team verdict moved (`calibrate.py --stored-only` after the corpus re-measure, then `--record`, which printed RECORD for the nine new cases alone and no SENSITIVE line). The two planted NULLs read NULL. ARCH2-s4's own `layering.py`, an independent closure census, reads byte-identical RESULT lines at both ends (the package is unchanged).

## Figures

Finder's harnesses, from their export (`$EXPORT` = `git archive b202335e2 dev/audit/rounds/round10/D7/arch2-s4`), copied into each tree because they locate `tools/audit` from their own path. They ran at the base (a `git worktree` of origin/main `c42d7cea6`) and at the head, `PYTHONPATH=tests/hastub`:

- `$EXPORT/dev/audit/rounds/round10/D7/arch2-s4/score_delta.py P1_one_utc_clock_owner.patch` (sha1 35570991d7150afff3931d5243ee945c6c8d1b6f): `delta_S=+0.0000` NULL -> `+0.4460` IMPROVES (`layer_violations` 21 -> 18, `private_cross_module` 19 -> 16). With `--revert`, `+0.0000` at the head.
- `$EXPORT/dev/audit/rounds/round10/D7/arch2-s4/layering.py` (sha1 314f35a49c474c1a21b6f4776aca7bb2af4efa1f): closure_store 28 (optimizer IN) and private_cross_module_names 17, identical at both ends. Its default `--ref` is the round's baseline `9061fbd3d`, so it reads the same at both ends by construction. The companion is the metric itself (`metrics/layering.measure`): 22 violations, 17 crossings and 1 unread boundary import on today's tree.
- Calibration: `python3 tools/audit/archscore/calibrate.py` at the head. The rule: only the nine new cases are not in part 2's `expected.json`, every new case classifies as its label says, and no SENSITIVE line is printed.
- Corpus: `calibrate.py --measure-corpus --only-metric layering --jobs 4`: 87 vectors ok, 0 errors.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, naming `tests/arch_score.py` (213 checks passed), `tests/arch_score_head.py` (16 passed) and `tests/entities.py` (2325 passed after the new rows). `run.sh`'s `run_always` scripts, `tests/structure.py` and `tools/audit/seat/tmp_paths.py --check` all pass. `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL` (no package change).

Class seams (step 8). The rule is every way one module can depend on another. That means every `ast.Import` and `ast.ImportFrom` at any scope (`grep -c "import" ` per module is not the rule; `metrics/layering.graph` walks every node), plus `importlib.import_module`. Imports at every scope are counted (C17); those under `TYPE_CHECKING` are excluded, by design. Private names are counted through import, module attribute and constant `getattr` (C18).

Residuals, named:
- `importlib.import_module` with a computed name: `__init__`'s platform loader and the optimizer's threadpool limiter.
- A private reached through an object rather than a module binding: that is `coordinator_private_reach`'s for the coordinator, and otherwise open.

## Raise justification

`tests/ci_budgets.json` gains three NEW rows. They are new ratchets, not raises, and no existing row moves: `archscore.layer_violations` 22, `archscore.private_cross_module` 17 and `archscore.unused_boundary_imports` 1. Each is recorded at the value `ci_ratchet.archscore_metrics()` derives at the merged head; `recorded_at` and `reason` are updated. They are needed because the layering metric adds three keys to the score vector, and `ci_ratchet` refuses a derived key with no row as growth.

Payments considered, and why each lost:
1. Make the metrics gate-only. They would still be vector keys, so they would still need rows.
2. Keep them out of the vector. The score would not price them, which is the roster item's point.

Approved by the orchestrator under mandate 6175172275 before the push. A change to a `*_budgets.json` merges only on the owner's approving review at its head (budget-raise-gate, 0013).

`Architecture score: dS +0.0000 NULL` (`score.py --diff origin/main`): no package code changed. The instrument on today's tree reads the three new keys as above, and every other key is unchanged.

## Unpinned sites

n/a for production code: the diff touches `tools/audit/archscore/` and tests only; the new predicates are pinned by the calibration cases and the mutants above.

## Architecture score

n/a: no package file changes; the instrument change takes effect after merge (`ABOUT.md`).

## Red checks

- `closures`: red at `77991f1ad` (the delivery-row commit), UNDER-SCOPED. The new `metrics/layering.py` is imported, through `archscore.vector`, by `tests/arch_score_head.py` and by `tests/entities.py` (its ci-ratchet checks call `ci_ratchet.archscore_metrics()`). This seat re-recorded only `tests/arch_score.py` with `derive_closures.sh --single`. The `closures-autofix` job re-recorded the other two (bot commit `551b660e7`, `ci: re-record closures`), and `closures` is green from that commit on. Answered by naming it (`ci-autofix.md`). The cheaper detector the seat skipped: `--single` on every script whose closure already holds `tools/audit/archscore/vector.py` (a `jq` over `tests/closures.json`). The standing cost is one `--single` per such script, the heaviest being `tests/entities.py` at about ten minutes. Part 4 does this before its handoff.
- `tests/entities.py`, the ci-ratchet null control "and main() passes the committed table at its own recorded count": red locally before the rows were added (the three keys had no row), and again after merging origin/main `12cf1764d` (`layer_violations` 21 -> 22, main's own change). It is the ratchet's own null control firing on the deliberate new keys, and the rows above answer it (2325 of 2325 pass after). No cheaper detector exists.
- `budget-raise-gate`: it flags `archscore.hub_solve_writes` 38 -> 41, which is part 2's raise carried in through the stack (answered in #2311's body), and the new rows if it reads them as raises. It stays red by design until tvofi approves at the head. The orchestrator posts the owner-gate approval under mandate 6175172275. No cheaper detector exists: the gate is the owner's approval itself.

## Forward-carry

- For R10-BRIEFS-FOLD: the D7 brief may cite `layer_violations`, `private_cross_module` and C17 to C19 (`tools/audit/archscore/ABOUT.md`). The orchestrator owns the roster edit and was told at handoff.
- R10-CONFIGFLOW-PAGES: remove `config_flow.py`'s unread `device_registry as dr` (the tripwire's one site today), and lower `tests/ci_budgets.json` `archscore.unused_boundary_imports` 1 -> 0 in the same PR. The orchestrator routed it into that group's roster carry (`dev/programme/rosters/wave-r10-groups.json`, R10-CONFIGFLOW-PAGES `carry`, roster PR #2315). This PR does not merge until that carry is on main.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
