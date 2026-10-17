Fix review: blocked 8833a1d9a47216330ba5d9e85e01a32d02691f3c class-open: a dotted chain that continues PAST the module boundary takes no edge (`_cc.<pkg>.optimizer._utc_step_starts.__call__(..)`: IMPROVES dS +0.5849, both metrics), because `_ends_chain` drops every node before the outermost and the outermost resolves past the module; and a module-level string constant bound by unpacking (`_MOD, _X = ".optimizer", 1`) is not in `tops`, so it reads IMPROVES +0.5849 too

bus-nonce: 398ffc20a896f874fff2e860cd6e8216

PR #2320, R10-ARCHSCORE-COVERAGE part 3, **round 5**. Reviewer `rev-2320`, detached worktree at the head. Contract `fix-review.md` from `origin/main` `e3f3b312f`; `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
Measured head `8833a1d9a47216330ba5d9e85e01a32d02691f3c`, re-read before posting and unchanged. Merge base `e3f3b312f`; `git diff --numstat $(git merge-base origin/main HEAD)...HEAD -- custom_components/` is empty.

**Round 4's block is closed.** Both public-leaf plants now read NULL (`price_model.py:50` and `disinfection.py:63`, re-spelled through `import custom_components`), the annotated module constant reads NULL, and every ancestor plant I filed across rounds 3 and 4 reads NULL or WORSENS. `M18` (the read arm private-only again) reopens exactly `rt_38` and `rt_39`; `M20` reopens `rt_40` alone; `M19` kills the chain-end rule's own over-fire. The function-local constant I reported is **properly dispositioned** — the body's table and `ABOUT.md` both carry it as OPEN with a stated reason. The design is sound and the boundaries are now largely stated.

Two boundaries of the same rule are not stated, and both are shippable and read IMPROVES.

## Blocking

**harness: class-open — a chain that continues past the module takes no edge.** `_ends_chain` drops every attribute that is another attribute's `value`, and the surviving outermost node has its **receiver** resolved. When the chain ends *on* a module member that is right (`_cc.<pkg>.optimizer._x` → receiver `<pkg>.optimizer` → `optimizer`). When the chain continues one step past the module, the outermost node's receiver is the module member, which resolves to nothing, and the node that would have resolved is dropped as a chain step. The body's stated rationale — "*every step before it names the same module and would take the edge again*" — is false for exactly this shape: the step does not name a module, its receiver does.

`S4`-style plant on the pin, same import, same call, one hop further (my harness `r3_classprobe.py`, named as mine; `evidence/seamhunt_r5.txt`):

| plant | spelling | verdict | dS | moved |
|---|---|---|---|---|
| `V5_deep_chain_ancestor` | `import custom_components as _cc` + `_cc.heatpump_optimizer.optimizer._utc_step_starts.__call__(..)` | **IMPROVES** | **+0.5849** | `layer_violations 3->2`, `private_cross_module 8->7` |

It is behaviour-preserving — `f.__call__(x) == f(x)` for a plain function (verified) — and it is the same runtime coupling: `silent_mode` still loads `optimizer` and reads its private `_utc_step_starts`. The same shape is natural one step over: `_cc.<pkg>.inputs.SomeClass.method(..)` loses the edge identically, because the outermost node's receiver `...inputs.SomeClass` is not a module and `...inputs` is dropped.

**A module-level string constant bound by unpacking is not in `tops`.** `_module_const` reads `mod.tops`, and `tops` is filled only from `ast.Name` targets (`common.py:275`), so `_MOD, _X = ".optimizer", 1` records nothing; `_module_const` then returns None and the dynamic import is invisible. It runs (verified):

| plant | spelling | verdict | dS |
|---|---|---|---|
| `V1_tuple_const` | `_MOD, _X = ".optimizer", 1` + `importlib.import_module(_MOD, __package__)._utc_step_starts(..)` | **IMPROVES** | **+0.5849** |

