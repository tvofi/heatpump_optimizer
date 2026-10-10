Fix review: merge 9eed9898b78297c47851619daa7171952c914727

bus-nonce: 33bb21e4acaa278f76b8f49c39ae556b

PR #2124 (R9-RC-POSTREVIEW-MERGE class RCA, issue #2096). Measured at head
`9eed9898b78297c47851619daa7171952c914727` (authored head `9a901e7abab9d2bdd2792a1b0208614659922333`,
one delivery-row commit on top) in a detached worktree; head confirmed unmoved
at publish. Evidence: `/Users/timmalmstrom/hpo-seats/r9rev-2124/ev/` (HEAD-EVIDENCE.md names the head).

## The agreement lane — run by this reviewer at both ends

At the head: `pair finding-class-id: 3 readers, 38 items, 0 divergent` —
AGREEMENT ok, rc 0. At the parent `0cb141661` (the refused first attempt, which
is also the registration commit's mutant): the DIVERGENT row reproduces
verbatim — `bugclasses.json ids + "new"=true  finding.schema.json enum=false
audit-find.js CLASS_GUESS (intake)=false` — rc 1. Failing-first arm confirmed:
this is the check that refused, and the registration commit turns exactly it green.

## The two reproductions — confirmed

- #2072: `pipe_grep_q_sites` at `04d10721b` rc 1 with exactly one site,
  `prepr.sh:1398: printf '%s\n' "$flow" | grep -q 'moved_line "'` (0.099 s);
  null controls rc 0 at `23d354970`, `00e31e8a3` and live `origin/main`;
  merge base `bd59a4af1` rc 1 with 4 sites. CI check-runs API: instrument-self-tests
  failure completed 21:47:51Z and pr-contract failure at `04d10721b`, zero
  failures at reviewed parent `316a36414`. My own run of `prepr.sh --self-test`
  at `04d10721b`: rc=2, 134 s (finder 122 s), `243 passed, 1 failed`, FAIL row
  byte-identical to CI's. Timeline 21:47:51Z → 07:29:47Z (9 h 42 m) → 12:11:35Z
  (14 h 24 m) re-derived from git and the PR API.
- #2066: `merge-tree` 0 conflicts against `d0f085ffb` at both heads; conflicts
  against `23d354970` (my counts 53/56 vs the finder's 27/30 — same command
  shape; the direction the claim needs reproduces at both heads; the count
  difference is noted, not explained away).

## The class is genuinely new

`N-postreview-merge-red` overlaps no existing entry. `nearest_existing: I3`
("a required check is skipped, runs a stale ref, or has a bypassable boundary")
is distinguished honestly and the difference is real: no check was improperly
skipped and none ran a stale ref — #2069's fast-path is designed behaviour whose
predicate cannot see the interaction of the two deltas; the countermeasure the
distinction motivates (change the unit, not re-arm a check) would be wrong under
I3. `N-approval-rebuy` (diff-identical head moves re-buying review) is a
different mechanism. Non-audit instances are `non_round_instances`, counted
nowhere — honest.

## Process state (c) — agreed

The recarry verdict ran exactly as written and the train's CI step stopped on
the red; nothing red merged. Not (a): `prepr.sh` step 3h existed and `selftest_owed`
held for this carry (`tools/pr/prepr.sh` in the three-dot diff). Not (b): no
instruction was disobeyed. Not (d): #2069's premise was incomplete as shipped,
not sound-then-broken. The state maps to the countermeasure actually proposed
(a unit change to what "clean" means), which is the contract's own test for a
correct state finding.

## The census — NOT reproduced as stated; direction conservative

The stated enumerator (`git log --all --since=2026-10-08 --grep=...`, mirrored
in `bugclasses.json`'s `detector` field) yields **124** recarry-shaped merges
over the same window against origin-visible refs, not 76; the finder's 76 is a
strict subset (their ref set was narrower). 36 of the 48 missed merges were
pushed and CI-graded; 11 more were green at parent 1 and reddened by the merge
(parents verified via check-runs). Corrected: ~26 merge-reddened of ~112-124
(~8.7/day, ~21%) vs the stated 15/76 (~5/day, 19.7%). Every correction enlarges
the defect side: the cost test passes a fortiori (standing cost at ~41
recarries/day ≈ 55 min/day vs defect ≈ 4.3 h/day at the corrected rate).
The `detector` text in `bugclasses.json` carries the undercounted figures and
should be refreshed when next re-measured; this does not block, because the
RCA's conclusion survives — is strengthened by — the correction.

## Red checks — none unanswered

No failing check-run at any head of this branch CI graded (head: 23 success,
0 failure, 14 skipped, 1 neutral, 2 still running at review time). The one red
in the body's account — the local prepr agreement lane at the parent — is named
and answered ("no cheaper detector: the lane is itself the comparison") and
demonstrated above. harness-headers inputs are byte-identical merge-base..head;
that red is main's, as claimed. fold_ledger check: 29 classes, 0 violations.
Structure ratchet passed; claims hygiene ok; VERSION/manifest/notes untouched.

## Mutation proof and forward-carry

No production code: the registration commit's failing-first arm is the agreement
lane itself, run above at both ends by this reviewer. The two propagation
sentences (countermeasure fixer brief; carry-lane budget-raise sub-shape) are in
the merged tree at `dev/audit/rca/R9-RC-POSTREVIEW-MERGE.md` section 7 with exact
text and named destinations; the r9 carry-lane brief file does not exist in-tree
at this head, so this PR could not have carried it in-tree — the orchestrator
owes the section-7 application when the countermeasure is dispatched. Recorded,
not blocking.

## Verdict

merge. The class is new and three-reader-registered; the reproductions, the
null controls, the timeline arithmetic and the process state all reproduce
under this reviewer's own runs. The census denominator and rate are undercounts
that the stated enumerator does not reproduce from a full ref set — reported
above rather than confirmed, and conservative in the direction that strengthens
the RCA's conclusion.
