Fix review: merge 5c2bfcb1ebb683fe0576e7dccf71ab67ddaddc39

bus-nonce: 519dcc2fd420f363fd64510c64cce2a5

## Round

Round 2. The only earlier verdict is round 1 (issue comment 6253921423, hpo-approver): `blocked acf14d8f carry-missing: not carried to R10-BRIEFS-FOLD`. Nothing else in round 1 blocked. Round 1 also raised the CodeQL alert as needing a decision before merge.

## Head

I measured `5c2bfcb1ebb683fe0576e7dccf71ab67ddaddc39` (`ev/HEAD`). It was still the PR head when I wrote this, and origin/main was still `07a09406`. The body names this SHA.

The head's parents are `acf14d8f` (round 1) and `ff914f548`. `ff914f548`'s parent is `22b9b6cf`, which merges origin/main `07a09406` into `acf14d8f`. `git diff ff914f548 5c2bfcb1` is empty, so the head's tree is the authored code head. The only authored change since round 1 is `22b9b6cf..ff914f548`, which touches `tests/debug_collect.py` alone:
- it adds `_unrecorded`;
- it changes the detail (third) argument of three `R.check` calls;
- it changes no check condition.

The contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Round-1 blocker: forward-carry (step 10), now present

- `origin/handoff/audit-r10-roster` is at `2020978559ef37e9e22ae0926a5f685622da65f5`, `roster_edit append-carry R10-BRIEFS-FOLD: #2399 D15 forward-carry`.
- Group `R10-BRIEFS-FOLD` is `resume.stage: not-started`, so it is a live destination. It has 10 `carry` entries. The last is byte-identical to the body's `> From R10-DIAG-REPLAY (#2399 ...` quote (`ev/carry_last.txt`, `ev/pr_body.md`; Python equality True).
- The carry includes the control (the "a cycle row carries the release that wrote it" check going red with the stamp removed, which my M4 reproduces). It states the precondition and asks for a re-measure at the D15 baseline.
- `node tools/policy/brief_lint.mjs` on that roster, run from an origin/main `07a09406` worktree: `TOTAL: 0 error(s) across 1 file(s)`.
- **Merge precondition for the orchestrator.** #2417's current head `c83ae12acc07` (`fix/audit-r10-roster`) does **not** contain `2020978`. It is not an ancestor, and the roster at that head has 0 matches for the carry. The dispatch says the carry lands with #2417, so #2417 must first be brought up to `handoff/audit-r10-roster` ≥ `2020978`, and #2417 must merge before #2399 (`finding-propagation.md`: "does not merge until the carry is in the tree"). This verdict's `merge` depends on that order.

## Mutation proof (step 1): my own runner, `ev/mut.py`, `ev/mutants.*.txt`

Each mutant is applied to a `git archive` copy, then `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` runs. Every replacement matched exactly once.

At the head:

    RESULT mutant=M0 rc=0 ALL 122 DEBUG COLLECT CHECKS PASSED
    RESULT mutant=M1 rc=1 TypeError (replay half missing)
    RESULT mutant=M2 rc=1 25 of 122 FAILED
    RESULT mutant=M3 rc=1 2 of 122 FAILED
    RESULT mutant=M4 rc=1 1 of 122 FAILED
    RESULT mutant=M5 rc=1 24 of 122 FAILED
    RESULT mutant=M6 rc=1 2 of 122 FAILED
    RESULT mutant=M7 rc=1 1 of 122 FAILED
    RESULT mutant=M8 rc=1 2 of 122 FAILED
    RESULT mutant=MA rc=1 2 of 122 FAILED  credential-bearing FAIL lines=0
    RESULT mutant=MB rc=1 1 of 122 FAILED  credential-bearing FAIL lines=0
    RESULT mutant=MC rc=1 2 of 122 FAILED  credential-bearing FAIL lines=0
    RESULT mutant=MD rc=1 1 of 122 FAILED  credential-bearing FAIL lines=0
    RESULT mutant=R1 seal floor 6->7      rc=1 1 of 122 FAILED
    RESULT mutant=R2 seal violations off  rc=1 1 of 122 FAILED

Every count matches the body's table. No mutant at the head prints a planted credential (`s3cret-value`, `bob123456`, `abc123456`, `secretvalue123`) in any FAIL line.

