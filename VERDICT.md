Fix review: blocked 46cdd1f9191180fc1f420a0d5eedd0f758b947ad introduced-red: check_scopes refuses D5 seat s7 over ledger.max_units (instrument-self-tests), and tests/features.py dies on a rebound _fl_coord before this PR's block

bus-nonce: d8bf065e262eb93d3c27ca904068ed39

## Block

`python3 tools/audit/seat/merge_train.py classify 46cdd1f9191180fc1f420a0d5eedd0f758b947ad --pr 3907` exits 1: `RED 46cdd1f9191180fc1f420a0d5eedd0f758b947ad pending: gate red: none introduced: 2`, with two INTRODUCED steps of `governance / instrument-self-tests` (job 139743769465): `Show a planted owner-only canary reaching no public path of the audit pipeline` and `Show the self-tests outside tools/audit/seat/ refusing their own fixtures`. Under fix-review.md step 11 and defect-root-cause.md, an `instrument-self-tests` step that is red at the head and selected by the diff's scope belongs to this pull request and blocks it.

Both steps fail for one cause, reproduced locally at the head and absent at the merge base 8f22a3b284:
- `python3 -I tools/audit/check_scopes.py --repo .` at the head exits 1. It prints `FAIL D5 mode=cells seats=10 universe=940 [... s7:3f/0loc/4541u ...]` and `over ledger.max_units 4500: s7 holds 4541 units`. At 8f22a3b284 the same command prints `ok D5 ... universe=936 [... s7:3f/0loc/4435u ...]`. The diff adds 106 units to D5 seat s7 and 4 files to the D5 universe.
- `python3 -I tools/audit/check_scopes.py --self-test --repo .` exits 1 at the head, because its arms `null control: the live D5 and D6 pass the cap and the line`, `the default verdict passes the live scopes` and `the default invocation exits 0 on the live scopes` read False. It exits 0 at 8f22a3b284.
- `python3 -I dev/audit/harnesses/owner_only_channel.py` prints `RESULT arms=48 failed=1` and `OWNER-ONLY CHANNEL BROKEN: SCOPES null: the planned shape ... passes check_scopes` at the head, rc 1. It prints `RESULT arms=48 failed=0` and `OWNER-ONLY CHANNEL HELD` at 8f22a3b284, rc 0.

The repair is the fixer's to choose. One option is to re-cut the D5 seats in `dev/audit/config/scopes.json` so that no seat is over `ledger.max_units`. The other is to move the units out of s7's files. Whether the 106 units are this group's or those of the stacked predecessors #3805 and #3835 is not separated here. The red is at this head either way, and the body does not answer it. It is not a re-recorded budget: the cap is policy configuration and is not to be raised.

Second block, on tests: at this head the whole `tests/features.py` dies before it reaches this pull request's block. `tests/features.py:35471` defines `def _fl_coord(supply=55.0, returned=47.0, action=None, **extra)`. Main's #3866 (merged here through b0313f213a) adds a second module-level `def _fl_coord(kw=1.0, how=None, attrs=None, option=None, ...)` at `:65985`. The R11-SEAM-learners unplanned-charge block's `_uc_flow` (`:104030`) calls `_fl_coord(action=...)`. The script therefore ends in `TypeError: _fl_coord() got an unexpected keyword argument 'action'. Did you mean 'option'?`, rc 1, with no summary line (`ev/full_hm_tail.txt`; that run carried one coordinator mutant, and the crash is in a test helper whatever the mutant). #3835 repairs exactly this in 334dd1bf31 (`_fcap_coord`), but this branch merged #3835 at 7748bdc269, and `git merge-base --is-ancestor 334dd1bf31 46cdd1f919` is false. The body's figures run each block through `features_block.py` preludes, which bind the first `_fl_coord`, so they read green; its whole-script figure `ALL 6256` is from 6e6b19d039, before the merge that brought #3866. CI's `tests / fast (3.14)` and `tests / coverage` were still running when this verdict was written; they run the whole script and are owed reds. The repair is to take #3835's rename, by merging #3835's current head or cherry-picking 334dd1bf31, and then to re-run the whole script.

## Findings

- Note: unpinned-sites: the body's one surviving hand mutant (`coordinator.py` `_record_accuracy`, `Span`'s third field `heat_energy.ran_hot_water(...)` forced to `False`) is killed by the whole `tests/features.py`, by the check `a hot-water dwell under a space plan folds no running-draw sample; an all-space dwell and an unobserved interval fold one each (nulls)` (FAIL at the head with the mutant). The base rule's equivalent at d972dae309 (`and not heat_energy.ran_hot_water(...)` dropped) fails the same check (`1 of 6238 FEATURE CHECKS FAILED`). So the arm is pinned at both ends, and the body's `## Unpinned sites` entry and its own-group carry should name that check instead of an open ruling. Carry: dismissed: the site is pinned in the tree; the body entry is paperwork the fixer corrects with the repair above

