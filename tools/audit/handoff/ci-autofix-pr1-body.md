<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: a branch that inherited main's claim list, or whose scoped test script read a file its committed closure does not list, was pushed as it stood. `fast` went red on INHERITED CLAIMS or `closures` went red on UNDER-SCOPED, and `claims-autofix` or `closures-autofix` then pushed the repair. Each repair cost a gate run, a held-run approval, and a bot commit on a head a reviewer may already have been reading.

After: `tools/audit/prepr.sh`, which `app_push.sh` runs before anything reaches the remote, refuses both. It prints the repair for the refusal it found, the same repair the bot would push.

The census behind this (every failed run in the week to 2026-09-24, classified per job) is in the project's `ci-autofix/ANALYSIS.md`.

How:
- **Step 6a** runs `env_drift.py --claims-only` with CI's own arguments: the merge base with `origin/main`, and the head as `CLAIM_HEAD`. So the claim list is compared with its own fork point, not main's tip. The remedy follows the refusal: `--drop-inherited <base>` for INHERITED CLAIMS, and restoring the files for RECORD PR CLAIMS.
- **Step 6b** derives the scope with `closure.py affected` over the three-dot diff, as the `closures` job does. It records each scoped script with `derive_closures.sh --single --record-only`, so the committed file is compared and never rewritten.
  - A recording whose own `rc` (read from its JSON, as `closure.py merge` reads it) is not 0 is refused as a failed recording. The remedy is to fix the script, not to re-derive it.
  - Otherwise `closure.py check --partial` decides UNDER-SCOPED.
- **What 6b leaves to CI:**
  - node scripts on a machine without strace (ci-autofix.md: a Darwin recording does not replace a Linux one);
  - any script `gate_lock.py needs-lease` names (`stress.py`), because a push takes no gate lease;
  - a `full` case, because gate-scoping.md forbids a full derive off Linux.
- **Skipping 6b:** `PREPR_SKIP_CLOSURES=1` skips it visibly, for a push that only re-bodies.
- **Self-test:** 6a and 6b are the functions `claims_line` and `closures_line`, and `--self-test` drives them over a throwaway clone.
  - 6a cases: a branch that inherits main's list (refused), a row-only branch forked before main claimed (passes), and a branch writing its own claim (passes).
  - 6b cases, with a stub recorder returning recordings built from the committed closure, so no script runs: covered (passes), an unlisted read (UNDER-SCOPED), the same read from a recording that exited 3 (a failed recording), and a docs-only diff (skipped).
- Both CI jobs stay as the backstop. ci-autofix.md's "wait for the bot" governs a red that has already happened, and this step runs before any red exists, so no policy text changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

`193371eb176ec3fb3975448036eddfe40de6454d`

The review fix is commit `193371eb`. The handoff commit after it only carries this body.

## Mutation proof

`bash tools/audit/prepr.sh --self-test` gives `95 passed, 1 failed` unmutated. The one failure is "the step's own output names the flag", which fails identically at the merge base on a machine without `gh`. Each mutant below adds a named FAIL:
- the claim base set to main's tip with no `CLAIM_HEAD`: `6a passes a row-only branch forked before main claimed`. (Either change alone is equivalent, because env_drift takes the fork point from `CLAIM_HEAD` when it is set.)
- 6a's rc swallowed, or the rc test flipped, or the INHERITED remedy unmatched: `6a refuses a branch that inherits main's claim list`
- the JSON `rc` ignored, or the failed-recording arm disabled: `6b refuses a recording that exited non-zero as failed, not UNDER-SCOPED`
- the `closure.py check` rc swallowed, or the verdict's rc swallowed: `6b refuses a scoped script that reads an unlisted file as UNDER-SCOPED`
- the changed-file list emptied, the `scoped` case unread, or no script ever recorded: `6b passes a scoped script its committed closure covers`
- a skip reported as a pass: `6b skips a diff that reaches no selectable script`
- the lease check dropped: `stress.py is left to CI: a push takes no gate lease`

## Null control

Each fixture has a passing twin run through the same function: the row-only branch and the own-claim branch for 6a, and the covered recording for 6b. A step that refused everything fails those. The review's scenario E (a row-only branch forked before main claimed) is the second 6a case.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
