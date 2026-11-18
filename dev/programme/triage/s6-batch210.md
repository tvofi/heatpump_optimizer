# Proposal triage, session s14, batch 210

Sources:
- Triage queue line 319, PROPOSAL (orchestrator s14, 2026-11-11T17:27:12Z): ruled as P641.
- Triage queue line 318, PRODUCT-RULING (orchestrator s14, via triage s14-24), from #3452 body
  items 7052beca and 9ac8c410, group R10-OUTSIDE-DISINFECTION-SETPOINT.
- origin/handoff-body/r10-product-ruling-dhw-hard-max at d507c499, `BODY.md` line 1.

## Record: triage queue line 318 ruled by a fable seat

Not a triage ruling: a product ruling, which is not this seat's to make. The orchestrator routed it to
a fable triage seat. This entry only records the result and the marks it leaves owed.

Ruled-by: fable seat, origin/handoff-body/r10-product-ruling-dhw-hard-max (d507c499). First line:
"Ruling: (1) round-down (2) respect-and-surface".

Questions, as queued on line 318, both on `dhw_hard_max_temp`:
1. May a no-cycle write round an off-step everyday set-point up past the user's hard maximum, or
   must it round down to the step at or below it? Ruled: round down.
2. When the hard maximum leaves a disinfection cycle short of the legionella guard's credit
   thresholds on a coarse step, does the optimizer respect the hard maximum and surface that the cycle
   cannot be credited, or raise the ceiling? Ruled: respect the hard maximum and surface it.

Owed (orchestrator s14 split, under mandate, 2026-11-11):
- Ruling (1) is part 2 of R10-OUTSIDE-DISINFECTION-SETPOINT, its own pull request after part 1
  merges. It discharges carry 7052beca (landed at 2ad7130319), marked `implemented` at part 2's merge.
- Ruling (2) is a new group, R10-DISINFECTION-STEP-NOTICE (source outside, after
  R10-OUTSIDE-DISINFECTION-SETPOINT). It is outside-sourced, so the over-20 freeze does not hold it.
  Carry 9ac8c410 (landed at ff4fefa44e) moves to it: an append-carry there, and the copy on
  R10-OUTSIDE-DISINFECTION-SETPOINT is marked `moved`. It is marked `implemented` at that group's merge.

Queue line 318 is ruled.

## P641: a reviewer dispatched at the handoff after its PR exists is re-keyed at dispatch

