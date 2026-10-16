R10-ARCHSCORE-COVERAGE, part 3 of 5: layering and private crossings in the architecture score (roster item 1, ARCH2-s4).

**Round 3.** The round-2 review (`review/2320`, head `353f7f3c4`) returned one block, `class-open`. The round-2 repair closed four *spellings* of one class; three further spellings of the same runtime coupling stayed open, each keeping the import and each reading `IMPROVES` at the head's own instrument, and the seam census added in the same pull request filed `ast.ImportFrom` and plain `ast.Import` of this package under one counter and planted only the `from` form. This push closes the three spellings and the census, and records the one spelling of the class that is refused rather than closed.

Part of #2259.

Part 1 (#2293) and part 2 (#2311) merged while this round was in review, and this head has origin/main `81ae048e8` merged into it with no hand resolution, so the diff against main is part 3's own. The part-3 delta alone is `git diff 134810973...HEAD`.

What changes: a new metric module, `tools/audit/archscore/metrics/layering.py`, with two score metrics at the floor weight. They guard no register class: `weights.json` is unchanged and its floor applies. There is also one gate-only tripwire and three counters.

The layers, lowest first:
- **pure**: imports neither boundary.
- **solver**: imports scipy.
- **glue**: imports Home Assistant.

A module's layer is the highest boundary it imports itself. An import may go down or across, never up.

- **`layer_violations`**: (module, layer) pairs where a module reaches, through other package modules, a layer above its own. The import graph counts every way one module reaches another that the runtime runs -- a relative import at any scope, an absolute self-import of the package's own path in any spelling, and a constant-name `importlib.import_module` -- and excludes only the `body` of a positive `if TYPE_CHECKING:`, which nothing runs.
  - Today: 22 at the merged head (21 before origin/main `12cf1764d`, whose R10-FAHRENHEIT change left `setpoint_check` importing neither boundary while it reaches both). The pure modules `quiet_windows` and `silent_mode` reach the solver for its private `_utc_step_starts`, and `optimizer` and `dhw_planner` (solver) reach the glue.
  - At the pin: 3.
- **`private_cross_module`**: distinct private names of one module that another names. That covers `from .m import _x`, `m._x` through a module binding, `getattr(m, "_x")`, and `_x` read off a resolved `import_module` call. Today: 17 at the merged head. It was 19 before origin/main `12cf1764d` removed two; the attribute spellings include `coordinator`'s `away_mode._parse_return_time`.
- **`unused_boundary_imports`** (gate-only): a boundary import whose names the module never reads. Today: 1, `config_flow`'s `device_registry as dr`.
- **Counters:** C17, every import the runtime runs is an edge (attempts 21, 24 to 31); C18, a private name read through a module binding crosses like its import (attempts 22, 26 to 31); C19, the tripwire (attempt 23).

### The class the round-2 review left open, and one predicate per spelling

The rule is that the reach is the reach whatever syntax spells it. Round 2 resolved it through four statements and left three, and each of the three reads as a decoupling at the round-2 head. Measured by adding the four attempt scripts to a worktree of `353f7f3c4` and running the same instrument at both ends:

| spelling | at `353f7f3c4` | at this head |
|---|---|---|
| `import <pkg>.optimizer as _o` + `_o._utc_step_starts(..)` (attempt 28) | IMPROVES `dS +0.5849` | NULL |
| `import <pkg>.optimizer` + the full dotted read (attempt 29) | IMPROVES `dS +0.5849` | NULL |
| `from <pkg> import optimizer as _o` + `_o._utc_step_starts(..)` (attempt 30) | IMPROVES `dS +0.1699` | NULL |
| `importlib.import_module(name=".optimizer", package=__package__)._utc_step_starts(..)` (attempt 31) | IMPROVES `dS +0.5849` | NULL |

Each is the same module loaded and the same private name read, so a seat shipping one keeps `silent_mode` (pure) reaching the solver. Three causes, one predicate each:

- **an `ast.Import` reached no edge arm.** `graph` added an edge from `ast.ImportFrom` only; an `ast.Import` of this package went to `_roots`, where `_self_module` returned not-None and dropped the name -- *"so it is no longer counted as an external root either"* -- and no edge took its place. `graph` now adds the edge for each name of a dotted `import` that resolves to a package module (attempts 28, 29).
- **a module binding had one provenance.** `modalias` was built from `Pkg.imports` entries recorded `("mod", name)`, which only a *relative* module import produces; an absolute self-import is filed as an external name, so `from <pkg> import optimizer as _o` gave the edge and no binding, and the private read off `_o` was no crossing (attempt 30). `_name_bindings` now builds the map from the statements the module runs -- relative, absolute from-import and plain dotted -- and `_module_attr` resolves a private read through the dotted path that binding roots, so the aliased dotted import and the no-alias full dotted read are the same arm.
- **`_dynamic_name` read one position.** It took the name from `node.args[0]` and returned None on a call with no positional argument. `import_module`'s first parameter is named `name` and its relative anchor `package`, so calling it by keyword is the same constant-name call with the same static anchor (attempt 31).

Refused rather than closed: `__import__(".optimizer", fromlist=[...], level=1)`, the same name in the builtin's own spelling. It is not code a seat can ship -- importing that module raises `KeyError: "'__name__' not in globals"` on CPython 3.14.7 (command in `## Figures`) -- so a rule that resolved it would be code no attempt could pin. It stays in `ABOUT.md`'s "What it does not see" list with the reproduction.

Also closed by the round-2 repair, which answered the round-1 review, and unchanged this round: the `else` of `if TYPE_CHECKING:` (24), which runs; `if not TYPE_CHECKING:` (25), true away from a type checker; a constant-name `importlib.import_module`, relative and anchored on `__package__` (26); and the absolute self-import `from <pkg>.m import _x` (27).

### The census, one counter per form

`dev/audit/harnesses/archscore_layering_seam_census.py` counted `ast.ImportFrom` and plain `ast.Import` of this package under one `absolute_self_import`, and its planted precondition tree carried only the `from` form -- so `absolute_self_import=0` over the corpus could not tell "no tree spells this" from "no tree spells the form the counter resolves", and the second was the state. The counters are now one per form, the dynamic-import counter reads the `name` keyword as the rule does, and the planted tree carries every spelling the census counts; a census whose planted tree leaves one at zero prints which and exits 1.

Calibration cases, all of them measured live on every run:
- attempts `rt_21` to `rt_31`, one per spelling of the class;
- `a3_layer_violations_*`: BAD, `drift.py` (pure) imports the optimizer; GOOD, the horizon clock moves to `step_clock.py` and `silent_mode` imports it there; NULL, the import moves within module level and `drift.py` gains an annotation-only `if TYPE_CHECKING:` import of the optimizer, so the guard's exclusion is measured in both directions;
- `a3_private_cross_module_*`: BAD, `drift.py` imports `freq_control._finite`; GOOD, `away._parse_return_time` is declared public; NULL, the same private imported under an alias.

Alternatives considered:
- A raw import-closure size per module (ARCH2-s4's `layering.py` metric 1): every module added or extracted grows someone's closure, so it rises on every decomposition.
- A statement-weighted closure: rises on any added code anywhere.
- The module-bound count: calibrated and refused (four GOOD corpus decompositions read WORSENS); `ABOUT.md` carries it.
- Counting only modules that reach without importing: the module that adds the boundary import escapes. That was attempt 23's first form; C19 closes it.
- For the guard: excluding every test that mentions `TYPE_CHECKING`, which round 1 shipped. Refused -- an `else` and a negated test are runtime code, and excluding them is how a seat gets `+0.1466` for moving an import into one.
- For dynamic imports: resolving them by importing the call, or by a second source regex. Refused -- the trees are never run (`metrics/common`'s docstring), and a second parser is a second rule to keep in agreement.
- For the three spellings this round closes: enumerating them by spelling (three more arms beside `ImportFrom`). Refused -- round 1 closed four spellings that way and the reviewer named three more, so the list is the defect. `_name_bindings` is built from the statements the module runs, and `_module_attr` resolves whatever dotted path that binding roots, so no spelling appears in the code.

## Head

`7c7e1b7869b764dd2929e7bce03c19736024cad0` (this round's repair and the closure re-record, on the round-2 head below; measured `2026-10-16T21:33Z`). The orchestrator merges it into this pull request's previous head and prefixes that merge's SHA here.

The branch's whole carry chain, oldest first, so `pr-contract`'s walk stops on a seat commit and not a bot one: `507bf3efd` (part 3's authored head, round 1) -> `aacdc1c4c` (origin/main merged in) -> `77991f1ad` (this pull request's own delivery row) -> `551b660e7` (bot, `ci: re-record closures`) -> `4a4107fcd` (bot, `ci: merge main`) -> `1a7e42bfc` (round-1 repair) -> `48b83e20e` (the seam census) -> `eebf3f366` (the closure re-record) -> `f25a8a915` (origin/main `81ae048e8` merged in, part 2 among it) -> `c4209f9db` (the seam census listed as an inert read of `tests/harness_headers.py`) -> `353f7f3c4` (that handoff tip merged into the pull request's branch) -> `bb66adaf5` (this round's repair) -> `7c7e1b786` (the closure re-record).

## Mutation proof

Four arms, each an in-place predicate edit on the committed head, restored with `git checkout --`, over the seventeen layering cases end to end (`rt_21` to `rt_31` and the six `a3_layer_*` / `a3_private_cross_module_*` cases):

    python3 tools/audit/archscore/calibrate.py --only rt_21_lazy_solver_import,rt_22_private_module_attr,rt_23_layer_owner_import,rt_24_layer_guarded_else,rt_25_layer_negated_guard,rt_26_layer_import_module,rt_27_layer_absolute_self_import,rt_28_layer_import_abs_alias,rt_29_layer_import_abs_plain,rt_30_layer_from_abs_module,rt_31_layer_import_module_kw,a3_layer_violations_control,a3_layer_violations_fix,a3_layer_violations_null,a3_private_cross_module_control,a3_private_cross_module_fix,a3_private_cross_module_null

- **M0**, no mutation (the runner's own null): `RED TEAM 11/11 attempts read NULL or inadmissible; IMPROVES: none`.
- **M11**, `_name_bindings` returns `{}`: `RED TEAM 7/11 ... IMPROVES: rt_22_private_module_attr, rt_28_layer_import_abs_alias, rt_29_layer_import_abs_plain, rt_30_layer_from_abs_module`. The binding map carries the crossing for the relative form (22) and for all three absolute forms it now covers.
- **M12**, the `ast.Import` edge arm removed: `RED TEAM 9/11 ... IMPROVES: rt_28_layer_import_abs_alias, rt_29_layer_import_abs_plain`. The edge arm is what `layer_violations` reads for those two.
- **M13**, `_dynamic_name` back to `node.args[0]` only: `RED TEAM 10/11 ... IMPROVES: rt_31_layer_import_module_kw`.

Round 2's arms still describe the predicates this diff does not touch (`M1`..`M8` edit `metrics/common.py`'s guard and the `ALL_SCOPES` use; `A1`..`A3` are the tree's own `ARCHSCORE_ABLATE` switch). Two of them cross into this diff and were re-run when it was first made: `M9` (`_dynamic_name` returns None) and `M10` (`_self_module` returns None) each moved `rt_26` and `rt_27` then. `M13` above is the same predicate as `M9` at the narrower edit this round's fix leaves, and it is the finer control: it moves only the keyword form.

## Null control

- Each of the four new predicates reads `IMPROVES` before it is in the tree and `NULL` after, on the same plants, at the same instrument: the four attempt scripts run against a worktree of `353f7f3c4` print `GAME IMPROVES` (the table above), and against this head `RED TEAM 64/64 attempts read NULL or inadmissible; IMPROVES: none`.
- `M0` (no mutation) moves nothing, so the arm harness itself does not shift a verdict.
- `a3_layer_violations_null` reads NULL with its added annotation-only import and WORSENS with the guard's exclusion ignored (`M6`, round 2's arm), so "nothing runs the guard body" is measured in both directions rather than assumed.
- The corpus re-measure owes its own control, and the census is it: it fires on a planted tree carrying every spelling (`2 / 1 / 3 / 4 / 2`) before it reports the corpus's `0 / 0 / 30 / 58 / 0`. A census that matched no spelling exits 1 rather than printing a zero.
- The finder's harness reads flat at both ends by construction: its `--ref` default is the round's baseline, so it re-reads the same git objects whatever the instrument. Named as flat, not as agreement.

## Figures

Finder's harnesses: `$EXPORT` = `git archive b202335e2 dev/audit/rounds/round10/D7/arch2-s4`, copied into the tree at the same relative path, because each locates `tools/audit` from its own path. Both arms run in a throwaway `git worktree` of `4a4107fcd`, the second with this head's two metric files copied over it, `PYTHONPATH=tests/hastub`.

- `$EXPORT/dev/audit/rounds/round10/D7/arch2-s4/score_delta.py P1_one_utc_clock_owner.patch` (sha1 `35570991d7150afff3931d5243ee945c6c8d1b6f`): `Architecture score: dS +0.4460 IMPROVES` at BOTH instruments (`layer_violations 21 -> 18 +0.2115`, `private_cross_module 19 -> 16 +0.2345`, `unused_boundary_imports 1 -> 1`), and `--revert` `dS +0.0000 NULL` at this head. The patch spells its imports the ordinary way, so the five seams do not reach it: the harness reads flat at both ends, and the companion applying the tree's own rule to the same inputs is the attempt set below, reading IMPROVES at the round-2 head and NULL here.
- `$EXPORT/dev/audit/rounds/round10/D7/arch2-s4/layering.py` (sha1 `314f35a49c474c1a21b6f4776aca7bb2af4efa1f`), the finder's independent census: `closure_store=28 modules (optimizer IN)`, `private_cross_module_names=17 count`. Its `--ref` default is the round's baseline `9061fbd3d`, so it reads the same at both ends by construction.
- The seam enumeration (`fixer.md` step 8). The rule is every way a package module reaches another, or a boundary, that the runtime runs, and the attempt set is its enumerator, measured live on every calibration run: `python3 tools/audit/archscore/calibrate.py` prints `RED TEAM 64/64 attempts read NULL or inadmissible; IMPROVES: none`. Its layering seams and dispositions:

  | seam | disposition |
  |---|---|
  | `from .m import _x`, at module scope or in a function | counted (attempt 21, counter C17) |
  | the `else` of `if TYPE_CHECKING:` | closed in round 2 (attempt 24) |
  | `if not TYPE_CHECKING:` | closed in round 2 (25) |
  | `from <pkg>.m import _x`, the absolute from-import | closed in round 2 (27) |
  | `import <pkg>.m as _o` and the full dotted read off `import <pkg>.m` | closed here (28, 29; M12, M11 reopen them) |
  | `from <pkg> import optimizer as _o` + `_o._x` | closed here (30; M11 reopens it) |
  | `m._x` through a relative module binding; `getattr(m, "_x")` | counted (counter C18, attempt 22) |
  | a constant-name `importlib.import_module(..)._x`, positional and by `name=` | closed (26 in round 2, 31 here; M13 reopens 31) |
  | the guard `else`, under `not`, and a disjoined test | closed in round 2 (24, 25) |
  | `__import__(.., level=1)`, the builtin's spelling | refused: raises at import (below), so no attempt can pin it |
  | `getattr(_o, "_x" + suffix)`, `vars(_o)["_x"]`, `_m = _o; _m._x` | OPEN, counter C18's class (round 1's p6, p7, p8). Written into `tools/audit/archscore/ABOUT.md` for the D7 brief and the next archscore part |
  | a name computed at runtime: `f".{module}"`, `exec`, a rebound binding | invisible by design; the metric's docstring and `ABOUT.md` state it |
  | an unread boundary import plus one bare read | OPEN, counter C19's class (round 1's p5). Same destination |

- `__import__(".optimizer", fromlist=["_f"], level=1)` from a package submodule, against a stand-in package: `KeyError: "'__name__' not in globals"` on this seat's CPython 3.14.7 (Python `3.14.7`), so the spelling is refused as an attempt rather than closed. Reproduced with `T=$(mktemp -d); mkdir -p "$T/p/s"; : > "$T/p/__init__.py"; printf 'def _f():\n    return 1\n' > "$T/p/s/mod.py"; printf 'a = __import__(".mod", fromlist=["_f"], level=1)\n' > "$T/p/s/who.py"; printf 'import p.s.who\n' > "$T/run.py"; ( cd "$T" && python3 run.py )`; no `if not node.args` guard turns it into a pass.
- `python3 tools/audit/archscore/calibrate.py` at this head: `calibration moved on 4 case(s)`, all four this round's. `--record` printed `RECORD` for those four and nothing else; the diff to `expected.json` is 24 insertions, 0 deletions. `CALIBRATION 95/124 labelled cases classify as their label says`, `RED TEAM 64/64 attempts read NULL or inadmissible`, `KNOWN-OPEN 1` (unchanged), no `SENSITIVE` line.
- `python3 tools/audit/archscore/calibrate.py --measure-corpus --only-metric layering --jobs 6`: 87 vectors `ok`, 0 `ERROR`, and `corpus_vectors.json` byte-identical to the file it re-derived (`cmp`).
- `python3 dev/audit/harnesses/archscore_layering_seam_census.py <wt> --corpus`: `corpus trees censused: 87`, `absolute_self_import=0`, `absolute_self_import_dotted=0`, `constant_dynamic_import=30` with `dynamic_names=['threadpoolctl']`, `guard_not_body=58`, `guard_not_body_imports=0`; planted `2 / 1 / 3 / 4 / 2`; `PRECONDITION ok`, rc=0. Both absolute self-import counters being zero is what licenses the byte-identical corpus re-measure above; under the round-2 census the two were one number, so the same zero would have covered either form.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> `MODE: SCOPED -- 3 script(s) run, 30 scoped out`, naming `tests/arch_score.py` (`ALL 221 ARCHITECTURE SCORE CHECKS PASSED`), `tests/arch_score_head.py` (`ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED`) and `tests/entities.py` (`ALL 2329 ENTITY CHECKS PASSED`). `run.sh`'s `run_always` scripts, run individually at this head, `PYTHONPATH=tests/hastub`: `tests/env_drift.py --claims-only 81ae048e8` (`claims hygiene: 81ae048e8bbdf2335fe2016e987ec2739481f293 ok`), `tests/closure.py selftest` (`ALL 115 closure shrink pins PASSED`), `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`) and `tests/layout.py` (`layout self-test: ok`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (no package file changed; every row `<=` its budget).
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- The three ci-ratchet rows at this head: `ci_ratchet.archscore_metrics()` reads `archscore.layer_violations` 22, `archscore.private_cross_module` 17 and `archscore.unused_boundary_imports` 1, unchanged from what the rows record, so no re-record is owed and `tests/ci_budgets.json` is not in this diff.
- The closure re-record lists the four new attempt scripts: `tests/arch_score.py` moves from 129 to 133 files, and `tests/closure.py`'s orphan list is empty at this head.

## Raise justification

`tests/ci_budgets.json` gains three NEW rows. They are new ratchets, not raises, and no existing row moves: `archscore.layer_violations` 22, `archscore.private_cross_module` 17 and `archscore.unused_boundary_imports` 1. Each is recorded at the value `ci_ratchet.archscore_metrics()` derives at the merged head; `recorded_at` and `reason` are updated. They are needed because the layering metric adds three keys to the score vector, and `ci_ratchet` refuses a derived key with no row as growth. This round derives the same three values, so no row moves and no re-record is owed.

Payments considered, and why each lost:
1. Make the metrics gate-only. They would still be vector keys, so they would still need rows.
2. Keep them out of the vector. The score would not price them, which is the roster item's point.

Approved by the orchestrator under mandate 6175172275 before the round-1 push. A change to a `*_budgets.json` merges only on the owner's approving review at its head (budget-raise-gate, 0013).

`Architecture score: dS +0.0000 NULL` (`score.py --diff origin/main`): no package code changed. The instrument on today's tree reads the three new keys as above, and every other key is unchanged.

## Unpinned sites

n/a for production code: the diff touches `tools/audit/archscore/`, one harness under `dev/audit/` and `tests/closures.json`; the new predicates are pinned by the calibration attempts and the mutants above.

## Architecture score

n/a: no package file changes; the instrument change takes effect after merge (`ABOUT.md`).

## Red checks

- `pr-contract` was red at `353f7f3c4` (run 117083222814) because `## Red checks` did not name `coverage-ratchet`, which is the check below. This section names it. No cheaper detector: the check IS the contract that the body answers what its own head went red on.
- `coverage-ratchet` (run 117074952157) is red at `353f7f3c4` on `every module >= 95.0 %`, `early_cutoff.py: 81.53 %` -- a `custom_components` module this diff does not touch, so the red is main's own stale base, not this branch's. The orchestrator's recarry carries it. It is named here because the body contract requires the name, not because this diff has an answer to it.
- `closures`: red at `77991f1ad` (the delivery-row commit), UNDER-SCOPED -- `metrics/layering.py` is imported by `tests/arch_score.py`, `tests/arch_score_head.py` and `tests/entities.py` through `tools/audit/archscore/vector.py`. `closures-autofix` re-recorded the others (bot commit `551b660e7`) and this round re-recorded `tests/arch_score.py` for the four new attempt scripts before its push, so the check is green from `7c7e1b786`. Answered by naming it (`ci-autofix.md`). The cheaper detector: `derive_closures.sh --single` on each script whose closure already holds `tools/audit/archscore/vector.py`, which is a `jq` over `tests/closures.json`; standing cost is one `--single` per such script (measured here: `tests/arch_score.py` at 5m19s, 23:08:07 to 23:13:26).
- `budget-raise-gate`: it flags `archscore.hub_solve_writes` 38 -> 41, part 2's raise carried in through the stack (answered in #2311's body). It stays red by design until tvofi approves at the head; the orchestrator posts the owner-gate approval under mandate 6175172275. No cheaper detector exists: the gate is the owner's approval itself.
- `tests/entities.py`, the ci-ratchet null control *"and main() passes the committed table at its own recorded count"*: it was red locally before the three rows were added, and again after merging origin/main `12cf1764d` (`layer_violations` 21 -> 22, main's own change). This round derives the same 22 / 17 / 1 as the rows, so it is green here. No cheaper detector: the null control is the row-versus-derivation comparison itself.

## Forward-carry

- **`dev/governance/dimensions/D7.md`, via R10-BRIEFS-FOLD.** The folded text must state what the layering counters do not see, because round 1's review measured that the metric's cheapest move reads as a decoupling: a private crossing spelled `getattr(_o, "_x" + suffix)`, `vars(_o)["_x"]` or through a rebound alias; C19's tripwire satisfied by one bare read; and `a3_private_cross_module_fix` being a pure rename of a private to a public name. The measurements live in the tree, in this pull request, at `tools/audit/archscore/ABOUT.md` under "What R10-ARCHSCORE-COVERAGE part 3 moved", with the attempt ids that carry each; the brief should cite them and re-measure at its own merge base rather than carry the counts. The roster entry that receives it is `dev/programme/rosters/wave-r10-groups.json`, R10-BRIEFS-FOLD's `carry` list, which this seat cannot write: the roster is the orchestrator's, and `groups[47].after` already places R10-BRIEFS-FOLD after this group.
- **The next archscore part** (parts 4 and 5 of this group): `rt_24` to `rt_31` and `a3_layer_violations_null`'s second arm are in the tree and run on every calibration, and `tools/audit/archscore/ABOUT.md`'s "What it does not see" list is what a part closing any of those seams has to move. `dev/audit/harnesses/archscore_layering_seam_census.py` is the census that says which trees carry which spelling.
- **R10-CONFIGFLOW-PAGES** (already on main as `084052aae`): remove `config_flow.py`'s unread `device_registry as dr`, the tripwire's one site today, and lower `tests/ci_budgets.json` `archscore.unused_boundary_imports` 1 -> 0 in the same pull request.

## Friction

- R10-ARCHSCORE-COVERAGE-p3-r3: contradiction: the seat brief said to work in the orchestrator's shared worktree and to hand off with `tools/audit/seat/handoff_push.sh`, while `dev/governance/rules/delivery-status-tracking.md` makes the pull-request update the orchestrator's; the seat pushed the code head and the body refs only. The orchestrator's correction moved the seat to its own scratch worktree off the shared one.
- R10-ARCHSCORE-COVERAGE-p3-r3: cost: `tools/audit/seat/handoff_push.sh` is named by the brief as the push instrument, and it cannot be run as written by a seat that must not write to GitHub: its first act is a `gh pr view` update.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
