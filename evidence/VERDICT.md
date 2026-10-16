Fix review: blocked aef20e8e98a227300317938850dbc7a5f655e18b class-open: an import whose dotted name is a strict ANCESTOR of the package (`import custom_components`, `from custom_components import heatpump_optimizer [as _p]`) is still no edge and roots no binding, so `custom_components.heatpump_optimizer.optimizer._utc_step_starts(..)` keeps the solver reach and reads IMPROVES dS +0.5849 at this head

bus-nonce: c903933b7ae7d1516de91fc66be9904f

PR #2320, R10-ARCHSCORE-COVERAGE part 3, **round 3**. Reviewer `rev-2320`, detached worktree at the head. Contract `fix-review.md` from `origin/main` `92accb2cf`; `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
Measured head `aef20e8e98a227300317938850dbc7a5f655e18b`, re-read before posting and unchanged.
Part 3's own delta is `git diff 92accb2cf...HEAD` (`git merge-base origin/main HEAD` = `92accb2cf`), and `git diff --numstat 92accb2cf...HEAD -- custom_components/` is empty.

Round 2's two blocks: `class-open` is **not** closed (below); `carry-missing` **is** addressed — the carry is present on the ref the body names (step 10). Round 2's `root-cause-unrecorded` reading is moot at this head: `pr-contract` is green here.

## Blocking

**harness: class-open (step 6).** The round-3 repair closes the three spellings round 2 named — I reproduce that — and it does so with a predicate that is still an enumeration, one level down: `_self_module` accepts `SELF` and `SELF.*` and returns `None` for a name that is a strict **prefix** of `SELF`. `_name_bindings`'s `ast.Import` arm (lines 130-136), its `_from_names` arm, and `graph`'s new `ast.Import` edge arm all key on it, so an import of the HA namespace package binds nothing, roots nothing, and takes no edge. Round 3 added the *descendant* direction (`import <pkg>.m`, attempts 28/29); the *ancestor* direction is the same statement family, is named nowhere in the diff, the body's seam table, `ABOUT.md` or the census, and reads the same +0.5849.

Five plants, each replacing the pin's `silent_mode.py` module-level `from .optimizer import _utc_step_starts` with one spelling of the same reach, every other metric unmoved (my harness `r3_classprobe.py`, named as mine; trees at the pin `7952d8f9e`, this head's instrument, `evidence/class_probe_head.txt`, `evidence/class_probe_head_part1.log`):

| plant | spelling | verdict | dS | moved |
|---|---|---|---|---|
| `S4_import_parent_ns` | `import custom_components as _cc` + `_cc.heatpump_optimizer.optimizer._x(..)` | **IMPROVES** | **+0.5849** | `layer_violations 3->2`, `private_cross_module 8->7` |
| `S5_from_parent_ns` | `from custom_components import heatpump_optimizer` + `heatpump_optimizer.optimizer._x(..)` | **IMPROVES** | **+0.5849** | same |
| `T2_from_parent_child_alias` | `from custom_components import heatpump_optimizer as _p` + `_p.optimizer._x(..)` | **IMPROVES** | **+0.5849** | same |
| `T3_import_parent_plain` | `import custom_components` + `custom_components.heatpump_optimizer.optimizer._x(..)` | **IMPROVES** | **+0.5849** | same |
| `T5_getattr_parent_chain` | `getattr(getattr(_cc, "heatpump_optimizer"), "optimizer")._x(..)` | **IMPROVES** | **+0.5849** | same |

**Behaviour is unchanged, not argued.** These plants hinge on `_p.optimizer` being a real attribute of the package, so I imported the spelling for real against a stand-in namespace package whose `__init__` deliberately does **not** pull the submodule in (the real one does not either — `custom_components/heatpump_optimizer/__init__.py:62` "Importing this package must not execute the coordinator's module graph"), then imported a sibling that does (`coordinator.py` imports `optimizer`, as it is at setup). `S4`, `S5` and `S8` each resolve to the same function object as the pinned spelling.

**The controls that bound this are on both sides.** The five spellings that *are* closed read NULL at this head through the same predicate: `T1` (`import <pkg> as _p` + `_p.optimizer._x`), `T4` (`from . import optimizer` no alias), and the four attempts 28-31. So the seam is exactly the strict prefix, not "attribute paths in general".

Counter-argument, recorded rather than hidden: the metric's model is *the import graph*, and in these plants the reach is made by attribute access rooted at an import of a non-package name — so one can read them as outside the graph rule and inside the residual that C18's "OPEN, counter C18's class" row lists. That reading does not reach the block, because the larger term is `layer_violations` (+0.415 of the +0.5849): that row is `private_cross_module`'s, and the metric's own definition of `layer_violations` is "a pure module that cannot load without the solver". Under `T3` `silent_mode` still cannot load without the solver, and the metric reports it free of the violation. Nothing in the body or `ABOUT.md` dispositions it.

