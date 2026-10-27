Fix review: merge 4172ef7ca842ebce920bf5863ba3c78896f68406

bus-nonce: 6e5d13bd71aa75f4c99427d810ab1bff

Round 1, this head, re-read at posting. Four triage rulings whose premises I re-measured
in the tree; no blocking finding. The diff writes no production line: two markdown files over
merge base `2b45d098c`, so no harness class rule is owed and no instrument moves.

## Evidence

- P207 premise confirmed: `tools/audit/seat/queue_pre_flight.py:176` defines `findings_gate`, 192
  short-circuits on `ca.finding_rows(body, comments)[0]`, 199 calls `ca.audit(body, comments,
  self.dests)`; `push_verdict()` opens at `tools/audit/seat/bus.sh:200` with `append_commit
  review` at 228; `git grep -n 'carry_audit' origin/main -- tools/audit/seat/bus.sh` prints
  nothing; the `review/7` arm the body cites is at bus.sh:1209-1221.
  Carry: dismissed: premise confirmed in tree

- P207 cost re-measured: three runs of `python3 -I tools/audit/carry_audit.py --roster-ref
  origin/main check --body <no-finding body>` printed `real 0.75 / 0.94 / 0.84`; `load_dests`
  printed `real 0.76` on origin/main and `0.68` on the round ref (record: 0.64/0.62/0.60, 0.63,
  1.13). "About 1-2 s per verdict" holds; the individual figures did not reproduce here.
  Carry: dismissed: figure re-measured within bound

- P208 premise confirmed: the `## Head` gate exists as `body_check()` at
  `tools/pr/prepr.sh:681`, called by `body_line()` at 793 and invoked from step 7 at 3462;
  step 1b at 3120 and steps 2-6f at 3163-3426 all run before it, so the early call it
  proposes is the existing check and no second parser is implied. `preflight` is logged at 77
  before `pr-body` at 78, so "step 7's first arm" holds of the body sub-checks the ruling
  turns on, not of every step-7 line.
  Carry: dismissed: premise confirmed in tree

- P208 cited range contradicted, not blocking: `grep -n` over
  `~/.local/state/hpo/pr/r10-buffer-store/p1.log` puts `REFUSE pr-body` at 78 and
  `ok figures` / `ok carry` / `ok unpinned sites` at 79/80/81, not the record's 82-85 (those
  lines are the push-order and ancestry skips and `PRE-PR:`). The order the correction draws
  is unaffected: the refusal is 78, before the three ok lines.
  Carry: dismissed: order claim unaffected

- P209 premise confirmed: `tests/entities.py:22387` carries the five-branches/ten-conflicts
  sentence; 22423 is `_CM_MERGED`, 22433 and 22442 pin the stamp/header/may-drift and
  comment-only shapes, 22449/22450 are the two claim constants and 22455 the `is None` pin;
  `tests/env_drift.py:1790-1792` parse base/ours/theirs. `_CM_BASE` and the two note constants
  carry no claim line, so the refusing case is exactly disjoint additions. A direct call with
  a deletion shape returns None, and the binding's `ours >= base` / `theirs >= base` predicate
  excludes it, so the retained refusal covers it.
  Carry: dismissed: premise confirmed in tree

- P209 policy sentence confirmed: `dev/governance/rules/claim-files.md:17` says the driver
  refuses "when both sides rewrote the bare claim list", which the union change makes false
  for disjoint additions; the record routes that edit to the fix's own pull request under the
  owner's review, as the policy file requires.
  Carry: dismissed: policy edit routed to fix

- P210 premise confirmed: `git show origin/main:tests/closures.json | grep -n
  '"tools/policy/field_coverage.mjs":'` prints nothing; the plain path matches line 1642
  inside a closure's file list, and the 34-key `recorded` map names no field-coverage script.
  `tools/pr/prepr.sh:3246` runs the step in 3f3, 3f4 opens at 3253, and `heavy_run()` at 605
  arms no wall-clock timeout.
  Carry: dismissed: premise confirmed in tree

- P210 mutant moves the check: planting `"tools/policy/field_coverage.mjs":
  {"rc":0,"seconds":52.5}` under `recorded` in `~/hpo-seats/r10s6/review-2884/ev/closures-mutant.json`
  makes the key-form grep print 1; the null control `closures-null.json` prints 0, its plain
  grep 1 from line 1642. The absence claim is falsifiable by its own command.
  Carry: dismissed: mutant moves the check

- Destinations live: on `origin/handoff/audit-r10-roster` (211 groups) the three ACCEPT groups
  are `R10-FLY-CARRY-DISPOSITION` not-started, `R10-996-RUNNER-CLAIMS` carries-open and
  `R10-RCA-BODY-LINT` fixing; their `files` name the files each carry touches, and
  R10-FLY-CARRY-DISPOSITION is the only group naming both `carry_audit.py` and `bus.sh`.
  Non-blocking: the record says `R10-RCA-BODY-LINT` is `done`, true at its 17:10Z sample but
  moved to `fixing` at 98997696f (17:37:49Z), so the prescribed reopen is no longer owed; the
  group remains a live destination.
  Carry: R10-RCA-BODY-LINT

- Delivery row confirmed: `dev/programme/delivery/2884.md` names #2884, `**open**`, the
  batch-39 title and the `triage-s6-batch39` branch; the PR body's `## Head` names this head
  `4172ef7c…` and the authored code head `cd75ce705…`, and the record is byte-identical to
  that blob (`git rev-parse` prints `2ddf8791…` at both; the diff is empty).
  Carry: dismissed: row current at head

- Mutation proof reproduced with the seat's own harness: `roster_edit.ruling_verdict` prints
  ACCEPT/ACCEPT/ACCEPT/DEFER for P207-P210 and None for P999; a P210 cite is refused "not an
  ACCEPT ruling (DEFER)"; an out-of-tree copy with P207 flipped to DEFER is refused the same
  way; a missing file is refused.
  Carry: dismissed: proof reproduced

- No red check at this commit: the check-runs list has no failed or cancelled conclusion;
  `tests / coverage` and `governance / instrument-self-tests` were in progress at posting, so
  the root-cause trigger is not fired. `git merge-tree --write-tree origin/main HEAD` exits 0.
  Carry: dismissed: no red check

- Arms run and not run: ran the four premise checks, the mutation proof, the P210 mutant with
  its null control, merge-tree, the head's check-runs and `carry_audit pr 2884`. Did not run
  a full `prepr.sh`, `field coverage`, any gate lane, or the claim-drift runners (the diff
  touches no claim file), per the cost discipline.
  Carry: dismissed: cost discipline held

## Forward-carry

none

## Friction

none
