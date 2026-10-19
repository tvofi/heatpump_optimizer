Fix review: merge 705a9b851d314f860f3fa29e0e092231d5c878ad

bus-nonce: 46cd0cfad829e180f6f0a07a572316d8

## Round

Round 3 of the PR's posted `Fix review:` comments. Round 1 (comment 6253921423) was `blocked acf14d8f carry-missing`. Round 2 (comment 6255452125) was `merge 5c2bfcb1`. The dispatch names a `merge` verdict at `d8889b62`, which merges main `fa5026c4` into `5c2bfcb1`. It is not posted on the PR as a `Fix review:` comment. The last verdict was `merge`, so `fixer.md`'s re-cut rule does not apply. This round judges the recarry delta and the re-taken body only.

## Head

- I measured `705a9b851d314f860f3fa29e0e092231d5c878ad` (`ev/HEAD`). It was still the PR head when I wrote this.
- Its parents are `d8889b62f` and main `06c6f3cf2`.
- `git merge-tree --write-tree d8889b62f 06c6f3cf2` gives tree `4da849e9`, which equals the head's tree. The driver printed `LEDGER-MERGE: resolved tests/closures.json`. So this is a clean recarry with no hand resolution.
- `git diff --stat ff914f548 705a9b851 -- custom_components tests tools/replay` prints only `tests/closures.json | 1 +`.
- The body's second stat over the production, driver and stub paths prints 0 lines.
- Production and test code are therefore byte-identical to the heads rounds 1 and 2 measured. The body names this SHA (step 7).

Contract: main moved `fix-review.md` step 10 and `finding-propagation.md` after this head (#2408). I followed main's copy. Under it, a roster carry is in the tree once it is on `handoff/audit-r10-roster`. That retires round 2's precondition that #2417 must merge first.

## Forward-carry (step 10)

- The carry SHA `2020978559ef` is an ancestor of `origin/handoff/audit-r10-roster`, now at `73bb15fe`.
- At that tip, R10-BRIEFS-FOLD is `resume.stage: not-started`, so it is live and not done. It holds exactly one #2399 carry, and that carry is byte-equal to the body's quote (`ev/carry_check.txt`: True at the tip and at `2020978`).
- The carry states its control, M4's check, and a precondition: the restart-gap rule applies only to rows without `version`.
- R10-TICK-DRIVERS is `done` (merged as #2390, `a96f4be4`), and the body does not use it as a destination. R10-DIAG-REPLAY's own group is not a destination either.
- `brief_lint.mjs` on that roster, from an origin/main `fa424fd9` worktree: `TOTAL: 0 error(s) across 1 file(s)` (`ev/brief_lint.txt`). `policy_lint.mjs` at main: 0 errors across 41 files.

## Mutation proof (step 1), at this head (`ev/mutants.txt`)

    RESULT mutant=M0 rc=0 ALL 122 DEBUG COLLECT CHECKS PASSED
    RESULT mutant=M5 rc=1 24 of 122 DEBUG COLLECT CHECKS FAILED cred_lines=0   (replay_doc.py:511 return clean -> return raw)
    RESULT mutant=M4 rc=1 1 of 122 DEBUG COLLECT CHECKS FAILED cred_lines=0    (debugger.py:142 "version" line deleted)

Both match the body's figures. The rest of the table (M1–M8, MA–MD) was reproduced in round 2 on byte-identical code, so I did not re-run it.

## Figures (step 8), re-taken at this head (`ev/figures.txt`)

These all match the body:
- `debug_collect`: 122/122 passed, `RESULT leak_probes_through_download=21 written=21 refused=0 unit=count`.
- Synthetic day: `IDENTICAL`.
- `export.py --check`: `0 violation(s)`.
- `entry_keys`: 216.
- Package files: 98.
- `Architecture score: dS +0.0000 NULL`.
- `closure.py select --diff 06c6f3cf`: `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`
- `claims hygiene: 06c6f3cf... ok`.
- `STRUCTURE RATCHET PASSED`.
- 25 commits in `06c6f3cf..705a9b85`.
- #2423 (`89e33859`) and #2424 (`fa5026c4`) are both ancestors of the head.
- The body's reader grep (`tools/(policy|audit)|stamp|delivery_status`) prints nothing.

Not re-derived: the merge-base values (214, 97), which round 2 measured; the CodeQL CLI 1→0 figure, which is the fixer's own run (round 2 said the same); and the census, which is the fixer's instrument.

## Body correction, not blocking

The `delivery-status` bullet says "This diff adds no delivery file". That is **false**: `git diff --name-only origin/main...HEAD` lists `dev/programme/delivery/2399.md`. It is this PR's own `open` row, added in `b931d0f44` ("record: the delivery row for #2399"), which `delivery-status-tracking.md` requires. So the diff does reach what `delivery-status` reads.

The answer still holds. Round 2 read the earlier red: `OVERDUE` on the rows for #2413, #2412 and #2407, not on #2399's row. `delivery-status` is green at this head (117852504479). Step 11 checks that the trigger was answered, not the answer, so this does not block. The sentence should read "This diff adds only its own open row".

## Red checks (step 11)

Every check run on this head has concluded (50 runs, `ev/check-runs.tsv`). The only red is `pr-contract` 117852619806 (01:54Z), whose error was that the body did not name `wave-script`. The latest `pr-contract`, 117869754472, started at 03:05:52Z, after the body edit at 03:05:46Z, and concluded `success`.

Every red of the range is named and answered in `## Red checks`: CodeQL, coverage-ratchet, delivery-status, mutation, validate-hacs and wave-script. At this head `CodeQL`, `Analyze (python)`, `mutation`, `coverage-ratchet`, `wave-script`, `delivery-status`, `closures` and `fast (3.14)` are green. I did not read the `mutation` log this round, because this head draws no new production line.

## Steps 4, 5, 13, 14, 15

- Neither claim file and no `*_budgets.json` is touched. `VERSION` and `RELEASE_NOTES.md` are untouched. The manifest diff adds only `recorder` to `after_dependencies`.
- `git merge-tree --write-tree origin/main 705a9b851` at main `fa424fd9`: rc=0, tree `c1e9e8f6`, and no claim-driver line (`ev/merge-tree.txt`).
- The recarry delta moves only `tests/closures.json` by one line, a resolved ledger merge from main. dS is NULL. The recarry adds no lines, so step 15 has nothing to judge.
