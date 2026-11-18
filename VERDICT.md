Fix review: blocked 007e7be48d0fcfe5c01c9bafb920f0c34c67d12a mutation-vacuous: draw_range.fold commit_runs(keep=not (frozen or distorted)) -> keep=True, keep=not distorted, keep=not frozen all survive

bus-nonce: dd9ab610bd427b39ab355d785165d896

## Block

- `custom_components/heatpump_optimizer/draw_range.py`, `fold`: the added line `draw.map.commit_runs(keep=not (frozen or distorted))` is the only place that stops a frozen or distorted interval's closed runs from becoming map rows. That exclusion is stated in `fold`'s docstring and in `MapRows`, and block A has a check named for it ("a frozen or distorted interval commits none"). That check calls `MapRows.commit_runs(False)` directly (tests/features.py:97022), not through `fold`, so nothing tests how `fold` wires `keep`. Three mutants of this line survive:
  - `keep=True`: block A 32 of 32 pass (ev/mutants_blockA.txt, M9). The full scoped closure under this mutant (`closure.py select --diff HEAD`, `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`) has every script exit 0, including `tests/features.py` (`ALL 5933 FEATURE CHECKS PASSED`) (ev/m9_closure_rc.txt, ev/m9_features_tail.txt, ev/m9_mutant.diff). `card.mjs` and `card_drift.mjs` first exited 1 only because the parallel run started them before `plan_view.py` had written its payload; run again after it, both exit 0.
  - `keep=not distorted` (frozen ignored): block A 32 of 32 pass (ev/mutants_fold_keep.txt, M9c).
  - `keep=not frozen` (distorted ignored): block A 32 of 32 pass (ev/mutants_fold_keep.txt, M9d).
  - Only `keep=False` is killed, by the window-null check's "rows were kept" precondition (M9b).
  - With any survivor in place, runs held during a frozen interval (a supply hold's freeze, a stale meter) or a distorted one become map rows. Map rows are the evidence part B's sweep fit reads. The `## Unpinned sites` list (from `ci_predict.py`) does not name this line, so CI's `tests / mutation` lane will not draw it either.
  - Owed: a check that goes through `fold` with `frozen=True` and with `distorted=True` (each alone) after a closed space run, and asserts no row is added; a control without either flag adds one.

## Findings

none beyond the block.

## Evidence

- Round: first review of this PR (no reviewed head).
- Head: `007e7be48d0fcfe5c01c9bafb920f0c34c67d12a` is still `refs/pull/3737/head` at verdict time; the body's head section names it. Merge base is 9fe63d00b59f100aea67267ddddc95522e164aa1. `git merge-tree --write-tree origin/main <head>` exits 0, so it merges cleanly.
- Block A at the head: `ALL 32 FEATURES BLOCK PASSED` (ev/blockA_head.txt).
- The body's mutation proof reproduces: `owed_scale(..., True)` fails 1 of 32, the dither's first experiment cycle (M1).
- Targeted mutants on the other added lines, all killed by block A (ev/mutants_blockA.txt):
  - the `judge_floor` experiment guard (6 fail);
  - the caller dropping `experiment` (5);
  - `experiment=False` (5);
  - `owed_scale` ignoring `read` (1);
  - `ArbiterInputs.draw` dropped (1);
  - action `kind` dropped (1);
  - the `_note_pass` call dropped (1);
  - the space-only filter (2);
  - persist and restore of map rows (KeyError; 4);
  - probe-origin collapse (1);
  - the settle filter (5);
  - the stopped-close (1);
  - the 30-minute close (1);
  - the boost origin (1);
  - the unequal-column guard (1).
- The harness's figures match the body at the head. `dev/audit/harnesses/draw_map_rows.py` has sha1 057455db8d886d3b112e0c43a2b422d3de37e220 and prints `store rows=672 ... added_bytes=58058`, `open_loop gain_kw_per_k=0.300 offset_kw=0.400`, and a shuffled null of `gain_kw_per_k=0.023` (ev/harness_head.txt). At the base it stops with `AttributeError: 'DrawRange' object has no attribute 'map'` (ev/harness_base.txt), as the body says. This harness was built by the fixer (it is in the diff), not taken from the finder.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`, `seam_cut_total 413 <= 413`. The budget moves down (415 -> 413), earned by `_dhw_current_hour` moving out of the coordinator class.
- The diff leaves both claim files and `VERSION`, the manifest and `RELEASE_NOTES.md` untouched.
- Sibling seams, re-run under the body's rules:
  - `git grep -n "judge_floor("` returns `coordinator.py:1199`, the heat-counter span close, guarded by `close.refusal`. The body dispositions it, and block A's check "a heat counter span holding an experiment cycle folds no COP" passes.
  - `git grep -n "owed_scale("` also returns `accuracy.py:1088`, `ScaleProbe.owed_scale`, the delegate. It already takes `read` and is not a separate seam.
- Forward-carries: all five name `R11-CARRY-DRAWMAP` parts B and F, which the approved note splits off, so they fall under fixer.md's split-part exception. carry_audit at the head: 5 routed, 0 unrouted.
- CI: `merge_train.py classify ... --pr 3737` read `WAIT ... pending: gate red: none` on every run from 15:39 to 16:02 UTC (scratch poll log). This does not affect the block.
- Red checks: none at this head.
