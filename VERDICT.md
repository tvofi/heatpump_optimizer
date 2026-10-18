Fix review: blocked acf14d8f2267718203d9dc1b313bc8c3e9f0bc8d carry-missing: not carried to R10-BRIEFS-FOLD

bus-nonce: b930fe4abb89d68c115bbd433edf87af

## Round

Round 1. No earlier `Fix review:` comment or review is on #2399: the issue-comment and review lists are both empty.

## Head

I measured `acf14d8f2267718203d9dc1b313bc8c3e9f0bc8d` (`ev/HEAD`). It was still the PR head when I finished. The body names `b931d0f44` as head. `acf14d8f` is github-actions' `ci: merge main` of `106af95a3` into `b931d0f44`. Its tree equals `git merge-tree --write-tree b931d0f44 106af95a3`, so the merge is clean with no hand resolution. The PR's own three-dot delta over `custom_components tests tools/replay docs` at `acf14d8f` equals the one at the handoff code `f32ad027`, apart from hunk offsets. The only path added is `dev/programme/delivery/2399.md`. The body's figures therefore describe this head, and I re-took them here.

I checked `dev/governance/roles/` against origin/main: the diff is empty, so my copy of the contract is current.

## Blocking: forward-carry (step 10)

The body's `## Forward-carry` names the D15 change and points it at the `R10-BRIEFS-FOLD` brief in `dev/programme/rosters/wave-r10-groups.json`. Two things change: a row now carries `version`, which invalidates M1's "integration_version is the download's", and "While the download's `replay` is null" is retired. The text is in the PR body only.

At origin/main `5756f2b1`:
- The R10-BRIEFS-FOLD group's JSON contains none of `2399`, `DIAG-REPLAY`, `restart-gap` or `row carrying`. Its stage is `not-started`, so the group is live.
- `dev/governance/dimensions/D15.md` still says, at line 10, "While the download's `replay` is null (until R10-DIAG-REPLAY)". At line 20 it still says "`integration_version` is the download's, not each row's".

The finding is measured with a control: M4 below turns "a cycle row carries the release that wrote it" red. `finding-propagation.md` says "The producing PR does not merge until the carry is in the tree", so this PR is blocked.

The fixer's seat may not write the roster. The orchestrator can clear this by putting the body's quoted carry text into R10-BRIEFS-FOLD's `brief` with `roster_edit.py`, and `brief_lint.mjs` reads it back. The branch needs no change. Re-review only that the carry landed: nothing else in this verdict depends on it.

## CodeQL: a real alert, not the tools-evidence class

- Check run 117752117325 (github-advanced-security) reports "1 new alert including 1 high severity security vulnerability". Its one annotation is `py/clear-text-logging-sensitive-data` at `tests/harness.py:50`, the `R.check` FAIL print (`ev/codeql_annotations.json`).
- This is **not** the tools-evidence class. `codeql-triage-poll.sh` handles only the three audit-evidence harness paths under `dev/audit/rounds/...`, under the 2026-09-29 mandate. This alert is in `tests/`, newly reached by this diff, and no mandate covers dismissing it.
- The source is test data, not a production leak. I could not read the SARIF threadFlow: the code-scanning alerts and analyses APIs return 403 to this seat too. So, like the body, I cannot confirm the source, only infer it. The label "sensitive data (secret)" is CodeQL's `secret|trusted` name heuristic. The only new `secret`-named value that reaches a check's `detail` is `str(_secret_drop)` at `tests/debug_collect.py:1144` (`ev/codeql_source_candidate.txt`), which holds the test literals `bob123456` and `abc123456`. `SECRET_KEY`, `SECRET_TEXT` and `secret` in `replay_doc.py` only moved, from `tools/replay/export.py`, and CodeQL was green at `33dfae1e`, which already carried them.
- Under step 11 the red is answered: the body names the check, the cheaper detector (a local CodeQL CLI run) and its standing cost (about 16 minutes per push plus the install).
- It still needs a decision before merge. One option is to dismiss it as used-in-tests, which needs someone with code-scanning access. The other is the #2163 pattern (`R9-CODEQL-SARIF-FIRST.md`): make that check's `detail` constant text. That cuts the modeled path and is not a rename. The body rejected only a rename, so the constant-detail fix remains open.
- The CodeQL check completed at 18:19:08Z. This head's `Analyze (python)` jobs finished later, at 18:35 and 18:45 (green), and no newer CodeQL check run was posted.

## CI at this head (check-runs API, every run: `ev/check-runs.tsv`)

- Red: `CodeQL` only.
- Green: `fast (3.14)` ×2, `mutation` ×2, `coverage-ratchet` ×2, `coverage`, `hassfest`, `validate-hacs`, `typing`, `nightly-ha` (both), `arch-score`, `budget-raise-gate`, `pr-contract` (18:17:42, before CodeQL concluded), `delivery-status`, `nightly-status`, `scope`, `closure-scope`, `briefs` and the rest.
- Still running: `closures` ×2.
- I read the `mutation` log (job 117751634850): `MUTATION TABLE PASSED`, with this diff's sites evaluated, for example `debugger.py:368 GUARD_OFF -- killed by tests/debug_collect.py`. It did not print INCONCLUSIVE.

