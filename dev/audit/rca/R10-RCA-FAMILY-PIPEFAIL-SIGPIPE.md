# R10-RCA-FAMILY-PIPEFAIL-SIGPIPE: an early-exit reader on a pipe under pipefail

Round-end family analysis (loop card L8). Measured at `origin/main` `a39627da59` on 2026-11-15.
Lands no code.

## 1. Instances

HANDOVER's count, family `pipefail-sigpipe`, three sites in round 10's last days:
- `tools/audit/seat/app_approve.sh`'s carry-tip read, introduced by #3514 (merged
  2026-11-14T17:00:16Z, `6790cd3fd8`): `printf` of about 8000 head lines into `grep -q` under
  `pipefail`; every own head read "no branch tip of origin", so `review_carry` printed
  FRESH-REVIEW and the relay HELD-STALE for every head (sweep lines 2354, 2358);
- the `gh_transient` census row of the same instrument's self-test, flaky on #3532 for the same
  cause (line 2358);
- `tools/audit/seat/open_pr.sh` near line 125, now a here-string with the comment naming the
  hazard.

The class is older: `09d2061b24` (2026-10-09, "drain every early-exit grep under pipefail in
the gating scripts") and `bca74aa97b` (2026-10-10) repaired the same shape; the hotfix's own
body counts it in comments at `prepr.sh` 216, 1881, 3664, `app_approve.sh` 1088,
`cloud_relay.sh` 308, `seat_venv.sh` 254 and `tick_loop.sh` 213 (intake carry 149).

No required check turned red; the regression reached main and broke an instrument for every
pull request. The family qualifies on count.

## 2. Named cause

Under `set -o pipefail`, a reader that exits at its first match (`grep -q`, `head`) closes the
pipe while the producer is still writing; the producer dies of SIGPIPE (141) and the pipeline's
status is the producer's, so a found match reads as failure. It bites only when the producer's
output exceeds the pipe buffer, so a test on a small fixture passes and production input fails.
Sites today: 237 `| grep -q` sites in the 42 `pipefail` shell files under `tools/` and 51 `|
head` sites (`git grep -n -E '\|[[:space:]]*grep -[a-zA-Z]*q'` per file), most with small
producers and harmless.

## 3. Process state: (c)

The round-9 countermeasure was a sweep of existing sites plus comments; it was followed, and it
did not stop new sites, because nothing reads an added line for the shape. Not (a): the hazard
was named and repaired before. Not (b): no seat skipped an instruction; none exists for new
code.

## 4. Class reach

Every new shell line in `tools/` under `pipefail` that feeds an early-exit reader; the round-10
Darwin-only reds (`wc -l` padding compared as a string) are the same kind of host- or
input-size-dependent shell hazard, which is why the countermeasure is one lint.

## 5. Cost test

- cost(defect): #3514's regression held every own head's carry read false from 17:00Z to the
  hotfix's merge at 20:27Z (`9acc181ca7`), about 3 h 27 min, with a local workaround from about
  17:19Z; one hotfix group (roster append 18:30Z to merge 20:27Z, 1 h 56 min) and one flaky
  self-test row.
- P(recurrence): three in round 10's last two days; two sweeps in round 9.
- cost(countermeasure, recurring): a diff-scoped scan of added shell lines in `prepr.sh`, under
  one second per run; it reads only added lines, so the 237 existing sites cost nothing.

Passes on the first instance a round.

## 6. Countermeasure

One diff-scoped lint in `tools/pr/prepr.sh`, on added lines of `tools/**/*.sh` only: refuse an
early-exit reader (`grep -q`, `grep -m`, `head`) fed by a pipe in a file that sets `pipefail`,
and print the here-string rewrite (L2: the refusal prints its own repair). It ships with the raw
`wc -l` string-compare lint as one shell-hazard step in R10-PREPR-DARWIN-SELFTEST-LANE, re-cut
(triage `dev/programme/triage/r10-round-end.md#P761` and `#P787`). Demonstration owed: the lint
red on `cb803e9eed^`'s `app_approve.sh` hunk and green at `cb803e9eed`; null control, a
here-string and a `|| true` drained pipe pass; shadow count on the last 20 merged heads before it
gates (L2).