This is a **third spelling of the construct the body settles as "a module-level string constant"** (`_MOD = "..."` and `_MOD: str = "..."` are the two it names). I record it as the weaker of the two: the fix is in `metrics/common.py`'s `tops`, which other metrics share, so a **disposition row is the cheaper legitimate answer** and I would take it.

The controls that bound both: `V2_binop_const` (`_MOD = "." + "optimizer"`) also reads +0.5849, and is *dispositioned* — it is a name computed at runtime, the row that exists. `V4_computed_getattr_ancestor_private` reads **WORSENS** (`reflective_writes`, `computed_attr_access` rise), so the computed-`getattr` family is caught by other counters. `V6_fn_local_const_kw` reads +0.5849 and is dispositioned by the function-local row. So the two above are the only shippable, behaviour-preserving, IMPROVES spellings I can construct that the body neither closes nor dispositions.

**What I am not asking for.** Not another arm per spelling and not a re-cut: the relation predicate, the read resolution and the derived census are the right shape. The first seam is a one-line change to where the edge is taken (resolve the longest prefix of the chain, or take the edge on the first node whose receiver resolves to a module, rather than on the outermost node). The second is either a small `tops` change or a row in `ABOUT.md`'s "What it does not see" list — the list the function-local constant is on, which is the model of how to close a review round.

## Verified

- **Step 1, mutation proof, re-run with the tree's own attempts** on a scratch worktree of this head (`evidence/mutants_r5.txt`):
  - `M0`, no mutation: 13/13 read NULL or inadmissible — `rt_28/29/30/31/32/35/37/38/39/40` NULL, `rt_33/34/36` WORSENS. Matches the body's `## Figures` and its note that `rt_36` moved to WORSENS this round.
  - `M18`, the read arm private-only again: `IMPROVES: rt_38, rt_39` and nothing else — the body's claim, reproduced exactly.
  - `M19`, `_ends_chain` always true: `IMPROVES: none`, with `rt_29`, `rt_32` and `rt_35` moving off their recorded verdict to WORSENS (the three recorded NULL; `rt_33/34/36` were already WORSENS). Matches.
  - `M20`, `_module_const` back to `ast.Assign` only: `IMPROVES: rt_40` alone. Matches.
  - `M14`, `_namespaced` descendant-only: reopens `rt_32` to `rt_36`, plus `rt_38` and `rt_39`, leaving `rt_37`/`rt_40`. Matches.
