R10-ARCHSCORE-COVERAGE, part 3 of 5: layering and private crossings in the architecture score (roster item 1, ARCH2-s4).

Part of #2259.

What changes: a new metric module, `tools/audit/archscore/metrics/layering.py`, with two score metrics at the floor weight. They guard no register class: `weights.json` is unchanged and its floor applies. There is also one gate-only tripwire and three counters.

The layers, lowest first: **pure** imports neither boundary, **solver** imports scipy, **glue** imports Home Assistant. A module's layer is the highest boundary it imports itself; an import may go down or across, never up.

- **`layer_violations`**: (module, layer) pairs where a module reaches, through other package modules, a layer above its own. Today: 22 at the merged head (21 before origin/main `12cf1764d`, whose R10-FAHRENHEIT change left `setpoint_check` importing neither boundary while it reaches both). The pure modules `quiet_windows` and `silent_mode` reach the solver for its private `_utc_step_starts`; `optimizer` and `dhw_planner` (solver) reach the glue. At the pin: 3.
- **`private_cross_module`**: distinct private names of one module that another names. Today: 17 at the merged head (19 before `12cf1764d` removed two); the attribute spellings include `coordinator`'s `away_mode._parse_return_time`.
- **`unused_boundary_imports`** (gate-only): a boundary import whose names the module never reads. Today: 1, `config_flow`'s `device_registry as dr`.
- **Counters:** C17, every import the runtime runs is an edge (attempts 21, 24 to 35, 37); C18, a private name read through a module binding crosses like its import (attempts 22, 26 to 37); C19, the tripwire (attempt 23).

### The rule, and what it follows

The reach is the reach whatever syntax spells it. It now follows every import that runs and names this package's namespace, and every private read that resolves to one of its modules through such an import:

- **the name's relation to the package is one predicate**, computed at a dot boundary: `self` (the package itself), `desc` (a module below it), `anc` (a strict PREFIX of it -- `custom_components`, the namespace the package is nested in). The ancestor and the descendant are the same rule, which is what a spelling list cannot express: `import <pkg>.optimizer` and `import custom_components` are one predicate's two directions, and a repair that adds an arm per spelling is how this class stayed open across three reviews.
- **the statements**: the relative form, the absolute from-import, the plain dotted import, and the same written from the namespace above -- aliased or not.
- **the reads**: `_o._x` off a module binding, the full dotted read off an unaliased one, the private read off a resolved `import_module(...)` call, and the same through an attribute chain or a `getattr` chain. A read that resolves to a module takes that module's EDGE as well as its crossing -- which is what an import of an ancestor needs, since that statement alone loads no module of ours.
- **the dynamic name**: passed positionally, as the `name` keyword, or held by a module-level string constant (statically readable, so it is the constant-name call it spells). `import_module`'s relative anchor is read the same way from `package=` or `__package__`.
- **the exclusion**: only the `body` of a positive `if TYPE_CHECKING:`, which nothing runs. An `else`, a negated test and a disjoined test are runtime code and their imports count.
- **not followed, and stated**: a name COMPUTED at runtime -- `f".{module}"` (the package's own is `__init__.py`'s lazy loader), `exec`, a name rebound after its import. `ABOUT.md`'s "What it does not see" list carries each with its attempt id, and the census counts the computed form as `dynamic:computed` rather than leaving it out.

Step 8's enumeration. The rule's enumerator is the attempt set, measured live on every calibration run -- `python3 tools/audit/archscore/calibrate.py` prints `RED TEAM 70/70 attempts read NULL or inadmissible; IMPROVES: none`. Every seam it returns, with its disposition:

