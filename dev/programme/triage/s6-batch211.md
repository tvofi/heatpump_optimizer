# Proposal triage, session s14, batch 211

Sources: triage queue lines 320, 321 and 322, three PROPOSAL lines (orchestrator s14,
2026-11-11T17:55:15Z), ruled as P642, P643 and P644. Line numbers are at origin/main c71d3f6e89.

## P642: the carry-fold level drops a handoff-wip ref its topic has superseded

Verdict: ACCEPT, as a carry on R10-RELAY-NOBODY-STALL.

Source: triage queue line 320. `cloud_relay.sh dispose` (:322) accepts only probe/, handoff/,
handoff-body/ and review/ refs. carry_fold_arm (:805-849), however, puts every
handoff-wip/<topic> whose BLOCKED.md is not CARRY-LANDED alone on the carry-fold level, every pass.
A line there is discharged only by deleting the ref.

Instances (2026-11-11, local state and git only):
- `grep carry-fold cloud-relay.log.level` gives 20 OWED carry-fold lines, written 17:26-17:30Z.
- For each line, the topic was checked against two signs that it is superseded. The first is a
  handoff-body/<topic> (from `git ls-remote origin 'refs/heads/handoff-body/*'`) whose committer
  time is later than the wip commit's. The second is a merge on origin/main from
  fix/<topic>[-pr] (`git log origin/main --format=%s`).