## Merge with origin/main

`git merge-tree --write-tree origin/main acf14d8f` at main `5756f2b1` exits 0, tree `c00813d2`. The ledger driver printed `LEDGER-MERGE: resolved tests/closures.json`. No claim file conflicts (`ev/merge-tree.txt`).

## Mutation proof (step 1), own runner at the head (`ev/mutants.txt`)

The unmutated run prints `ALL 122 DEBUG COLLECT CHECKS PASSED` (`ev/debug_collect.head.txt`).

The body's M1–M8 all fail:

    RESULT mutant=M1 rc=1  (TypeError after "Download diagnostics fills the bundle's replay half..." FAIL)
    RESULT mutant=M2 rc=1  25 of 122 FAILED
    RESULT mutant=M3 rc=1  2 of 122 FAILED
    RESULT mutant=M4 rc=1  1 of 122 FAILED  (a cycle row carries the release...)
    RESULT mutant=M5 rc=1  24 of 122 FAILED
    RESULT mutant=M6 rc=1  2 of 122 FAILED
    RESULT mutant=M7 rc=1  1 of 122 FAILED
    RESULT mutant=M8 rc=1  2 of 122 FAILED

These counts match the body's table: M2=25, M5=24, M3, M6 and M8 two each, M4 and M7 one each.

My own mutants:

    RESULT mutant=R1 seal leak test off            rc=1  1 FAILED
    RESULT mutant=R2 seal violations test off      rc=1  1 FAILED
    RESULT mutant=R3 no-recorder guard removed     rc=1  (crash: FakeEntry has no minor_version)
    RESULT mutant=R4 DOWNLOAD_HEADROOM dropped     rc=1  2 FAILED
    RESULT mutant=R5 replay window 5x REPLAY_SPAN  rc=1  1 FAILED
    RESULT mutant=R6 seal floor 6 -> 7             rc=1  1 FAILED
    RESULT mutant=R8 _since < -> <=                rc=1  1 FAILED
    RESULT mutant=R9 _public skipped on entry      rc=1  24 FAILED
    RESULT mutant=R7 manifest drops "recorder"     debug_collect rc=0, ha_contract rc=0, entities unchanged

R7 is not caught by the local suite. `entities.py` fails 1 of 2347 at the unmutated head too: the pre-existing graders-head-copy check the body names (`ev/entities.head.txt`). The detector for R7 is CI's `hassfest`, which checks the declared dependencies and is green at this head. This is an observation and does not block.

## Figures (step 8), re-taken at this head and at merge base `106af95a` (`ev/figures.*.txt`)

All of these match the body:
- `debug_collect`: 122/122, `RESULT leak_probes_through_download=21 written=21 refused=0`.
- Synthetic day: `IDENTICAL`.
- `export.py --check`: `0 violation(s)`.
- `entry_keys`: 214 at the merge base, 216 at the head.
- `sanitiser_checks`: `56 0` at both ends.
- Package files: 97 at the merge base, 98 at the head.
- `STRUCTURE RATCHET PASSED`; `ha_contract` `ALL 96 contracts PASSED`; `doc_claims` `ALL 169 checks PASSED`.
- D6: `arch_modules_on_disk=80`, `arch_map_listed=80`, `arch_map_missing=0`, `ha_module_level_importers=28`, `claims_true=123`, `claims_false=0`.
- `closure.py select --diff 106af95a`: `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`
- `env_drift --claims-only`: `claims hygiene: origin/main ok`.

Not re-derived:
- Coverage at 83 % → 100 %. CI's `coverage-ratchet` is green at this head, which covers the per-module floor.
- The 44 ledger rows and `PIN KILLED: 10 pinned`. CI's `mutation` passes; I did not re-run the table, by step 11.
- The conf-keys mutant `216 against 214` (body: not re-run since `aaa61a95`). The 214→216 figure itself re-derives.

## Other steps

- Step 5: `VERSION`, `RELEASE_NOTES.md` and the manifest `version` (7.0.0) are untouched. The manifest diff adds `recorder` to `after_dependencies` only.
- Step 4: neither claim file and no `*_budgets.json` is touched.
- Step 9, harness: the "finder" is the owner's design (#2271 and the roster brief). Every design item has a check: shared module (export loads it by path), recorder history in the executor, 7-day window, inline cap, shared Tibber choice, `--check` on a generated download, planted-credential null control, `LEAK_PROBES`, A10, and the per-row version stamp. I found no `design-trace-missing`.
- Step 14: the closures, ledger and D6 counts move with the new module and checks. Architecture score: `dS +0.0000 NULL`, no raise. `replay_doc.py` is classified in 14 closures.
- Closing: the roster's `fixes` is `[]`, so "Part of #2271" is correct.
