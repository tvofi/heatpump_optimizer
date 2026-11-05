R10-HOTFIX-RECORD-ATTRIB carry repair, round 2. #3194 fixed `record_row.py` (`attribute_merge`). `tools/policy/policy_lint.mjs` `fetchPullsBySha` recovered a number from the subject on an empty `/commits/<sha>/pulls` answer without confirming it against `/pulls/<n>`'s `merge_commit_sha`. Round 1 added `confirmGapMerge` and the guard in `fetchPullsBySha`; the fix review blocked it as mutation-vacuous (M3 deleted the guard and the fixture stayed ok). This repair: `fetchPullsBySha(commits, get = ghGet, slug = repoSlug())` and `confirmGapMerge(sha, pr, get, slug)` take an injectable getter and slug; three enumeration-level pins; and the refusal wording now names both causes (merge commit differs, or `/pulls/<n>` could not be read: HTTP error or rate limit).

## Head

`1c42ca3fda183b63a6c3579071bef9a8e354acef` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`007f8a66cdf89780c779292d9a1be34f5469f6dd`. origin/main is 499162c89d0f4f8369e16e6e41fb3a620bc1ecb0, already merged in; it did not move between the `tools/pr/prepr.sh` run and the handoff, so no second run.

## Mutation proof

Mutant M3 (the reviewer's): the `if (resolved.source === 'subject-gap' && !confirmGapMerge(...)) { return { ok: false, ... } }` block in `fetchPullsBySha` deleted. `node tools/policy/policy_lint.mjs` then printed `FIXTURE VACUOUS: resolvePrFromCommit ["an enumeration gap whose pull request merged at a different commit was trusted, or its refusal does not name both causes"]`, rc=1. Restored. The round-1 mutants M1, M2 and M4 (the helper) are still killed by the helper pins.

## Null control

Unmutated tree: `node tools/policy/policy_lint.mjs` prints `FIXTURE ok: 93 error(s) hold 266 pins across 12 check classes`, rc=0. The three new enumeration pins drive `fetchPullsBySha` with a stub getter: an API row (taken, absent from `gapShas`); an empty answer whose `/pulls/900` merge_commit_sha equals the sha (recovered, listed in `gapShas`); one whose merge commit differs (`ok:false`, the `why` matching "could not be read").

## Figures

Pins in the `FIXTURE ok` line: 263 at the reviewed head, 266 here (three added). Command: `node tools/policy/policy_lint.mjs | grep 'FIXTURE ok'`. `python3 tests/structure.py`: PASSED. `tools/pr/prepr.sh`: every step ok (gate mode SCOPED, self-test 486 passed, claim files byte-identical to origin/main, no version edit). Not run locally: `tests/entities.py` and goldens (the toolchain was not refreshed; CI is the authority). No golden touched.

## Red checks

none concluded: this head has not yet run in CI at handoff.

## Forward-carry

none

## Friction

none
