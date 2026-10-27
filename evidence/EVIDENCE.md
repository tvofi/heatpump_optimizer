# #2884 evidence — head 4172ef7ca842ebce920bf5863ba3c78896f68406

Worktree: `~/hpo-seats/r10s6/review-2884/wt` at the head above. Diff against
merge base `2b45d098c92ed880a37a2848eac99713c3a2730b`: two files,
`dev/programme/triage/s6-batch39.md` and `dev/programme/delivery/2884.md`.

RESULT p207-tree: `queue_pre_flight.py` `findings_gate` at 176, `finding_rows` short-circuit at
192, `ca.audit(body, comments, self.dests)` at 199; `bus.sh` `push_verdict()` at 200,
`append_commit review` at 228; `git grep -n 'carry_audit' origin/main -- tools/audit/seat/bus.sh`
prints nothing.

RESULT p207-cost: `/usr/bin/time -p python3 -I tools/audit/carry_audit.py --roster-ref origin/main
check --body <no-finding body>` printed `real 0.75 / 0.94 / 0.84` over three runs;
`load_dests('.', 'origin/main')` `real 0.76`, `load_dests('.',
'origin/handoff/audit-r10-roster')` `real 0.68`. The record prints 0.64/0.62/0.60, 0.63 and
1.13. The ruling's "about 1-2 s per verdict" holds; the individual figures did not reproduce.

RESULT p208-tree: the `## Head` gate is `body_check()` at `tools/pr/prepr.sh:681`, called by
`body_line()` at 793, invoked from step 7 at 3462; step 1b at 3120 and steps 2-6f at
3163-3426 run before it. `heavy_run()` at 605.

RESULT p208-log: `grep -n 'REFUSE\|ok       figures\|ok       carry\|ok       unpinned'
~/.local/state/hpo/pr/r10-buffer-store/p1.log` prints REFUSE pr-body at 78, `ok figures` at
79, `ok carry` at 80, `ok unpinned sites` at 81, `app_push: REFUSE` at 86.
The record cites the three ok lines at 82-85; 82-85 in that file are the push-order and
ancestry skips and `PRE-PR:`. The order the record draws (78 before the three oks) holds.

RESULT p209-tree: `tests/entities.py:22387` carries the five-branches/ten-conflicts sentence;
22423 is `_CM_MERGED`; 22433 and 22442 are the stamp/header/may-drift and comment-only checks;
22449/22450 are `_CM_OURS_CLAIM`/`_CM_THEIRS_CLAIM` and 22455 is the `... is None` pin;
`tests/env_drift.py:1790-1792` parse base/ours/theirs claim maps. `_CM_BASE` (22394-22401) and
`_CM_OURS`/`_CM_THEIRS` carry no claim lines, so the refusing case is disjoint additions.

RESULT p209-deletion: direct call, base with claim A, ours dropping A, theirs keeping A and
adding B -> `merge_claim_file` returns None. Disjoint adds also return None today; one-sided
add merges. The binding's `ours >= base`, `theirs >= base` predicate excludes the deletion shape.

RESULT p210-absence: `git show origin/main:tests/closures.json | grep -n
'"tools/policy/field_coverage.mjs":'` prints nothing; the plain path matches only line 1642,
inside a closure's file list; the `recorded` map has 34 keys and none names field coverage.

RESULT p210-mutant: `~/hpo-seats/r10s6/review-2884/ev/closures-mutant.json` plants
`"tools/policy/field_coverage.mjs": {"rc":0,"seconds":52.5}` under `recorded`; the key-form
grep prints 1 there and 0 in the null control `closures-null.json` (whose plain grep prints 1,
from line 1642). The check moves under its own perturbation.

RESULT muproof: `ruling_verdict` on the committed file prints ACCEPT/ACCEPT/ACCEPT/DEFER for
P207-P210 and None for P999; a P210 cite is refused "not an ACCEPT ruling (DEFER)"; an
out-of-tree copy with P207 flipped to DEFER is refused the same way; a missing file is refused.

RESULT byte-identity: `git rev-parse HEAD:dev/programme/triage/s6-batch39.md` and
`cd75ce705:dev/programme/triage/s6-batch39.md` both print
`2ddf87911d1390e3bb4922d1db316d47ccf6fd0c`; the diff between them is empty.

RESULT destinations: on `origin/handoff/audit-r10-roster` (211 groups; origin/main has 208):
R10-FLY-CARRY-DISPOSITION `not-started`, R10-RCA-BODY-LINT `fixing`, R10-996-RUNNER-CLAIMS
`carries-open`, R10-PREPR-CAP `done`. R10-FLY-CARRY-DISPOSITION is the only group whose `files`
name both `tools/audit/carry_audit.py` and `tools/audit/seat/bus.sh`.

RESULT stage-move: commit 98997696f on the roster branch, 2026-10-27T17:37:49+01:00
(17:37:49Z), sets R10-RCA-BODY-LINT from `done` to `fixing`; the record's own samples are at
17:10Z, so the record's `done` was true when written and is not true at this head.

RESULT head: PR 2884 is OPEN, `headRefOid` 4172ef7ca842ebce920bf5863ba3c78896f68406.
Check-runs at that commit: no failed or cancelled conclusion; `tests / coverage` and
`governance / instrument-self-tests` in progress; all other completed runs success.

RESULT merge-tree: `git merge-tree --write-tree origin/main HEAD` exits 0 with tree
edfb362f27c9fea2b91ad39e8d5983121f358f0c (no conflict).

RESULT carry-audit-pr: `python3 -I tools/audit/carry_audit.py --roster-ref
origin/handoff/audit-r10-roster pr 2884` -> `CARRY-AUDIT #2884: 0 finding item(s): 0 routed,
0 unrouted, 0 bad destination(s)`.