| seam | disposition |
|---|---|
| `from .m import _x`, at module scope or in a function | counted (attempt 21, counter C17) |
| the `else` of `if TYPE_CHECKING:` | closed (attempt 24) |
| `if not TYPE_CHECKING:` / a disjoined test | closed (attempt 25) |
| the absolute from-import `from <pkg>.m import _x` | closed (attempt 27) |
| `import <pkg>.m as _o` + `_o._x`, and the full dotted read off `import <pkg>.m` | closed (attempts 28, 29) |
| `from <pkg> import optimizer as _o` + `_o._x` | closed (attempt 30) |
| a constant-name `importlib.import_module(..)._x`, positional | closed (attempt 26) |
| the same with the name passed as `name=` | closed (attempt 31) |
| **`import custom_components as _cc` + `_cc.<pkg>.optimizer._x`** (a strict PREFIX of the package) | closed (attempt 32) |
| **`from custom_components import heatpump_optimizer` + the dotted read** | closed (attempt 33) |
| **the same aliased** | closed (attempt 34) |
| **`import custom_components` + the full dotted read** | closed (attempt 35) |
| **`getattr(getattr(_cc, "heatpump_optimizer"), "optimizer")._x`** | closed (attempt 36) |
| **the dynamic name held by a module-level string constant** | closed (attempt 37) |
| `m._x` through a relative module binding; `getattr(m, "_x")` | counted (counter C18, attempt 22) |
| `getattr(_o, "_x" + suffix)`, `vars(_o)["_x"]`, `_m = _o; _m._x` | OPEN, counter C18's class (round 1's p6, p7, p8). Written into `ABOUT.md` for the D7 brief and the next archscore part |
| a name computed at runtime: `f".{module}"`, `exec`, a rebound binding | invisible by design; `ABOUT.md` and the metric's docstring state it, and the census counts it |
| an unread boundary import plus one bare read | OPEN, counter C19's class (round 1's p5). Same destination |
| `__import__(.., level=1)`, the builtin's spelling | refused, not open: importing that module raises `KeyError: "'__name__' not in globals"` on CPython 3.14.7 (command in `## Figures`), so it is not code a seat can ship and no attempt could pin a rule for it |

Calibration cases, all measured live on every run:
- attempts `rt_21` to `rt_37`, one per seam above;
- `a3_layer_violations_*`: BAD, `drift.py` (pure) imports the optimizer; GOOD, the horizon clock moves to `step_clock.py` and `silent_mode` imports it there; NULL, the import moves within module level and `drift.py` gains an annotation-only `if TYPE_CHECKING:` import of the optimizer, so the guard's exclusion is measured in both directions;
- `a3_private_cross_module_*`: BAD, `drift.py` imports `freq_control._finite`; GOOD, `away._parse_return_time` is declared public; NULL, the same private imported under an alias.