## Evidence

- Head measured: 46cdd1f9191180fc1f420a0d5eedd0f758b947ad (`ev/HEAD.txt`). Merge base with origin/main: 8f22a3b2842987bf6da13dedb08c4b99b7447f1f. `git merge-tree --write-tree origin/main 46cdd1f919` exits 0, and `LEDGER-MERGE: resolved tests/closures.json` was printed. Roles drift `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Round: first review of this head. Scope: full, per the packet's `## Review scope`. The stacked predecessors #3805 and #3835 are still open and unmerged, so this PR's three-dot diff carries their code too. The review concentrated on this group's own diff `d972dae309...18849164a8` and on the sysid repair `c1d1056a0c..4041ef88b2`.
- CI: `classify` polled every 60 s. It read WAIT until 07:19:44Z, then RED with 2 introduced (`ev/classify_log.txt`, `ev/classify_poll.txt`). Owed-reds set: `ev/owed_reds.txt`.
- The approach block at the head: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude ... "R11-OUTSIDE-START-APPROACH: a run's"` reads `ALL 19 FEATURES BLOCK PASSED` (`ev/block_head.txt`), matching the body's 19.
- Hand mutants re-driven at the head, each one textual replacement in a scratch worktree, block above, unmutated control `ALL 19` (`ev/mut_C1.txt`). Every one is killed:
  - M1, the floor-ask gate in `approach.py:101`: 1 of 19 checks fail.
  - M2, median to max in `approach.py:207`: 1 of 19 fail.
  - M3, the excess max dropped in `runs.py:143`: 4 of 19 fail.
  - M4, the true-objective guard dropped in `optimizer.py:353`: 1 of 19 fail.
  - M5, the gap test in `approach.py:115`: 2 of 19 fail.
  - M6, the COP judge's approach arm in `accuracy.py:1305`: 2 of 19 fail.
  - M7, the pause test in `_entry_action` at `runs.py:326`: 1 of 19 fail.
  - M9, the p_max bound in `runs.py:189`: 1 of 19 fail.
  - Logs: `ev/mut_M*.txt`.
- M8, the sysid switch forced on in `sysid.py:2508`, is inconclusive. The R10-CEILING-PROBE block emitted this way crashed unmutated too (`TypeError` at the block's line 1616, `ev/mut_C2.txt`), so it measures nothing. The repair itself is a one-line read of `config.system_identification_enabled`, the field `arm_from_config` passes. No `SysIdConfig.enabled` reader is left in `custom_components/`, `tests/`, `tools/` or the live `dev/audit/harnesses/`. Old round-study scripts under `dev/audit/rounds/` still build `SysIdConfig(enabled=True)`; that comes from #3835 and is not gated. CI's `tests / fast` and `tests / typing` at this head are the authority for the repair.
- Security read of the new code, by an extractor read of `approach.py` in full and the stored-record paths in `draw_range.py`, `accuracy.py` and `store.py`:
  - Every stored field of `ApproachProfile.from_dict` goes through `finite_float`, `isinstance` or a negative-value filter.
  - Bins are `deque(maxlen=9)`, capped at 24 and 3 bins. `_put` bounds its index.
  - There are no `eval`, `exec`, `pickle`, `subprocess`, file or network calls, and no actuator or service call in the changed modules.
  - Finite but out-of-range clock values (for example a far-past `entered_s`) give an empty bin range and read as no profile.
  - None of this is a defect.
- Structure: `PYTHONPATH=tests/hastub python3 tests/structure.py` reads `STRUCTURE RATCHET PASSED`. Against the merge base, `tests/structure_budgets.json` only lowers (for example `class_excess_loc` 17228 -> 17222, `methods_over_200` 7 -> 6), so no budget is raised.
- Claim files: `tests/golden/claimed_drift.txt`'s three-dot diff holds only #3805's `cycling_cost` and `everything_on` claims and their may-drift suspensions. This group claims nothing. `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched.
- Not re-derived by this seat: the harness-arm figures (0.373 kWh and the 2.24/2.06/1.88/1.70 ratios), the axis grep counts, the closures counts (107 modules, 126 files, 192/561 pairs) and the architecture-score dS. CI's `arch-score` is green at this head. The `gate` and `mutation` lanes are left to CI, which classify reads as no gate red.
- Comms: seat_comms init, ckpt and inbox ran, and no command arrived.