- 14 of the 20 are superseded:
  - ci-edit-runner;
  - combi-tank-pr (#3358 merged);
  - dependabot-3414-compat (#3426 merged);
  - hotfix-combi-census-main-red (#3466 merged);
  - mutant-run-forkcap;
  - outside-disinfection-setpoint;
  - outside-supply-stale-step;
  - plan-page-residue;
  - rca-dependabot-stale-hash (#3429 merged);
  - rca-restore-base-skew (#3438 merged);
  - relay-arm-order;
  - review-dispatch-residue-p3 (#3450 merged);
  - sav-valuation-residue;
  - standing-contracts-p2.

  These include the proposal's five (forkcap b0b75526, disinfection-setpoint 7769fe7f,
  relay-arm-order 347b713f, review-dispatch-residue-p3 8b91a9b4 and sav-valuation 35bdd7aa).
- The other 6 are not superseded by either test:
  - arbiter-off-restore;
  - duty-switch-restart-learning;
  - ext-3226-recut;
  - fly-cloud-frugal-off;
  - hotfix-restore-base-skew;
  - process-slim.

The rule, run per instance:
- Measure: carry-fold level lines that are false (their topic has moved on). That is 14 of 20
  (70%), and each prints on every tick as an OWED line nobody can discharge. The fix takes the 14
  to 0 and leaves the 6 live lines unchanged.
- The proposal's other candidate, dispose accepting handoff-wip/, would still cost one manual
  action per line (14 today). It is rejected for that reason.
- Severity: medium, R10-RELAY-NOBODY-STALL's roster severity. That group owns cloud_relay.sh, is
  not started, and its seam is the refused body kept on handoff-wip (keep_refused).

Cost:
- About 10 lines in carry_fold_arm. The handoff-body/* pattern joins the arm's existing
  `git ls-remote` call, and the merged test is a local `git log` on origin/main. No API call.
- Two self-test assertions in the existing carry-fold block (:1827-1847).
- No new file and no new check. cloud_relay.sh has no row in tests/structure_budgets.json, and no
  policy_budgets.json measure moves.

Binding: 70% false OWED lines removed, for about 10 lines in a file the group already edits.

Bar: severity medium (R10-RELAY-NOBODY-STALL). Figure: 14 of 20 carry-fold level lines (70%),
over 20%, on the measure above. Basis: over-20%, and also a severity-exempt defect repair
(medium). It is a carry on an existing group, so no new group starts.

Destination: append-carry on R10-RELAY-NOBODY-STALL, with this text:

> CARRY-FOLD-SUPERSEDED (triage P642). carry_fold_arm in tools/audit/seat/cloud_relay.sh puts
> every handoff-wip/<topic> that is not CARRY-LANDED alone on the carry-fold level, every pass.
> dispose refuses handoff-wip/ refs, so only deleting the ref clears such a line. On 2026-11-11, 14
> of 20 carry-fold level lines had a topic that had moved on.
> Repair: the arm writes no level line, and folds nothing, for a wip ref whose topic either (a) has
> a handoff-body/<topic> whose committer time is later than the wip commit's, or (b) has
> fix/<topic> or fix/<topic>-pr merged into origin/main (a local git log, no API). handoff-body/*
> joins the arm's existing ls-remote. Do not widen dispose to handoff-wip/.
> Demonstration: in the carry-fold self-test, a wip ref with a later handoff-body is absent from
> the level, and so is one whose fix branch merged. Both fail on the base and pass on the fix.
> Null control: a wip ref with no handoff-body and no merge keeps its OWED line.

## P643: the opener skips a moved handoff tip until the relay pass ends

Verdict:
- REJECT part (a), the opener re-reading the tip: it is already accepted and routed.
- REJECT part (b), publishing the handoff-no-pr level on tip moves: a second writer for the same
  end.
- DEFER part (c), the STALE CHECKOUT refusal.

Source: triage queue line 321. open_driver.py (:278-279) skips `moved` when origin's tip differs
from the board's sha. The board's handoff-no-pr lines are written once per relay pass, before the
serial update loop (cloud_relay.sh handoff_level, :554-569).

Instances (open-driver/open-driver.log, 2026-11-11):
- `grep -E '^2026-11-11' open-driver.log | grep -cE 'SKIP \S+ \S+ moved'` gives 49 moved skips,
  over 7 topics:
  - r10-outside-supply-stale-step: 16;
  - r10-hotfix-replay-class-cut: 9 (17:09-17:48Z, a hotfix);
  - r10-outside-disinfection-setpoint: 9 (09:53-10:33Z; PR #3452 opened 10:32Z);
  - r10-process-slim-p2: 9 (03:09-09:13Z; PR #3451 opened 09:22Z);
  - r10-outside-climate-native-temp: 3;
  - r10-mutant-run-forkcap: 2;
  - r10-train-residue-p2: 1.

  The same day had 66 RESULT lines.
- STALE CHECKOUT: `grep -h 'STALE CHECKOUT' open-driver/t-*.log` gives 3 refusals. Two are in
  RESULT lines at 17:53:52Z (r10-hotfix-replay-class-cut fdab889c and
  r10-outside-supply-stale-step 68646456): the beat's tools checkout a7887485 was 4 commits behind
  origin/main c71d3f6e89 on tools/.

The rule, run per part:
- Part (a) is OPENER-LIVE-TIP (triage: dev/programme/triage/s6-batch183.md#P603), which re-runs the
  candidate checks at the live tip instead of skipping `moved`. It is already on the roster: it was
  moved by the orchestrator's ruling on #3465 to R10-SEAT-IDENTITY-P5 (severity medium, not
  started, which lists open_driver.py), as carries 6 and 7.
  - A second carry would duplicate it.
  - The figure has grown: P603 counted 18 moved skips, and today has 49, including a hotfix held
    39 min and process-slim-p2 held about 6 h before its PR opened.
  - That figure is for the orchestrator's priority call on starting R10-SEAT-IDENTITY-P5's opener
    seam under the open-PR cap. It is not a new triage ACCEPT.
- Part (b) solves the same latency by another route, a second writer of the handoff-no-pr level
  inside the serial loop. Part (a) removes the dependency on the level's freshness altogether.
  Duplicate machinery, rejected.
- Part (c) is a correct refusal: open_pr.sh refuses to run from a checkout behind main on tools/.
  Its cost today is 2 of 66 opener results (3%), under 20% and unclassified (no group owns the
  beat checkout's freshness), so it is classified normal. It would change on either of two events:
  stale-checkout refusals reaching 20% of a day's opener results, or the red-check root-cause
  trigger firing for a refusal (`defect-root-cause.md`). Until then the orchestrator's checkout
  rotation (a fresh branch-backed worktree) stays the remedy.

Cost: none for (a), which is already planned. (b) is a second level writer in cloud_relay.sh, a
hot file three groups edit. (c) would be a new sync mechanism for a 3% event.

Binding: (a) is already planned. (b) duplicates (a) at the cost of a hot-file edit. (c) is
measured under 20% at normal severity.

## P644: a refused record write prints OWED although the record posted

Verdict: ACCEPT, as a carry on R10-TICK-RESIDUE-P3.

Source: triage queue line 322. record_beat.py record() (:123-137) raises Owed whenever
`gh_comment.py post` exits non-zero. postmerge.py then prints `#<pr> OWED record`, and `--retry`
(:96) posts again. On 2026-11-11 the record comment already existed when the OWED printed, so each
retry posted a duplicate.

Instances:
- Local:
  - s14/seat/merge/s14-4/pm3447.out: "OWED record: the #3394 comment was refused (1: gh shim: a
    comment write on a record issue ...)".
  - s14/seat/merge/STATE-HANDOFF.md: "#3466 and #3472 both logged OWED record (gh shim refused the
    #3394 comment)", and a `postmerge.py --retry 3466` run.
- Orchestrator's figures, cited and not re-read through the API: record comments 6802888538,
  6803025015 and 6803121283 existed, and the retries made duplicates 6803196345, 6803198573 and
  6803199372.
- Denominator: `git log origin/main --first-parent --since=2026-11-11T00:00Z --format=%s | grep -c
  '^Merge pull request'` gives 30 merges.
- The checkout is not the cause:
  - The installed shim's gcpy is tools-wt-63bcdcaa.
  - The train's batch-wt shares its git common dir, and is listed by that tree's `git worktree
    list`, so the P449 sibling-worktree admission (seat-gh :340-353) applies to it.
  - The refused write's cause is therefore not established. That is for the fixer.

The rule, run per instance:
- Measure: record runs that print a false OWED. That is 3 of 30 merges today (10%), each costing a
  duplicate public comment on #3394 and a retry run. Under 20%.
- Severity: medium, R10-TICK-RESIDUE-P3's roster severity. That group is not started and owns
  postmerge.py and record_beat.py. A false OWED on the owner's record issue, which writes
  duplicate public comments, is a defect repair.
- Candidate (b), reading the record back before printing OWED, is the one taken. It makes the
  record idempotent whatever the second writer turns out to be. Candidate (a), finding the writer,
  is owed inside the same carry as its diagnosis. Accepting it alone would accept an unmeasured
  investigation.

Cost:
- About 15 lines in record_beat.py: one read of #3394 through gh_comment.py's existing thread
  fetch (:206), only on a non-zero exit and on `--retry`. No read on the clean path.
- Two self-test assertions.
- No new file and no new check. No structure_budgets.json row for either file.

Binding: duplicate public record comments and false OWED lines removed, at one conditional read.

Bar: severity medium (R10-TICK-RESIDUE-P3). Figure: 3 of 30 merges (10%), under 20%. Basis:
severity-exempt defect repair (medium) only. On the 20% bar alone it would be REJECTed. It is a
carry on an existing group, so no new group starts.

Destination: append-carry on R10-TICK-RESIDUE-P3, with this text:

> RECORD-OWED-READBACK (triage P644). tools/audit/seat/record_beat.py record() raises Owed whenever
> `gh_comment.py post` exits non-zero, so postmerge.py prints `#<pr> OWED record` and `--retry`
> posts again. On 2026-11-11 the #3394 record had already posted three times (#3447, #3466, #3472)
> when the gh shim refusal printed OWED, and the retries left three duplicate comments.
> Repair: before raising Owed, and before any `--retry` post, record() reads #3394 through
> gh_comment.py's thread fetch for a comment whose body equals the rendered record. If one exists,
> the PR is recorded: no OWED, no second post. Also name the second write the shim refuses after
> the POST: the shim log or gh_calls.log at the refusal. Fix it, or state why it is harmless.
> Demonstration: in record_beat's self-test, a post that exits 1 while the thread already holds
> the record prints `recorded`, not OWED, and a retry posts nothing. Both fail on the base and pass
> on the fix. Null control: an exit 1 with no such comment in the thread stays OWED.
