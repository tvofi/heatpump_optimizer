# Sweep: "an approval bound to an exact head is re-bought on a diff-identical move"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D13-s1-02
(weakened(medium), medium). Not a ledger class (new).

## Enumerator

Reused verbatim from the finder (`tools/audit/round9/D13/s1/yield_rounds.mjs`,
already committed on this branch, not just the evidence branch); copied into
this sweep dir with its sibling data file (`window.json.gz`) and one relative
import path fixed for the extra directory depth
(`../../../../../.claude/...` -> `../../../../../../.claude/...`).

```
$ HPO_PLANDATA=$(mktemp -d) node tools/audit/round9/D14/sweep/approval_bound_exact_head/yield_rounds.mjs
RESULT reverify_rounds=22
RESULT reverify_blocked=0
RESULT reverify_moved_by_merges_only=11
RESULT reverify_moved_by_ci_bot_only=1
RESULT reverify_moved_by_branch_content=10
```

Reproduces the finding's numbers exactly: 22 re-verification rounds, 0
blocked, 12 (11+1) moved only by a merge commit or a `ci:` bot commit.

## Positive control

The re-run above IS the positive control (the finding's own metric, taken
from the merge/PR history window the script reads, which is fixed evidence,
not a live production seam a fresh checkout could diverge on).

## Null control

`reverify_moved_by_branch_content=10`: 10 of the 22 rounds moved on a real
content diff, and the script does not count those toward
`reverify_moved_by_merges_only`/`_ci_bot_only` — the partition is exhaustive
and disjoint (10 + 11 + 1 = 22), so the metric does not over-count content
moves as diff-identical ones.

## Perturbation

This is a process/governance metric (fix-review re-verification rounds
already recorded in PR history), not a live code seam with a one-line
mutant to reintroduce. The class's own mechanism — `fix-review.md`'s
re-verification triggers on any head move, whether or not the diff against
the previous reviewed head changed — is demonstrated by the split itself:
`reverify_moved_by_merges_only` + `_ci_bot_only` (12) is exactly the set of
rounds where the head moved but nothing in the diff a reviewer reads could
have changed, matching the finding's claim ("12 heads moved only by merges
or ci: commits").

## Baseline vs main

`tools/audit/briefs/fix-review.md`, `.claude/workflows/web-fix-wave.js` and
`tools/audit/app_approve.sh` are unchanged between `1936d5ca` and
`origin/main` (not in the 4-file diff list). The seam still exists on main.

## Disposition

| seam | disposition |
|---|---|
| `fix-review.md`'s re-verification trigger (any head move, not a diff-scoped one) | instance — D13-s1-02, the 12 diff-identical re-verification rounds the metric counts |

No historical instances: this is a process-metric class, not a ledger
class, and the finder's own scope (this round's merge/PR window) is the
whole population the metric can measure.

## Count

N = 1 verified finding + 0 sweep-confirmed instances = **1**. **rca: false**,
matching the brief.

## Barrier proposal

None built (N < 3); the finder's own scope (rerun re-verification only when
the diff against the last-reviewed head is non-empty) is the natural
barrier shape, left for a fixer/policy seat since `fix-review.md` is policy
and needs the owner's approval to change (`CLAUDE.md`'s policy rule).

## Gate seconds

~1s (reads a pre-fetched, gzipped merge/PR window; no live GitHub calls).