Alternatives considered:
- A raw import-closure size per module (ARCH2-s4's `layering.py` metric 1): every module added or extracted grows someone's closure, so it rises on every decomposition.
- A statement-weighted closure: rises on any added code anywhere.
- The module-bound count: calibrated and refused (four GOOD corpus decompositions read WORSENS); `ABOUT.md` carries it.
- Counting only modules that reach without importing: the module that adds the boundary import escapes; C19 closes it.
- For the guard: excluding every test that mentions `TYPE_CHECKING`, which round 1 shipped. Refused -- an `else` and a negated test are runtime code, and excluding them is how a seat gets `+0.1466` for moving an import into one.
- For dynamic imports: resolving them by importing the call, or by a second source regex. Refused -- the trees are never run (`metrics/common`'s docstring), and a second parser is a second rule to keep in agreement.
- **For the spellings, an arm per spelling.** Refused, and this is the alternative that three review rounds measured: an enumeration whose domain is a hand-list closes exactly what it was shown (round 1's four, round 2's three, round 3's three more). The predicate is now the name's relation to the package, so a descendant and an ancestor are one arm and there is no list to be one spelling short of.
- **For the census, a counter per spelling.** Refused the same way. Its keys are now built from the node's own slot and the name's relation to SELF, the planted tree is generated from the same tables, and a package-naming node with no key refuses the census instead of reading as a zero.

## Head

`c8768c1d74c35eeac7afd95ded2c61e918054d8f` (this round's repair, the re-record and the closure), on the PR's previous head; the orchestrator merges it into `fix/r10-archscore-coverage-p3` and prefixes that merge's SHA here. The figures below are taken against this branch's base `81ae048e8` on `2026-10-16T23:46Z`; `origin/main` was `d7b171229` then. The chain the section has to name, oldest first: `507bf3efd` -> `aacdc1c4c` -> `77991f1ad` -> `551b660e7` (bot) -> `4a4107fcd` (bot) -> `1a7e42bfc` -> `48b83e20e` -> `eebf3f366` -> `f25a8a915` -> `c4209f9db` -> `353f7f3c4` -> `bb66adaf5` -> `7c7e1b786` -> `aef20e8e9` (the pull request's head) -> `8e894e226` (this round's repair) -> `5ddc97443` (the re-record) -> `c8768c1d7` (the closure).

## Mutation proof

Eight arms, each an in-place predicate edit on the committed head, restored with `git checkout --`, over the ten attempts this round's predicates serve end to end:

    python3 tools/audit/archscore/calibrate.py --only rt_28_layer_import_abs_alias,rt_29_layer_import_abs_plain,rt_30_layer_from_abs_module,rt_31_layer_import_module_kw,rt_32_layer_parent_ns_alias,rt_33_layer_parent_ns_from,rt_34_layer_parent_ns_from_alias,rt_35_layer_parent_ns_plain,rt_36_layer_getattr_chain,rt_37_layer_module_const_name

- **M0**, no mutation (the runner's own null): `RED TEAM 10/10 attempts read NULL or inadmissible; IMPROVES: none`.
- **M11**, `_name_bindings` returns `{}`: reopens `rt_28`, `rt_29`, `rt_30`, `rt_32`, `rt_33`, `rt_34`, `rt_35`, `rt_36`. The binding map is load-bearing for every arm that resolves a read.
- **M12**, the `ast.Import` edge arm removed: **reopens nothing**, and that is disclosed rather than claimed as a kill. Every planted spelling also reads a private through the binding, and the read arm adds the edge (M17), so no attempt separates the two. The arm stays because it is the model's rule -- an import that runs loads the module, whether or not the module is read -- and no attempt exists for it: a bare `import <pkg>.m` with no read *worsens* `layer_violations`, so it is no seat's move and no GAME case can carry it. The census agrees: no corpus tree spells a bare absolute import at all.
- **M13**, `_dynamic_name` back to `node.args[0]` only: reopens `rt_31` and `rt_37` (the `name=` keyword and the module-level constant both pass through it).
- **M14**, `_namespaced` back to the descendant direction only: reopens `rt_32`, `rt_33`, `rt_34`, `rt_35`, `rt_36` -- the whole ancestor family -- and leaves `rt_37`, whose name is relative.
- **M15**, `_dotted_path` without its `getattr` arm: reopens `rt_36` alone. The finer control.
- **M16**, `_module_const` returns None: reopens `rt_37` alone.
- **M17**, the read arm adds the crossing but not the edge: reopens `rt_32`, `rt_33`, `rt_34`, `rt_35`, `rt_36`.

## Null control

- Each attempt reads `IMPROVES` before its predicate is in the tree and NULL or inadmissible after, at the same instrument: the six this round adds, run against a worktree of the PR's previous head `aef20e8e9` with the scripts copied in, print `GAME IMPROVES dS +0.5849` each (`layer_violations +0.415`, `private_cross_module +0.170`); at this head they print `IMPROVES: none` under `RED TEAM 70/70 attempts read NULL or inadmissible`.
- `M0` (no mutation) moves nothing, so the arm harness shifts no verdict by itself.
- `a3_layer_violations_null` reads NULL with its annotation-only import and WORSENS with the guard's exclusion ignored (round 2's `M6` arm), so "nothing runs the guard body" is measured in both directions rather than assumed.
- The corpus re-measure owes its own control, and the census is it: it fires on a generated tree carrying every key before it reports the corpus's zeros, and it refuses when one classifier arm is dropped (211 `unkeyed`). Without that arm the corpus's zero for the whole absolute family -- the ancestor direction included -- would be indistinguishable from a census that cannot see it, which is what the previous census's single `absolute_self_import` counter made of it.
- The finder's own instrument reads flat at both ends by construction: its `--ref` default is the round's baseline, so it re-reads the same git objects whatever the metric does. Named as flat, not as agreement.

## Figures

Finder's harnesses: `$EXPORT` = `git archive b202335e2 dev/audit/rounds/round10/D7/arch2-s4`, copied into the tree it measures, because each locates `tools/audit` from its own path. Both arms run in a throwaway `git worktree` of `4a4107fcd`, the second with this head's two metric files copied over it, `PYTHONPATH=tests/hastub`.

- `$EXPORT/dev/audit/rounds/round10/D7/arch2-s4/score_delta.py P1_one_utc_clock_owner.patch` (sha1 `35570991d7150afff3931d5243ee945c6c8d1b6f`): `Architecture score: dS +0.4460 IMPROVES` at this head, with `layer_violations 21 -> 18 +0.2115`, `private_cross_module 19 -> 16 +0.2345`, `unused_boundary_imports 1 -> 1`; `--revert` `dS +0.0000 NULL`. The patch spells its imports the ordinary way, so the seams do not reach it: the harness reads flat at both ends, and the companion that applies the tree's own rule to the same inputs is the attempt set above.
- `$EXPORT/dev/audit/rounds/round10/D7/arch2-s4/layering.py` (sha1 `314f35a49c474c1a21b6f4776aca7bb2af4efa1f`), the finder's independent census: `closure_store=28 modules (optimizer IN)`, `private_cross_module_names=17 count`. Its `--ref` default is the round's baseline `9061fbd3d`, so it reads the same at both ends by construction.
- The attempts at both ends: `python3 tools/audit/archscore/calibrate.py --only rt_32_layer_parent_ns_alias,rt_33_layer_parent_ns_from,rt_34_layer_parent_ns_from_alias,rt_35_layer_parent_ns_plain,rt_36_layer_getattr_chain,rt_37_layer_module_const_name` in a worktree of `aef20e8e9` with the six scripts copied in -> `IMPROVES dS +0.5849` each; at this head -> `NULL`, `WORSENS`, `WORSENS`, `NULL`, `NULL`, `NULL`.
- `python3 tools/audit/archscore/calibrate.py --record` at this head printed `RECORD` for exactly the six cases above and nothing else (no existing verdict moved); the diff to `expected.json` is 36 insertions, 0 deletions. The same run printed `CALIBRATION 95/124 labelled cases classify as their label says`, `RED TEAM 70/70 attempts read NULL or inadmissible`, `KNOWN-OPEN 1` (unchanged) and no `SENSITIVE` line, and `tests/arch_score.py` re-derives that record at this head and passes.
- `python3 tools/audit/archscore/calibrate.py --measure-corpus --only-metric layering --jobs 6`: 87 vectors `ok`, 0 `ERROR`, and `corpus_vectors.json` byte-identical to the file it re-derived (`cmp`).
- `python3 dev/audit/harnesses/archscore_layering_seam_census.py <wt> --corpus`: `corpus trees censused: 87`; every one of the twelve absolute statement keys `0` -- `import:self`, `import:desc`, `import:anc` and the aliased and `from` forms -- with `from_rel:self=1590`, `from_rel:desc=7330`, `from_rel_as:self=279`, `from_rel_as:desc=463`, `dynamic:positional=30`, `dynamic:computed=58`, `guard:body=90`, `guard:else=58`, and `unkeyed=0`. Planted: every derived key `>= 1`, `planted_unkeyed=0`, and with the statement arm dropped `211` unkeyed. The twelve zeros are what licenses the byte-identical corpus re-measure above, and they are *derived* keys: the previous census's one `absolute_self_import` counter could not have separated the ancestor direction from the descendant one.
- `python3 dev/audit/harnesses/archscore_layering_seam_census.py <wt>` on today's tree: the same twelve keys `0`, `from_rel:self=39`, `from_rel:desc=259`, `dynamic:positional=1`, `dynamic:computed=1`, `guard:body=4`, `guard:else=2`, `unkeyed=0`.
- `__import__(.., level=1)` from a package submodule, against a stand-in package: `KeyError: "'__name__' not in globals"` on this seat's CPython 3.14.7, so the builtin's spelling is refused rather than closed. Reproduced with `T=$(mktemp -d); mkdir -p "$T/p/s"; : > "$T/p/__init__.py"; printf 'def _f():\n    return 1\n' > "$T/p/s/mod.py"; printf 'a = __import__(".mod", fromlist=["_f"], level=1)\n' > "$T/p/s/who.py"; printf 'import p.s.who\n' > "$T/run.py"; ( cd "$T" && python3 run.py )`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> `MODE: SCOPED -- 3 script(s) run, 30 scoped out`, naming `tests/arch_score.py` (`ALL 227 ARCHITECTURE SCORE CHECKS PASSED`), `tests/arch_score_head.py` (`ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED`) and `tests/entities.py` (`ALL 2329 ENTITY CHECKS PASSED`). `run.sh`'s `run_always` scripts, run individually at this head, `PYTHONPATH=tests/hastub`: `tests/env_drift.py --claims-only 81ae048e8` (`claims hygiene: 81ae048e8bbdf2335fe2016e987ec2739481f293 ok`), `tests/closure.py selftest` (`ALL 115 closure shrink pins PASSED`), `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`) and `tests/layout.py` (`layout self-test: ok`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (no package file changed; every row `<=` its budget).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL` (no package file changes). Run as `--diff origin/main` it reads `dS -0.0158 WORSENS (coord_footprint 2547 -> 2575)`, only because `origin/main` advanced to `d7b171229` (#2336) past this branch's base `81ae048e8`: `git diff --numstat 81ae048e8...c8768c1d7 -- custom_components/` is empty, stated so the figure is not read as a regression.
- The three ci-ratchet rows at this head: `ci_ratchet.archscore_metrics()` reads `archscore.layer_violations` 22, `archscore.private_cross_module` 17 and `archscore.unused_boundary_imports` 1, unchanged from what the rows record, so no re-record is owed and `tests/ci_budgets.json` is not in this diff.
- The closure re-record lists the six new attempt scripts: `tests/arch_score.py` moves from 133 to 139 files, and `python3 -c "import sys; sys.path.insert(0,'tests'); import closure; print(closure.orphan_files())"` prints `[]`.

## Raise justification

`tests/ci_budgets.json` gains three NEW rows. They are new ratchets, not raises, and no existing row moves: `archscore.layer_violations` 22, `archscore.private_cross_module` 17 and `archscore.unused_boundary_imports` 1. Each is recorded at the value `ci_ratchet.archscore_metrics()` derives at the merged head; `recorded_at` and `reason` are updated. They are needed because the layering metric adds three keys to the score vector, and `ci_ratchet` refuses a derived key with no row as growth. This round derives the same three values, so no row moves and no re-record is owed.

Payments considered, and why each lost:
1. Make the metrics gate-only. They would still be vector keys, so they would still need rows.
2. Keep them out of the vector. The score would not price them, which is the roster item's point.

Approved by the orchestrator under mandate 6175172275 before the round-1 push. A change to a `*_budgets.json` merges only on the owner's approving review at its head (budget-raise-gate, 0013).

`Architecture score: dS +0.0000 NULL` (`score.py --diff $(git merge-base origin/main HEAD) HEAD`): no package code changed. The instrument on today's tree reads the three new keys as above, and every other key is unchanged.

## Unpinned sites

n/a for production code: the diff touches `tools/audit/archscore/`, one harness under `dev/audit/` and `tests/closures.json`; the new predicates are pinned by the calibration attempts and the mutants above.

## Architecture score

n/a: no package file changes; the instrument change takes effect after merge (`ABOUT.md`).

## Red checks

- `pr-contract`: red earlier on this branch, when `## Red checks` omitted `coverage-ratchet`; this section names it. The check is the body contract itself; the cheaper detector is running `tools/pr/prepr.sh` over the body before the push, which this seat did (`PR-BODY: 0 error(s)`, `FIGURES: 15 resolved, 5 not verified, 0 refused`).
- `coverage-ratchet`: red at the PR's head on `every module >= 95.0 %`, `early_cutoff.py: 81.53 %` -- a `custom_components` module this diff does not touch, so the red is main's own base, not this branch's. Named here because the body contract requires the name. No cheaper detector: the check is its own lane, and a fixer's brief forbids re-running it.
- `closures`: red earlier on this branch (UNDER-SCOPED) when `metrics/layering.py` landed without its readers re-recorded; `closures-autofix` and this seat's `derive_closures.sh --single` re-recorded them, and this round re-recorded `tests/arch_score.py` for the six new attempt scripts before its push. Answered by naming it (`ci-autofix.md`). The cheaper detector: `derive_closures.sh --single` per script whose closure already holds `tools/audit/archscore/vector.py`, a `jq` over `tests/closures.json`.
- `budget-raise-gate`: it flags `archscore.hub_solve_writes` 38 -> 41, part 2's raise carried in through the stack (answered in #2311's body). It stays red by design until tvofi approves at the head; the orchestrator posts the owner-gate approval under mandate 6175172275. No cheaper detector exists: the gate is the owner's approval itself.
- `tests/entities.py`, the ci-ratchet null control "and main() passes the committed table at its own recorded count": red locally before the three rows were added, and again after merging origin/main `12cf1764d` (`layer_violations` 21 -> 22, main's own change). It derives the same 22 / 17 / 1 as the rows at this head. No cheaper detector: the null control is the row-versus-derivation comparison itself.

## Forward-carry

- **`dev/governance/dimensions/D7.md`, via R10-BRIEFS-FOLD.** The folded text must state the boundary this rule draws: what the layering counters do not see (`getattr(_o, "_x" + suffix)`, `vars(_o)["_x"]`, a rebound alias; a name computed at runtime; C19's tripwire satisfied by one bare read; and `a3_private_cross_module_fix` being a pure rename of a private to a public name, which is this metric's cheapest move). The measurements live in the tree, in this pull request, at `tools/audit/archscore/ABOUT.md` under "What R10-ARCHSCORE-COVERAGE part 3 moved", with the attempt ids that carry each; the brief should cite them and re-measure at its own merge base rather than carry the counts. The roster entry that receives it is `dev/programme/rosters/wave-r10-groups.json`, R10-BRIEFS-FOLD's `carry` list, which this seat cannot write: the roster is the orchestrator's, and `groups[47].after` already places R10-BRIEFS-FOLD after this group.
- **The next archscore part** (parts 4 and 5 of this group): `rt_21` to `rt_37` and `a3_layer_violations_null`'s second arm are in the tree and run on every calibration, and `tools/audit/archscore/ABOUT.md`'s "What it does not see" list is what a part closing any of those seams has to move. `dev/audit/harnesses/archscore_layering_seam_census.py` is the census that says which trees carry which form, by derived key.
- **R10-CONFIGFLOW-PAGES** (already on main as `084052aae`): remove `config_flow.py`'s unread `device_registry as dr`, the tripwire's one site today, and lower `tests/ci_budgets.json` `archscore.unused_boundary_imports` 1 -> 0 in the same pull request.

## Friction

- R10-ARCHSCORE-COVERAGE-p3-r4: contradiction: the seat brief names `tools/audit/seat/handoff_push.sh` as the push instrument, while the pull-request update is the orchestrator's; the seat pushes the code and body refs only, as `dev/governance/rules/delivery-status-tracking.md` requires.
- R10-ARCHSCORE-COVERAGE-p3-r4: cost: `fix-review.md` step 6's block grammar names a seam, and this round's seam was a predicate's DOMAIN rather than a missing arm. A seat reading "add a case per spelling" from it would have added a fourth enumeration; the fix was to move the predicate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
