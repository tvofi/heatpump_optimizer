Fix review: blocked e6a9720b8cd5a3f75d11b62be28a326633166c06 class-open: the edge an ancestor import needs is added only by the PRIVATE-read arm, so a PUBLIC read through `import custom_components as _cc` takes no edge and a pure module's `layer_violations` is droppable by re-spelling a public higher-layer import (`price_model.py:50`, `disinfection.py:63`: IMPROVES dS +0.4150 each, behaviour unchanged)

bus-nonce: b7fa5985578bba3379e8a3131d986382

PR #2320, R10-ARCHSCORE-COVERAGE part 3, **round 4** (the fifth review of this pull request). Reviewer `rev-2320`, detached worktree at the head. Contract `fix-review.md` from `origin/main` `e3f3b312f`; `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
Measured head `e6a9720b8cd5a3f75d11b62be28a326633166c06`, re-read before posting and unchanged. Merge base `e3f3b312f`; `git diff --numstat $(git merge-base origin/main HEAD)...HEAD -- custom_components/` is empty.

**Round 3's block is closed.** The five plants I filed — `import custom_components as _cc` + dotted private read, `from custom_components import heatpump_optimizer` (plain and aliased) + dotted read, `import custom_components` + full dotted read, and the `getattr` chain — now read NULL, WORSENS, WORSENS, NULL, NULL. The eleven attempts 28-37 read NULL or inadmissible. `M14` (`_namespaced` descendant-only) reopens exactly the ancestor family and nothing else. `M16` reopens `rt_37` alone. `carry-missing` stays addressed.

The block below is a different seam, in the predicate that closed the ancestor direction rather than in its domain.

## Blocking

**harness: class-open — a public read through an ancestor import takes no edge.** The body states the mechanism it relies on: "*A read that resolves to a module takes that module's EDGE as well as its crossing -- which is what an import of an ancestor needs, since that statement alone loads no module of ours*" (`## The rule`). In `graph()` the only arm that can give the ancestor statement an edge is

    elif PRIVATE_ATTRS and isinstance(n, ast.Attribute) and _private(n.attr) \
            and (t := _reached(pkg, modalias, m, n.value)) is not None:
        cross(m, t, n.attr)

and it requires `_private(n.attr)`. The `ast.Import` and `_from_names` arms cannot supply it — `_pkg_module(pkg, "custom_components")` is None, `_relative("custom_components")` is None — which is exactly why the read arm was given the edge. So the edge exists only when the leaf name is private, and a **public** leaf read off the ancestor chain yields neither an edge nor a crossing. `layer_violations` is the metric about layers, not about privates, so it is the one that falls.

