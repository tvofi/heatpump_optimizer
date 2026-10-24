# Fixer brief — R10-STAMP (v7.0.2 stamp preparation)

Role: `dev/governance/roles/fixer.md`. Repo `tvofi/heatpump_optimizer`. LOCAL seat, no cloud.
**Environment: `/usr/bin/git` is BROKEN on this box (missing Xcode CommandLineTools). Every Bash call must start with `export PATH=/opt/homebrew/bin:$PATH` (Homebrew git 2.38.1 works).**

## What this group owes (from the roster's carry array, read at origin/handoff/audit-r10-roster)

1. **Drop the inherited stress override and re-measure the floors.** `tests/stress_budgets.json` carries
   `coverage_floor_override` (`floor` 18, `calls_floor` 6) from R10-PUMP-MODEL-D2 (#2368). Nothing expires it at
   merge, so every later branch inherits those floors. The stamp's stress re-record must drop the override and
   re-measure the solver-work floors from the tree as it now stands (after the drain). Check: after the re-record
   `tests/stress_budgets.json` carries no `coverage_floor_override`, and `tools/policy/budget_raise_gate.py`
   reports the floors at their re-measured values with no override line. The override is one-sided
   (may only LOWER); a re-measure that RAISES a floor is a budget raise and needs the owner — measure first,
   and if the honest re-measure is higher, STOP and report rather than writing it.
2. **The #2441 ledger landing.** R10-RCA-STRUCTURE-BLIND's ledger record in `dev/audit/config/bugclasses.json`
   should name the pull request that landed the structure-blind arm. Read the record as it stands and make the
   minimum edit that makes the landing nameable; if the row as written cannot take a landing, report that rather
   than inventing a field.
3. **Leave `tests/golden/claimed_drift.txt` alone.** `tools/release/stamp.py` restores the suspended may-drift
   entries itself (`restore_suspended`); a branch edit there conflicts with the stamp. Verify the stamp would
   restore them by reading `restore_suspended` and counting the suspension notes, not by editing.

## How

- Worktree: `git -C /Users/timmalmstrom/heatpump_optimizer worktree add <ABS>/wt -B handoff/r10-stamp origin/main`
  under your absolute scratch dir; merge `origin/main` first.
- Fixer contract: failing test first, mutation proof, the finder's harness at both ends, a null control for every
  quantified claim, `GATE_SCOPE=auto`, `tests/structure.py` before the push. A budget file's numbers must be
  derived, never carried.
- Push only the handoff refs (`handoff/r10-stamp`, and `handoff-body/r10-stamp` via
  `tools/audit/seat/body_push.sh`); the orchestrator opens the pull request.

## Report

The code SHA (40 hex), the body ref SHA, the stress floors before/after with the command that measured them, the
override's removal shown by `budget_raise_gate`, and anything you could not do honestly (state it, do not fake it).
