Fix review: blocked fbba2ccb58a74111c4cfb139639533238835cd66 harness: class-open rename source paths: the scope job's `git diff --name-only` detects renames, so a .py/.js/action.yml renamed to an inert suffix drops off the list and that leg skips

bus-nonce: ef136ec87836d220d288d8297276c985

Round 1. Reviewed head `fbba2ccb58a74111c4cfb139639533238835cd66` (authored code head `54a69b23a`, merge base `63816b857`). `git diff <mb>...origin/main -- dev/governance/roles/` was empty, so this contract is current.

## The finding (blocks)

The body says a leg skips "only when every changed file's suffix is on that leg's INERT allow-list" and calls the rule "fail-closed in every arm". The script keeps that promise for the list it receives. The workflow builds the list with `git diff --name-only "$BASE...$HEAD"`, and porcelain `git diff` detects renames by default (`diff.renames=true` since git 2.9). For a rename it prints only the destination path. When a file moves from a suffix the extractor reads to an inert one, the source path is changed (deleted from that leg's tree) but never reaches `decide`.

Reproduced in a scratch repo (git 2.38.1). The runner's git is 2.55.0 (scope job log), where rename detection is also the default. One commit runs `git mv lib.py lib.md`.

- `git diff --name-only B...H` prints `lib.md`. `decide --language python` prints `skip: all 1 changed file(s) are inert to the python extractor`.
- `git diff --no-renames --name-only B...H` prints `lib.md` and `lib.py`. `decide` prints `analyze: lib.py (.py) may be read by the python extractor`.

The same gap exists on every leg: `*.js`/`*.mjs` → `.md` skips javascript-typescript, and an `action.yml` outside `.github/` → `.md` skips actions. Deleting a module changes that leg's analysis (for example a sanitizer or a model that other files use), so the PR's required `Analyze (<leg>)` reports success without analyzing a tree that differs from main for that extractor. `push` on main still analyzes after the merge, so the exposure is limited to PR-time findings. It still contradicts the body's fail-closed claim.

**Fix:** add `--no-renames` to the `git diff` in the `scope` job (so both sides of a rename are listed), and say in the body which arm covers it. A comment in the workflow pinning the flag would help, since the self-test cannot reach the workflow. This line is in the body's own "Unpinned sites" (the wiring), and that's why no local check caught it.

## RESULT lines (mine, this seat)

- RESULT self_test_head=`codeql_scope self-test: 42 checks, 0 failed` (seat venv python 3.14.7). I re-derived the count from the source: 3+3+6+24+3+1+2 = 42.
- RESULT ci_self_test=`codeql_scope self-test: 42 checks, 0 failed`, from the `instrument-self-tests` log (check-run 117685239877, success). The tally grep step ran.
- Mutation proof, re-run against scratch copies of the head's script:
  - event guard → 15 failed
  - suffix allow-list → 10 failed
  - `.github/` force → 3 failed
  - empty list → 2 failed
  - These four match the body.
  - My own mutants: dropping `.lower()` → 1 failed. `.json` inert for javascript-typescript → 1 failed. `.sh` added to `_PROSE` → 1 failed. Unreadable list returning 0 → 1 failed. Removing the unknown-leg guard → the self-test raises KeyError and never prints the tally, so the CI grep fails.
  - No vacuous check found.
- RESULT codeowners_gap_head: covered_by_an_owner=45, uncovered_files=0. This matches the body's 86/45/0 for the owned and uncovered figures. I did not re-derive the base figure (85/44/0).
- RESULT merge_tree: `git merge-tree --write-tree origin/main fbba2ccb5` exited 0, so there is no conflict.
- RESULT version_untouched: VERSION, manifest.json and the notes are not in the diff.
- RESULT workflow_null_control: the `scope` job log (117685278108) shows `codeql_scope: <leg>: analyze: .github/CODEOWNERS changes the analysis itself` for all three legs. `Analyze (actions)` (117685403018) and `Analyze (javascript-typescript)` (117685402966) log `codeql scope for <leg>: analyze` and ran init, analyze and upload. `Analyze (python)` was still in progress when I read it. The body's `.github/` arm holds in CI.
- The skip arm has no CI proof at any head. The body discloses this as a projection under "Unpinned sites", and I have not verified it.
- Ruleset 23698884 has no `code_scanning` rule, so a skipped leg's missing SARIF does not block a merge. The new `scope` job name collides with no required context.

## Other steps

- Step 2/9 (harness): the finding is a cost measurement, not a defect harness. The fixer's own instrument is the self-test, and it is disclosed as theirs.
- Step 6 (other configurations): suffix case, unknown suffix, no suffix, blank list, unreadable list, each non-PR event, and `.github/` paths are all covered. A path with non-ASCII characters is quoted by `core.quotepath` (suffix ends in `"`) and so analyzes (fail-closed). Renames are the open seam above.
- A partial `scope` failure leaves earlier legs' words written. Each written word is still a correct decision for its leg, and unwritten legs read empty and analyze, so nothing opens there.
- A PR that edits `codeql_scope.py` runs its own edited copy, so "editing this decision analyzes every leg" holds only if the edit keeps that arm. This is no new surface (a PR could always edit `codeql.yml`), and CODEOWNERS now owns both. I note it and do not block on it.
- Step 10: forward-carry is none, and item 2(ii) is named as the coordinator's split. Acceptable.
- Step 11: the prior head 54a69b23a has only `cancelled` runs (concurrency-superseded), no red. At the reviewed head, `closures` and `Analyze (python)` were still in progress when I read them. All other runs were success, skipped or neutral (`CodeQL`). The body's "Red checks: none" is not contradicted so far.
- Step 14: no budget, ratchet or golden moved. Not applicable.
- Step 15: added lines follow the least-privilege split (read-only `scope`, `security-events: write` only in `analyze`). I found no architecture breach.
- Step 4 (env_drift --all): **not verified**. The run (`timeout 300 python3 tests/env_drift.py --all`) printed nothing in 300 s on a loaded box, which reads as a timeout. The diff touches no fixture and no claim file (`git diff --stat` lists only `.github/`, `tools/pr/codeql_scope.py` and one delivery row), so no claim is owed. That rests on reading the diff, not on the instrument.

Evidence: ~/hpo-seats/r10s3/review-2405/evidence/
