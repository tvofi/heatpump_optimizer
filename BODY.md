R10-ARCHSCORE-COVERAGE, part 3 of 5: layering and private crossings in the architecture score (roster item 1, ARCH2-s4).

**Round 2.** The round-1 review (`verdict/2320`, head `4a4107fcd`) blocked twice, and this push answers both: the four seams its `## Blocking` section names inside the layering rule, each worth `dS +0.1466` to a seat gaming the score, and the `## Head` lines a body edit dropped.

Part of #2259.

**Part 1 (#2293) and part 2 (#2311) both merged while this round was in review**, and this head has origin/main `81ae048e8` merged into it with no hand resolution, so the diff against main is part 3's own. The part-3 delta alone is `git diff 134810973...HEAD`.

What changes: a new metric module, `tools/audit/archscore/metrics/layering.py`, with two score metrics at the floor weight. They guard no register class: `weights.json` is unchanged and its floor applies. There is also one gate-only tripwire and three counters.

The layers, lowest first:
- **pure**: imports neither boundary.
- **solver**: imports scipy.
- **glue**: imports Home Assistant.

A module's layer is the highest boundary it imports itself. An import may go down or across, never up.

- **`layer_violations`**: (module, layer) pairs where a module reaches, through other package modules, a layer above its own. The import graph counts every way one module reaches another that the runtime runs -- a relative import at any scope, an absolute self-import of the package's own path, and a constant-name `importlib.import_module` -- and excludes only the `body` of a positive `if TYPE_CHECKING:`, which nothing runs.
  - Today: 22 at the merged head (21 before origin/main `12cf1764d`, whose R10-FAHRENHEIT change left `setpoint_check` importing neither boundary while it reaches both). The pure modules `quiet_windows` and `silent_mode` reach the solver for its private `_utc_step_starts`, and `optimizer` and `dhw_planner` (solver) reach the glue.
  - At the pin: 3.
- **`private_cross_module`**: distinct private names of one module that another names. That covers `from .m import _x`, `m._x` through a module binding, `getattr(m, "_x")`, and `_x` read off a resolved `import_module` call. Today: 17 at the merged head. It was 19 before origin/main `12cf1764d` removed two; the attribute spellings include `coordinator`'s `away_mode._parse_return_time`.
- **`unused_boundary_imports`** (gate-only): a boundary import whose names the module never reads. Today: 1, `config_flow`'s `device_registry as dr`.
- **Counters:**
  - C17: every import the runtime runs is an edge -- a function-scope import (attempt 21), the `else` of a guard (24), under `if not TYPE_CHECKING:` (25), an absolute self-import (27), a constant-name `import_module` (26).
  - C18: `m._x` is a crossing (attempt 22), and so is `_x` off a resolved `import_module` call (26, 27).
  - C19: the tripwire (attempt 23, each violating module climbing a layer with an unread boundary import).

### The four seams round 1 named, and how each is closed

They were one predicate's fault in three places, and each now has an attempt that reads `IMPROVES` against the round-1 instrument and `NULL` against this one (`## Figures`):

- **the `else` of `if TYPE_CHECKING:`** (attempt 24) runs. `common._in_type_checking` walked the whole `ast.If`. `_type_checking_guard` now returns the `body` and nothing else.
- **`if not TYPE_CHECKING:`** (25) is true away from a type checker. The old test was `ast.unparse(test).endswith("TYPE_CHECKING")`, so the negation matched. The guard is now the bare `TYPE_CHECKING` name, or `typing`/`typing_extensions`.`TYPE_CHECKING`; an `else`, a negated test and a disjoined test are read as code that runs, so their imports count.
- **a constant-name `importlib.import_module`** (26). `layering.graph` had no such arm. `_dynamic_name` resolves a constant first argument to the module it names -- absolute, or relative against the `package` argument, with `__package__` (the anchor a call defaults to) read as the calling module's own package -- and `_dynamic_target` maps it into the package. The private read off the resolved call is the crossing C18 already counts through a module binding. A name COMPUTED at runtime stays invisible.
- **an absolute self-import** (27). `from custom_components.heatpump_optimizer.optimizer import _x` was filed as the external root `custom_components` and became no edge. `_self_module` strips the package's own prefix, so an absolute self-import resolves exactly as the relative one does, and it is no longer counted as an external root either.

The guard's other end is pinned, because the repair changes when the exclusion fires: `a3_layer_violations_null` now also gives `drift.py` an annotation-only `if TYPE_CHECKING:` import of the optimizer. Nothing runs it, so the case still reads NULL; with the exclusion ignored (M6) the pure module gains the solver and the case reads WORSENS. Round 1 shipped no calibration case the exclusion moved, and the review measured exactly that.

ARCH2-s4's P1 prototype (one owner of the UTC clock) read delta-S +0.0000 on every earlier metric. It now reads IMPROVES (`score_delta.py`, below).

**Calibrated first, and one definition dropped.** The first definition counted modules bound to a boundary, whether by importing it or by reaching it. It read four GOOD corpus decompositions as WORSENS (`ca937daa`, `69781076`, `ec263d82`, `33cedffa`), because a module extracted from the glue that imports Home Assistant is one more bound module. The layer rule counts an extracted glue module as glue, and no recorded corpus verdict moves under it.

`56cb0027` (GOOD) already read WORSENS on `duplication_copies`, and it also rises on `layer_violations`. Its unit read made `price_model`, a pure module, reach Home Assistant through `inputs`. That is a real leak, and the gate asks for its explanation.

Calibration cases:
- `a3_layer_violations_*`:
  - BAD: `drift.py`, pure, imports the optimizer.
  - GOOD: the horizon clock moves to `step_clock.py`, and `silent_mode` imports it there.
  - NULL: the import moves within module level, and `drift.py` gains an annotation-only `if TYPE_CHECKING:` import of the optimizer.
- `a3_private_cross_module_*`:
  - BAD: `drift.py` imports `freq_control._finite`.
  - GOOD: `away._parse_return_time`, used across modules, is declared public.
  - NULL: the same private imported under an alias.
- Attempts `rt_21`, `rt_22`, `rt_23`, and this round's `rt_24` to `rt_27`.

`expected.json` gains those four cases; the corpus vectors were re-measured for the `layering` job.

Alternatives considered:
- A raw import-closure size per module (ARCH2-s4's `layering.py` metric 1): every module added or extracted grows someone's closure, so it rises on every decomposition.
- A statement-weighted closure: rises on any added code anywhere.
- The module-bound count: calibrated and refused, as above.
- Counting only modules that reach without importing: the module that adds the boundary import escapes. That was attempt 23's first form; C19 closes it.
- For the guard: excluding every test that mentions `TYPE_CHECKING`, which is what round 1 shipped. Refused -- an `else` and a negated test are runtime code, and excluding them is how a seat gets `0.1466` for moving an import into one.
- For dynamic imports: resolving them by importing the call, or by a second source regex. Refused -- the trees are never run (`metrics/common`'s docstring), and a second parser is a second rule to keep in agreement.

## Head

`c4209f9dbfed343f3002e54fb61f071bf0432b0d` (round-2 repair, the seam census and the closure re-record, on the merge below; measured `2026-10-16T16:00Z`).

The branch's whole carry chain, oldest first, so `pr-contract`'s walk stops on a seat commit and not a bot one: `507bf3efd` (part 3's authored head, round 1) -> `aacdc1c4c` (origin/main merged in) -> `77991f1ad` (this pull request's own delivery row) -> `551b660e7` (bot, `ci: re-record closures`) -> `4a4107fcd` (bot, `ci: merge main`) -> `1a7e42bfc` (this round's repair) -> `48b83e20e` (the seam census) -> `eebf3f366` (the closure re-record) -> `f25a8a915` (origin/main `81ae048e8` merged in, part 2 among it) -> `c4209f9db` (the seam census listed as an inert read of `tests/harness_headers.py`). Round 1's body edit dropped the middle three, which is why run 116780967581 refused it with "`## Head` does not name 4a4107f ... 77991f1ad is not authored and committed as github-actions[bot]": the walk reaches `77991f1ad`, a seat commit, and the section has to name it.

## Mutation proof

Eleven arms, each run against the same thirteen cases end to end:

    python3 tools/audit/archscore/calibrate.py --only rt_21_lazy_solver_import,rt_22_private_module_attr,rt_23_layer_owner_import,rt_24_layer_guarded_else,rt_25_layer_negated_guard,rt_26_layer_import_module,rt_27_layer_absolute_self_import,a3_layer_violations_control,a3_layer_violations_fix,a3_layer_violations_null,a3_private_cross_module_control,a3_private_cross_module_fix,a3_private_cross_module_null

M0 to M10 are in-place predicate edits on the committed head, restored with `git checkout -- tools/audit/archscore/metrics/common.py tools/audit/archscore/metrics/layering.py`. A1 to A3 are the tree's own switch, `ARCHSCORE_ABLATE`.

- **M0**, no mutation (the runner's own null): nothing moved.
- **M1**, `live = _module_level(mod.tree)` (C17 off by use): MOVED `rt_21` (NULL -> IMPROVES).
- **M2**, `PRIVATE_ATTRS = False`: moved nothing, and that is a finding rather than a pass. `vector.py` assigns C17 to C19 from `ARCHSCORE_ABLATE` on every measurement, so an edit to the module constant is overwritten and the switch is A2. Disclosed, not dropped: round 1's body recorded M2 and M3 as moving cases, and this measurement does not support that.
- **M3**, `UNUSED_IMPORTS = False`: the same no-op; the switch is A3.
- **M4**, `if r > 2)` (no layer above another): `calibrate.py` exits 1 with `CalledProcessError` and prints no table -- attempt 23 asserts `no violating module` when no module violates, and `cases.build` runs every attempt with `check=True`. The mutant is killed by the crash. Round 1 disclosed the same and ran a subset by hand; this is the exit code.
- **M5**, `_private` returns False: MOVED `a3_private_cross_module_control` (WORSENS -> NULL) and `a3_private_cross_module_fix` (IMPROVES -> NULL).
- **M6**, `real = False`, the TYPE_CHECKING exclusion ignored: MOVED `a3_layer_violations_null` (NULL -> WORSENS). This is the mutant round 1 ran against the nine cases and found nothing could kill.
- **M7**, the guard read as the whole `If` (`return [node]`): MOVED `rt_24` (NULL -> IMPROVES).
- **M8**, the guard read from `ast.unparse(node.test).endswith("TYPE_CHECKING")`: MOVED `rt_25` (NULL -> IMPROVES).
- **M9**, `_dynamic_name` returns None, no dynamic import resolved: MOVED `rt_26` (NULL -> IMPROVES).
- **M10**, `_self_module` returns None, no absolute self-import resolved: MOVED `rt_26` and `rt_27` (each NULL -> IMPROVES). The coarser of the two, because the dynamic resolver resolves through the same prefix test.
- **A1**, `ARCHSCORE_ABLATE=C17`: MOVED `rt_21` (NULL -> IMPROVES).
- **A2**, `=C18`: MOVED `rt_22` and `rt_26` (each NULL -> IMPROVES) -- the private read off a resolved `import_module` call is a C18 crossing, so ablating C18 reopens both. Round 1's "C18 only rt_22" is now "rt_22 and rt_26", which is this round's arm joining C18.
- **A3**, `=C19`: MOVED `rt_23` (WORSENS -> IMPROVES).

## Null control

- Each new predicate reads `IMPROVES` before it is in the tree and `NULL` after it, on the same four plants. With the two metric files checked out from `4a4107fcd`, the enumerator printed `RED TEAM 0/4 attempts read NULL or inadmissible; IMPROVES: rt_24_layer_guarded_else, rt_25_layer_negated_guard, rt_26_layer_import_module, rt_27_layer_absolute_self_import`; with this head's files restored, `RED TEAM 7/7 attempts read NULL or inadmissible; IMPROVES: none`.
- Every arm's null is in `## Mutation proof`: M0 (no mutation) moves nothing; M2 and M3 are themselves nulls, an edit that lands and changes no reading, which is what shows the constant is inert; M4's kill is the exit code and not a table.
- `a3_layer_violations_null` reads NULL with the added annotation-only import and WORSENS under M6, so "nothing runs the guard body" is measured in both directions rather than assumed.
- The base instrument has no layering metric, so ARCH2-s4's P1 reads `delta_S=+0.0000` NULL there (`score_delta.py`, below); `--revert` reads `+0.0000` at this head.
- Honest code: `IMPROVES: none` across all 60 attempts, the four planted NULLs unmoved, no recorded corpus verdict moved.
- The corpus re-measure owes its own null control, and the census is it: it fires on a planted tree carrying all four spellings (1 / 2 / 4 / 2) before it reports the corpus's `0 / 30 / 58 / 0`.

## Figures

Finder's harnesses: `$EXPORT` = `git archive b202335e2 dev/audit/rounds/round10/D7/arch2-s4`, copied into the tree it measures, because each locates `tools/audit` from its own path. Both arms run in a throwaway `git worktree` of `4a4107fcd`, the second with this head's two metric files copied over it, `PYTHONPATH=tests/hastub`.

- `$EXPORT/dev/audit/rounds/round10/D7/arch2-s4/score_delta.py P1_one_utc_clock_owner.patch` (sha1 `35570991d7150afff3931d5243ee945c6c8d1b6f`): `Architecture score: dS +0.4460 IMPROVES` (`layer_violations 21 -> 18 +0.2115`, `private_cross_module 19 -> 16 +0.2345`, `unused_boundary_imports 1 -> 1`) at BOTH instruments, and `--revert` `dS +0.0000 NULL` at both. The patch spells its imports the ordinary way, so the four seams do not reach it: the harness reads flat at both ends, and the companion that applies the tree's own rule to the same inputs is the enumerator below, reading IMPROVES at the round-1 instrument and NULL here.
- `$EXPORT/dev/audit/rounds/round10/D7/arch2-s4/layering.py` (sha1 `314f35a49c474c1a21b6f4776aca7bb2af4efa1f`), the finder's independent census: `closure_store=28 modules (optimizer IN)` and `private_cross_module_names=17 count`, identical at both instruments. Its `--ref` default is the round's baseline `9061fbd3d`, so it reads the same at both ends by construction; that is stated as flat, not as agreement.
- The seam enumeration (`fixer.md` step 8). The rule is every way a package module reaches another, or a boundary, that the runtime runs, and the attempt set is its enumerator, measured live on every calibration run:

      python3 tools/audit/archscore/calibrate.py --only rt_21_lazy_solver_import,rt_22_private_module_attr,rt_23_layer_owner_import,rt_24_layer_guarded_else,rt_25_layer_negated_guard,rt_26_layer_import_module,rt_27_layer_absolute_self_import

  printed `RED TEAM 7/7 attempts read NULL or inadmissible; IMPROVES: none`, so every seam the enumerator returns is closed. Its seams and dispositions:

  | seam | disposition |
  |---|---|
  | `from .m import _x`, at module scope or in a function | counted (attempt 21, counter C17) |
  | the `else` of `if TYPE_CHECKING:` | closed here (attempt 24; M7 reopens it) |
  | `if not TYPE_CHECKING:` | closed here (25; M8) |
  | a constant-name `importlib.import_module`, absolute or `__package__`-relative | closed here (26; M9) |
  | the private read off a resolved `import_module` call | closed here (26; A2) |
  | an absolute self-import `from <pkg>.m import _x` | closed here (27; M10) |
  | `import <pkg>.m` | closed here (27) |
  | `m._x` through a module binding; `getattr(m, "_x")` | counted (counter C18, attempt 22) |
  | `getattr(_o, "_x" + suffix)`, `vars(_o)["_x"]`, `_m = _o; _m._x` | OPEN, counter C18's class (round 1's p6, p7, p8, each `private_cross_module 17 -> 16`). Not closed here; written into `tools/audit/archscore/ABOUT.md` for the D7 brief and the next archscore part |
  | an unread boundary import plus one bare read | OPEN, counter C19's class (round 1's p5). Same destination |
  | a name computed at runtime: `f".{module}"`, `exec`, a rebound binding | invisible by design; the metric's docstring and `ABOUT.md` both state it |
- `python3 tools/audit/archscore/calibrate.py` at this head: `calibration moved on 4 case(s)`, all four this round's. `--record` printed `RECORD` for those four and nothing else, and the diff to `expected.json` is 24 insertions, 0 deletions; `CALIBRATION 95/124 labelled cases classify as their label says`, `RED TEAM 60/60 attempts read NULL or inadmissible`, `KNOWN-OPEN 1` (unchanged), no `SENSITIVE` line.
- `python3 tools/audit/archscore/calibrate.py --measure-corpus --only-metric layering --jobs 4`: 87 vectors `ok`, 0 `ERRORS`, and `corpus_vectors.json` byte-identical to the round-1 file (`cmp`).
- `python3 dev/audit/harnesses/archscore_layering_seam_census.py <wt> --corpus`: `corpus trees censused: 87`, `absolute_self_import=0`, `constant_dynamic_import=30` with `dynamic_names=['threadpoolctl']`, `guard_not_body=58`, `guard_not_body_imports=0`, planted `1 / 2 / 4 / 2`, `PRECONDITION ok`, rc=0.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out`, naming `tests/arch_score.py` (`ALL 217 ARCHITECTURE SCORE CHECKS PASSED`), `tests/arch_score_head.py` (`ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED`) and `tests/entities.py` (`ALL 2329 ENTITY CHECKS PASSED`). `run.sh`'s `run_always` scripts, run individually at this head: `tests/env_drift.py --claims-only origin/main` (`claims hygiene: origin/main ok`), `tests/closure.py selftest` (`ALL 115 closure shrink pins PASSED`), `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`) and `tests/layout.py` (`layout self-test: ok`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (no package file changed; every row `<=` its budget).
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- The three ci-ratchet rows at this head: `ci_ratchet.archscore_metrics()` reads `archscore.layer_violations` 22, `archscore.private_cross_module` 17 and `archscore.unused_boundary_imports` 1, unchanged from what the rows record, so no re-record is owed and `ci_budgets.json` is not in this diff.

## Raise justification

`tests/ci_budgets.json` gains three NEW rows. They are new ratchets, not raises, and no existing row moves: `archscore.layer_violations` 22, `archscore.private_cross_module` 17 and `archscore.unused_boundary_imports` 1. Each is recorded at the value `ci_ratchet.archscore_metrics()` derives at the merged head; `recorded_at` and `reason` are updated. They are needed because the layering metric adds three keys to the score vector, and `ci_ratchet` refuses a derived key with no row as growth. This round derives the same three values at `f25a8a9`, so no row moves and no re-record is owed.

Payments considered, and why each lost:
1. Make the metrics gate-only. They would still be vector keys, so they would still need rows.
2. Keep them out of the vector. The score would not price them, which is the roster item's point.

Approved by the orchestrator under mandate 6175172275 before the round-1 push. A change to a `*_budgets.json` merges only on the owner's approving review at its head (budget-raise-gate, 0013).

`Architecture score: dS +0.0000 NULL` (`score.py --diff origin/main`): no package code changed. The instrument on today's tree reads the three new keys as above, and every other key is unchanged.

## Unpinned sites

n/a for production code: the diff touches `tools/audit/archscore/` and one harness under `dev/audit/`; the new predicates are pinned by the calibration cases and the mutants above.

## Architecture score

n/a: no package file changes; the instrument change takes effect after merge (`ABOUT.md`).

## Red checks

- `pr-contract`: red at `4a4107fcd` (run 116780967581) with "`## Head` does not name 4a4107f ... 77991f1ad is not authored and committed as github-actions[bot]", and at `77991f1ad` and `551b660e7` before it. The `## Head` section above answers it by naming the head and the whole chain, which is the correction the steward contract prescribes after a bot push. No cheaper detector: the check IS the contract that the body names the head CI ran on.
- `closures`: red at `77991f1ad` (the delivery-row commit), UNDER-SCOPED. The new `metrics/layering.py` is imported, through `archscore.vector`, by `tests/arch_score_head.py` and by `tests/entities.py` (its ci-ratchet checks call `ci_ratchet.archscore_metrics()`). The seat re-recorded only `tests/arch_score.py` with `derive_closures.sh --single`. The `closures-autofix` job re-recorded the other two (bot commit `551b660e7`, `ci: re-record closures`), and `closures` is green from that commit on. Answered by naming it (`ci-autofix.md`). The cheaper detector the seat skipped: `--single` on every script whose closure already holds `tools/audit/archscore/vector.py` (a `jq` over `tests/closures.json`). The standing cost is one `--single` per such script, the heaviest being `tests/entities.py` at about ten minutes. This round re-recorded `tests/arch_score.py` again for the four new attempts, before its push rather than at the autofix.
- `tests/entities.py`, the ci-ratchet null control "and main() passes the committed table at its own recorded count": red locally before the rows were added (the three keys had no row), and again after merging origin/main `12cf1764d` (`layer_violations` 21 -> 22, main's own change). It is the ratchet's own null control firing on the deliberate new keys, and the rows above answer it (2325 of 2325 pass after). No cheaper detector exists.
- `budget-raise-gate`: it flags `archscore.hub_solve_writes` 38 -> 41, which is part 2's raise carried in through the stack (answered in #2311's body). It stays red by design until tvofi approves at the head. The orchestrator posts the owner-gate approval under mandate 6175172275. No cheaper detector exists: the gate is the owner's approval itself.

## Forward-carry

- **`dev/governance/dimensions/D7.md`, via R10-BRIEFS-FOLD** (the group whose roster entry owns that file, and which lists this group in its `after`). The folded text must state what the layering counters do not see, because round 1's review found the metric's cheapest move reads as a decoupling: a private crossing spelled `getattr(_o, "_x" + suffix)`, `vars(_o)["_x"]` or through a rebound alias; C19's tripwire satisfied by one bare read; and `a3_private_cross_module_fix` being a pure rename of a private to a public name. The measurements live in the tree, in this pull request, at `tools/audit/archscore/ABOUT.md` under "What R10-ARCHSCORE-COVERAGE part 3 moved", with the attempt ids that carry each; the brief should cite them and re-measure at its own merge base rather than carry the counts. The roster edit is the orchestrator's (`dev/programme/rosters/wave-r10-groups.json`, R10-BRIEFS-FOLD `carry`); this pull request does not merge until that carry is on main.
- **The next archscore part** (parts 4 and 5 of this group): `rt_24` to `rt_27` and `a3_layer_violations_null`'s second arm are in the tree and run on every calibration, and `tools/audit/archscore/ABOUT.md`'s "What it does not see" list is what a part closing any of those seams has to move. `dev/audit/harnesses/archscore_layering_seam_census.py` is the census that says which trees carry which spelling.
- **R10-CONFIGFLOW-PAGES** (already on main as `084052aae`): remove `config_flow.py`'s unread `device_registry as dr`, the tripwire's one site today, and lower `tests/ci_budgets.json` `archscore.unused_boundary_imports` 1 -> 0 in the same pull request.

## Friction

- R10-ARCHSCORE-COVERAGE-p3-r2: contradiction: the seat brief names `tools/audit/seat/handoff_push.sh` as the push instrument, while `dev/governance/rules/delivery-status-tracking.md` says that script is the orchestrator's and that a fixer writes no delivery row; the seat pushed `handoff/r10-archscore-coverage-p3` and `handoff-body/r10-archscore-coverage-p3` only and left the pull-request update to the orchestrator.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
