Fix review: blocked 6fb0f76ae8f54632dc6e80fc6ca696dab104d5e0 tests-red: tests / fast (3.14) fails tests/entities.py's #1218 selection-cost note: this head's closures give 184 of the 561 pairs, tests/deployment_shape.py's note still says 182

bus-nonce: 89c90a3b37b2015f2394929b0e7aaafa

## Block

Delta round (reviewed head 19eafc0fb12c, now 6fb0f76ae8f5). The prior finding is resolved, and the code delta is sound. The head is still not mergeable: the required `tests / fast (3.14)` is red, because of this branch's own merge.

- CI run 45574230739, job 139069398309 (`ev/fast_job.log`):
  - `FAILED python3 tests/entities.py`, `1 of 2762 ENTITY CHECKS FAILED`;
  - the failing check is `and the lane's docstring records those measured numbers as the selection-cost note (#1218)`, with `missing markers -> ['184 of the 561']`;
  - `gate` reads `FAIL tests / fast (3.14): failure (this run)`.
- Cause (`ev/d308.txt`, entities.py's own pair predicate re-run on each tree's `tests/closures.json`):
  - main f52e700d and main bb6377b4 both read 182 of 561, and the note matches.
  - a83f56d8 (this branch, before its last merge) also reads 182.
  - d25757cc (the merge of main f52e700d) reads 184. The +2 pairs are `env_drift.py`/`manual_plan.py` and `golden.py`/`manual_plan.py`: they are main's closures with this PR's `flow_limit.py` added to them. The production-file count is 122.
  - `tests/deployment_shape.py`'s note still says `182 of the 561` and `all 182 among the 435`.
  - The body's step-6 re-execution ran `deployment_shape.py` and `doc_claims.py` but not `tests/entities.py`, the script that owns this marker.
- Repair: update the note in `tests/deployment_shape.py` to 184 (both places). Add a history clause: 182 on main before R11-OWNER-FLOWCAP's `flow_limit.py` joined those closures. Then re-run `tests/entities.py`. A delta reviewer judges the new head.

## Findings

- Prior finding (round 1, blocked 19eafc0fb12c, mutation-vacuous on `pump_arbiter.py:936` GUARD_OFF) is **resolved**, by 6d54e9bd:
  - the two cap lines in `_boost_ceiling_c` are deleted;
  - the docstring now points at `_map_inputs`;
  - `_map_inputs` (:997-999) still takes `min(boost_c or heat ceiling, _space_limit_c(inp) or inf)`, so the boost stays capped where it is written.

  Carry: dismissed: resolved at this head
- b4a84ed9 shortens five pump_arbiter.py docstrings to pay `module_excess_loc` after #3812. I read each one: the rule and the finding id are kept in each, and no code changed. `docs/architecture.md` now says 65 HA-free modules, which doc_claims measures. Carry: dismissed: no defect
- The new features.py edge check (8e00fd0f, 27d878ee) kills `pump_arbiter.py:1103` CMP_BOUND, and its 0.1 K arms are real null controls (below). Carry: dismissed: no defect

## Evidence

- Head reviewed: 6fb0f76ae8f54632dc6e80fc6ca696dab104d5e0 (`ev/HEAD.txt`), which `refs/pull/3866/head` matches.
  - Delta: `git diff 19eafc0fb12c 6fb0f76ae8f5` (`ev/delta.diff`). It is mostly main merges. The fixer's own commits are 6d54e9bd, 8c2c57a3, b4a84ed9, ee1abf61/7fb673f3/e813b123 (ledger pins), 8e00fd0f and 27d878ee (features.py), and a83f56d8 (closures.json resolution).
  - `git merge-tree --write-tree origin/main <head>` is clean (`ev/merge_tree.txt`).
- Harness: there is no finder's harness for this group. As in round 1, the trace is the design's "Tests the build owes" list, run as `tests/features.py` blocks through `tools/audit/seat/features_block.py` with emitted preludes (`ev/drive.sh`, `ev/muts.sh`, `ev/muts.log`):
  - block A is R11-OWNER-FLOWCAP, 12 checks;
  - block B is the `_fb_unit` boundary block, 10 checks.
- Base (head, unmutated): A rc=0, B rc=0.
- M1103 (`v >= lowest` -> `v > lowest` at :1103): B fails 1 of 10, the new edge check; A passes. The body's M13 claim is confirmed.
- MCAP, the body's M8 (`_space_limit_c(inp) or math.inf` dropped in `_map_inputs`): A fails 6 of 12, which matches the body's "6 of 12 at 6d54e9bd". The space-boost check is among the six, so the deleted cap's work is now pinned at the one live site.
- MRESTORE, the null control (the deleted round-1 lines re-added): A rc=0 and B rc=0. Nothing moves, which confirms the deleted lines were equivalent and the deletion changed no behaviour.
- The tree was restored after each mutant, and `git status` is clean.
- CI at the head, when read: codeql python, env-matrix, instrument-self-tests, browser and closures were still in progress. The red above is final for this head.