## Null control (step 3), at `22b9b6cf`, the merge before the fix

    RESULT mutant=M0 rc=0 ALL 122 PASSED
    RESULT mutant=MA rc=1 2 FAILED  credential-bearing FAIL lines=1
    RESULT mutant=MB rc=1 1 FAILED  credential-bearing FAIL lines=1
    RESULT mutant=MC rc=1 2 FAILED  credential-bearing FAIL lines=2
    RESULT mutant=MD rc=1 1 FAILED  credential-bearing FAIL lines=1

These match the body: the failure counts are the same (2, 1, 2, 1), the leaks are 1, 1, 2, 1 before the fix and 0 at the head. The fix therefore cuts the echo without weakening any check.

I did **not** run the CodeQL CLI myself. The body's "1 alert → 0 alerts" is the fixer's own local measurement and is not re-derived here. CI's `CodeQL` check at this head is `neutral`, titled "1 configuration not found" ("cannot determine the alerts introduced by this pull request"), so CI has not confirmed 0 alerts either. My value-level run above is the independent evidence that no check detail echoes a planted credential. The census rule (an AST walk over sensitive names) is the fixer's instrument. I did not rebuild it. Its value-level complement is the MA–MD runs above, which I did reproduce.

## Figures (step 8): re-taken at the head and at `07a09406` (`ev/figures.txt`, `ev/cheap-checks.txt`)

All of these match the body:
- `debug_collect`: 122/122, `RESULT leak_probes_through_download=21 written=21 refused=0 unit=count`.
- Synthetic day: `IDENTICAL`.
- `export.py --check`: `0 violation(s)`.
- `entry_keys`: 214 at the base, 216 at the head.
- `sanitiser_checks`: `56 0` at both ends.
- Package files: 97 at the base, 98 at the head.
- D6: `arch_modules_on_disk=80`, `arch_map_listed=80`, `arch_map_missing=0`, `ha_module_level_importers=28`, `claims_true=123`, `claims_false=0`.
- `Architecture score: dS +0.0000 NULL`.
- `closure.py select`: `MODE: SCOPED -- 31 script(s) run, 2 scoped out.` with `--diff 07a09406`, and `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` with `--diff 22b9b6cf`.
- `STRUCTURE RATCHET PASSED`, `ALL 109 HARNESS HEADER CHECKS PASSED`, `claims hygiene: 07a09406... ok`, `ALL 96 contracts PASSED`, and `tmp_paths: 0 refused`.

## Steps 4, 5, 13, 14

- Neither claim file and no `*_budgets.json` is touched. `VERSION` and `RELEASE_NOTES.md` are untouched. The manifest diff only adds `recorder` to `after_dependencies`.
- `git merge-tree --write-tree origin/main 5c2bfcb1` exits 0, tree `8c9a7477`. Main equals the merge base, so no driver was invoked (`ev/merge-tree.txt`).
- No number moved this round: the authored delta is test-detail text only, and dS is NULL.

## CI at this head (check-runs API, every run: `ev/check-runs.tsv`)

Green:
- `mutation`. I read the log: `MUTATION TABLE PASSED`, not INCONCLUSIVE, and 4217 unpinned equals the ratchet base.
- `coverage-ratchet`, and the other completed lanes.

Neutral: `CodeQL`, as above.

Still running when I wrote this: `Analyze (python)`, `fast (3.14)` and `closures`. Not every workflow has concluded, so step 11 does not allow a `root-cause-unanswered` verdict yet in any case.

Red, and main's, not this PR's:
- **`wave-script`** (117790959649): `DIVERGENT merge-subject-pr` on "Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)" and "#2379 (R10-SENSOR-PAYLOAD)", with `AGREEMENT REFUSED`. That is exactly the line the dispatch names. `wave-script` is also `failure` on main at `5756f2b1`. The diff touches none of the readers (`stamp.py`, `delivery_status.py`, `policy_lint.mjs`). The fix is in flight as R10-MERGE-SUBJECT.
- **`pr-contract`** (×2, the later one 117791718734): its only ERROR is "check `wave-script` is red and `## Red checks` does not name it". This is the same cause as `wave-script`. It clears when R10-MERGE-SUBJECT lands and the contract re-runs, or when the body names `wave-script`.
- **`delivery-status`**: `OVERDUE` on rows for #2413, #2412 and #2407 (record batches), not on this PR's row. It is not a required context.

## Step 15

The added lines are a test-local helper in the shape of `seal`'s own refusal. There is no architectural concern.