Two plants, **behaviour-preserving**: the same names, the same calls, only the import statement moves (my harness `r4_publicprobe.py`, named as mine, not the finder's; `evidence/public_probe_r4.txt`):

| plant | change | verdict | dS | moved |
|---|---|---|---|---|
| `price_model.py:50` | `from .inputs import normalize_price_per_kwh` -> `import custom_components as _cc` + `_cc.heatpump_optimizer.inputs.normalize_price_per_kwh(..)` | **IMPROVES** | **+0.4150** | `layer_violations 3->2` |
| `disinfection.py:63` | `from .inputs import UNBOUNDED, parse_bool` -> the same, both reads re-spelled | **IMPROVES** | **+0.4150** | `layer_violations 3->2` |

`inputs` is glue (rank 2) and both modules are pure (rank 0): each keeps its `(0 -> 2)` violation in fact and loses it in the metric. Both plants keep the module unable to load without Home Assistant.

**The controls separate the ancestor direction from the public leaf.** The *same* re-spelling through the descendant is NULL in both forms — `import custom_components.heatpump_optimizer.inputs` + the full dotted public read, and `from custom_components.heatpump_optimizer import inputs` + `inputs.*`: `verdict=NULL dS=+0.0000` each. So the ancestor statement is the seam, not the public name; the descendant spellings take their edge from the statement, which is the arm the ancestor spelling has no analogue of.

**Behaviour is unchanged, not argued.** `inputs` is loaded as an attribute of the package by `coordinator.py:316`, `disinfection.py`, `pump_arbiter.py` and `setpoint_check.py`, and the re-spelled read is a call-time read, so `_cc.heatpump_optimizer.inputs` resolves. The same attribute argument round 4 accepted for its own ancestor attempts.

**Why the attempt set does not carry it.** The body names the attempt set as the rule's enumerator (`Step 8's enumeration. The rule's enumerator is the attempt set`), and every ancestor attempt spells its read with the private `_utc_step_starts` — `32_layer_parent_ns_alias.py` and its four siblings. The body's own table spells the ancestor rows `_cc.<pkg>.optimizer._x`, a private leaf; `ABOUT.md`'s "What it does not see" list names no public-leaf form; and the word "public" does not appear anywhere in this round's diff of `layering.py`, the census or `ABOUT.md`. Nothing in the diff or the body dispositions it.

**A repair hint I measured, offered as a probe and not as the fix.** Dropping the `_private` guard from that arm closes both plants (`NULL`), but over-fires: the intermediate nodes of a dotted chain then take edges too, so `rt_32` to `rt_35` read `WORSENS layer_violations 3->4` (my `M18` probe, `evidence/repair_probe_M18.txt`). The edge has to be added for the node the chain *ends* on, with the crossing staying private-only. Stated so the next seat does not read "remove the guard" as the repair.

**A second boundary of the same round's predicate: `_module_const` reads only `ast.Assign`.**

- `_MOD: str = ".optimizer"` at module level, then `importlib.import_module(_MOD, __package__)._utc_step_starts(..)`: **IMPROVES +0.5849**, and it runs (verified against a stand-in package). `common.py:275` already records the annotated node — `tops.setdefault(t.id, node)` with `getattr(node, "target", None)` stores the `AnnAssign` — so `_module_const`'s `isinstance(assign, ast.Assign)` is the only thing refusing it. This is the construct the body and `ABOUT.md` settled in round 4 ("*a name held by a module-level string constant is NOT in this list: it is statically readable*"), the same construct with a type annotation.
- A function-local constant (`_M = ".optimizer"` inside the function) also reads **IMPROVES +0.5849**; `tops` is built from the module body only (`common.py:270`). Reported for completeness: a seat writes that constant at module level.

**And the census cannot see this seam.** Its keys are the node's slot crossed with the name's relation, and the node families it keys are `ast.Import`, `ast.ImportFrom`, the dynamic call and the `If` test. An attribute read is none of them, so `touches`/`unkeyed` never fires for a read-side seam: the control round 4 added refuses a *statement* the classifier has no key for, which is where rounds 2 and 3's seams were, not where this one is.

## Verified

- **Step 1, mutation proof, re-run with the tree's own attempts** on a scratch worktree of this head (`evidence/mutants_r4.txt`):
  - `M0`, no mutation: `rt_32` NULL, `rt_33` WORSENS, `rt_34` WORSENS, `rt_35` NULL, `rt_36` NULL, `rt_37` NULL — the body's `## Figures` line exactly.
  - `M14`, `_namespaced` back to the descendant direction only: reopens `rt_32`, `rt_33`, `rt_34`, `rt_35`, `rt_36` at `+0.5849` (`layer_violations +0.415`, `private_cross_module +0.170`), `rt_37` NULL — the body's claim, arm for arm.
  - `M16`, `_module_const` returns None: reopens `rt_37` alone. Matches.
  Each mutant moves only the attempts the body names.
- **Step 8, round 3's five plants at this head** (my `r3_classprobe.py`, the same scripts I filed the round-3 block with, `evidence/class_probe_r4.txt`): `S4` NULL, `S5` WORSENS, `T2` WORSENS, `T3` NULL, `T5` NULL — matching the body's NULL/WORSENS/WORSENS/NULL/NULL/NULL for `rt_32` to `rt_36`. `S8` (module-level constant) NULL, the round-3 attempts 28-31 NULL, `T1`/`T4`/`S6`/`S9` unchanged. **The ancestor direction is closed.**
- **Step 8, the census figures** (`evidence/census_corpus.txt`): `corpus trees censused: 87`; the twelve absolute statement keys all `0`; `from_rel:self=1590`, `from_rel:desc=7330`, `from_rel_as:self=279`, `from_rel_as:desc=463`, `dynamic:positional=30`, `dynamic:computed=58`, `guard:body=90`, `guard:else=58`, `unkeyed=0`; planted every derived key `>= 1`, `planted_unkeyed=0`, and with the statement arm dropped `211` unkeyed. Exact match with the body. The keys are genuinely derived (SLOTS x RELATIONS), and the planted tree is generated from the same table.
- **Step 8, the six attempts at both ends**: at `aef20e8e9` with the six scripts `+0.5849` each; at this head NULL, WORSENS, WORSENS, NULL, NULL, NULL. Reproduced.
- **Step 14, no number the diff moves is the instrument's.** `ci_ratchet.archscore_metrics()` derives `22 / 17 / 1` == the three rows, `hub_solve_writes` 41 unmoved; `expected.json` this round is 36 insertions, 0 deletions; `score.py --diff <merge-base> HEAD` = `dS +0.0000 NULL`; `tests/structure.py` -> `STRUCTURE RATCHET PASSED`; `VERSION`, the manifest version, `RELEASE_NOTES.md` and both claim files untouched; `env_drift.py --claims-only e3f3b312f` -> `claims hygiene: ... ok`. The raise justification is unchanged from round 3 and no row moves.
- **Step 10, forward-carry.** `dev/programme/rosters/wave-r10-groups.json` at `origin/handoff/audit-r10-roster` (`e3f2468c6` = PR #2343's head): `R10-BRIEFS-FOLD`'s `carry[3]` is the part-3 carry, with the measurements and the re-measure instruction; the body's `## Forward-carry` names that file and group. Not yet on `origin/main` — #2343 is the orchestrator's sequencing.
- **Step 11.** 45 check-runs at this head, all concluded: 29 success, 15 skipped, **1 failure** (`coverage-ratchet`, `117258039041`), named and answered in `## Red checks`; `git diff --numstat <merge-base>...HEAD -- custom_components/` is empty. `closures` concluded green, as did `arch-score`, `mutation`, `coverage`, `fast (3.14)`, `composed-proof` and `budget-raise-gate`. `pr-contract` concluded **green** on a run started after the last red concluded, so the body contract holds at this head.
- **Step 13.** `git merge-tree --write-tree origin/main HEAD` exits 0 with no `MERGE-CLAIM` marker: no conflict.
- **Disclosed as mine, not the finder's**: `r3_classprobe.py`, `r4_publicprobe.py`, `r4_mut.py`. `calibrate.py` and the census are the tree's own, run unchanged; CI's heavy lanes are cited, not re-run.

## RESULT lines

    RESULT head e6a9720b8cd5a3f75d11b62be28a326633166c06 measured; unchanged at post
    RESULT round3_plants_closed S4=NULL S5=WORSENS T2=WORSENS T3=NULL T5=NULL S8=NULL (ancestor direction closed)
    RESULT mutation M0={32 NULL,33 WORSENS,34 WORSENS,35 NULL,36 NULL,37 NULL}; M14 reopens 32-36 at +0.5849; M16 reopens 37 alone
    RESULT class_open public_read_ancestor price_model_public_inputs=+0.4150 IMPROVES disinfection_public_inputs=+0.4150 IMPROVES (layer_violations 3->2)
    RESULT class_open controls desc_plain=NULL desc_from=NULL (the ancestor statement is the seam, not the public leaf)
    RESULT class_open module_const_boundary annassign_const=+0.5849 IMPROVES; fn_local_const=+0.5849 IMPROVES
    RESULT repair_probe M18 drops the private guard: both public plants NULL, but rt_32..rt_35 WORSENS 3->4
    RESULT census 87 trees; twelve absolute statement keys 0; from_rel:self=1590 from_rel:desc=7330 from_rel_as:self=279 from_rel_as:desc=463 dynamic:positional=30 dynamic:computed=58 guard:body=90 guard:else=58 unkeyed=0; planted all >=1; dropped arm 211 unkeyed
    RESULT attempts at aef20e8e9 = +0.5849 each; at this head NULL/WORSENS/WORSENS/NULL/NULL/NULL
    RESULT ci_ratchet derived 22 / 17 / 1 == the rows, hub_solve_writes 41; expected.json 36 insertions 0 deletions; structure PASSED; env_drift claims ok
    RESULT merge_tree rc=0
    RESULT head check-runs 45 concluded: 29 success, 15 skipped, 1 failure (coverage-ratchet, named in ## Red checks); pr-contract green
    RESULT forward_carry present at origin/handoff/audit-r10-roster e3f2468c6 (PR #2343) R10-BRIEFS-FOLD carry[3]

## Friction

- **This is round 4 and a re-cut is owed, not another arm** (`fix-review.md`: from the fourth, `fixer.md` owes a re-cut). The ancestor direction is closed and the predicate is genuinely general for statements; the seam that survives is in how the read arm was attached to it, and the round-4 body's own sentence about that attachment is false for public leaves. A fifth spelling list would not reach it.
- The block grammar names a seam, and two rounds running the seam has been a predicate's *interior* rather than a missing arm: round 3's was a predicate's domain, this one is which arm a rule hangs off. Both were found by planting the rule's own kind of move, not by reading the diff.
- `fix-review.md` step 6's "a body whose rule returns nothing is a body whose class is one seam" does not cover this shape: the rule returns a large population (every read that resolves to a module) and the *implementation* covers a subset of it. A reviewer keying on the enumerated attempt set alone would read the round as closed.
