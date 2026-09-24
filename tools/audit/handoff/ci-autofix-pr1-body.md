<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJVA2kVqxpintcB5Hq57Hy1wN)_

Before: a branch that inherited main's claim list, or whose scoped test script read a file its committed closure does not list, was pushed as it stood. `fast` went red on INHERITED CLAIMS or `closures` went red on UNDER-SCOPED, and `claims-autofix` or `closures-autofix` then pushed the repair. Each repair cost a gate run, a held-run approval, and a bot commit on a head a reviewer may already have been reading.

After: `tools/audit/prepr.sh`, which `app_push.sh` runs before anything reaches the remote, refuses both. It prints the repair command, the same one the bot would run.

The census behind this (every failed run in the week to 2026-09-24, classified per job) is in the project's `ci-autofix/ANALYSIS.md`. These two were the most frequent reds that a machine can repair.

How: step 6a runs `env_drift.py --claims-only origin/main`, the same line `run.sh` runs unconditionally. Step 6b derives the scope with `closure.py affected` over the three-dot diff, as the `closures` job does. It records each scoped script with `derive_closures.sh --single --record-only` and runs `closure.py check --partial`, so the committed file is compared and never rewritten. Node scripts are left to CI on a machine without strace (ci-autofix.md: a Darwin recording does not replace a Linux one). A `full` case is skipped, because gate-scoping.md forbids a full derive off Linux. `PREPR_SKIP_CLOSURES=1` skips 6b visibly, for a push that only re-bodies. Both CI jobs stay as the backstop. ci-autofix.md's "wait for the bot" governs a red that has already happened, and this step runs before any red exists, so no policy text changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AJvUdyMZC5ztrV1UH5FmiH

## Head

`54a89693e923018f695ca2a891964c3c7e6545cf`

## Mutation proof

- **6a:** I replaced the step's `claims_check origin/main` call with `true`. On a probe branch cut from `c7e317ef^`, whose claim list is non-empty, a production-only commit then printed `ok claims hygiene`. Unmutated, it printed `REFUSE claims hygiene INHERITED CLAIMS: tests/golden/claimed_drift.txt claims exactly`.
- **6b:** I replaced both the `(exit 0)` test and the `closure.py check` call with no-ops. On a probe commit where `tests/open_meteo.py` opens `README.md`, the step then printed `ok closures scoped recordings are covered`. Unmutated, it printed `REFUSE closures UNDER-SCOPED: tests/open_meteo.py really reads 1 file(s) the committed closure does not list`.
- **Self-test:** `closure_lane` is pinned by three new `--self-test` cases, including a null control.

## Null control

- **6a:** the same probe branch with its claim list emptied (what `--drop-inherited` writes) printed `ok claims hygiene claims hygiene: origin/main ok`.
- **6b:** a probe commit that only adds a comment to `tests/open_meteo.py` printed `ok closures scoped recordings are covered`.
- **Remedy path:** re-deriving `open_meteo.py` changes `tests/closures.json`, which puts the diff in the `full` case. The step then prints its `skip`, as the `closures` job would.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