Verdict: ACCEPT, as a carry on R10-REVIEW-DISPATCH-RESIDUE (it rides the group's next part).

Source: triage queue line 319, PROPOSAL (orchestrator s14). `bus.sh dispatch-handoff` records
`topic:<topic>`, and only `open_pr.sh` runs `bus.sh rekey` (open_pr.sh :154 at origin/main). A
reviewer dispatched at the handoff after the PR already opened is never re-keyed, so
`cloud_relay.sh` topic_verdict (its `mut:topicheld` arm) reports HELD-NOPR every pass and never
posts the verdict.

Instances (all 2026-11-11; local state before the API, one graphql read for PR creation times):
- Handoff dispatches today: `grep -c '^topic:' ~/.zcode/bus/dispatched` gives 42.
- Of those, 14 were dispatched after their PR's createdAt (PR createdAt from one graphql read of
  the last 60 PRs; dispatch time is field 5 of the `topic:` record):
  - r10-process-slim-p2 9c5485e3 (#3451, opened 09:22Z; dispatched 15:38Z);
  - r10-gh-read-residue-p2 01164518 (#3462, 11:49Z; 13:24Z);
  - r10-relay-arm-order befd1f54 and 9647bc11 (#3465, 12:19Z; 13:40Z and 14:35Z);
  - r10-codeql-pr-paths 04a1f28c (#3467, 13:00Z; 14:45Z);
  - r10-train-residue-p2 cb30b77f (#3470, 13:17Z; 14:07Z);
  - r10-mutant-run-forkcap e87b955d (#3475, 14:23Z; 14:52Z);
  - r10-review-dispatch-residue-p1 bb3933b1 (#3448, 08:24Z; 15:12Z);
  - r10-tick-residue-p2 1131843c (#3471, 13:17Z; 15:29Z);
  - r10-card-collapse 82e14f6d (#3441, 06:33Z; 16:05Z);
  - r10-sav-valuation-residue 611102f0 (#3442, 06:34Z; 16:35Z);
  - r10-outside-supply-stale-step b3b51d42 and 68646456 (#3457, branch fix/supply-stale-step-write,
    10:57Z; 13:24Z and 16:37Z);
  - r10-introduced-reds-barrier 537d9f04 (#3476, 15:47Z; 16:45Z).
- 8 of the 14 now have a `<topic> <head> <pr>` line in ~/.zcode/bus/rekeyed (for example :28
  codeql 04a1f28c 3467, :32 process-slim 9c5485e3 3451, :33 gh-read 01164518 3462). open_pr.sh
  had already run for each before that dispatch, so every one of those lines is a hand rekey.
  The other 6 have none.
- Held verdicts on the relay level (`grep handoff-verdict-held cloud-relay.log.level`): 4 OWED
  lines, among them probe/revt-r10-process-slim-p2-731821ba and r10-gh-read-residue-p2-02dc9ced
  (the two instances the proposal names: about 1.7 h and 4 h unposted) and
  r10-tick-residue-p2-1a9f4edd.
- Keying on the branch alone would miss some: #3457's branch is fix/supply-stale-step-write, not
  fix/r10-outside-supply-stale-step[-pr]. So the candidate "open PR on fix/<topic>[-pr]" misses 2
  of the 14 dispatches.
- What a local key would cover: 8 of the 14 dispatches are for a topic that already has a
  `rekeyed` line from an earlier dispatch (process-slim, relay-arm-order x2, codeql,
  train-residue, forkcap, review-dispatch-residue-p1, introduced-reds). For those the PR number
  is known from local state, with no API call.

The rule, run per instance:
- Measure: handoff dispatches whose verdict cannot post without a hand rekey. That is 14 of 42
  today (33%). The fix takes it to 0 for the 8 locally keyed dispatches, and to 0 for the other 6
  where the dispatcher names the PR. Each held verdict delays a merge verdict by hours (1.7 h and
  4 h measured).
- Severity: medium, R10-REVIEW-DISPATCH-RESIDUE's roster severity. That group owns bus.sh and the
  residue of R10-DISPATCH-AT-HANDOFF, the group that introduced dispatch-handoff.

Cost:
- About 15 lines in tools/audit/seat/bus.sh (dispatch_handoff) and two self-test assertions in
  its existing selftest. No new file and no new check.
- No API call on any relay pass. At most one PR lookup per dispatch, and only when local state
  has no PR.
- bus.sh and cloud_relay.sh have no row in tests/structure_budgets.json (`git show
  origin/main:tests/structure_budgets.json | grep -c 'bus.sh|cloud_relay'` gives 0), and the
  change moves no policy_budgets.json measure.
- Hot file bus.sh: the change is in the group's own seam (the handoff dispatch record), so the
  carry adds no new group and no new overlap.

Binding: a medium defect repair that also clears the 20% bar on its own measure (33%), at about
15 lines in a file its owning group already edits.

Bar: severity medium (R10-REVIEW-DISPATCH-RESIDUE). Figure: 14 of 42 handoff dispatches (33%),
over 20%, on the measure above. Basis: over-20%, and also a severity-exempt defect repair
(medium). It needs no start after the PR cap clears, because it is a carry on an in-progress
group.

Destination: append-carry on R10-REVIEW-DISPATCH-RESIDUE, with this text:

> HANDOFF-DISPATCH-AFTER-PR (triage P641). tools/audit/seat/bus.sh dispatch_handoff records only
> `topic:<topic>`. Only open_pr.sh runs `bus.sh rekey`, so a reviewer dispatched at the handoff
> after the PR already exists is never keyed to it, and cloud_relay.sh topic_verdict reports
> HELD-NOPR forever. On 2026-11-11 that was 14 of 42 handoff dispatches: 8 were re-keyed by hand
> and 6 were held (relay level handoff-verdict-held; #3451 about 1.7 h, #3462 about 4 h).
> Repair: after it records, dispatch_handoff re-keys the new record itself whenever the PR is
> known. That is (a) a `<topic> * <pr>` line already in <bus>/rekeyed, a local read, or (b) an
> explicit `--pr N`, which the dispatcher passes when it dispatches at a handoff for an open PR.
> Do not key only on fix/<topic>[-pr]: #3457's branch is fix/supply-stale-step-write. No API
> call per relay pass. Demonstration: the bus.sh selftest asserts that a second dispatch-handoff
> for a topic already re-keyed to #55 adds a `55 <head> ...` record and a rekeyed line, and that
> `--pr 56` keys a fresh topic. Both fail on the base and pass on the fix. Null control: a topic
> with no PR and no `--pr` stays `topic:`-only, so HELD-NOPR is unchanged.