- **Step 8, my round-3 and round-4 plants at this head** (`evidence/class_probe_r5.txt`, `evidence/public_probe_r5.txt`): every ancestor plant NULL/WORSENS (`S4` NULL, `S5` WORSENS, `T2` WORSENS, `T3` NULL, `T5` WORSENS, `S8` NULL, `U4` NULL); `price_model_public_inputs` NULL, `disinfection_public_inputs` NULL; descendant controls NULL; `T1`/`T4`/`S6`/`S9` unchanged. **The class round 4 named is closed.**
- **Step 8, the census** (`evidence/census_corpus.txt`): `corpus trees censused: 87`; the twelve absolute statement keys `0`; `read_attr:anc:public/private`, `read_attr:self:public/private`, `read_getattr:anc:*`, `read_getattr:self:*` all `0`; `from_rel:self=1590`, `from_rel:desc=7330`, `read_attr:desc:public=13271`, `read_attr:desc:private=175`, `dynamic:positional=30`, `dynamic:computed=58`, `guard:body=90`, `guard:else=58`, `unkeyed=0`; all 36 derived keys planted `>= 1`, `planted_unkeyed=0`, and with the statement arm dropped `223` unkeyed. Exact match with the body. The read keys and the planted tree are generated from the same tables as the classifier.
- **Step 8, the three new attempts at both ends**: at `e6a9720b8` with the scripts copied in, `+0.4150 / +0.4150 / +0.5849`; at this head NULL each. Reproduced.
- **Step 14.** `ci_ratchet.archscore_metrics()` derives `22 / 17 / 1` == the three rows, `hub_solve_writes` 41; `expected.json` this round is 19 insertions, 1 deletion (the `rt_36` re-record the body discloses); `score.py --diff <merge-base> HEAD` = `dS +0.0000 NULL`; `tests/structure.py` -> `STRUCTURE RATCHET PASSED`; `VERSION`, the manifest version, `RELEASE_NOTES.md` and both claim files untouched; `env_drift.py --claims-only e3f3b312f` -> `claims hygiene: ... ok`.
- **Step 10, forward-carry.** `dev/programme/rosters/wave-r10-groups.json` at `origin/handoff/audit-r10-roster` (`e3f2468c6`, PR #2343) carries the part-3 entry in `R10-BRIEFS-FOLD`; the body's `## Forward-carry` names that file and group. Not yet on `origin/main` — the orchestrator's sequencing.
- **Step 11.** 45 check-runs at this head, all concluded: 29 success, 15 skipped, **1 failure** (`coverage-ratchet`), named and answered in `## Red checks`; the diff touches no `custom_components/` file. `pr-contract` is green. The prior rounds' `closures`, `budget-raise-gate` and `entities` readings are green here.
- **Step 13.** `git merge-tree --write-tree origin/main HEAD` exits 0, no `MERGE-CLAIM` marker: no conflict.
- **Disclosed as mine, not the finder's**: `r3_classprobe.py`, `r4_publicprobe.py`, `r4_mut.py`, `r5_mut.py`. `calibrate.py` and the census are the tree's own, run unchanged; CI's heavy lanes are cited, not re-run.

## RESULT lines

    RESULT head 8833a1d9a47216330ba5d9e85e01a32d02691f3c measured; unchanged at post
    RESULT round4_plants_closed price_model_public_inputs=NULL disinfection_public_inputs=NULL AnnAssign_const=NULL; all ancestor plants NULL/WORSENS
    RESULT mutation M0=13/13 NULL-or-inadmissible; M18 reopens 38+39 only; M19 none (29/32/35 -> WORSENS); M20 reopens 40 only; M14 reopens 32-36+38+39
    RESULT class_open deep_chain V5_deep_chain_ancestor=+0.5849 IMPROVES (layer_violations 3->2, private_cross_module 8->7); f.__call__ verified behaviour-preserving
    RESULT class_open tuple_const V1_tuple_const=+0.5849 IMPROVES; runs; _MOD is absent from common.tops
    RESULT class_open controls V2_binop=+0.5849 (dispositioned: computed); V4_computed_getattr=WORSENS; V6_fn_local=+0.5849 (dispositioned)
    RESULT census 87 trees; twelve statement keys 0; read_attr/read_getattr anc+self all 0; from_rel:self=1590 from_rel:desc=7330 read_attr:desc:public=13271 read_attr:desc:private=175 dynamic:positional=30 dynamic:computed=58 guard:body=90 guard:else=58 unkeyed=0; 36 planted keys >=1; dropped arm 223 unkeyed
    RESULT ci_ratchet derived 22 / 17 / 1 == the rows, hub_solve_writes 41; expected.json 19 insertions 1 deletion; structure PASSED; score +0.0000 NULL; env_drift claims ok
    RESULT merge_tree rc=0
    RESULT head check-runs 45 concluded: 29 success, 15 skipped, 1 failure (coverage-ratchet, named in ## Red checks); pr-contract green
    RESULT forward_carry present at origin/handoff/audit-r10-roster e3f2468c6 (PR #2343) R10-BRIEFS-FOLD

## Friction

- Round 5 is a genuine re-cut and the design is right; the two seams above are boundaries of a finite static reader, not missing arms. If the next seat judges them out of scope, the contract's other exit is a row in the body's table and `ABOUT.md`'s "What it does not see" list — which is what the function-local constant got, and that row is why I am not blocking on it.
- The body's `## The rule` bullet 1 still says it follows "every **private** read that resolves to one of its modules through such an import", while bullet 3 and the table make the edge public-or-private. A one-word correction, noted because a later reader who quotes bullet 1 would carry the round-4 defect forward.