A second spelling, not rested on: `_MOD = ".optimizer"` then `importlib.import_module(_MOD, __package__)._x(..)` (`S8_module_const_name`) reads **IMPROVES +0.5849**; `_dynamic_name` requires `ast.Constant`, and a module-level string constant is statically resolvable rather than computed. The body's row is worded "a name computed at runtime", and `ABOUT.md`'s is "a dynamic import whose name is computed" — the mechanism a reader meets is the same (`first` is an `ast.Name`), so I treat this one as dispositioned by that row and do not rest the block on it. A fix that closes the ancestor arm should say which of the two it means.

**The census is again a hand-list, and that is round 2's own criticism one level up.** `dev/audit/harnesses/archscore_layering_seam_census.py` now carries one counter per form and its planted tree fires every counter (`PRECONDITION ok`), which is the repair round 2 asked for. But the counters are still an enumeration of the forms the author thought of, and the planted tree plants exactly those, so `absolute_self_import=0 / absolute_self_import_dotted=0` over the corpus cannot separate "no corpus tree spells this class" from "no corpus tree spells a form the census counts". Neither the ancestor form nor the constant-variable form is a counter. The body does not over-claim for the census (it says "every spelling **the census counts**"); it over-claims where it says the attempt set is the rule's enumerator, and the attempt set lacks both.

None of the five occurs anywhere in the tree today (`git grep -n "import custom_components" -- custom_components/` returns nothing), so the seam is latent — the same status round 2 gave its own three, and round 1 its four.

## Verified

- **Step 1, mutation proof, re-run with my own harness** (`r3_mut.py`, mine; in-place edits on a scratch worktree of this head, restored with `git checkout`; the four attempts measured at the pin against the mutated instrument). `evidence/mutants.txt`:
  - `M0`, no mutation: 28/29/30/31 all `NULL dS +0.0000`.
  - `M11`, `_name_bindings` returns `{}`: `28_import_abs_alias`, `29_import_abs_plain`, `30_from_abs_module_alias` each `IMPROVES`, `31` `NULL`. Matches the body arm for arm.
  - `M12`, the `ast.Import` edge arm removed: `28`, `29` `IMPROVES`; `30`, `31` `NULL`. Matches.
  - `M13`, `_dynamic_name` back to `node.args[0]` only: `31_import_module_kw` `IMPROVES`; the rest `NULL`. Matches.
  Each mutant moves only the attempts the body names, so each new predicate is load-bearing. (dS differs between arms because the mutated instrument has a different base count; the verdicts are what the body claims.)
