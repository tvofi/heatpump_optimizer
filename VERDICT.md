Fix review: merge 2845e5459331f79adbc39b72cd052cf55703f1aa

bus-nonce: 443aff6cb4135efdf0762caace83160b

Round 2 of R10-LIVESTATE (#2675). Measured head `2845e5459331f79adbc39b72cd052cf55703f1aa` from a detached worktree; merge base `144fb4f900768195c64469f9647ece583a54a52b` (origin/main tip). Head re-read before posting: unchanged, PR OPEN. Round 1 verdict: `review/2675` 1e36cdce4 (blocked carry-missing at a9e26e070).

## Round-1 blocker cured

- `python3 -I tools/audit/carry_audit.py check --body <current body>` at the head: `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (round 1: 1 bad destination, rc 1).
- `dev/programme/carries/carry-2674.json` (44aaa080a): `node tools/policy/brief_lint.mjs` reads it `0 error(s), 0 warning(s)`, rc 0. It states the control as a precondition (a lead is a finding only through ls-r1's probe with its null; a null not 0 is a broken probe; a fix without a reproducing probe is refused) and a re-measure instruction (establish per lead whether the writer runs in the first refresh, at the stage's own merge base, re-anchored by name).
- `tests/closures.json` (5c2fa6de5): the only branch-side change against round 1 besides the carry file is that one path added to `tests/entities.py`'s closure; the rest of the hunk is round 1's INERT READS entries at a shifted offset.

## The merge brings nothing beyond main's

- Production patch: `git diff 6120fb513 a9e26e070 -- custom_components` and `git diff 144fb4f90 2845e5459 -- custom_components` are byte-identical (`evidence/prod_delta.out`). Round 1's production measurements (finder harnesses at both ends, nulls, mutants, boost_drift_replay hh_scale identity) therefore carry.
- Three-dot file list against the merge base equals round 1's plus `dev/programme/carries/carry-2674.json`; `tests/features.py`, `tests/structure_budgets.json`, `tests/ci_budgets.json` diffs identical to round 1. Only `dev/programme/delivery/2675.md` among delivery rows. VERSION, manifest, RELEASE_NOTES, `tests/golden/` untouched. `git merge-tree --write-tree origin/main <head>` exit 0.

## Checks at this head (read after all concluded)

Every check-run at the head concluded success or skipped (`evidence/checks.tsv`), including `tests / fast (3.14)`, `tests / closures`, `tests / typing`, `tests / mutation`, `pr-contract` (two runs started 01:30Z and 01:58Z, both success) and `gate` (two, success). The `mutation` log evaluated mutants, not INCONCLUSIVE: it lists this diff's sites (`boost.py:515` GUARD_OFF, `coordinator.py:3458` CLAMP_DROP, `:5996`, `:9737` GUARD_OFF, `drift.py:65`/`:67`, `price_tiles.py:75` RETURN_DEL) each killed, then `MUTATION TABLE PASSED`.

## Red checks answered

- `pr-contract` at a9e26e070: named, process state (b), cheaper detector `carry_audit.py check --body` (< 1 s), recorded that prepr does not run it (confirmed: `tools/pr/prepr.sh` has no `carry_audit` call), no new countermeasure. Answered.
- `env-matrix`, `policy-docs` at a9e26e070: named, state (d), the pre-cut-over `required-contexts` fixture against the live ruleset; no cheaper detector; cured by the main merge. Answered.
- `typing`, `fast (3.14)`, R10-SAV-REASONS, `delivery-status`: unchanged from round 1, answered there.
- The CI-edit run 40048233274's attempts 1 and 2 failed `pr-contract`/`gate` in `tools/ci/codescan_wait.py` (rc 1, output redirected to `/tmp/pr-alerts.txt`), while `codeql / Analyze (python)` was still running; the step reads code-scanning results, not this diff, and later attempts at the same head went green. Not this diff's red, so not owed in the body.

## Non-blocking notes

- `codescan_wait.py` fails the first edit-run attempt(s) at a head whose CodeQL python leg has not finished, and prints nothing to the log because its stdout goes to `/tmp/pr-alerts.txt`; the orchestrator reports it as the recurring first-run red since the cut-over. Carry: dismissed: CI infrastructure outside this diff, already tracked by the orchestrator, which reported it in this dispatch
- `tools/pr/prepr.sh` does not run `carry_audit.py check --body`, the sub-second detector for round 1's blocker; the body records "no new countermeasure". Carry: dismissed: the body answers the root-cause trigger with the cost-test outcome, and fix-review checks that it was answered, not the answer
