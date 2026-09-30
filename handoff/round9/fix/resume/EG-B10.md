# R9-EG-B10 resume — solve lifecycle (#1754, #1755)

Seat: opus fixer, high effort. Lane EG, group R9-EG-B10, class architecture,
`rca: false` — the Root-cause sections were posted on the issues by this seat.

## State (current)

- branch `handoff/r9-eg-solve-lifecycle`, worktree
  `/Users/timmalmstrom/fix-r9-eg-solve-lifecycle` (Mac).
- merge base after absorbing origin/main: `9d578722` (origin/main tip; the
  absorb brought only VERSION→6.7.11, RELEASE_NOTES, delivery rows, plan/claim
  docs — `git diff 4be53607 HEAD -- coordinator.py tests/features.py` is EMPTY,
  so the fix and the pins are byte-identical across the merge and the mutation
  proof at `4be53607` carries).
- commits: `4be53607` fix + the two failing-test blocks → `c4995d3f` merge
  origin/main → `f66f6762` structure-budget re-record (the raise).
- Both findings re-measured at the base and reproduce (C2 #1754, C1 #1755).
- features.py at the merged head: my 7 checks pass; the only FAIL is the
  pre-existing Mac-float `R9-F2.1 P3` storage-optimality arm (green in the
  hpo-ci container), present at base too. `1 of 3587 FEATURE CHECKS FAILED`.
- structure.py: `STRUCTURE RATCHET PASSED` after the re-record.
- Mutation proof COMPLETE at `4be53607` (`/tmp/eg-b10-mutation.log`): M1 delete
  re-run → #1754 re-solve check FAILS; M2 revert release identity → #1754
  O1-pinned check FAILS; M3 ignore entry key → both #1755 probe checks FAIL;
  M4 global streak reset → #1755 cap check FAILS. Each restored clean.

## The budget raise (must clear before push)

5 rows raised: coordinator_attrs 153→154, coordinator_loc 9010→9031,
coordinator_multiassigned_attrs 115→116, internal_call_edges 307→308,
max_class_loc 9031←9010. Mandate-confirmed per the orchestrator (roster rev
3.1) but OWED: post on #201 with these values + reason BEFORE the push, and the
PR requests tvofi's approving review at the head (budget-raise-gate 0013 +
code-owned). Never self-approve, never wait silently.

## Next steps

1. Derive the scoped gate (`tests/closure.py select --diff 9d578722`), run what
   `scope.run` names with `PYTHONPATH=tests/hastub`, `GOLDEN_MODE=drift` against
   the merge base; container for typing/mutation lanes (HOST-leased), stress to
   CI. Check whether `tests/closures.json` needs a re-record (no new tracked
   file; features.py already imports manual_plan — likely unchanged).
2. Post the Root-cause sections on #1754 and #1755 via
   `.claude/workflows/gh_comment.py post` (read back). Bodies:
   `/tmp/eg-b10/rca/rca-1754.md`, `rca-1755.md`.
3. Post the budget raise on #201 (values + reason) via gh_comment.py (read back).
4. Finalize the PR body (`/tmp/eg-b10/pr-body.md`): set ## Head to the final tip,
   re-stamp any figure that is a function of origin/main's tip. Run
   `tools/audit/prepr.sh <body> 1754 1755`.
5. Hand off: `tools/audit/app_push.sh tvofi/heatpump_optimizer <worktree>
   handoff/r9-eg-solve-lifecycle <body.md> 1754 1755` (this Mac holds the
   hpo-author key). The Mac adds `docs/delivery/<N>.md`; the fixer does not.
6. Watch the PR's CI to the first full conclusion (check-runs API); report every
   red to the orchestrator within minutes. Request tvofi's review at the head.

## Evidence locations

- finder harnesses + companions: `/tmp/eg-b10-evidence/` (C1.py, C2.py, rig.py
  from handoff/audit-r9-alt; C1_companion/C2_companion/rig_companion — the C2
  companion is redundant now: the contextvar lets the ORIGINAL C2 run at head).
- features runs: `/tmp/eg-b10-features-base.log` (6 FAIL: my 5 + R9-F2.1 P3),
  `-head2.log` (1 FAIL @ 4be53607), `-merged.log` (1 FAIL @ c4995d3f).
- mutation: `/tmp/eg-b10-mutation.log`, runner `/tmp/eg-b10-mutate.sh`.
- C2 head out `/tmp/eg-b10-C2-head.out` (NOTE: that file is the cdbc tree — the
  authoritative C2-at-head run is in this seat's transcript: solves ['O1','O2'],
  O1 41, O2 28).