- **Step 8, the four quoted dS re-derived at both ends, the fixer's own instrument.** `evidence/calibrate_r2head_only4.txt`, `evidence/calibrate_head_only4.txt`: at `353f7f3c4` with the four attempt scripts copied in, `calibrate.py --only <the four>` prints `IMPROVES dS +0.5849` / `+0.5849` / `+0.1699` / `+0.5849`; at this head the same four print `NULL dS +0.0000`. **Exact match with the body's table.**
- **Step 8, the census figures.** `evidence/census_corpus.txt`: `corpus trees censused: 87`, `absolute_self_import=0`, `absolute_self_import_dotted=0`, `constant_dynamic_import=30`, `guard_not_body=58`, `guard_not_body_imports=0`, `dynamic_names=['threadpoolctl']`, planted `2 / 1 / 3 / 4 / 2`, `PRECONDITION ok`, rc 0. **Exact match.**
- **Step 14, no number the diff moves is the instrument's.** `ci_ratchet.archscore_metrics()` at this head derives `layer_violations 22`, `private_cross_module 17`, `unused_boundary_imports 1` — exactly the three new `tests/ci_budgets.json` rows; no existing row moves (`hub_solve_writes` still 41), and the row diff against the merge base is three additions plus `reason`/`recorded_at`. `expected.json` this round is 24 insertions, 0 deletions (the new cases only — no existing verdict moved), and CI's `arch-score` is green here. `corpus_vectors.json` is untouched this round (`git diff 353f7f3c4 HEAD`). `tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- **The quoted `dS +0.0000 NULL` is right against the body's own base, and stale against today's main.** `score.py --diff 92accb2cf HEAD` -> `Architecture score: dS +0.0000 NULL`. Run as the body writes it, `--diff origin/main`, it now reads `dS -0.0158 WORSENS (coord_footprint 2547->2575)` — only because `origin/main` advanced to `d7b171229` (#2336) after this head's merge; the diff touches no package file. Stated so the figure is not read as a regression.
- **Step 10, forward-carry.** `<repo>/dev/programme/rosters/wave-r10-groups.json` at `origin/handoff/audit-r10-roster` (`e3f2468c6` = PR #2343's head): `groups[47]` `R10-BRIEFS-FOLD`'s `carry[3]` reads "From R10-ARCHSCORE-COVERAGE part 3 (#2320): the D7 brief must state what the layering counters do not see ... The measurements live in `tools/audit/archscore/ABOUT.md` under \"What R10-ARCHSCORE-COVERAGE part 3 moved\", with the attempt ids; cite them and re-measure at your merge base." The body's `## Forward-carry` names that file and that group. Not yet on `origin/main` — #2343 is the orchestrator's sequencing, as round-2's brief said.
- **Step 11.** 45 check-runs at this head, 29 success, 15 skipped, **1 failure**: `coverage-ratchet` (`117219528069`). The body's `## Red checks` names it and reports the red as `every module >= 95.0 %`, `early_cutoff.py: 81.53 %` — a `custom_components` module; `git diff --numstat 92accb2cf...HEAD -- custom_components/` is empty, so no module on that lane is this diff's. I did not re-run the coverage lane (the fixer's brief and `ci-autofix.md` both forbid it), so I verify the naming and the diff, not the figure. `pr-contract` is **green** at this head (`117225661643`, 22:29:33Z, after `coverage-ratchet` concluded at 22:11:02Z), so the body contract holds. `arch-score`, `mutation`, `closures`, `coverage`, `fast (3.14)`, `composed-proof` and `budget-raise-gate` all success.
- **Steps 4, 5, 13.** `env_drift.py --claims-only 92accb2cf` -> `claims hygiene: ... ok`; neither claim file is in the diff. `VERSION`, the manifest version and `RELEASE_NOTES.md` untouched. `git merge-tree --write-tree origin/main HEAD` (against today's `origin/main`) exits 0 with no `MERGE-CLAIM` marker: no conflict.
- **Disclosed as mine, not the finder's**: `r3_classprobe.py` and `r3_mut.py`. The census and `calibrate.py` are the tree's own and I ran them unchanged; CI's heavy lanes are cited, not re-run.

## RESULT lines

    RESULT head aef20e8e98a227300317938850dbc7a5f655e18b measured; unchanged at post
    RESULT mutation M0=all four NULL; M11={28,29,30 IMPROVES, 31 NULL}; M12={28,29 IMPROVES}; M13={31 IMPROVES}
    RESULT attempts dS at 353f7f3c4 = +0.5849 / +0.5849 / +0.1699 / +0.5849 IMPROVES; at this head all NULL +0.0000
    RESULT census 87 corpus trees: absolute_self_import=0 absolute_self_import_dotted=0 constant_dynamic_import=30 guard_not_body=58 guard_not_body_imports=0; planted 2/1/3/4/2; PRECONDITION ok
    RESULT class_open ancestor_import: S4=+0.5849 S5=+0.5849 T2=+0.5849 T3=+0.5849 T5=+0.5849 all IMPROVES, each moving layer_violations 3->2 and private_cross_module 8->7
    RESULT class_open controls T1=NULL T4=NULL (strict-prefix is the seam, not attribute paths in general)
    RESULT class_open S8_module_const_name=+0.5849 IMPROVES (dispositioned only by the "name computed at runtime" row; not the block)
    RESULT ci_ratchet derived 22 / 17 / 1 == the three new rows; hub_solve_writes 41 unmoved; expected.json 24 insertions 0 deletions
    RESULT merge_tree rc=0 vs origin/main d7b171229
    RESULT structure STRUCTURE RATCHET PASSED; score.py --diff 92accb2cf HEAD = +0.0000 NULL; env_drift claims ok
    RESULT head check-runs 45: 29 success, 15 skipped, 1 failure (coverage-ratchet, named in ## Red checks; pr-contract green at this head)
    RESULT forward_carry present at origin/handoff/audit-r10-roster e3f2468c6 (PR #2343), R10-BRIEFS-FOLD carry; not yet on origin/main

## Friction

- `fix-review.md` step 6's block grammar names a seam, and the seam here is a predicate's domain rather than a missing statement arm: `_self_module` is the single test, and it accepts descendants of `SELF` but not ancestors. A repair that closes `S4`/`T3` by adding arms per spelling would repeat round 1's defect, so the seat should expect to move that predicate, not add a case — `_module_attr` already resolves whatever dotted path a binding roots, so only the binding/edge arms need the prefix.
- Round 3's own arithmetic: round 1 closed four spellings, round 2 named three, round 3 closed those three and the class is open again. If the next repair is again a spelling list, this will be round 5's verdict too. The instrument's value is the claim "the reach is the reach whatever syntax spells it"; a predicate whose domain is a prefix test has a boundary, and the boundary should be stated in `ABOUT.md`'s "What it does not see" list whichever way it is drawn.
