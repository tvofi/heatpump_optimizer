Fix review: merge 49a45dd8a8aad27f63b797bc747e79d9246e439a

bus-nonce: 03a1b574d029ce9b62c259f453768c0d

## Scope

Delta review (fix-review.md step 12) of handoff r10-outside-disinfection-setpoint, group R10-OUTSIDE-DISINFECTION-SETPOINT, from the merge verdict at 1713468b91e6d7fb1345ad391b03213df1148ce9 to 49a45dd8a8aad27f63b797bc747e79d9246e439a. `review_carry.py 1713468b 49a45dd8` prints FRESH-REVIEW (a main merge sits in the range), so the review covers the merge resolution 340c426e0 (`git show --remerge-diff`), the three commits after it (b8736ad3, 1aa850c2, 49a45dd8), and the three-dot diff against origin/main cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf, which is also the merge base. Measured from a detached worktree at the head; ev/HEAD.txt names it. Round: second review of this handoff (a delta round, so no re-cut is owed).

## Evidence

- Head: 49a45dd8a8aad27f63b797bc747e79d9246e439a, the head BODY.md names under `## Head`; it was re-read before return. No pull request exists yet, so there is no review packet, no check runs to read and no CI to wait on. Step 11 (red checks) cannot be judged against live runs and is left to the PR's own checks.
- Merge with main: `git merge-tree --write-tree origin/main HEAD` gave rc=0 (ev/merge_tree.txt), and origin/main is the merge base: no conflict.
- Merge resolution (ev: remerge-diff read inline). `thermal_model.py` `dhw_hard_max_temp`: main's `min(70, max(sp, leg) if legionella_cycle_active else sp)` and the group's `min(70, sp if dhw_cycle_temp is None else dhw_cycle_temp)`, with `dhw_cycle_temp = max(sp, dhw_disinfection_temp)` and `dhw_disinfection_temp = leg if legionella_cycle_active else None`, are algebraically identical, so #3398's ceiling is kept. `setpoint_check.py` `_dhw_floor`: `max(floor, disinfection)` where not None equals main's `legionella_cycle_active` branch, so both behaviours are kept. The three `tests/features.py` fakes now use a real `ThermalParameters` (`_r9f12_tp`), from which `legionella_cycle_active` derives. After the merge, the remaining `.dhw_legionella_enabled` readers in custom_components are the predicate itself (thermal_model.py:327) and the coordinator diagnostics echo (coordinator.py:7933). Neither acts on the cycle's temperature.
- Mutation harness at the head: `python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py` gave rc=0. NULL SURVIVED, and M1 through M10 were all KILLED, including M10-enabled-not-active, the resolution reverted to `dhw_legionella_enabled` (ev/mutants.txt).
- RESULT block_duty head: `tests/block_duty.py` passed 62 of 62, rc=0 (ev/block_duty.txt).
- RESULT block_duty failing-first: the head's `tests/block_duty.py` run in an origin/main cbd23f1c worktree failed 9 of 62 (rc=1), including both faces named in the body. No `null control:` check fails there (ev/block_duty_at_main.txt).
- RESULT null control: harness `dev/audit/harnesses/r10_disinfection_setpoint.py` (sha1 276cb8cf1d68e145cb169db474825d317319d5e0, the body's sha) run at origin/main and at the head. All 80 `null_*` lines are IDENTICAL, and 36 of the 40 `stock`/`offstep` lines changed (ev/harness_base.txt, ev/harness_wt.txt). This matches the body. The harness is this PR's, as the body says (the fixer's own, disclosed).
- `tests/structure.py` at the head: rc=0, STRUCTURE RATCHET PASSED (ev/structure.txt). `class_excess_loc` measures 17531 at the head, 17534 at origin/main (ev/structure_at_main.txt) and 17534 at 1713468b (ev/structure_at_1713468b.txt). The 3-line drop therefore comes from the merge resolution itself: the group's shorter form replaced main's duplicated predicate lines in `ThermalParameters`. It is not "main's own reduction", as commit 1aa850c2's message words it. The move is downward and earned by the resolution, so this is a wording inaccuracy and does not block.
- Ledger commit 49a45dd8: the two deleted killed_by pins anchor `old` lines (`if params.legionella_cycle_active:`, `if self.legionella_cycle_active:`) that no longer exist at the head. `python3 tools/pr/ci_predict.py` at the head gave rc=0 with no STALE PIN, 11 ADDED UNPINNED sites (the same 11 the body lists under `## Unpinned sites`), and "no closures, fast, governance or instrument red predicted" (ev/ci_predict.txt).
- Architecture score: `score.py --diff <merge-base>` printed `Architecture score: dS +0.0023 IMPROVES`, which matches the body (ev/archscore.txt).
- Claims and versions: the three-dot diff touches neither `VERSION`, nor the manifest, nor `RELEASE_NOTES.md`, nor either claim file.
- Inherited red: the vendor-regex census (`alpha.?innotec|mfs ?[0-9]|luxtronik`) over package Python counts 6 lines at origin/main and 6 at the head, against `_CB_VENDOR_BASE = 4` (tests/features.py:12387). The red is main's and this diff adds none of it.
- RESULT features head: `PYTHONPATH=tests/hastub python3 tests/features.py` failed 1 of 5237 checks (rc=1). The one failure is the `combi_type_branch census` vendor clause, which is the inherited main red above. The checks that use the three resolved fakes pass (ev/features.txt). This matches the body's figure.
- Owed-reds set as printed (ev/owed_reds.txt). With no PR there are no runs to read against it.

## Findings

none
