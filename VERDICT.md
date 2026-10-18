Fix review: blocked 89d2b94654bf54b49d879e08caced815a75ea5f5 class-open: the JS twin of the changed-file list still detects renames: card_rig.mjs threeDotFiles (read by card_drift.mjs's claim gate) and card_browser.mjs gridScope, and RENAME_SITES skips *.mjs
bus-nonce: 4e582de29d537bde3ef7d611a24e2746

Round 2. Reviewed from a detached worktree at `89d2b94654bf54b49d879e08caced815a75ea5f5`. The roles diff against main was empty. I judged the delta since round 1 (`a7d97f55b`): the fix commits `f658e418a` and `8212a3e61`, plus two merges. Evidence: `~/hpo-seats/r10s3/review-2406/evidence-r2/`.

## The round-1 finding is fixed on the Python side, and the fix holds

- RESULT producer: `closure.changed_between` (`--no-renames`) is the one list, and `changed_files`, lane_skip's main delta and all 6 `tests.yml` sites (1888 graders-head-copy, 2297 and 2308 closure-scope, 2465 and 2473 closures, 2751 composed-proof) consume it through `closure.py changed`. Each of those jobs runs `setup-python` before its call site. `closure-scope` concluded success on this head.
- RESULT my round-1 probe on this head (a card file renamed onto `dev/programme/delivery/99999.md`): `closure.py changed` lists both paths, and lane_skip prints `typing -- RUN` and `browser -- RUN` (`evidence-r2/js-twin-probe.txt`). In round 1, the same shape of rename (the integration's `__init__.py`) skipped all three lanes.
- RESULT self-tests at the head (`evidence-r2/r2-tests.txt`): lane_skip `54/54`, closure `ALL 122 ... PASSED`, `rename_sites()` returns `([], [])`, roster_lib 18/0 failed, tick 104/0, state_docs passed.
- RESULT mutation, my re-run of MB8 (`--no-renames` dropped from `changed_between`): lane_skip `51/54` (the three `runs on a rename` pins) and closure `3 of 122 ... FAILED` (both sides, the 0-script scope, the census). This matches the body, so the pins are not vacuous.
- RESULT merges: both merges in the range (`204da95e1`, `89d2b9465`) have trees equal to `git merge-tree --write-tree` of their parents, so no resolution was made by hand. `git merge-tree --write-tree origin/main(be2d3676e) HEAD` returns rc 0.
- RESULT `8212a3e61`: it adds only a trailing comment marker, which the layout guard requires.

## Why it is blocked: class-open (step 6)

The body's class is "every lane and the gate read the files a diff changed from here", and the census is its rule. The census globs `.github/workflows/*.yml`, `tests/*.py|sh`, `tools/pr/*.py|sh` and `tools/audit/seat/*.py|sh`. So it never reads a `.mjs` file. Run over the whole tree, the same rule (rename-detecting `--name-only`, excluding plumbing, `ls-tree`, empty-tree and `--name-status` sites; `evidence-r2/nameonly-all.txt`) returns seams that are neither in the diff nor dispositioned in the body:

1. **`tests/card_rig.mjs:838-839` `threeDotFiles`.** Its docstring calls it env_drift.py's `three_dot_files`, "same three commands in the same order". This PR gave the Python twin `--no-renames` and left the JS twin as it was. `card_drift.mjs:691` feeds it to `claimsAreThisBranchs`, the card claim gate. The probe renames the card file onto a delivery row: `card_rig.threeDotFiles` returns `["dev/programme/delivery/99999.md"]`, while `closure.py changed` returns both paths. The two claim judges now disagree on the same diff, and the JS one loses the claimable card path. The parity pin at `tests/card.mjs:10800-10803` (`threeDotFiles runs the sibling's three commands in order`) still asserts the old `diff --name-only REF...HEAD`, so it now pins the divergence.
2. **`tests/card_browser.mjs:981` `gridScope`.** On the same probe it prints `P9 grid MODE: SCOPED -- SKIPPED, NOT A PASS (none of 1 changed file(s) is on the card surface ...)` while the card file is deleted. No workflow sets `HPO_BROWSER_SCOPE`, so CI runs the grid in full, and the opt-in `auto` mode is only reached locally. It is still a lane's own list with the round-1 shape.
3. **`.claude/hooks/stop-selfcheck.sh:197-198`.** Its `CHANGED` list is the same porcelain shape, outside `RENAME_SITES`.

Remedy: give each one `--no-renames` (or delegate to `closure.py changed`), move the `card.mjs` parity pin with the twin, and widen `RENAME_SITES` to `tests/*.mjs`, `tools/policy/*.mjs` and `.claude/hooks/*.sh`. Either that, or have the body disposition each site by name. The residual sites inside the census are safe, and I checked each: `mutation_table.py:1524` refuses an `R` code (fails closed), `bus.sh:478` handles `R*`, `prepr.sh:1140` is a `git log` with deletions passing by design, and the rest are plumbing or `ls-tree`. One more gap in the census: it is line-based, so a `git diff \` with `--name-only` on the next line passes it. Say so in the body, or match across continuations.

## The owed steps are parked, not routed (step 10)

The coordinator asked about the two items moved from `## Forward-carry` to `## Unpinned sites`:
- **The state-docs beat restart (no `--roster-ref`).** Without it, the beat change does nothing on the live box. I found it in the PR body only. It is not in any roster group's brief on either `origin/main` or `origin/handoff/audit-r10-roster` (jq over `.groups[]` for these terms returned none), no issue carries it, and the orchestrator's out-of-tree `SEATS.md` does not have it.
- **The `codeql_scope.changed` -> `closure.changed_between` delegation.** It sits in this body, in #2405's `## Forward-carry` prose, and as an `OWED` line in the orchestrator's out-of-tree `SEATS.md` (15:52Z). It is not in a roster brief, an issue, or anything a later seat reads.

Under `finding-propagation.md`, a PR body is a record, not a delivery. Each item needs a destination a later seat reads: a roster group with its brief, or an issue. The body should name that destination in `## Forward-carry` instead of `none`. On its own, this would be `carry-missing`.

## Other steps

- RESULT checks (step 11; `evidence-r2/checkruns-r2.tsv`): 37 runs and no red in the range (`f658e418a`, `8212a3e61`, `204da95e1`, `89d2b9465`). `fast (3.14)`, `coverage` and `Analyze (python)` were still in progress at 14:58Z.
- RESULT version, claims and budgets: none of them is touched in the delta.
- RESULT projection: corrected to 6.4, which matches my round-1 note.
- RESULT head (step 12): `gh pr view` reported `89d2b94654bf54b49d879e08caced815a75ea5f5` when I wrote this.
