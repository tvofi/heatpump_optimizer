Fix review: blocked 7afd9452b7ac703bfa9f6ef88033120189d39d4b structure-breach: seam_cut_total 424 > 418 at the head, which already contains origin/main 662a3809c; round 3's block is unpaid (also carry-missing, see Block)

bus-nonce: f47ec3e295950be772e72a63d2e79164

Review round 4 for #2712. Three earlier `Fix review:` verdicts blocked 5fb0a083b, a126c8b3f and f0a975b0a. By `fixer.md`, a fourth round owes a re-cut, not a repair. I measured head 7afd9452b7ac703bfa9f6ef88033120189d39d4b. `git ls-remote` showed it as the PR head at review time (`ev/HEAD.txt`). I read fix-review.md from origin/main 662a3809c, and its roles diff against the merge base is empty. Each mutant ran in its own fresh detached worktree at the head.

## Block

- **structure-breach: the round-3 block is unpaid.** origin/main 662a3809c is an ancestor of this head, so the head is the merge. `git merge-tree --write-tree origin/main <head>` exits 0 (`ev/merge_tree.txt`). Results of `python3 tests/structure.py`:
  - At the head: `FAIL seam_cut_total 424 > 418 (+6)` and `1 STRUCTURE BUDGET(S) BREACHED`, rc=1. Helpers charged: 20. Internal calls crossing a seam: 178 (`ev/structure_head.txt`).
  - At origin/main: `ok seam_cut_total 420 <= 420` and `STRUCTURE RATCHET PASSED`. Helpers charged: 19 (`ev/structure_origin_main.txt`).
  - The head's `tests/structure_budgets.json` records `seam_cut_total: 418`. That value is main's 420 minus the diff's old-definition delta of -2. Under main's definition (86d4dba1c, #2711), the diff adds +4: the new `_track_dhw` helper plus its crossings. Round 3 established the same.
  - Since f0a975b0a, nothing has moved in `custom_components`, `tests/features.py`, `tests/mutation_ledger`, `tests/seam_map.json` or the budget row, apart from main's own merges (`ev/delta_since_round3.txt`). Nothing was paid, and there is no raise with the owner's prior confirmation.
  - This head cannot merge: its own structure ratchet is red. Repair: pay the +6, or get an owner-confirmed raise (CLAUDE.md rule 2).
- **carry-missing (step 10).** The body at this head is a stale text. Its Carry markers do not match what the roster holds (`ev/carries.txt`, `handoff/audit-r10-roster` at 2124781cf, `wave-r10-groups.json`):
  - `Optimality ... Carry: R10-COP-PARTLOAD` and `dhw_temp_trajectory ... Carry: R10-HEAT-METER`: those groups hold 0 carries from r10-demand-overbook. Both items sit in R10-BUFFER-STORE. This is review round 1's `carry-missing: not carried to R10-COP-PARTLOAD, R10-HEAT-METER`, returned.
  - Both `## Friction` items (R10-FIXER-DISPATCH-REF and R10-HARNESS-COPY-NAME) carry to R10-ORCH-MACHINERY. That group is at stage `absorbed` and holds neither, the same dead-destination defect round 3 blocked on.
  - Round 3's R10-PREPR-UNPINNED-RED friction item is gone from the body. It was not routed to a live group, and the body names no roster SHA.
  - Repair: point each Carry at the group that holds it, carry the friction items to a live group, and cite the roster SHA.

## Findings

- The body's figures and its `## Head` are stale against this head. It quotes `ALL 4367 FEATURE CHECKS PASSED`; the head prints `ALL 4369` (`ev/features_head.txt`). It describes the head as the merge of 1193fd228 and 662a3809c, and states "Nothing is raised" and `STRUCTURE RATCHET PASSED`. The last is false at this head. Carry: R10-DEMAND-OVERBOOK
- The `killed_by` reason on `running_kw.CMP_BOUND.5f36889b` says `rc=1 failed=2`. The mutant fails 1 check (`ev/mutants/cmp.txt`), as rounds 2 and 3 also found. Carry: R10-DEMAND-OVERBOOK
- The body is still a repair-round body at r4, where `fixer.md` owes a re-cut from the fourth round. Carry: R10-DEMAND-OVERBOOK

## Evidence

- RESULT seam_cut_total head=424 budget=418 main=420 (`ev/structure_head.txt`, `ev/structure_origin_main.txt`).
- Add/add resolution (brief). The head's `tests/mutation_ledger/killed_by/draw_range.py/running_kw.CMP_BOUND.5f36889b.json` names `killed_by: tests/features.py` (`ev/cmp_bound_pin.txt`). Its mutant (`drawn_kw > floor` -> `drawn_kw >= floor`, draw_range.py:296) takes `PYTHONPATH=tests/hastub python3 tests/features.py` from `ALL 4369 FEATURE CHECKS PASSED` rc=0 to `1 of 4369 FEATURE CHECKS FAILED` rc=1, `FAIL #2499: a draw at the running floor is standby, not heat`. The named test really kills it as a value check.
- RESULT mutation, re-run at this head (`ev/mutants/SUMMARY.txt`):
  - M3 `shared=False` (coordinator.py:1005): `1 of 4369` rc=1, the immersion-latch check `[slab=24.170]`.
  - M4 `space_served=True` (coordinator.py:1006): `1 of 4369` rc=1, the hot-water-only check `[slab dhw-only/off=24.170/22.840 ...]`.
  - Null control, a comment on line 1006: `ALL 4369 FEATURE CHECKS PASSED` rc=0.
  - M1, M2 and M5 I did not re-run. Production code and `tests/features.py` are byte-identical to f0a975b0a (`ev/delta_since_round3.txt`), where round 3 killed all five named sites with the null control. Those three results are cited from round 3, not re-taken.
- Harness figures (step 2). I did not re-run `dev/audit/harnesses/r10_demand_overbook.py`, so the `## Figures` table is not verified at this head. Production is unchanged since review round 1, which verified directions only. The harness is the fixer's own instrument, as the body discloses (step 9).
- Architecture (step 15). Not re-run. Production is unchanged since round 3, which printed `dS +0.3249 WORSENS (inadmissible: coord_footprint 2463->2465)`, matching the body.
- CI (step 11). On this head, `prelude`, `refresh` and `cancel-superseded` (two runs each) were `queued`, and `arm` was skipped. Nothing had concluded, so I could not judge the red-check trigger. The structure ratchet, which is a gate script, will go red here (see Block).
- Versions (step 5). The diff leaves `VERSION`, the manifest and `RELEASE_NOTES.md` untouched against merge base 662a3809c (they do not appear in `git diff --stat`). The claim files are untouched too.
